# pylint: disable=redefined-outer-name
import datetime

from aiohttp import web
import pytest

from supportai_calls.generated.cron import run_cron
import supportai_calls.models as db_models
from test_supportai_calls import common


@pytest.mark.config(
    TVM_RULES=[
        {'src': 'supportai-calls', 'dst': 'supportai-context'},
        {'src': 'supportai-calls', 'dst': 'stq-agent'},
    ],
)
@pytest.mark.parametrize(
    'calls_direction', ['all_incoming', 'all_outgoing', 'mixed'],
)
async def test_update_separate_calls(
        stq3_context, mockserver, calls_direction,
):
    project_to_chat_ids = {'slug1': ['0', '1', '2'], 'slug2': ['3', '4']}
    chat_id_to_status = {
        '2': db_models.CallStatus.QUEUED,
        '4': db_models.CallStatus.ERROR,
    }
    chat_id_to_updated_status = {
        '0': db_models.CallStatus.ERROR,
        '1': db_models.CallStatus.ENDED,
        '3': db_models.CallStatus.PROCESSING,
    }

    chat_id_to_call_direction = {
        chat_id: (
            db_models.CallDirection.INCOMING
            if calls_direction == 'all_incoming'
            else db_models.CallDirection.OUTGOING
        )
        for chat_id in list(map(str, range(5)))
    }
    if calls_direction == 'mixed':
        chat_id_to_call_direction['0'] = db_models.CallDirection.INCOMING

    incoming_calls = []
    for project_slug, chat_ids in project_to_chat_ids.items():
        incoming_calls.extend(
            [
                common.get_preset_call(
                    project_slug,
                    direction=chat_id_to_call_direction[chat_id],
                    chat_id=chat_id,
                    task_id=None,
                    status=chat_id_to_status.get(
                        chat_id, db_models.CallStatus.INITIATED,
                    ),
                    attempt_number=1,
                    initiated=datetime.datetime.now(),
                )
                for chat_id in chat_ids
            ],
        )
    async with stq3_context.pg.master_pool.acquire() as conn:
        await db_models.Call.insert_bulk(stq3_context, conn, incoming_calls)

    @mockserver.json_handler('/supportai-context/v1/contexts/multiple')
    async def _(request):
        project_slug_ = request.query['project_id']
        chat_ids_ = set(request.json['chat_ids'])
        if project_slug_ == 'slug1':
            assert chat_ids_ == {'0', '1'}
        elif project_slug_ == 'slug2':
            assert chat_ids_ == {'3'}
        else:
            assert False

        contexts = [
            common.create_context(
                chat_id=chat_id,
                error_code='some error'
                if chat_id_to_updated_status[chat_id]
                == db_models.CallStatus.ERROR
                else None,
                is_ended=chat_id_to_updated_status[chat_id]
                == db_models.CallStatus.ENDED,
            )
            for chat_id in chat_ids_
        ]
        return web.json_response(
            data={'contexts': contexts, 'total': len(contexts)},
        )

    statistics_records = []

    @mockserver.json_handler(
        '/supportai-statistics/supportai-statistics/v1/calls_statistics',
    )
    async def _statistics_handle(request):
        nonlocal statistics_records
        statistics_records = request.json.get('records')
        return {}

    await run_cron.main(
        ['supportai_calls.crontasks.update_separate_calls', '-t', '0'],
    )

    async with stq3_context.pg.master_pool.acquire() as conn:
        updated_calls = await db_models.Call.search_by_filters(
            stq3_context, conn, separate_calls=True, limit=5, offset=0,
        )

    assert len(updated_calls) == 5

    for call in updated_calls:
        if call.chat_id in chat_id_to_status:
            assert call.status == chat_id_to_status[call.chat_id]
            continue
        assert call.status == chat_id_to_updated_status[call.chat_id]

    assert _statistics_handle.times_called == 1

    assert len(statistics_records) == 2
    for record in statistics_records:
        assert record.get('batch_id') is None

        expected_status = chat_id_to_updated_status.get(
            record.get('chat_id'),
        ).value
        assert record.get('status') == expected_status
        if expected_status == 'error':
            assert record.get('talk_duration') is None
            assert record.get('total_duration') is None
            assert record.get('call_connected') is False
        elif expected_status == 'ended':
            assert record.get('talk_duration') is not None
            assert record.get('total_duration') is not None
            assert record.get('call_connected') is True
        else:
            assert False
