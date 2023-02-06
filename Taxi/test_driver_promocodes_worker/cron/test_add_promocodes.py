# pylint: disable=redefined-outer-name
import pytest

from driver_promocodes_worker.generated.cron import run_cron


class TableNode:
    def __init__(self, name, owner, type_='table'):
        self.name = name
        self.owner = owner
        self.type = type_

    def __repr__(self):
        return self.name

    @property
    def attributes(self):
        return {'type': self.type, 'owner': self.owner}


@pytest.mark.config(
    DRIVER_PROMOCODES_WORKER_SETTINGS={
        'is_enabled': True,
        'table_prefix': 'promocodes_to_add',
    },
)
async def test_add_promocodes(patch, mockserver):
    plugin_path = (
        'driver_promocodes_worker.generated.cron.'
        'yt_wrapper.plugin.AsyncYTClient'
    )

    @patch(plugin_path + '.list')
    async def _yt_list(path, *args, **kwargs):
        if path.endswith('dir1'):
            return [
                TableNode(name='promocodes_to_add_2021', owner='vdovkin'),
                TableNode(name='other_node', owner='vdovkin'),
            ]
        return [
            TableNode(name='promocodes_to_add_2021', owner='vdovkin'),
            TableNode(name='other_node', owner='vdovkin'),
            TableNode(name='dir1', owner='vdovkin', type_='map_node'),
        ]

    @patch(plugin_path + '.read_table')
    async def _yt_read(path, *args, **kwargs):
        assert path.endswith('promocodes_to_add_2021')
        return [
            {
                'entity_id': 'entity_1',
                'series_name': 'series',
                'can_activate_until': '2021-02-01T00:00:00+00:00',
                'ticket': 'TAXI-101',
            },
            {'entity_id': 'invalid_row', 'series_name': 'random'},
            {
                'entity_id': 'entity_error_400',
                'series_name': 'series',
                'can_activate_until': '2021-02-01T00:00:00+00:00',
                'ticket': 'TAXI-101',
            },
        ]

    @patch(plugin_path + '.move')
    async def _yt_move(*args, **kwargs):
        return

    @patch(plugin_path + '.write_table')
    async def _yt_write_table(path, content):
        assert content == [
            {
                'entity_id': 'invalid_row',
                'series_name': 'random',
                'error': 'Field can_activate_until not found',
            },
            {
                'entity_id': 'entity_error_400',
                'series_name': 'series',
                'can_activate_until': '2021-02-01T00:00:00+00:00',
                'ticket': 'TAXI-101',
                'error': {'code': '400', 'message': 'Bad Request'},
            },
        ]

    @mockserver.json_handler('/driver-promocodes/internal/v1/promocodes')
    async def _(request):
        entity_id = request.json['entity_id']
        if entity_id == 'entity_error_400':
            return mockserver.make_response(
                status=400, json={'code': '400', 'message': 'Bad Request'},
            )
        return mockserver.make_response(
            status=200,
            json={
                'antifraud_resolutions': [],
                'can_activate_until': '2020-06-01T09:00:00+00:00',
                'chatterbox_ticket': 'chatterbox1',
                'country': 'rus',
                'created_at': '2020-07-21T16:20:54.409661+00:00',
                'created_by': 'vdovkin',
                'currency': 'RUB',
                'description': 'Описание выдачи',
                'description_key': 'DriverPromocodes_TestKey',
                'entity_id': 'park_0_driver_0',
                'entity_type': 'park_driver_profile_id',
                'id': '5e07ffb6ad3a4d128d9f2ecdfcd4db60',
                'is_created_by_service': False,
                'is_seen': False,
                'is_support_series': False,
                'series_name': 'test-series-2',
                'status': 'published',
                'tags': ['tag_group_1', 'tag_no_group'],
                'tariffs': ['comfort', 'econom'],
                'tickets': [],
                'title_key': 'DriverPromocodes_TestKey',
                'type': 'tag',
                'updated_at': '2020-07-21T16:20:54.409661+00:00',
                'used_for_orders': [],
            },
        )

    await run_cron.main(
        ['driver_promocodes_worker.crontasks.add_promocodes', '-t', '0'],
    )
