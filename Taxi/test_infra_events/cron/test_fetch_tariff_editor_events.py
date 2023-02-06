import datetime

import pytest

from infra_events.common import db
from infra_events.generated.cron import cron_context as context
from infra_events.generated.cron import run_cron


@pytest.mark.config(
    INFRA_EVENTS_FEATURES={'fetch_tariff_editor_events': False},
)
async def test_disabled_feature(mongo):
    await run_cron.main(
        ['infra_events.crontasks.fetch_tariff_editor_events', '-t', '0'],
    )

    header = 'Изменение в админке: save_value (changed_object_name)'
    res = await mongo.lenta_events.find_one({'header': header})
    assert res is None


@pytest.mark.config(
    INFRA_EVENTS_TARIFF_EDITOR={'ignored_actions': ['ignored_action']},
    INFRA_EVENTS_FEATURES={'fetch_tariff_editor_events': True},
)
async def test_getting_events(mockserver, load_json, mongo):
    @mockserver.json_handler('/audit/v1/robot/logs/retrieve/')
    def _robot_logs_retrieve(request):
        request_data = request.json
        sort = request_data.get('sort')
        if sort:
            return [
                {
                    'id': 'tariff-editor:601169794da26f0000000001',
                    'action': 'already_seen',
                    'login': 'login1',
                    'timestamp': '2021-01-27T13:24:08.997Z',
                    'system_name': 'tariff-editor',
                    'revision': 10,
                },
            ]
        return [
            {
                'id': '601169794da26f0000000005',
                'action': 'ignored_action',
                'login': 'login2',
                'timestamp': '2021-01-27T13:24:08.997Z',
                'system_name': 'tariff-editor',
                'revision': 11,
            },
            {
                'id': '60116f1b16843d00000000010',
                'action': 'save_value',
                'login': 'login3',
                'object_id': 'changed_object_name',
                'timestamp': '2021-01-27T13:48:11.832Z',
                'system_name': 'tariff-editor',
                'revision': 12,
            },
            {
                'id': '60116f1b16843d00000000015',
                'action': 'invalid_action',
                'timestamp': '2021-01-27T13:48:11.832Z',
                'system_name': 'tariff-editor',
                'revision': 13,
            },
        ]

    await run_cron.main(
        ['infra_events.crontasks.fetch_tariff_editor_events', '-t', '0'],
    )

    header = 'Изменение в админке: already_seen'
    res = await mongo.lenta_events.find_one({'header': header})
    assert res is None

    header = 'Изменение в админке: ignored_action'
    res = await mongo.lenta_events.find_one({'header': header})
    assert res is None

    header = 'Изменение в админке: save_value (changed_object_name)'
    res = await mongo.lenta_events.find_one({'header': header})
    assert _robot_logs_retrieve.times_called == 1
    del res['_id']
    assert res == {
        'body': (
            '((https://tariff-editor.taxi.yandex-team.ru/audit/'
            '60116f1b16843d00000000010 Смотреть в журнале))'
        ),
        'header': 'Изменение в админке: save_value (changed_object_name)',
        'source': 'tariff-editor',
        'timestamp': datetime.datetime.fromisoformat(
            '2021-01-27T13:48:11.832',
        ),
        'tags': ['staff:login3', 'tariff-editor:save_value'],
        'views': ['__all__'],
    }

    header = 'Изменение в админке: invalid_action'
    res = await mongo.lenta_events.find_one({'header': header})
    assert res is None

    test_context = context.create_context()

    last_id = await db.get_tariff_editor_last_seen_id(test_context)
    assert last_id == 13


@pytest.mark.config(
    INFRA_EVENTS_TARIFF_EDITOR={'ignored_actions': ['ignored_action']},
    INFRA_EVENTS_FEATURES={'fetch_tariff_editor_events': True},
    INFRA_EVENTS_VIEWS=['taxi', 'eda'],
)
async def test_getting_events_with_namespaces(mockserver, load_json, mongo):

    audit_logs = [
        {
            'id': '60116f1b16843d00000000020',
            'action': 'save_value_with_namespace_taxi',
            'login': 'login4',
            'object_id': 'changed_object_name',
            'timestamp': '2021-01-27T13:48:11.832Z',
            'system_name': 'tariff-editor',
            'tplatform_namespace': 'taxi',
            'revision': 1,
        },
        {
            'id': '60116f1b16843d00000000025',
            'action': 'save_value_with_namespace_eda',
            'login': 'login5',
            'object_id': 'changed_object_name',
            'timestamp': '2021-01-27T13:48:11.832Z',
            'system_name': 'tariff-editor',
            'tplatform_namespace': 'eda',
            'revision': 2,
        },
    ]

    @mockserver.json_handler('/audit/v1/robot/logs/retrieve/')
    def _robot_logs_retrieve(request):  # pylint: disable=unused-variable
        return audit_logs

    await run_cron.main(
        ['infra_events.crontasks.fetch_tariff_editor_events', '-t', '0'],
    )

    header = 'Изменение в админке: already_seen'
    res = await mongo.lenta_events.find_one({'header': header})
    assert res is None

    header = 'Изменение в админке: ignored_action'
    res = await mongo.lenta_events.find_one({'header': header})
    assert res is None

    header = 'Изменение в админке: invalid_action'
    res = await mongo.lenta_events.find_one({'header': header})
    assert res is None

    for log in audit_logs:
        header = f'Изменение в админке: {log["action"]} (changed_object_name)'
        res = await mongo.lenta_events.find_one({'header': header})

        del res['_id']
        assert res == {
            'body': (
                '((https://tariff-editor.taxi.yandex-team.ru/audit/'
                f'{log["id"]} Смотреть в журнале))'
            ),
            'header': (
                'Изменение в админке: '
                f'{log["action"]} (changed_object_name)'
            ),
            'source': 'tariff-editor',
            'timestamp': datetime.datetime.fromisoformat(
                '2021-01-27T13:48:11.832',
            ),
            'tags': [
                f'staff:{log["login"]}',
                f'tariff-editor:{log["action"]}',
            ],
            'views': [log['tplatform_namespace']],
        }


async def assert_doc(mongo, compare_doc):
    q_filter = {'tariff-editor.last_seen_id': {'$exists': True}}
    doc = await mongo.lenta_misc.find_one(q_filter)
    doc.pop('_id')
    assert doc == compare_doc


@pytest.mark.config(
    INFRA_EVENTS_FEATURES={
        'fetch_tariff_editor_events': True,
        'use_audit_api': True,
    },
    INFRA_EVENTS_VIEWS=['taxi'],
)
@pytest.mark.nofilldb
async def test_empty_db(mongo, mockserver):
    @mockserver.json_handler('/audit/v1/robot/logs/retrieve/')
    def _robot_logs_retrieve(*args, **kwargs):
        return [
            {
                'id': '601169794da26f0000000001',
                'action': 'save_value_with_namespace_taxi',
                'login': 'login4',
                'object_id': 'changed_object_name',
                'timestamp': '2022-03-16T13:00:00',
                'system_name': 'tariff-editor',
                'tplatform_namespace': 'taxi',
                'revision': 1,
            },
        ]

    await run_cron.main(
        ['infra_events.crontasks.fetch_tariff_editor_events', '-t', '0'],
    )
    compare_doc = {'tariff-editor': {'last_seen_id': 1}}
    await assert_doc(mongo, compare_doc)
