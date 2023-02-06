import datetime

import pytest

from replication.foundation import consts
from replication.replication.core import replication

ZENDESK_TICKET_RULE_NAME = 'test_rule_zendesk_tickets'
ZENDESK_TICKET_EVENT_RULE_NAME = 'test_rule_zendesk_ticket_events'

NOW = datetime.datetime(2018, 11, 26, 0)


@pytest.mark.parametrize(
    'rule_name,handler_to_mock,zendesk_data_file,expected_queue',
    [
        (
            ZENDESK_TICKET_RULE_NAME,
            'tickets',
            'zendesk_tickets.json',
            'expected_staging_tickets.json',
        ),
        (
            ZENDESK_TICKET_EVENT_RULE_NAME,
            'ticket_events',
            'zendesk_ticket_events.json',
            'expected_staging_events.json',
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_zendesk_replication(
        load_py_json,
        run_replication,
        mock_zendesk_source,
        patch_queue_current_date,
        rule_name,
        handler_to_mock,
        zendesk_data_file,
        expected_queue,
):
    mock_zendesk_source(handler_to_mock, zendesk_data_file)
    targets_data = await run_replication(rule_name)
    staging_docs_tickets = targets_data.queue_data_by_id(
        drop_targets_updated=False,
    )
    expected_staging_docs_tickets = load_py_json(expected_queue)
    expected_staging_docs_tickets = {
        doc['_id']: doc for doc in expected_staging_docs_tickets
    }
    assert (
        staging_docs_tickets == expected_staging_docs_tickets
    ), 'Zendesk replication to queue failed'


@pytest.mark.parametrize(
    'source_type,rule_name,doc,expected_base_stamp',
    [
        (
            consts.SOURCE_TYPE_QUEUE_MONGO,
            'test_rule_zendesk_tickets',
            {
                '_id': 'doc_id',
                'updated': datetime.datetime(2019, 1, 1, 10),
                'data': {'generated_timestamp': 1570430000.012},
            },
            datetime.datetime(2019, 10, 7, 6, 33, 20, 12000),
        ),
    ],
)
@pytest.mark.nofilldb
async def test_get_max_base_stamp(
        replication_ctx,
        units_getter,
        source_type,
        rule_name,
        doc,
        expected_base_stamp,
):
    source, _ = (await units_getter(source_type, rule_name))[0]
    # pylint: disable=protected-access
    assert (
        replication._get_max_base_stamp(replication_ctx, source, doc)
        == expected_base_stamp
    )
