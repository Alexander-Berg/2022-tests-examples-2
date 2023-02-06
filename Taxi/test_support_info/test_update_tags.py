# pylint: disable=redefined-outer-name
import datetime

import pytest

from taxi.util import dates

from support_info.crontasks import update_tags
from support_info.internal import update_tags as update_tags_int

NOW = datetime.datetime(2020, 1, 1, 0, 0)


@pytest.fixture
def mock_replication(mockserver):
    @mockserver.json_handler(
        '/replication/state/yt_target_info/support_chatterbox',
    )
    def _get_target_info(*args, **kwargs):
        return {
            'table_path': 'test_table_path',
            'full_table_path': 'test_table_path',
            'target_names': ['hahn', 'arnold'],
            'clients_delays': [
                {
                    'client_name': 'hahn',
                    'current_timestamp': dates.timestring(NOW),
                },
            ],
        }

    return _get_target_info


@pytest.fixture
def mock_yt_create_temp_table(patch):
    @patch('yt.wrapper.client.Yt.create_temp_table')
    def _dummy_create(
            path=None, prefix=None, attributes=None, expiration_timeout=None,
    ):
        return 'temp_table_name'

    return _dummy_create


@pytest.fixture
def mock_yt_remove(patch):
    @patch('yt.wrapper.client.Yt.remove')
    def _dummy_remove(table, force):
        pass

    return _dummy_remove


@pytest.fixture
def mock_yt_read_table(patch):
    @patch('yt.wrapper.client.Yt.read_table')
    def _dummy_read_table(table):
        return [
            {
                'field': 'udid',
                'value': 'some_unique_driver_id',
                'tag': 'chatterbox_tag_one',
                'until': 1577847600,
            },
            {
                'field': 'udid',
                'value': 'some_unique_driver_id',
                'tag': 'chatterbox_tag_three',
                'until': 1577847600,
            },
            {
                'field': 'user_phone_id',
                'value': '000000000000000000000001',
                'tag': 'chatterbox_tag_two',
                'until': 1577847600,
            },
            {
                'field': 'user_phone_id',
                'value': '000000000000000000000001',
                'tag': 'chatterbox_tag_four',
                'until': 1578625200,
            },
        ]

    return _dummy_read_table


@pytest.fixture
def mock_yt_run_map_reduce(patch):
    @patch('yt.wrapper.client.Yt.run_map_reduce')
    def _dummy_run_map_reduce(
            source_table,
            destination_table,
            reducer,
            reduce_by,
            sort_by,
            mapper=None,
            spec=None,
    ):
        pass

    return _dummy_run_map_reduce


@pytest.fixture
def mock_passenger_tags_upload(mockserver):
    @mockserver.json_handler('/passenger-tags/v1/upload')
    async def _tags_upload(request):
        return {}

    return _tags_upload


@pytest.fixture
def mock_tags_upload(mockserver):
    @mockserver.json_handler('/tags/v1/upload')
    async def _tags_upload(request):
        return {}

    return _tags_upload


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'row, expected_rows',
    [
        (
            {
                'created': datetime.datetime(2019, 12, 22, 3, 0).timestamp(),
                'meta_info': {
                    'unique_driver_id': 'some_unique_driver_id',
                    'user_phone_id': '000000000000000000000001',
                    'park_db_id': 'some_park_db_id',
                    'driver_uuid': 'some_driver_uuid',
                },
                'tags': ['адин', 'джва', 'три'],
            },
            [
                {
                    'field': 'user_phone_id',
                    'value': '000000000000000000000001',
                    'tag': 'just_one',
                    'created': datetime.datetime(
                        2019, 12, 22, 3, 0,
                    ).timestamp(),
                },
                {
                    'field': 'user_phone_id',
                    'value': '000000000000000000000001',
                    'tag': 'chatterbox_tag_two',
                    'created': datetime.datetime(
                        2019, 12, 22, 3, 0,
                    ).timestamp(),
                },
                {
                    'field': 'udid',
                    'value': 'some_unique_driver_id',
                    'tag': 'chatterbox_tag_one',
                    'created': datetime.datetime(
                        2019, 12, 22, 3, 0,
                    ).timestamp(),
                },
                {
                    'field': 'udid',
                    'value': 'some_unique_driver_id',
                    'tag': 'just_three',
                    'created': datetime.datetime(
                        2019, 12, 22, 3, 0,
                    ).timestamp(),
                },
            ],
        ),
        (
            {
                'created': datetime.datetime(2019, 12, 17, 3, 0).timestamp(),
                'meta_info': {'user_phone_id': '000000000000000000000001'},
                'tags': ['адин', 'джва', 'три'],
            },
            [
                {
                    'field': 'user_phone_id',
                    'value': '000000000000000000000001',
                    'tag': 'chatterbox_tag_two',
                    'created': datetime.datetime(
                        2019, 12, 17, 3, 0,
                    ).timestamp(),
                },
            ],
        ),
        (
            {
                'created': datetime.datetime(2019, 12, 17, 3, 0).timestamp(),
                'meta_info': {
                    'park_db_id': 'some_park_db_id',
                    'driver_uuid': 'some_driver_uuid',
                    'unique_driver_id': 'some_unique_driver_id',
                },
                'tags': ['адин', 'джва', 'три'],
            },
            [
                {
                    'field': 'udid',
                    'value': 'some_unique_driver_id',
                    'tag': 'chatterbox_tag_one',
                    'created': datetime.datetime(
                        2019, 12, 17, 3, 0,
                    ).timestamp(),
                },
            ],
        ),
        (
            {
                'created': datetime.datetime(2019, 12, 17, 2, 59).timestamp(),
                'meta_info': {
                    'user_phone_id': '000000000000000000000001',
                    'park_db_id': 'some_park_db_id',
                    'driver_uuid': 'some_driver_uuid',
                    'unique_driver_id': 'some_unique_driver_id',
                },
                'tags': ['адин', 'джва', 'три'],
            },
            [],
        ),
    ],
)
async def test_mapper(row, expected_rows):
    min_created = datetime.datetime.utcnow() - datetime.timedelta(days=15)
    mapper = update_tags_int.Mapper(
        min_created=min_created,
        client_tag_conditions=[
            {
                'tag': 'адин',
                'name': 'one',
                'external_tag': 'just_one',
                'day_limit': 10,
            },
            {'tag': 'джва', 'name': 'two', 'day_limit': 15},
        ],
        driver_tag_conditions=[
            {'tag': 'адин', 'name': 'one', 'day_limit': 15},
            {
                'tag': 'три',
                'name': 'three',
                'external_tag': 'just_three',
                'day_limit': 10,
            },
        ],
        tags_entity_mapping={
            'udid': '%(unique_driver_id)s',
            'user_phone_id': '%(user_phone_id)s',
        },
    )
    mapped_rows = [mapped_row for mapped_row in mapper(row)]
    assert mapped_rows == expected_rows


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'key, rows, expected_rows',
    [
        (
            {
                'field': 'udid',
                'value': 'some_unique_driver_id',
                'tag': 'chatterbox_tag_one',
            },
            [
                {
                    'field': 'udid',
                    'value': 'some_unique_driver_id',
                    'tag': 'chatterbox_tag_one',
                    'created': datetime.datetime(
                        2019, 12, 17, 3, 0,
                    ).timestamp(),
                },
                {
                    'field': 'udid',
                    'value': 'some_unique_driver_id',
                    'tag': 'chatterbox_tag_one',
                    'created': datetime.datetime(
                        2019, 12, 20, 3, 0,
                    ).timestamp(),
                },
                {
                    'field': 'udid',
                    'value': 'some_unique_driver_id',
                    'tag': 'chatterbox_tag_one',
                    'created': datetime.datetime(
                        2019, 12, 22, 3, 0,
                    ).timestamp(),
                },
            ],
            [
                {
                    'field': 'udid',
                    'value': 'some_unique_driver_id',
                    'tag': 'chatterbox_tag_one',
                    'until': 1578528000,
                },
            ],
        ),
        (
            {
                'field': 'user_phone_id',
                'value': '000000000000000000000001',
                'tag': 'two',
            },
            [
                {
                    'field': 'user_phone_id',
                    'value': '000000000000000000000001',
                    'tag': 'two',
                    'created': datetime.datetime(
                        2019, 12, 20, 3, 0,
                    ).timestamp(),
                },
            ],
            [],
        ),
    ],
)
async def test_reducer(key, rows, expected_rows):
    reducer = update_tags_int.Reducer(
        client_tag_conditions=[
            {
                'tag': 'адин',
                'name': 'one',
                'external_tag': 'just_one',
                'day_limit': 10,
                'threshold': 2,
            },
            {'tag': 'джва', 'name': 'two', 'threshold': 2, 'day_limit': 15},
        ],
        driver_tag_conditions=[
            {'tag': 'адин', 'name': 'one', 'threshold': 2, 'day_limit': 20},
            {
                'tag': 'три',
                'name': 'three',
                'external_tag': 'just_three',
                'day_limit': 5,
                'threshold': 2,
            },
        ],
    )
    reduced_rows = [row for row in reducer(key, rows)]
    assert reduced_rows == expected_rows


@pytest.mark.config(
    CHATTERBOX_TAGS_SERVICE_MAPPING={
        'udid': '%(unique_driver_id)s',
        'user_phone_id': '%(user_phone_id)s',
    },
    SUPPORT_INFO_PASSENGER_TAGS_UPLOAD_RULES=[
        {
            'external_tag': 'just_one',
            'tags': ['адин'],
            'day_limit': 10,
            'threshold': 2,
        },
        {
            'external_tag': 'chatterbox_tag_two',
            'tags': ['джва'],
            'day_limit': 10,
            'threshold': 2,
        },
        {
            'external_tag': 'chatterbox_tag_passenger_cancels_orders',
            'tags': ['dr_info_feedback_about_rider_excessive_cancellations'],
            'day_limit': 60,
            'threshold': 3,
        },
    ],
    SUPPORT_INFO_DRIVER_TAGS_UPLOAD_RULES=[
        {
            'external_tag': 'chatterbox_tag_one',
            'tags': ['адин'],
            'day_limit': 10,
            'threshold': 2,
        },
        {
            'external_tag': 'just_three',
            'tags': ['три'],
            'day_limit': 10,
            'threshold': 2,
        },
        {
            'external_tag': 'chatterbox_tag_driver_rudeness',
            'tags': ['rd_feedback_quality_professionalism_rude_driver'],
            'day_limit': 60,
            'threshold': 3,
        },
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_update_tags(
        support_info_context,
        loop,
        mock_replication,
        mock_yt_create_temp_table,
        mock_yt_run_map_reduce,
        mock_yt_read_table,
        mock_yt_remove,
        mock_tags_upload,
        mock_passenger_tags_upload,
):
    await update_tags.do_stuff(support_info_context, loop)

    map_reduce_call = mock_yt_run_map_reduce.calls[0]
    assert map_reduce_call['source_table'] == 'test_table_path'
    assert map_reduce_call['destination_table'] == 'temp_table_name'
    assert map_reduce_call['reduce_by'] == ['field', 'value', 'tag']
    assert map_reduce_call['sort_by'] == ['field', 'value', 'tag', 'created']

    assert isinstance(map_reduce_call['mapper'], update_tags_int.Mapper)
    assert map_reduce_call['mapper'].client_tag_conditions == {
        'just_one': {
            'tags': ['адин'],
            'external_tag': 'just_one',
            'day_limit': 10,
            'threshold': 2,
            'created_after_ts': 1576972800.0,
        },
        'chatterbox_tag_two': {
            'tags': ['джва'],
            'external_tag': 'chatterbox_tag_two',
            'threshold': 2,
            'day_limit': 10,
            'created_after_ts': 1576972800.0,
        },
        'chatterbox_tag_passenger_cancels_orders': {
            'external_tag': 'chatterbox_tag_passenger_cancels_orders',
            'tags': ['dr_info_feedback_about_rider_excessive_cancellations'],
            'day_limit': 60,
            'threshold': 3,
            'created_after_ts': 1572652800.0,
        },
    }
    assert map_reduce_call['mapper'].driver_tag_conditions == {
        'chatterbox_tag_one': {
            'tags': ['адин'],
            'external_tag': 'chatterbox_tag_one',
            'threshold': 2,
            'day_limit': 10,
            'created_after_ts': 1576972800.0,
        },
        'just_three': {
            'tags': ['три'],
            'external_tag': 'just_three',
            'day_limit': 10,
            'threshold': 2,
            'created_after_ts': 1576972800.0,
        },
        'chatterbox_tag_driver_rudeness': {
            'external_tag': 'chatterbox_tag_driver_rudeness',
            'tags': ['rd_feedback_quality_professionalism_rude_driver'],
            'day_limit': 60,
            'threshold': 3,
            'created_after_ts': 1572652800.0,
        },
    }

    assert isinstance(map_reduce_call['reducer'], update_tags_int.Reducer)
    assert map_reduce_call['reducer'].client_tag_conditions == {
        'just_one': {
            'tags': ['адин'],
            'external_tag': 'just_one',
            'day_limit': 10,
            'threshold': 2,
            'created_after_ts': 1576972800.0,
        },
        'chatterbox_tag_two': {
            'tags': ['джва'],
            'external_tag': 'chatterbox_tag_two',
            'threshold': 2,
            'day_limit': 10,
            'created_after_ts': 1576972800.0,
        },
        'chatterbox_tag_passenger_cancels_orders': {
            'external_tag': 'chatterbox_tag_passenger_cancels_orders',
            'tags': ['dr_info_feedback_about_rider_excessive_cancellations'],
            'day_limit': 60,
            'threshold': 3,
            'created_after_ts': 1572652800.0,
        },
    }
    assert map_reduce_call['reducer'].driver_tag_conditions == {
        'chatterbox_tag_one': {
            'tags': ['адин'],
            'external_tag': 'chatterbox_tag_one',
            'threshold': 2,
            'day_limit': 10,
            'created_after_ts': 1576972800.0,
        },
        'just_three': {
            'tags': ['три'],
            'external_tag': 'just_three',
            'day_limit': 10,
            'threshold': 2,
            'created_after_ts': 1576972800.0,
        },
        'chatterbox_tag_driver_rudeness': {
            'external_tag': 'chatterbox_tag_driver_rudeness',
            'tags': ['rd_feedback_quality_professionalism_rude_driver'],
            'day_limit': 60,
            'threshold': 3,
            'created_after_ts': 1572652800.0,
        },
    }

    passenger_tags_upload_call = mock_passenger_tags_upload.next_call()
    assert passenger_tags_upload_call['request'].json == {
        'merge_policy': 'append',
        'entity_type': 'user_phone_id',
        'tags': [
            {
                'name': 'chatterbox_tag_two',
                'match': {
                    'id': '000000000000000000000001',
                    'until': '2020-01-01T04:00:00+0000',
                },
            },
            {
                'name': 'chatterbox_tag_four',
                'match': {
                    'id': '000000000000000000000001',
                    'until': '2020-01-06T01:00:00+0000',
                },
            },
        ],
    }

    tags_upload_call = mock_tags_upload.next_call()
    assert tags_upload_call['request'].json == {
        'merge_policy': 'append',
        'entity_type': 'udid',
        'tags': [
            {
                'name': 'chatterbox_tag_one',
                'match': {
                    'id': 'some_unique_driver_id',
                    'until': '2020-01-01T04:00:00+0000',
                },
            },
            {
                'name': 'chatterbox_tag_three',
                'match': {
                    'id': 'some_unique_driver_id',
                    'until': '2020-01-01T04:00:00+0000',
                },
            },
        ],
    }
