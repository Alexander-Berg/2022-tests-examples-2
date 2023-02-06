# pylint: disable=import-only-modules, import-error, redefined-outer-name

# pylint: disable=import-error
import json

import pytest

from tests_shuttle_control.utils import select_named


DRIVER_DBID_UUID_888 = (
    '11111111111111111111111111111111_88888888888888888888888888888888'
)
DRIVER_DBID_UUID_887 = (
    '11111111111111111111111111111111_88888888888888888888888888888887'
)
DRIVER_DBID_UUID_889 = (
    '11111111111111111111111111111111_88888888888888888888888888888889'
)
DRIVER_DBID_UUID_222 = (
    '11111111111111111111111111111111_22222222222222222222222222222222'
)
DRIVER_DBID_UUID_333 = (
    '11111111111111111111111111111111_33333333333333333333333333333333'
)

KNOWN_DRIVERS = [
    DRIVER_DBID_UUID_887,
    DRIVER_DBID_UUID_888,
    DRIVER_DBID_UUID_889,
    DRIVER_DBID_UUID_222,
]


@pytest.fixture
def external_mocks(mockserver):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _mock_driver_profiles(request):
        assert dict(request.args) == {'consumer': 'shuttle-control'}
        request = json.loads(request.get_data())
        return {
            'profiles': [
                {'park_driver_profile_id': dbid_uuid, 'data': {}}
                if dbid_uuid in KNOWN_DRIVERS
                else {'park_driver_profile_id': dbid_uuid}
                for dbid_uuid in request['id_in_set']
            ],
        }


def parsed(dbid_uuid):
    return f'({dbid_uuid[0:32]},{dbid_uuid[33:]})'


def get_driver_subs(shift_id, pgsql):
    db_drivers_ = select_named(
        'SELECT driver_id FROM state.drivers_workshifts_subscriptions '
        'WHERE workshift_id = \'' + shift_id + '\' AND is_active IS TRUE',
        pgsql['shuttle_control'],
    )
    db_drivers = []
    for db_driver in db_drivers_:
        driver_id = db_driver['driver_id']
        driver_id = driver_id[1 : len(driver_id) - 1]
        db_drivers.append(driver_id.replace(',', '_'))
    return db_drivers


@pytest.mark.now('2020-01-16T18:17:38+0000')
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.parametrize(
    'shift, drivers, sub_hash, status, error_code',
    [
        (
            '427a330d-2506-464a-accf-346b31e288b8',
            [DRIVER_DBID_UUID_887],
            '5287617810125887769',
            200,
            None,
        ),
        (
            '427a330d-2506-464a-accf-346b31e288b8',
            [DRIVER_DBID_UUID_888],
            '5287617810125887769',
            200,
            None,
        ),
        (
            '427a330d-2506-464a-accf-346b31e288b8',
            [DRIVER_DBID_UUID_888],
            '0',
            409,
            'WORKSHIFT_SUBSCRIPTIONS_CHANGED',
        ),
        (
            '427a330d-2506-464a-accf-346b31e28899',
            [DRIVER_DBID_UUID_888],
            '0',
            400,
            'NO_SUCH_WORKSHIFT',
        ),
        (
            '427a330d-2506-464a-accf-346b31e288b8',
            [DRIVER_DBID_UUID_889],
            '5287617810125887769',
            400,
            'WORKSHIFT_INTERSECTS',
        ),
        (
            '427a330d-2506-464a-accf-346b31e288c1',
            [DRIVER_DBID_UUID_888, DRIVER_DBID_UUID_889, DRIVER_DBID_UUID_887],
            '5287617810125887769',
            400,
            'TOO_MANY_DRIVERS',
        ),
        (
            '427a330d-2506-464a-accf-346b31e288b8',
            [DRIVER_DBID_UUID_888, DRIVER_DBID_UUID_888],
            '5287617810125887769',
            400,
            'SAME_DRIVER_IN_WORKSHIFT',
        ),
        (
            '427a330d-2506-464a-accf-346b31e288b8',
            ['11111111111111111111111111111111'],
            '5287617810125887769',
            400,
            'INVALID_DBID_UUID',
        ),
    ],
)
@pytest.mark.parametrize('is_check', [False, True])
async def test_main(
        taxi_shuttle_control,
        pgsql,
        external_mocks,
        shift,
        drivers,
        sub_hash,
        status,
        error_code,
        is_check,
):
    subs_before = get_driver_subs(shift, pgsql)
    uri = '/admin/shuttle-control/v1/shifts/item'
    if is_check:
        uri = uri + '/check'

    response = await taxi_shuttle_control.post(
        uri,
        json={
            'shifts': [
                {
                    'shift_id': shift,
                    'subscribed_drivers': drivers,
                    'subscriptions_hash': sub_hash,
                },
            ],
        },
    )
    assert response.status_code == status

    subs_after = get_driver_subs(shift, pgsql)
    if status != 200:
        assert response.json()['code'] == error_code
    if status == 200 and is_check is False:
        assert len(drivers) == len(subs_after)
        for i in drivers:
            assert i in subs_after
            subs_after.remove(i)
    else:
        assert len(subs_before) == len(subs_after)
        for i in subs_before:
            subs_after.remove(i)
    assert not subs_after


@pytest.mark.now('2020-01-16T18:17:38+0000')
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_unknown_driver(taxi_shuttle_control, pgsql, external_mocks):
    subs_before = get_driver_subs(
        '427a330d-2506-464a-accf-346b31e288b8', pgsql,
    )
    uri = '/admin/shuttle-control/v1/shifts/item/check'

    response = await taxi_shuttle_control.post(
        uri,
        json={
            'shifts': [
                {
                    'shift_id': '427a330d-2506-464a-accf-346b31e288b8',
                    'subscribed_drivers': [DRIVER_DBID_UUID_333],
                    'subscriptions_hash': '5287617810125887769',
                },
            ],
        },
    )
    assert response.status_code == 400
    assert response.json()['code'] == 'UNKNOWN_DRIVER'

    subs_after = get_driver_subs('427a330d-2506-464a-accf-346b31e288b8', pgsql)
    assert len(subs_before) == len(subs_after)
    for i in subs_before:
        subs_after.remove(i)
    assert not subs_after


@pytest.mark.now('2020-01-10T18:17:38+0000')
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.parametrize(
    'req, status, db_data',
    [
        (
            {
                'shifts': [
                    {
                        'shift_id': '427a330d-2506-464a-accf-346b31e288c1',
                        'subscribed_drivers': [DRIVER_DBID_UUID_887],
                        'subscriptions_hash': '18263137043306888377',
                    },
                    {
                        'shift_id': '427a330d-2506-464a-accf-346b31e288b8',
                        'subscribed_drivers': [DRIVER_DBID_UUID_887],
                        'subscriptions_hash': '5287617810125887769',
                    },
                ],
            },
            200,
            [
                {
                    'workshift_id': '427a330d-2506-464a-accf-346b31e288b8',
                    'driver_id': parsed(DRIVER_DBID_UUID_887),
                },
                {
                    'workshift_id': '427a330d-2506-464a-accf-346b31e288c2',
                    'driver_id': parsed(DRIVER_DBID_UUID_889),
                },
                {
                    'workshift_id': '427a330d-2506-464a-accf-346b31e288c1',
                    'driver_id': parsed(DRIVER_DBID_UUID_887),
                },
                {
                    'workshift_id': '427a330d-2506-464a-accf-346b31e288b9',
                    'driver_id': parsed(DRIVER_DBID_UUID_222),
                },
            ],
        ),
        (
            {
                'shifts': [
                    {
                        'shift_id': '427a330d-2506-464a-accf-346b31e288c1',
                        'subscribed_drivers': [DRIVER_DBID_UUID_889],
                        'subscriptions_hash': '18263137043306888377',
                    },
                    {
                        'shift_id': '427a330d-2506-464a-accf-346b31e288b8',
                        'subscribed_drivers': [DRIVER_DBID_UUID_889],
                        'subscriptions_hash': '5287617810125887769',
                    },
                    {
                        'shift_id': '427a330d-2506-464a-accf-346b31e288c2',
                        'subscribed_drivers': [DRIVER_DBID_UUID_889],
                        'subscriptions_hash': '5287617810125887770',
                    },
                ],
            },
            400,
            [
                {
                    'workshift_id': '427a330d-2506-464a-accf-346b31e288b8',
                    'driver_id': parsed(DRIVER_DBID_UUID_888),
                },
                {
                    'workshift_id': '427a330d-2506-464a-accf-346b31e288c1',
                    'driver_id': parsed(DRIVER_DBID_UUID_888),
                },
                {
                    'workshift_id': '427a330d-2506-464a-accf-346b31e288c2',
                    'driver_id': parsed(DRIVER_DBID_UUID_889),
                },
                {
                    'workshift_id': '427a330d-2506-464a-accf-346b31e288c1',
                    'driver_id': parsed(DRIVER_DBID_UUID_889),
                },
                {
                    'workshift_id': '427a330d-2506-464a-accf-346b31e288b9',
                    'driver_id': parsed(DRIVER_DBID_UUID_222),
                },
            ],
        ),
    ],
)
async def test_change_few_workshifts(
        taxi_shuttle_control, pgsql, external_mocks, req, status, db_data,
):
    response = await taxi_shuttle_control.post(
        '/admin/shuttle-control/v1/shifts/item', json=req,
    )
    assert response.status_code == status

    subs = select_named(
        'SELECT workshift_id, driver_id '
        'FROM state.drivers_workshifts_subscriptions '
        'WHERE is_active IS TRUE',
        pgsql['shuttle_control'],
    )
    assert len(subs) == len(db_data)
    for i in db_data:
        assert i in subs
        subs.remove(i)
    assert not subs


@pytest.mark.now('2020-01-18T18:17:38+0000')
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.parametrize('change', [False, True])
async def test_change_happened_shift(
        taxi_shuttle_control, external_mocks, change,
):
    response = await taxi_shuttle_control.post(
        '/admin/shuttle-control/v1/shifts/item',
        json={
            'shifts': [
                {
                    'shift_id': '427a330d-2506-464a-accf-346b31e288b8',
                    'subscribed_drivers': [
                        DRIVER_DBID_UUID_887
                        if change
                        else DRIVER_DBID_UUID_888,
                    ],
                    'subscriptions_hash': '5287617810125887769',
                },
            ],
        },
    )
    assert response.status == 400 if change else 200


@pytest.mark.now('2020-01-18T18:17:38+0000')
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_change_ongoing_sub(taxi_shuttle_control, external_mocks):
    response = await taxi_shuttle_control.post(
        '/admin/shuttle-control/v1/shifts/item',
        json={
            'shifts': [
                {
                    'shift_id': '427a330d-2506-464a-accf-346b31e288b9',
                    'subscribed_drivers': [],
                    'subscriptions_hash': '5016008118339644761',
                },
            ],
        },
    )
    assert response.status == 400
