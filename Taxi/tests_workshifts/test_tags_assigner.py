import datetime as dt
from typing import Any
from typing import Dict
from typing import List
from typing import Optional


import pytest
import pytz

_NOW = dt.datetime(2022, 1, 20, 10, 27, 13, tzinfo=pytz.timezone('UTC'))


def make_db_driver_workshift(workshift_id: str, tags_status: Optional[str]):
    result = {'workshift_id': workshift_id}

    if tags_status:
        result['subvention_tags_status'] = tags_status

    return result


def make_tags_request(tags):
    return {
        'append': [{'entity_type': 'dbid_uuid', 'tags': tags}],
        'provider_id': 'driver-workshifts-subventions',
    }


def find_workshifts_tags_status(mongodb):
    return list(
        mongodb.driver_workshifts.find(
            {}, {'workshift_id': 1, 'subvention_tags_status': 1, '_id': 0},
        ).sort('workshift_id', 1),
    )


@pytest.mark.config(
    WORKSHIFTS_DRIVER_TAGS_ASSIGN_WORKER={
        'is_enabled': True,
        'polling_delay_ms': 1,
        'chunk_size': 10,
        'max_workshift_age_h': 48,
    },
    WORKSHIFTS_SUBVENTIONS_RULES={
        'tariff_zones': {
            'penza': {
                'rules': [
                    {
                        'subvention_disable_type': 'subv_disable_nmfg',
                        'start_at': '2019-08-07T20:00:00+03:00',
                        'stop_at': '2020-08-07T20:00:00+03:00',
                    },
                    {
                        'subvention_disable_type': 'subv_disable_goal',
                        'start_at': '2021-08-07T20:00:00+03:00',
                    },
                ],
            },
        },
    },
)
@pytest.mark.parametrize(
    'expected_tags_status, expected_upload_tags_request',
    [
        pytest.param(
            [
                make_db_driver_workshift('workshift1', None),
                make_db_driver_workshift('workshift2', None),
                make_db_driver_workshift('workshift_from_past', None),
                make_db_driver_workshift('workshift_with_status', 'processed'),
            ],
            None,
            marks=[
                pytest.mark.config(
                    WORKSHIFTS_DRIVER_TAGS_ASSIGN_WORKER={
                        'is_enabled': False,
                        'polling_delay_ms': 1,
                        'chunk_size': 30,
                        'max_workshift_age_h': 24,
                    },
                ),
            ],
            id='disabled worker do nothing',
        ),
        pytest.param(
            [
                make_db_driver_workshift('workshift1', None),
                make_db_driver_workshift('workshift2', None),
                make_db_driver_workshift('workshift_from_past', 'ignored'),
                make_db_driver_workshift('workshift_with_status', 'processed'),
            ],
            None,
            marks=[
                pytest.mark.config(
                    WORKSHIFTS_DRIVER_TAGS_ASSIGN_WORKER={
                        'is_enabled': True,
                        'polling_delay_ms': 1,
                        'chunk_size': 1,
                        'max_workshift_age_h': 48,
                    },
                ),
            ],
            id='process not more chunk_size',
        ),
        pytest.param(
            [
                make_db_driver_workshift('workshift1', 'processed'),
                make_db_driver_workshift('workshift2', 'ignored'),
                make_db_driver_workshift('workshift_from_past', 'ignored'),
                make_db_driver_workshift('workshift_with_status', 'processed'),
            ],
            make_tags_request(
                [
                    {
                        'entity': 'dbid1_uuid1',
                        'name': 'subv_disable_goal',
                        'until': '2022-01-20T15:27:14.183+0000',
                    },
                ],
            ),
            id='process all workshifts',
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.filldb(driver_workshifts='tags_worker')
async def test_worker(
        taxi_workshifts,
        mockserver,
        testpoint,
        taxi_config,
        mongodb,
        driver_tags_mocks,
        expected_tags_status: List[Dict[str, Any]],
        expected_upload_tags_request: Dict[str, Any],
):
    @testpoint('driver-tags-assigner-testpoint')
    def tags_assigner_testpoint(arg):
        pass

    @mockserver.json_handler('/tags/v2/upload')
    def tags_upload_mock(request):
        return {'status': 'ok'}

    await taxi_workshifts.run_task('distlock/driver-tags-assigner')

    await tags_assigner_testpoint.wait_call()

    actual_tags_status = find_workshifts_tags_status(mongodb)

    assert actual_tags_status == expected_tags_status

    if expected_upload_tags_request:
        assert tags_upload_mock.times_called == 1
        upload_request = tags_upload_mock.next_call()['request']
        assert upload_request.json == expected_upload_tags_request
    else:
        assert tags_upload_mock.times_called == 0

    # in this test rules with tag condition not used, so must be no calls
    assert driver_tags_mocks.count_calls() == 0


@pytest.mark.config(
    WORKSHIFTS_DRIVER_TAGS_ASSIGN_WORKER={
        'is_enabled': True,
        'polling_delay_ms': 1,
        'chunk_size': 10,
        'max_workshift_age_h': 48,
    },
    WORKSHIFTS_SUBVENTIONS_RULES={
        'tariff_zones': {
            'penza': {
                'rules': [
                    {
                        'subvention_disable_type': 'subv_disable_goal',
                        'start_at': '2021-08-07T20:00:00+03:00',
                    },
                ],
            },
        },
    },
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.filldb(driver_workshifts='tags_worker')
async def test_worker_tags_upload_failed(
        taxi_workshifts, mockserver, testpoint, taxi_config, mongodb,
):
    @testpoint('driver-tags-assigner-testpoint')
    def tags_assigner_testpoint(arg):
        pass

    @mockserver.json_handler('/tags/v2/upload')
    def tags_upload_mock(request):
        raise mockserver.TimeoutError()

    await taxi_workshifts.run_task('distlock/driver-tags-assigner')

    await tags_assigner_testpoint.wait_call()

    assert tags_upload_mock.times_called == 1

    actual_tags_status = find_workshifts_tags_status(mongodb)

    expected_tags_status = [
        make_db_driver_workshift('workshift1', None),
        make_db_driver_workshift('workshift2', 'ignored'),
        make_db_driver_workshift('workshift_from_past', 'ignored'),
        make_db_driver_workshift('workshift_with_status', 'processed'),
    ]

    assert actual_tags_status == expected_tags_status


@pytest.mark.config(
    WORKSHIFTS_DRIVER_TAGS_ASSIGN_WORKER={
        'is_enabled': True,
        'polling_delay_ms': 1,
        'chunk_size': 10,
        'max_workshift_age_h': 48,
    },
    WORKSHIFTS_SUBVENTIONS_RULES={
        'tariff_zones': {
            'moscow': {
                'rules': [
                    {
                        'tag_condition': {'any_of': ['not_exists_tag']},
                        'subvention_disable_type': 'subv_disable_nmfg',
                        'start_at': '2019-08-07T20:00:00+03:00',
                    },
                    {
                        'tag_condition': {'any_of': ['some_tag']},
                        'subvention_disable_type': 'subv_disable_goal',
                        'start_at': '2019-08-07T20:00:00+03:00',
                    },
                ],
            },
            'penza': {
                'rules': [
                    {
                        'subvention_disable_type': 'subv_disable_goal',
                        'start_at': '2019-08-07T20:00:00+03:00',
                    },
                ],
            },
        },
    },
)
@pytest.mark.parametrize(
    'expected_tags_status',
    [
        pytest.param(
            [
                make_db_driver_workshift('workshift_1_moscow', 'ignored'),
                make_db_driver_workshift('workshift_2_moscow', 'ignored'),
                make_db_driver_workshift('workshift_3_penza', 'processed'),
            ],
            id='no tags',
        ),
        pytest.param(
            [
                make_db_driver_workshift('workshift_1_moscow', 'processed'),
                make_db_driver_workshift('workshift_2_moscow', 'ignored'),
                make_db_driver_workshift('workshift_3_penza', 'processed'),
            ],
            marks=pytest.mark.driver_tags_match(
                dbid='dbid1', uuid='uuid1', tags=['some_tag'],
            ),
            id='single tag',
        ),
        pytest.param(
            [
                make_db_driver_workshift('workshift_1_moscow', 'processed'),
                make_db_driver_workshift('workshift_2_moscow', 'processed'),
                make_db_driver_workshift('workshift_3_penza', 'processed'),
            ],
            marks=[
                pytest.mark.driver_tags_match(
                    dbid='dbid1', uuid='uuid1', tags=['some_tag'],
                ),
                pytest.mark.driver_tags_match(
                    dbid='dbid2', uuid='uuid2', tags=['some_tag'],
                ),
            ],
            id='multiple tags',
        ),
        pytest.param(
            [
                make_db_driver_workshift('workshift_1_moscow', None),
                make_db_driver_workshift('workshift_2_moscow', None),
                make_db_driver_workshift('workshift_3_penza', 'processed'),
            ],
            marks=[
                pytest.mark.driver_tags_error(
                    handler='/v1/drivers/match/profiles_fbs',
                    error_code=500,
                    error_message={'message': 'Server error', 'code': '500'},
                ),
            ],
            id='not process workshift on match tag error',
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.filldb(driver_workshifts='tags_worker_match_tags')
async def test_worker_driver_tags_rules(
        taxi_workshifts,
        mockserver,
        testpoint,
        taxi_config,
        mongodb,
        expected_tags_status: List[Dict[str, Any]],
):
    @testpoint('driver-tags-assigner-testpoint')
    def tags_assigner_testpoint(arg):
        pass

    @mockserver.json_handler('/tags/v2/upload')
    def _tags_upload_mock(request):
        return {'status': 'ok'}

    await taxi_workshifts.run_task('distlock/driver-tags-assigner')

    await tags_assigner_testpoint.wait_call()

    actual_tags_status = find_workshifts_tags_status(mongodb)

    expected_tags_status = expected_tags_status

    assert actual_tags_status == expected_tags_status
