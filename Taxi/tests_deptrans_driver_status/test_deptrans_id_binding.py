import pytest

from tests_deptrans_driver_status import utils

ENDPOINT = '/driver/v1/deptrans-status/v1/binding'


def _get_auth_headers(park_id, driver_id):
    return {
        'Accept-Language': 'ru',
        'X-YaTaxi-Park-Id': park_id,
        'X-YaTaxi-Driver-Profile-Id': driver_id,
        'X-Request-Application-Version': '9.60 (1234)',
    }


@pytest.mark.config(
    DEPTRANS_DRIVER_STATUS_PROFILE_TAGS={
        'approved': [],
        'temporary': [],
        'temporary_requested': [{'name': 'kis_art_temp_requested'}],
        'temporary_outdated': [],
        'failed': [],
    },
    DEPTRANS_DRIVER_STATUS_SUPPORTED_COUNTRIES={
        'supported_countries': ['rus', 'oth', 'blr'],
    },
    DEPTRANS_DRIVER_STATUS_IDENTITY_PASSPORTS={
        'passports': ['passport_rus', 'passport_blr'],
    },
    DEPTRANS_DRIVER_STATUS_LICENSE_PREFIXES=utils.license_prefixes(),
)
@pytest.mark.pgsql('deptrans_driver_status', files=['deptrans_profiles.sql'])
@pytest.mark.parametrize(
    [
        'park_id',
        'driver_id',
        'requested_deptrans_id',
        'after_binding_deptrans_id',
        'checking_deptrans_id',
        'request_temporary_id',
        'stq_deptrans_driver_status_bind_ids_called',
        'country_state',
        'passport',
        'passport_state',
        'expected_code',
    ],
    [
        pytest.param(
            'park2',
            'driver2',
            'some_id',
            'some_id',
            'some_id',
            False,
            True,
            'good',
            'passport_rus',
            'not necessary',
            200,
            id='New full',
        ),
        pytest.param(
            'park5',
            'driver1',
            'some_id',
            'some_id',
            'some_id',
            False,
            False,
            'not_supported_country',
            'passport_rus',
            'not necessary',
            200,
            id='Country is not in DEPTRANS_DRIVER_STATUS_SUPPORTED_COUNTRIES',
        ),
        pytest.param(
            'park3',
            'driver3',
            'some_id',
            'some_id',
            'some_id',
            False,
            False,
            'null_country',
            'passport_rus',
            'not necessary',
            200,
            id='Country is null',
        ),
        pytest.param(
            'park1',
            'driver1',
            '1',
            '1',
            None,
            False,
            False,
            'good',
            'passport_rus',
            'not necessary',
            200,
            id='Update full (only agreement)',
        ),
        pytest.param(
            'park1',
            'driver2',
            'some_id',
            'some_id',
            None,
            False,
            False,
            'good',
            'passport_rus',
            'not necessary',
            423,
            id='Trying update pending profile',
        ),
        pytest.param(
            'park3',
            'driver4',
            'other_id',
            '8',
            'some_id',
            False,
            False,
            'good',
            'passport_rus',
            'not necessary',
            423,
            id='Trying update pending temporary profile',
        ),
        pytest.param(
            'park2',
            'driver1',
            'some_id',
            '3',
            'some_id',
            False,
            True,
            'good',
            'passport_rus',
            'not necessary',
            200,
            id='Trying update temporary profile',
        ),
        pytest.param(
            'park2',
            'driver2',
            None,
            None,
            None,
            True,
            True,
            'good',
            'passport_rus',
            'exist',
            200,
            id='Request temporary. No profile before. Russian passport',
        ),
        pytest.param(
            'park2',
            'driver2',
            None,
            None,
            None,
            True,
            True,
            'good',
            'passport_blr',
            'exist',
            200,
            id='Request temporary. No profile before. Good passport',
        ),
        pytest.param(
            'park2',
            'driver2',
            None,
            None,
            None,
            True,
            True,
            'good',
            'sailor_rus',
            'exist',
            200,
            id='Request temporary. No profile before. Not a passport',
        ),
        pytest.param(
            'park2',
            'driver2',
            None,
            None,
            None,
            True,
            True,
            'good',
            '',
            'not checked',
            200,
            id='Request temporary. No profile before. Passport is not ready',
        ),
        pytest.param(
            'park1',
            'driver1',
            None,
            '1',
            None,
            True,
            True,
            'good',
            'passport_rus',
            'not necessary',
            409,
            id='Request temp for approved',
        ),
        pytest.param(
            'park1',
            'driver2',
            None,
            '2',
            '2',
            True,
            True,
            'good',
            'passport_rus',
            'not necessary',
            409,
            id='Request temp for pending',
        ),
        pytest.param(
            'park2',
            'driver1',
            None,
            '3',
            None,
            True,
            True,
            'good',
            'passport_rus',
            'not necessary',
            409,
            id='Request temp for temporary',
        ),
        pytest.param(
            'park3',
            'driver1',
            None,
            None,
            None,
            False,
            False,
            'good',
            'passport_rus',
            'not necessary',
            400,
            id='Client error',
        ),
        pytest.param(
            'park3',
            'driver1',
            None,
            None,
            None,
            None,
            True,
            'good',
            'passport_rus',
            'not necessary',
            400,
            id='Client error',
        ),
        pytest.param(
            'park6',
            'driver1',
            None,
            None,
            None,
            True,
            True,
            'good',
            'passport_blr',
            'exist',
            200,
            id='Request temporary. No profile before. '
            'Good passport and oth+prefix license',
        ),
        pytest.param(
            'park6',
            'driver2',
            None,
            None,
            None,
            True,
            True,
            'good',
            'passport_blr',
            'exist',
            200,
            id='Request temporary. No profile before. '
            'Good passport and rus+prefix license',
        ),
        pytest.param(
            'park6',
            'driver3',
            None,
            None,
            None,
            True,
            True,
            'null_country',
            'passport_blr',
            'exist',
            200,
            id='Request temporary. No profile before. Null license country',
        ),
        pytest.param(
            'park6',
            'driver4',
            None,
            None,
            None,
            True,
            True,
            'good',
            'passport_blr',
            'exist',
            200,
            id='Request temporary. No profile before. '
            'Oth license counry. No prefix',
        ),
    ],
)
async def test_set_deptrans_id(
        taxi_deptrans_driver_status,
        personal,
        mockserver,
        driver_profile,
        tags,
        client_notify,
        unique_drivers,
        pg_deptrans_driver_status,
        pg_deptrans_profile_status_logs,
        pgsql,
        stq,
        park_id,
        driver_id,
        requested_deptrans_id,
        after_binding_deptrans_id,
        checking_deptrans_id,
        request_temporary_id,
        stq_deptrans_driver_status_bind_ids_called,
        country_state,
        passport,
        passport_state,
        expected_code,
):
    @mockserver.json_handler('/quality-control/api/v1/data/confirmed')
    def _mock_quality_control(request):
        if passport_state == 'not necessary':
            return {}

        if passport_state == 'exist':
            return {'data': {'identity_id': passport}}

        # if passport_state == 'not checked':
        return {'data': {}}

    tags.add_tags('unique_driver_id_1', {'kis_art_temp_requested': {}})

    params = {}
    if request_temporary_id:
        params['request_temporary_id'] = request_temporary_id

    data = {'user_agreement_link': 'some_url'}
    if requested_deptrans_id:
        data['deptrans_id'] = requested_deptrans_id

    if country_state in {'not_supported_country', 'null_country'}:
        client_notify.set_message(country_state)

    if request_temporary_id:
        if passport_state == 'exist':
            if passport == 'passport_rus':
                client_notify.set_message('not_supported_passport_country')
            if passport == 'sailor_rus':
                client_notify.set_message('doc_is_not_passport')
        if passport_state == 'not checked':
            client_notify.set_message('passport_not_ready')

    license_pd_id = driver_profile(park_id, driver_id).license_pd_id
    initial_profile = pg_deptrans_driver_status.get_deptrans_profile(
        license_pd_id, pgsql,
    )

    response = await taxi_deptrans_driver_status.post(
        ENDPOINT,
        headers=_get_auth_headers(park_id, driver_id),
        params=params,
        json=data,
    )
    assert response.status_code == expected_code

    if expected_code == 200:

        if country_state in {'not_supported_country', 'null_country'}:
            assert client_notify.push.times_called == 1
        elif passport_state == 'exist':
            if passport == 'passport_rus':
                assert client_notify.push.times_called == 1
            if passport == 'sailor_rus':
                assert client_notify.push.times_called == 1
        elif passport_state == 'not checked':
            assert client_notify.push.times_called == 1

        else:

            assert pg_deptrans_driver_status.agreement_accepted(
                license_pd_id, 'some_url', pgsql,
            )

            if request_temporary_id:
                assert pg_deptrans_driver_status.request_exists(
                    park_id, driver_id, pgsql,
                )
                assert tags.assign.times_called == 1
                assert (
                    pg_deptrans_profile_status_logs.fetch_logs(
                        license_pd_id, pgsql,
                    )
                    == [
                        (
                            license_pd_id,
                            after_binding_deptrans_id,
                            'temporary_requested',
                        ),
                    ]
                )
            else:
                assert (
                    pg_deptrans_driver_status.get_deptrans_profile(
                        license_pd_id, pgsql,
                    )
                    == (
                        after_binding_deptrans_id,
                        None
                        if initial_profile is None
                        else initial_profile[1],
                        checking_deptrans_id,
                    )
                )
                assert (
                    stq.deptrans_driver_status_bind_ids.times_called
                    == stq_deptrans_driver_status_bind_ids_called
                )

                if stq_deptrans_driver_status_bind_ids_called:
                    response_kwargs = (
                        stq.deptrans_driver_status_bind_ids.next_call()[
                            'kwargs'
                        ]
                    )
                    response_kwargs.pop('log_extra')
                    assert response_kwargs == {
                        'deptrans_id': 'some_id',
                        'park_id': park_id,
                        'driver_profile_id': driver_id,
                        'taximeter_app': 'Taximeter 9.60 (1234)',
                        'accept_language': 'ru',
                    }
                    if (
                            initial_profile is None
                            or initial_profile[0] != after_binding_deptrans_id
                    ):
                        assert (
                            pg_deptrans_profile_status_logs.fetch_logs(
                                license_pd_id, pgsql,
                            )
                            == [
                                (
                                    license_pd_id,
                                    after_binding_deptrans_id,
                                    'pending'
                                    if initial_profile is None
                                    else initial_profile[1],
                                ),
                            ]
                        )

                assert tags.assign.times_called == 0
