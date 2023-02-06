# pylint: disable=redefined-outer-name
import pytest

from contractor_permits.generated.cron import run_cron
from contractor_permits.integration import api_integration
from contractor_permits.logic import lv_block
from test_contractor_permits.cron import atd_responses


def return_mock_atd_response(data, atd_failed, mockserver):
    if 'ValidTaxiDrivingLicenses' in data:
        if atd_failed:
            return mockserver.make_response(
                atd_responses.VALID_TAXI_DRIVING_LICENSE['REJECT_ALL'],
            )
        return mockserver.make_response(
            atd_responses.VALID_TAXI_DRIVING_LICENSE['OK'],
        )
    if 'ValidVehicleDocument' in data:
        if atd_failed:
            return mockserver.make_response(
                atd_responses.VALID_VEHICLE_DOCUMENT['NOT_FOUND'],
            )
        if 'T3PERMITEXPIRED' in data:
            return mockserver.make_response(
                atd_responses.VALID_VEHICLE_DOCUMENT['NOT_FOUND'],
            )
        if 'T1' in data:
            return mockserver.make_response(
                atd_responses.VALID_VEHICLE_DOCUMENT['OK'],
            )
        if 'TQ2' in data:
            return mockserver.make_response(
                atd_responses.VALID_VEHICLE_DOCUMENT['OK'],
            )
    raise Exception('Unrecognised method call on ATD mock')


@pytest.mark.parametrize('do_block_drivers', (True, False))
@pytest.mark.parametrize('atd_failed', (True, False))
@pytest.mark.now('2018-06-29 08:15:27.243860')
async def test_latvia(
        mock_driver_profiles_ctx,
        mock_tags_ctx,
        mock_fleet_vehicles_ctx,
        mock_personal_ctx,
        mock_csdd_ctx,
        mockserver,
        proxy_in_secdist,
        taxi_config,
        do_block_drivers,
        atd_failed,
):
    taxi_config.set_values(
        {
            'CONTRACTOR_PERMITS_LV_SETTINGS': {
                'enabled': True,
                'lv_parks': ['dbid1'],
                'atd_settings': {'throttling': 1, 'do_log_responses': True},
                'csdd_settings': {'throttling': 1, 'do_block': True},
                'proxy_settings': {'host': '', 'port': 0, 'use_proxy': False},
                'lv_driver_licences_prefix': 'LAT',
                'yellow_license_plates_prefix': ['TQ', 'TX', 'EX', 'TE'],
                'do_block_drivers': do_block_drivers,
                'blocking_tag': 'driver',
                'blocking_tag_car': 'car',
                'tags_chunk_size': 2,
                'ignore_driver_license_mismatch': ['TV-7'],
                'block_limit_percent_driver': 80,
                'block_limit_percent_car': 80,
            },
        },
    )

    @mockserver.handler('atd-api')
    async def _atd_handler(request):
        data = request.get_data().decode('utf-8')
        if 'Authorization' in data:
            assert 'atd_username' in data
            assert 'atd_password' in data
            return mockserver.make_response(
                atd_responses.AUTHORIZATION['SUCCESS'],
            )
        assert 'valid_session_key' in data  # The request is authorized
        return return_mock_atd_response(data, atd_failed, mockserver)

    await run_cron.main(['contractor_permits.crontasks.latvia', '-t', '0'])

    assert mock_personal_ctx.handler.times_called == 1
    assert mock_fleet_vehicles_ctx.handler.times_called == 1

    if do_block_drivers and not atd_failed:
        assert mock_tags_ctx.handler.times_called == 11

        assert sorted(mock_tags_ctx.blocked_drivers) == sorted(
            ['dbid1_uuid2', 'dbid1_uuid4', 'dbid1_uuid5'],
        )
        assert sorted(mock_tags_ctx.blocked_cars) == sorted(
            ['dbid1_car_id_3', 'dbid1_car_id_10'],
        )
        assert sorted(mock_tags_ctx.unblocked_drivers) == sorted(
            [
                'dbid1_uuid1',
                'dbid1_uuid3',
                'dbid1_uuid6',
                'dbid1_uuid7',
                'dbid1_uuid8',
                'dbid1_uuid9',
                'dbid1_uuid10',
                'dbid1_uuid11',
            ],
        )
        assert sorted(mock_tags_ctx.unblocked_cars) == sorted(
            [
                'dbid1_car_id_1',
                'dbid1_car_id_2',
                'dbid1_car_id_4',
                'dbid1_car_id_5',
                'dbid1_car_id_6',
                'dbid1_car_id_7',
                'dbid1_car_id_8',
                'dbid1_car_id_9',
            ],
        )

        # Just in case - this should not be touched
        assert (
            'dbid1_car_id_11' not in mock_tags_ctx.unblocked_cars
            and 'dbid1_car_id_11' not in mock_tags_ctx.blocked_cars
        )
    else:
        assert mock_tags_ctx.handler.times_called == 0


@pytest.mark.now('2018-06-29 08:15:27.243860')
@pytest.mark.config(
    CONTRACTOR_PERMITS_LV_SETTINGS={
        'enabled': True,
        'lv_parks': ['dbid1'],
        'atd_settings': {'throttling': 1, 'do_log_responses': True},
        'csdd_settings': {'throttling': 1, 'do_block': True},
        'proxy_settings': {'host': '', 'port': 0, 'use_proxy': False},
        'lv_driver_licences_prefix': 'LAT',
        'yellow_license_plates_prefix': ['TQ', 'TX', 'EX', 'TE'],
        'do_block_drivers': True,
        'blocking_tag': 'driver',
        'blocking_tag_car': 'car',
        'tags_chunk_size': 2,
        'ignore_driver_license_mismatch': ['TV-7'],
    },
)
async def test_token_refresh(
        mock_driver_profiles_ctx,
        mock_tags_ctx,
        mock_fleet_vehicles_ctx,
        mock_personal_ctx,
        mock_csdd_ctx,
        mockserver,
        proxy_in_secdist,
):
    mock_atd_state = 'ok'

    @mockserver.handler('atd-api')
    async def _atd_handler(request):
        nonlocal mock_atd_state
        data = request.get_data().decode('utf-8')
        if 'Authorization' in data:
            assert 'atd_username' in data
            assert 'atd_password' in data
            mock_atd_state = 'ok'
            return mockserver.make_response(
                atd_responses.AUTHORIZATION['SUCCESS'],
            )
        assert 'valid_session_key' in data  # The request is authorized
        if mock_atd_state == 'ok':
            mock_atd_state = 'token_expired'
            return return_mock_atd_response(data, False, mockserver)
        if mock_atd_state == 'token_expired':
            if 'ValidTaxiDrivingLicense' in data:
                return mockserver.make_response(
                    atd_responses.VALID_TAXI_DRIVING_LICENSE['EXPIRED_TOKEN'],
                    status=500,
                )
            return mockserver.make_response(
                atd_responses.VALID_VEHICLE_DOCUMENT['EXPIRED_TOKEN'],
                status=500,
            )
        assert False

    await run_cron.main(['contractor_permits.crontasks.latvia', '-t', '0'])

    assert mock_tags_ctx.handler.times_called == 11
    assert len(mock_tags_ctx.blocked_drivers) == 3
    assert len(mock_tags_ctx.blocked_cars) == 2
    assert len(mock_tags_ctx.unblocked_drivers) == 8
    assert len(mock_tags_ctx.unblocked_cars) == 8


@pytest.mark.config(
    CONTRACTOR_PERMITS_LV_SETTINGS={
        'enabled': False,
        'lv_parks': ['dbid1'],
        'atd_settings': {'throttling': 1},
        'csdd_settings': {'throttling': 1, 'do_block': True},
        'proxy_settings': {'host': '', 'port': 0, 'use_proxy': False},
        'lv_driver_licences_prefix': 'LAT',
        'yellow_license_plates_prefix': ['TQ', 'TX', 'EX', 'TE'],
        'do_block_drivers': True,
        'blocking_tag': 'driver',
    },
)
@pytest.mark.now('2018-06-29 08:15:27.243860')
async def test_latvia_disabled(
        mock_driver_profiles, mockserver, proxy_in_secdist,
):
    @mock_driver_profiles('/v1/driver/profiles/retrieve_by_park_id')
    async def _mocked_dp_handler(request):
        assert False

    await run_cron.main(['contractor_permits.crontasks.latvia', '-t', '0'])


def test_chunk_func():
    assert list(
        lv_block.iterables_in_chunks(
            range(1, 4), [], range(4, 8), chunk_size=2,
        ),
    ) == [[[1, 2], [], []], [[3], [], [4]], [[], [], [5, 6]], [[], [], [7]]]
    assert list(lv_block.iterables_in_chunks(chunk_size=2)) == []


def test_car_plates_normalization_func():
    assert api_integration.clean_car_plate('TQ4423') == 'TQ4423'
    assert api_integration.clean_car_plate('tq-4412') == 'TQ4412'
    assert (
        api_integration.clean_car_plate(' ABZ09tq-44 1 2 !\t') == 'ABZ09TQ4412'
    )


def test_should_block():
    config = {
        'do_block_drivers': True,
        'block_limit_percent_driver': 74,
        'block_limit_percent_car': 74,
    }
    assert lv_block.should_block(
        config,
        drivers_to_block=[''] * 74,
        drivers_to_unblock=[''] * 26,
        drivers_to_ignore=[''] * 0,
        cars_to_block=[''] * 0,
        cars_to_unblock=[''] * 1,
        cars_to_ignore=[''] * 0,
    )
    assert not lv_block.should_block(
        config,
        drivers_to_block=[''] * 75,
        drivers_to_unblock=[''] * 25,
        drivers_to_ignore=[''] * 0,
        cars_to_block=[''] * 0,
        cars_to_unblock=[''] * 1,
        cars_to_ignore=[''] * 0,
    )
    assert lv_block.should_block(
        config,
        drivers_to_block=[''] * 0,
        drivers_to_unblock=[''] * 1,
        drivers_to_ignore=[''] * 0,
        cars_to_block=[''] * 74,
        cars_to_unblock=[''] * 26,
        cars_to_ignore=[''] * 0,
    )
    assert not lv_block.should_block(
        config,
        drivers_to_block=[''] * 0,
        drivers_to_unblock=[''] * 1,
        drivers_to_ignore=[''] * 0,
        cars_to_block=[''] * 75,
        cars_to_unblock=[''] * 25,
        cars_to_ignore=[''] * 0,
    )
