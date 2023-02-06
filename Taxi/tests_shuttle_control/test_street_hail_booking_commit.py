# pylint: disable=import-only-modules, import-error, redefined-outer-name
import pytest

from tests_shuttle_control.utils import select_named


HEADERS = {
    'X-Request-Application': 'taximeter',
    'X-Request-Platform': 'android',
    'X-Request-Application-Version': '9.07',
    'X-YaTaxi-Park-Id': '111',
    'X-YaTaxi-Driver-Profile-Id': '888',
    'Accept-Language': 'ru',
}


@pytest.mark.now('2020-01-17T18:17:38+0000')
@pytest.mark.parametrize(
    'offer_id,shuttle_id,response_code',
    [
        ('2fef68c9-25d0-4174-9dd0-bdd1b3730775', 'gkZxnYQ73QGqrKyz', 200),
        ('2fef68c9-25d0-4174-9dd0-bdd1b3730777', 'Pmp80rQ23L4wZYxd', 200),
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730778',
            'gkZxnYQ73QGqrKyz',
            400,
        ),  # expired offer
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3738888',
            'VlAK13MzaLx6Bmnd',
            400,
        ),  # no seats available in shuttle
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730778',
            'gkZxnYQ73QGqrKyz',
            400,
        ),  # no such offer
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            'Pmp80rQ23L4wZYxd',
            400,
        ),  # wrong shuttle_id
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730780',
            'bjoAWlMYJRG14Nnm',
            400,
        ),  # for service booking only
    ],
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_main(
        taxi_shuttle_control,
        pgsql,
        experiments3,
        offer_id,
        shuttle_id,
        response_code,
):
    experiments3.add_experiment(
        name='shuttle_procaas_settings',
        consumers=['shuttle-control/create_booking'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/create_booking'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': {'processing_type': 'procaas'},
            },
        ],
    )

    for _ in range(2):
        response = await taxi_shuttle_control.post(
            '/driver/v1/shuttle-control/v1/street_hailing/commit_booking',
            headers=HEADERS,
            json={'offer_id': offer_id},
            params={'shuttle_id': shuttle_id},
        )
        assert response.status_code == response_code

        if response_code == 200:
            expected_num_passengers = (
                1 if shuttle_id == 'gkZxnYQ73QGqrKyz' else 2
            )

            generated_codes = response.json()['tickets']
            assert len(generated_codes) == expected_num_passengers
            assert generated_codes[0][:2] == 'A-'

            expected_response = {'tickets': generated_codes, 'items': []}
            generated_codes.sort()

            assert response.json() == expected_response

            rows = select_named(
                'SELECT booking_id, yandex_uid, user_id, shuttle_id, stop_id, '
                'dropoff_stop_id, shuttle_lap, dropoff_lap, offer_id, origin, '
                'status, processing_type '
                'FROM state.passengers '
                f'WHERE offer_id = \'{offer_id}\'',
                pgsql['shuttle_control'],
            )

            booking_id = rows[0]['booking_id']
            del rows[0]['booking_id']

            assert rows == [
                {
                    'yandex_uid': None,
                    'shuttle_id': 1 if shuttle_id == 'gkZxnYQ73QGqrKyz' else 2,
                    'stop_id': 5,
                    'dropoff_stop_id': 2,
                    'shuttle_lap': (
                        4 if shuttle_id == 'gkZxnYQ73QGqrKyz' else 2
                    ),
                    'dropoff_lap': (
                        5 if shuttle_id == 'gkZxnYQ73QGqrKyz' else 3
                    ),
                    'offer_id': offer_id,
                    'origin': 'street_hail',
                    'status': 'transporting',
                    'user_id': None,
                    'processing_type': 'procaas',
                },
            ]

            rows = select_named(
                f"""
                SELECT booking_id, code, status
                FROM state.booking_tickets
                WHERE booking_id = '{booking_id}'
                ORDER BY code
                """,
                pgsql['shuttle_control'],
            )
            assert rows[0] == {
                'booking_id': booking_id,
                'code': generated_codes[0],
                'status': 'confirmed',
            }

            if expected_num_passengers == 2:
                assert rows[1] == {
                    'booking_id': booking_id,
                    'code': generated_codes[1],
                    'status': 'confirmed',
                }

        else:
            assert (
                response.json()['message']
                == 'Этот вариант посадки уже недоступен'
            )
