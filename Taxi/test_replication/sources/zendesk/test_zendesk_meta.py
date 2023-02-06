import pytest

from replication.foundation import consts


ZENDESK_META_TEST_CASES = [
    (
        'zendesk',
        'zendesk_rule',
        {'zendesk_id': 'ZENDESK_SECRET', 'resource': 'ticket_events'},
        ['zendesk_rule'],
        {
            'zendesk_id': ['ZENDESK_SECRET'],
            'resource': ['ticket_events'],
            'replicate_by': ['timestamp'],
            'iteration_type': [
                consts.IterationType.MOVING_BOUNDARIES_AND_FREE_NEW_BOUND,
            ],
        },
    ),
    (
        'zendesk',
        'zendesk_rule',
        {'zendesk_id': 'ZENDESK_SECRET', 'resource': 'tickets'},
        ['zendesk_rule'],
        {
            'zendesk_id': ['ZENDESK_SECRET'],
            'resource': ['tickets'],
            'replicate_by': ['generated_timestamp'],
            'iteration_type': [
                consts.IterationType.MOVING_BOUNDARIES_AND_FREE_NEW_BOUND,
            ],
        },
    ),
]


@pytest.mark.parametrize(
    'source_type,source_name,raw_meta,' 'expected_names,expected_meta_attrs',
    ZENDESK_META_TEST_CASES,
)
@pytest.mark.nofilldb
async def test_zendesk_meta_construct(
        source_meta_checker,
        source_type,
        source_name,
        raw_meta,
        expected_names,
        expected_meta_attrs,
):
    source_meta_checker(
        source_type,
        source_name,
        raw_meta,
        expected_names,
        expected_meta_attrs,
    )
