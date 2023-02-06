# pylint: disable=too-many-lines
from typing import List

from aiohttp import web
import asyncpg
import pytest

from taxi.pg import pool as pool_module

from taxi_antifraud.generated.cron import run_cron
from test_taxi_antifraud.cron.utils import mock as mock_module

YT_DIRECTORY_PATH = '//home/taxi-fraud/unittests/kopatel'
YT_TABLE_PATH = YT_DIRECTORY_PATH + '/driver_communication'

PG_DATABASE_NAME = 'antifraud_py'
CURSOR_STATE_NAME = 'driver_communication_cursor'


async def _insert_to_state_table(pool: pool_module.Pool) -> None:
    query = """
        insert into
            crontasks_common.cronstate
        values
            ('driver_communication_cursor', 0);
        """
    async with pool.acquire() as connection:
        await connection.execute(query)


async def _extract_records(pool: pool_module.Pool) -> List[asyncpg.Record]:
    query = """
        select
            *
        from
            crontasks_common.cronstate
        """
    async with pool.acquire() as connection:
        return await connection.fetch(query)


async def _prepare_data(data, yt_client, master_pool):
    await _insert_to_state_table(master_pool)
    yt_client.create(
        'map_node',
        path=YT_DIRECTORY_PATH,
        recursive=True,
        ignore_existing=True,
    )
    yt_client.write_table(YT_TABLE_PATH, data)


async def mock(mock_taxi_driver_wall, mock_driver_profiles):
    @mock_taxi_driver_wall('/internal/driver-wall/v1/add')
    async def _driver_wall_add(request):
        return web.json_response({'id': 'some_id'})

    @mock_driver_profiles('/v1/driver/app/profiles/retrieve')
    async def _retrieve(request):
        ids = request.json['id_in_set']
        return {
            'profiles': [
                {'data': {'locale': 'ru'}, 'park_driver_profile_id': id_}
                for id_ in ids
            ],
        }

    return _driver_wall_add, _retrieve


@pytest.mark.translations(
    taximeter_backend_driver_messages={
        'service_standards_violation': {
            'ru': 'Нарушение сервисных стандартов.',
        },
        'parameters_string': {
            'ru': '%(username)s, не превышайте скорость на дорогах города %(city)s',  # noqa: E501 pylint: disable=line-too-long
        },
    },
    taximeter_messages={
        'imagine_dragons_song': {'ru': 'It\'s %(subject)s to %(action)s'},
    },
)
@pytest.mark.config(
    AFS_CRON_DRIVER_COMMUNICATION_ENABLED=True,
    AFS_CRON_DRIVER_COMMUNICATION_INPUT_TABLE_SUFFIX='kopatel/driver_communication',  # noqa: E501 pylint: disable=line-too-long
    AFS_CRON_DRIVER_COMMUNICATION_SEND_BATCHES_SIZE_OF_BATCH=1,
    AFS_CRON_DRIVER_COMMUNICATION_SLEEP_TIME_SECONDS=0.01,
)
@pytest.mark.parametrize(
    'data,expected_requests',
    [
        (
            [
                {
                    'driver_uuid': '891ad56ed7123ac829ef4829af245ead',
                    'db_id': '678123',
                    'title': 'Warning about fraud',
                    'text': 'Please, do not fraud anymore!',
                },
                {
                    'driver_uuid': '827abc711d98283f01a23c74837acd98',
                    'db_id': '712982',
                    'title': 'Tunker message',
                    'text': {
                        'keyset': 'taximeter_backend_driver_messages',
                        'key': 'service_standards_violation',
                    },
                },
                {
                    'driver_uuid': '4897b74ae86649018ab2b71e56595d73',
                    'db_id': '491283',
                    'title': 'Tanker parametrized message',
                    'text': {
                        'keyset': 'taximeter_backend_driver_messages',
                        'key': 'parameters_string',
                    },
                    'text_parameters': {'username': 'Иван', 'city': 'Барнаул'},
                },
                {
                    'driver_uuid': '4897b74ae86649018ab2b71e56595d73',
                    'db_id': '491283',
                    'title': '%(name)s shrugged',
                    'title_parameters': {'name': 'Atlas'},
                    'text': {
                        'keyset': 'taximeter_messages',
                        'key': 'imagine_dragons_song',
                    },
                    'text_parameters': {'subject': 'time', 'action': 'begin'},
                    'format': 'Raw',
                },
                {
                    'driver_uuid': '78adb5cd9023ef018ab2b71e56595d73',
                    'db_id': '891283',
                    'text': '%(name)s %(surname)s is %(state)s',
                    'text_parameters': {
                        'name': 'Vladimir',
                        'surname': 'Putin',
                        'state': 'President Mira',
                    },
                    'title': {
                        'keyset': 'taximeter_messages',
                        'key': 'imagine_dragons_song',
                    },
                    'title_parameters': {
                        'subject': 'my kingdom',
                        'action': 'come!',
                        'odd_parameter': 'Stuff',
                    },
                    'format': 'Markdown',
                },
            ],
            [
                {
                    'id': 'kopatel_driver_communication_e3c1f81207bcd94e905ee98feeb44417',  # noqa: E501 pylint: disable=line-too-long
                    'drivers': [
                        {
                            'driver': (
                                '678123_891ad56ed7123ac829ef4829af245ead'
                            ),
                            'title': 'Warning about fraud',
                            'text': 'Please, do not fraud anymore!',
                            'format': 'Raw',
                            'alert': False,
                        },
                    ],
                    'template': {},
                    'application': 'taximeter',
                },
                {
                    'id': 'kopatel_driver_communication_3343af41abb7ad3452f24ae4fcf587f9',  # noqa: E501 pylint: disable=line-too-long
                    'drivers': [
                        {
                            'driver': (
                                '712982_827abc711d98283f01a23c74837acd98'
                            ),
                            'title': 'Tunker message',
                            'text': 'Нарушение сервисных стандартов.',
                            'format': 'Raw',
                            'alert': False,
                        },
                    ],
                    'template': {},
                    'application': 'taximeter',
                },
                {
                    'id': 'kopatel_driver_communication_b24930c84979179bf34891d1c1c0f756',  # noqa: E501 pylint: disable=line-too-long
                    'drivers': [
                        {
                            'driver': (
                                '491283_4897b74ae86649018ab2b71e56595d73'
                            ),
                            'title': 'Tanker parametrized message',
                            'text': 'Иван, не превышайте скорость на дорогах города Барнаул',  # noqa: E501 pylint: disable=line-too-long
                            'format': 'Raw',
                            'alert': False,
                        },
                    ],
                    'template': {},
                    'application': 'taximeter',
                },
                {
                    'id': 'kopatel_driver_communication_45c925f23ea59075b9ce21032cd2527f',  # noqa: E501 pylint: disable=line-too-long
                    'drivers': [
                        {
                            'driver': (
                                '491283_4897b74ae86649018ab2b71e56595d73'
                            ),
                            'title': 'Atlas shrugged',
                            'text': 'It\'s time to begin',
                            'format': 'Raw',
                            'alert': False,
                        },
                    ],
                    'template': {},
                    'application': 'taximeter',
                },
                {
                    'id': 'kopatel_driver_communication_98690a7b1db8662f2c5b11501b0f7531',  # noqa: E501 pylint: disable=line-too-long
                    'drivers': [
                        {
                            'driver': (
                                '891283_78adb5cd9023ef018ab2b71e56595d73'
                            ),
                            'title': 'It\'s my kingdom to come!',
                            'text': 'Vladimir Putin is President Mira',
                            'format': 'Markdown',
                            'alert': False,
                        },
                    ],
                    'template': {},
                    'application': 'taximeter',
                },
            ],
        ),
    ],
)
async def test_cron(
        mock_taxi_driver_wall,
        mock_driver_profiles,
        yt_client,
        cron_context,
        data,
        expected_requests,
):

    _driver_wall_add, _retrieve = await mock(
        mock_taxi_driver_wall, mock_driver_profiles,
    )
    processed_records = len(data)

    master_pool = cron_context.pg.master_pool
    await _prepare_data(data, yt_client, master_pool)

    await run_cron.main(
        ['taxi_antifraud.crontasks.driver_communication', '-t', '0'],
    )

    got_requests = mock_module.get_requests(_driver_wall_add)

    assert got_requests == expected_requests

    assert await _extract_records(master_pool) == [
        (CURSOR_STATE_NAME, str(processed_records)),
    ]


@pytest.mark.translations(
    taximeter_backend_driver_messages={
        'parameters_string': {
            'ru': '%(username)s, не превышайте скорость на дорогах города %(city)s',  # noqa: E501 pylint: disable=line-too-long
        },
        'empty': {'ru': ''},
    },
)
@pytest.mark.config(
    AFS_CRON_DRIVER_COMMUNICATION_ENABLED=True,
    AFS_CRON_DRIVER_COMMUNICATION_INPUT_TABLE_SUFFIX='kopatel/driver_communication',  # noqa: E501 pylint: disable=line-too-long
    AFS_CRON_DRIVER_COMMUNICATION_SEND_BATCHES_SIZE_OF_BATCH=1,
    AFS_CRON_DRIVER_COMMUNICATION_SLEEP_TIME_SECONDS=0.01,
)
@pytest.mark.parametrize(
    'data,expected_error_message',
    [
        (
            [
                {
                    'driver_uuid': '891ad56ed7123ac829ef4829af245ead',
                    'title': 'Title',
                    'text': 'Text',
                },
            ],
            'db_id is empty',
        ),
        (
            [
                {
                    'driver_uuid': '',
                    'db_id': '555555',
                    'title': 'Title',
                    'text': 'Text',
                },
            ],
            'driver_uuid is empty',
        ),
        (
            [
                {
                    'driver_uuid': '827abc711d98283f01a23c74837acd98',
                    'db_id': '712982',
                    'title': 'Title',
                },
            ],
            'text is empty',
        ),
        (
            [
                {
                    'driver_uuid': '4897b74ae86649018ab2b71e56595d73',
                    'db_id': '491283',
                    'title': {
                        'keyset': 'taximeter_backend_driver_messages',
                        'key': 'parameters_string',
                    },
                    'text': 'immortale',
                    'title_parameters': {'username': 'Иван'},
                },
            ],
            'Impossible to insert parameters into \'%\\(username\\)s, не '
            'превышайте скорость на дорогах города %\\(city\\)s\': there is no'
            ' \'city\' among parameters: {\'username\': \'Иван\'}',
        ),
        (
            [
                {
                    'driver_uuid': '4897b74ae86649018ab2b71e56595d73',
                    'db_id': '491283',
                    'title': 'Atlas shrugged',
                    'text': {'keyset': 'taximeter_backend_driver_messages'},
                },
            ],
            'Key is not defined in {\'keyset\': \'taximeter_backend_driver_messages\'}',  # noqa: E501 pylint: disable=line-too-long
        ),
        (
            [
                {
                    'driver_uuid': '4897b74ae86649018ab2b71e56595d73',
                    'db_id': '491283',
                    'title': 'Atlas shrugged',
                    'text': {'key': 'some_key'},
                },
            ],
            'Keyset is not defined in {\'key\': \'some_key\'}',
        ),
        (
            [
                {
                    'driver_uuid': '4897b74ae86649018ab2b71e56595d73',
                    'db_id': '491283',
                    'title': 'Atlas shrugged',
                    'text': {'keyset': 'stuff', 'key': 'second_stuff'},
                },
            ],
            'There is no keyset \'stuff\' in taxi-antifraud service',
        ),
        (
            [
                {
                    'driver_uuid': '78adb5cd9023ef018ab2b71e56595d73',
                    'db_id': '891283',
                    'text': 'May today',
                    'title': 4567,
                },
            ],
            'Inappropriate type of translated text: 4567',
        ),
        (
            [
                {
                    'driver_uuid': '891ad56ed7123ac829ef4829af245ead',
                    'db_id': '678123',
                    'title': 'Title for empty text',
                    'text': {
                        'keyset': 'taximeter_backend_driver_messages',
                        'key': 'empty',
                    },
                    'text_parameters': {},
                },
            ],
            'translated text is empty',
        ),
        (
            [
                {
                    'driver_uuid': '891ad56ed7123ac829ef4829af245ead',
                    'db_id': '678123',
                    'title': '',
                    'text': {
                        'keyset': 'taximeter_backend_driver_messages',
                        'key': 'empty',
                    },
                    'text_parameters': {},
                },
            ],
            'title is empty',
        ),
        (
            [
                {
                    'driver_uuid': '891ad56ed7123ac829ef4829af245ead',
                    'db_id': '678123',
                    'title': {
                        'keyset': 'taximeter_backend_driver_messages',
                        'key': 'empty',
                    },
                    'text': '%(name)s',
                    'text_parameters': {'name': 'Иван'},
                },
            ],
            'translated title is empty',
        ),
        (
            [
                {
                    'driver_uuid': '891ad56ed7123ac829ef4829af245ead',
                    'db_id': '678123',
                    'title': {
                        'keyset': 'taximeter_backend_driver_messages',
                        'key': 'empty',
                    },
                    'text': '%(name)',
                    'text_parameters': {'name': 'Иван'},
                },
            ],
            'Incomplete formatting of translated string: \'%\\(name\\)\'',
        ),
        (
            [
                {
                    'driver_uuid': 'some_uuid',
                    'db_id': '555555',
                    'title': 'Title',
                    'text': 'Text',
                    'format': 'wrong_format',
                },
            ],
            'incorrect format: wrong_format',
        ),
    ],
)
async def test_exceptions(
        mock_taxi_driver_wall,
        mock_driver_profiles,
        yt_client,
        cron_context,
        data,
        expected_error_message,
):
    _driver_wall_add, _retrieve = await mock(
        mock_taxi_driver_wall, mock_driver_profiles,
    )

    master_pool = cron_context.pg.master_pool
    await _prepare_data(data, yt_client, master_pool)
    with pytest.raises(Exception, match=expected_error_message):
        await run_cron.main(
            ['taxi_antifraud.crontasks.driver_communication', '-t', '0'],
        )


@pytest.mark.config(
    AFS_CRON_DRIVER_COMMUNICATION_ENABLED=True,
    AFS_CRON_DRIVER_COMMUNICATION_INPUT_TABLE_SUFFIX='kopatel/driver_communication',  # noqa: E501 pylint: disable=line-too-long
    AFS_CRON_DRIVER_COMMUNICATION_SEND_BATCHES_SIZE_OF_BATCH=3,
    AFS_CRON_DRIVER_COMMUNICATION_SLEEP_TIME_SECONDS=0.01,
)
@pytest.mark.parametrize(
    'data,expected_requests',
    [
        (
            [
                {
                    'driver_uuid': '111111',
                    'db_id': '678123',
                    'title': 'some_title_1',
                    'text': 'some_text_1',
                },
                {
                    'driver_uuid': '222222',
                    'db_id': '678123',
                    'title': 'some_title_2',
                    'text': 'some_text_2',
                },
                {
                    'driver_uuid': '333333',
                    'db_id': '678123',
                    'title': 'some_title_3',
                    'text': 'some_text_3',
                },
                {
                    'driver_uuid': '444444',
                    'db_id': '678123',
                    'title': 'some_title_4',
                    'text': 'some_text_4',
                },
                {
                    'driver_uuid': '555555',
                    'db_id': '678123',
                    'title': 'some_title_5',
                    'text': 'some_text_5',
                },
                {
                    'driver_uuid': '666666',
                    'db_id': '678123',
                    'title': 'some_title_6',
                    'text': 'some_text_6',
                },
                {
                    'driver_uuid': '777777',
                    'db_id': '678123',
                    'title': 'some_title_7',
                    'text': 'some_text_7',
                },
            ],
            [
                {
                    'id': (
                        'kopatel_driver_communication_'
                        '0eaaacd88965ea2c766a5a7c79f9d7cf'
                    ),
                    'drivers': [
                        {
                            'driver': '678123_111111',
                            'title': 'some_title_1',
                            'text': 'some_text_1',
                            'format': 'Raw',
                            'alert': False,
                        },
                        {
                            'driver': '678123_222222',
                            'title': 'some_title_2',
                            'text': 'some_text_2',
                            'format': 'Raw',
                            'alert': False,
                        },
                        {
                            'driver': '678123_333333',
                            'title': 'some_title_3',
                            'text': 'some_text_3',
                            'format': 'Raw',
                            'alert': False,
                        },
                    ],
                    'template': {},
                    'application': 'taximeter',
                },
                {
                    'id': (
                        'kopatel_driver_communication_'
                        '44342fd025a1fb1b4a04e9479edf2f4d'
                    ),
                    'drivers': [
                        {
                            'driver': '678123_444444',
                            'title': 'some_title_4',
                            'text': 'some_text_4',
                            'format': 'Raw',
                            'alert': False,
                        },
                        {
                            'driver': '678123_555555',
                            'title': 'some_title_5',
                            'text': 'some_text_5',
                            'format': 'Raw',
                            'alert': False,
                        },
                        {
                            'driver': '678123_666666',
                            'title': 'some_title_6',
                            'text': 'some_text_6',
                            'format': 'Raw',
                            'alert': False,
                        },
                    ],
                    'template': {},
                    'application': 'taximeter',
                },
                {
                    'id': (
                        'kopatel_driver_communication_'
                        '0a7aecafac7be7ed0235a06131fa046d'
                    ),
                    'drivers': [
                        {
                            'driver': '678123_777777',
                            'title': 'some_title_7',
                            'text': 'some_text_7',
                            'format': 'Raw',
                            'alert': False,
                        },
                    ],
                    'template': {},
                    'application': 'taximeter',
                },
            ],
        ),
        (
            [
                {
                    'driver_uuid': '111111',
                    'db_id': '678123',
                    'title': 'some_title_1',
                    'text': 'some_text_1',
                },
                {
                    'driver_uuid': '111111',
                    'db_id': '678123',
                    'title': 'some_title_1',
                    'text': 'some_text_1',
                },
                {
                    'driver_uuid': '222222',
                    'db_id': '678123',
                    'title': 'some_title_2',
                    'text': 'some_text_2',
                },
            ],
            [
                {
                    'id': (
                        'kopatel_driver_communication_'
                        '065a4fc8e34cd632d25446a46d41c831'
                    ),
                    'drivers': [
                        {
                            'driver': '678123_111111',
                            'title': 'some_title_1',
                            'text': 'some_text_1',
                            'format': 'Raw',
                            'alert': False,
                        },
                        {
                            'driver': '678123_222222',
                            'title': 'some_title_2',
                            'text': 'some_text_2',
                            'format': 'Raw',
                            'alert': False,
                        },
                    ],
                    'template': {},
                    'application': 'taximeter',
                },
                {
                    'id': (
                        'kopatel_driver_communication_'
                        '0680ebc0ddd3740bef1d9c1e8bb3c581'
                    ),
                    'drivers': [
                        {
                            'driver': '678123_111111',
                            'title': 'some_title_1',
                            'text': 'some_text_1',
                            'format': 'Raw',
                            'alert': False,
                        },
                    ],
                    'template': {},
                    'application': 'taximeter',
                },
            ],
        ),
    ],
)
async def test_batches(
        mock_taxi_driver_wall,
        mock_driver_profiles,
        yt_client,
        cron_context,
        data,
        expected_requests,
):
    _driver_wall_add, _retrieve = await mock(
        mock_taxi_driver_wall, mock_driver_profiles,
    )
    processed_records = len(data)

    master_pool = cron_context.pg.master_pool
    await _prepare_data(data, yt_client, master_pool)

    await run_cron.main(
        ['taxi_antifraud.crontasks.driver_communication', '-t', '0'],
    )

    got_requests = mock_module.get_requests(_driver_wall_add)

    assert got_requests == expected_requests

    assert await _extract_records(master_pool) == [
        (CURSOR_STATE_NAME, str(processed_records)),
    ]


@pytest.mark.config(
    AFS_CRON_DRIVER_COMMUNICATION_ENABLED=True,
    AFS_CRON_DRIVER_COMMUNICATION_INPUT_TABLE_SUFFIX='kopatel/driver_communication',  # noqa: E501 pylint: disable=line-too-long
    AFS_CRON_DRIVER_COMMUNICATION_SEND_BATCHES_SIZE_OF_BATCH=1,
    AFS_CRON_DRIVER_COMMUNICATION_SLEEP_TIME_SECONDS=0.01,
)
@pytest.mark.parametrize(
    'data,expected_requests',
    [
        (
            [
                {
                    'driver_uuid': '891ad56ed7123ac829ef4829af245ead',
                    'db_id': '678123',
                    'title': 'Warning about fraud',
                    'text': 'Please, do not fraud anymore!',
                    'image_id': '123456/qwerty1234567890',
                },
            ],
            [
                {
                    'id': 'kopatel_driver_communication_965f32c4dbc7bdadfea41af1690d0918',  # noqa: E501 pylint: disable=line-too-long
                    'drivers': [
                        {
                            'driver': (
                                '678123_891ad56ed7123ac829ef4829af245ead'
                            ),
                            'title': 'Warning about fraud',
                            'text': 'Please, do not fraud anymore!',
                            'format': 'Raw',
                            'image_id': '123456/qwerty1234567890',
                            'alert': False,
                        },
                    ],
                    'template': {},
                    'application': 'taximeter',
                },
            ],
        ),
    ],
)
async def test_send_images(
        mock_taxi_driver_wall,
        mock_driver_profiles,
        yt_client,
        cron_context,
        data,
        expected_requests,
):
    _driver_wall_add, _retrieve = await mock(
        mock_taxi_driver_wall, mock_driver_profiles,
    )
    processed_records = len(data)

    master_pool = cron_context.pg.master_pool
    await _prepare_data(data, yt_client, master_pool)

    await run_cron.main(
        ['taxi_antifraud.crontasks.driver_communication', '-t', '0'],
    )

    got_requests = mock_module.get_requests(_driver_wall_add)

    assert got_requests == expected_requests

    assert await _extract_records(master_pool) == [
        (CURSOR_STATE_NAME, str(processed_records)),
    ]


@pytest.mark.config(
    AFS_CRON_DRIVER_COMMUNICATION_ENABLED=True,
    AFS_CRON_DRIVER_COMMUNICATION_INPUT_TABLE_SUFFIX='kopatel/driver_communication',  # noqa: E501 pylint: disable=line-too-long
    AFS_CRON_DRIVER_COMMUNICATION_SEND_BATCHES_SIZE_OF_BATCH=1,
    AFS_CRON_DRIVER_COMMUNICATION_SLEEP_TIME_SECONDS=0.01,
)
@pytest.mark.parametrize(
    'comment,data,expected_requests',
    [
        (
            'with alert equals True',
            [
                {
                    'driver_uuid': '891ad56ed7123ac829ef4829af245ead',
                    'db_id': '678123',
                    'title': 'Warning about fraud',
                    'text': 'Please, do not fraud anymore!',
                    'alert': True,
                },
            ],
            [
                {
                    'id': 'kopatel_driver_communication_11e05c5fbbe5fa724c009c78656a52e9',  # noqa: E501 pylint: disable=line-too-long
                    'drivers': [
                        {
                            'driver': (
                                '678123_891ad56ed7123ac829ef4829af245ead'
                            ),
                            'title': 'Warning about fraud',
                            'text': 'Please, do not fraud anymore!',
                            'format': 'Raw',
                            'alert': True,
                        },
                    ],
                    'template': {},
                    'application': 'taximeter',
                },
            ],
        ),
        (
            'with alert equals False',
            [
                {
                    'driver_uuid': '891ad56ed7123ac829ef4829af245ead',
                    'db_id': '678123',
                    'title': 'Warning about fraud',
                    'text': 'Please, do not fraud anymore!',
                    'alert': False,
                },
            ],
            [
                {
                    'id': 'kopatel_driver_communication_e3c1f81207bcd94e905ee98feeb44417',  # noqa: E501 pylint: disable=line-too-long
                    'drivers': [
                        {
                            'driver': (
                                '678123_891ad56ed7123ac829ef4829af245ead'
                            ),
                            'title': 'Warning about fraud',
                            'text': 'Please, do not fraud anymore!',
                            'format': 'Raw',
                            'alert': False,
                        },
                    ],
                    'template': {},
                    'application': 'taximeter',
                },
            ],
        ),
        (
            'without alert',
            [
                {
                    'driver_uuid': '891ad56ed7123ac829ef4829af245ead',
                    'db_id': '678123',
                    'title': 'Warning about fraud',
                    'text': 'Please, do not fraud anymore!',
                },
            ],
            [
                {
                    'id': 'kopatel_driver_communication_e3c1f81207bcd94e905ee98feeb44417',  # noqa: E501 pylint: disable=line-too-long
                    'drivers': [
                        {
                            'driver': (
                                '678123_891ad56ed7123ac829ef4829af245ead'
                            ),
                            'title': 'Warning about fraud',
                            'text': 'Please, do not fraud anymore!',
                            'format': 'Raw',
                            'alert': False,
                        },
                    ],
                    'template': {},
                    'application': 'taximeter',
                },
            ],
        ),
    ],
)
async def test_alert(
        mock_taxi_driver_wall,
        mock_driver_profiles,
        yt_client,
        cron_context,
        comment,
        data,
        expected_requests,
):
    _driver_wall_add, _retrieve = await mock(
        mock_taxi_driver_wall, mock_driver_profiles,
    )
    processed_records = len(data)

    master_pool = cron_context.pg.master_pool
    await _prepare_data(data, yt_client, master_pool)

    await run_cron.main(
        ['taxi_antifraud.crontasks.driver_communication', '-t', '0'],
    )

    got_requests = mock_module.get_requests(_driver_wall_add)

    assert got_requests == expected_requests

    assert await _extract_records(master_pool) == [
        (CURSOR_STATE_NAME, str(processed_records)),
    ]


@pytest.mark.config(
    AFS_CRON_DRIVER_COMMUNICATION_ENABLED=True,
    AFS_CRON_DRIVER_COMMUNICATION_INPUT_TABLE_SUFFIX='kopatel/driver_communication',  # noqa: E501 pylint: disable=line-too-long
    AFS_CRON_DRIVER_COMMUNICATION_SEND_BATCHES_SIZE_OF_BATCH=3,
    AFS_CRON_DRIVER_COMMUNICATION_SLEEP_TIME_SECONDS=0.01,
)
@pytest.mark.parametrize(
    'comment,data,expected_requests',
    [
        (
            'all messages with one comment',
            [
                {
                    'driver_uuid': '891ad56ed7123ac829ef4829af245ead',
                    'db_id': '678123',
                    'title': 'Warning about fraud',
                    'text': 'Please, do not fraud anymore!',
                    'communication_id': 'some_communication_id',
                },
                {
                    'driver_uuid': '891ad56ed7123ac829ef4829af245eae',
                    'db_id': '678123',
                    'title': 'Warning about fraud',
                    'text': 'Please, do not fraud anymore!',
                    'communication_id': 'some_communication_id',
                },
                {
                    'driver_uuid': '891ad56ed7123ac829ef4829af245eaf',
                    'db_id': '678123',
                    'title': 'Warning about fraud',
                    'text': 'Please, do not fraud anymore!',
                    'communication_id': 'some_communication_id',
                },
            ],
            [
                {
                    'id': 'some_communication_id',
                    'drivers': [
                        {
                            'driver': (
                                '678123_891ad56ed7123ac829ef4829af245ead'
                            ),
                            'title': 'Warning about fraud',
                            'text': 'Please, do not fraud anymore!',
                            'format': 'Raw',
                            'alert': False,
                        },
                        {
                            'driver': (
                                '678123_891ad56ed7123ac829ef4829af245eae'
                            ),
                            'title': 'Warning about fraud',
                            'text': 'Please, do not fraud anymore!',
                            'format': 'Raw',
                            'alert': False,
                        },
                        {
                            'driver': (
                                '678123_891ad56ed7123ac829ef4829af245eaf'
                            ),
                            'title': 'Warning about fraud',
                            'text': 'Please, do not fraud anymore!',
                            'format': 'Raw',
                            'alert': False,
                        },
                    ],
                    'template': {},
                    'application': 'taximeter',
                },
            ],
        ),
        (
            'messages with different communication id',
            [
                {
                    'driver_uuid': '891ad56ed7123ac829ef4829af245ead',
                    'db_id': '678123',
                    'title': 'Warning about fraud',
                    'text': 'Please, do not fraud anymore!',
                    'communication_id': 'some_communication_id',
                },
                {
                    'driver_uuid': '891ad56ed7123ac829ef4829af245eae',
                    'db_id': '678123',
                    'title': 'Warning about fraud',
                    'text': 'Please, do not fraud anymore!',
                    'communication_id': 'other_communication_id',
                },
                {
                    'driver_uuid': '891ad56ed7123ac829ef4829af245eaf',
                    'db_id': '678123',
                    'title': 'Warning about fraud',
                    'text': 'Please, do not fraud anymore!',
                    'communication_id': 'another_communication_id',
                },
            ],
            [
                {
                    'id': 'some_communication_id',
                    'drivers': [
                        {
                            'driver': (
                                '678123_891ad56ed7123ac829ef4829af245ead'
                            ),
                            'title': 'Warning about fraud',
                            'text': 'Please, do not fraud anymore!',
                            'format': 'Raw',
                            'alert': False,
                        },
                        {
                            'driver': (
                                '678123_891ad56ed7123ac829ef4829af245eae'
                            ),
                            'title': 'Warning about fraud',
                            'text': 'Please, do not fraud anymore!',
                            'format': 'Raw',
                            'alert': False,
                        },
                        {
                            'driver': (
                                '678123_891ad56ed7123ac829ef4829af245eaf'
                            ),
                            'title': 'Warning about fraud',
                            'text': 'Please, do not fraud anymore!',
                            'format': 'Raw',
                            'alert': False,
                        },
                    ],
                    'template': {},
                    'application': 'taximeter',
                },
            ],
        ),
        (
            'some messages without id',
            [
                {
                    'driver_uuid': '891ad56ed7123ac829ef4829af245ead',
                    'db_id': '678123',
                    'title': 'Warning about fraud',
                    'text': 'Please, do not fraud anymore!',
                },
                {
                    'driver_uuid': '891ad56ed7123ac829ef4829af245eae',
                    'db_id': '678123',
                    'title': 'Warning about fraud',
                    'text': 'Please, do not fraud anymore!',
                    'communication_id': 'some_communication_id',
                },
                {
                    'driver_uuid': '891ad56ed7123ac829ef4829af245eaf',
                    'db_id': '678123',
                    'title': 'Warning about fraud',
                    'text': 'Please, do not fraud anymore!',
                },
            ],
            [
                {
                    'id': 'some_communication_id',
                    'drivers': [
                        {
                            'driver': (
                                '678123_891ad56ed7123ac829ef4829af245ead'
                            ),
                            'title': 'Warning about fraud',
                            'text': 'Please, do not fraud anymore!',
                            'format': 'Raw',
                            'alert': False,
                        },
                        {
                            'driver': (
                                '678123_891ad56ed7123ac829ef4829af245eae'
                            ),
                            'title': 'Warning about fraud',
                            'text': 'Please, do not fraud anymore!',
                            'format': 'Raw',
                            'alert': False,
                        },
                        {
                            'driver': (
                                '678123_891ad56ed7123ac829ef4829af245eaf'
                            ),
                            'title': 'Warning about fraud',
                            'text': 'Please, do not fraud anymore!',
                            'format': 'Raw',
                            'alert': False,
                        },
                    ],
                    'template': {},
                    'application': 'taximeter',
                },
            ],
        ),
    ],
)
async def test_communication_id(
        mock_taxi_driver_wall,
        mock_driver_profiles,
        yt_client,
        cron_context,
        comment,
        data,
        expected_requests,
):
    _driver_wall_add, _retrieve = await mock(
        mock_taxi_driver_wall, mock_driver_profiles,
    )
    processed_records = len(data)

    master_pool = cron_context.pg.master_pool
    await _prepare_data(data, yt_client, master_pool)

    await run_cron.main(
        ['taxi_antifraud.crontasks.driver_communication', '-t', '0'],
    )

    got_requests = mock_module.get_requests(_driver_wall_add)

    assert got_requests == expected_requests

    assert await _extract_records(master_pool) == [
        (CURSOR_STATE_NAME, str(processed_records)),
    ]
