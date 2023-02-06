# pylint: disable=redefined-outer-name, import-only-modules, too-many-lines
# flake8: noqa F401
import pytest

from tests_callcenter_qa.utils import get_aggregator_config


@pytest.mark.now('2020-07-19T11:14:00.00Z')
@pytest.mark.parametrize(
    'expected_ticket_data',
    (
        pytest.param(
            {
                'incidentTime': '2020-07-19T11:13:58+0000',
                'summary': 'test_summary 2020-07-19T11:13:58+0000',
                'queue': 'CCMASSINCIDENT',
                'description': (
                    '**Feedbacks found:** 2\n**'
                    'Created after:** 2020-07-19T11:13:58+0000\n\n'
                    '**Projects:** ["test_project_2", "test_project"]\n'
                    '**CallCenter numbers:** ["+71234567890"]\n'
                    '**Cities:** []\n**Callcenters:** ["test-callcenter"]\n'
                    '**Queues:** ["disp_on_2", "disp_on_1"]\n'
                    '**Metaqueues:** ["disp"]\n'
                    '**Errors:** ["{"error_code": "500", '
                    '"error_path": "test_error_path"}", '
                    '"{"error_code": "500", "error_path": '
                    '"test_error_path_2"}"]\n'
                ),
                'descriptionRenderType': 'PLAIN',
                'links': [
                    {
                        'relationship': 'RELATES',
                        'issue': {
                            'id': 'ticket_id1',
                            'key': 'https://example.com/CCINCIDENT_1',
                        },
                    },
                    {
                        'relationship': 'RELATES',
                        'issue': {
                            'id': 'ticket_id2',
                            'key': 'https://example.com/CCINCIDENT_2',
                        },
                    },
                ],
                'tags': ['mass_ServerError'],
            },
        ),
    ),
)
@pytest.mark.config(
    CALLCENTER_QA_FEEDBACKS_AGGREGATION_SETTINGS=get_aggregator_config(
        feedback_type_to_settings={
            'ServerError': {
                'thresholds': [{'interval': 2, 'limit': 1}],
                'processors': [
                    {
                        'type': 'mass_incident_creator',
                        'settings': {
                            'queue': 'CCMASSINCIDENT',
                            'summary': 'test_summary',
                            'tags': ['mass_ServerError'],
                        },
                    },
                ],
            },
        },
    ),
)
@pytest.mark.pgsql('callcenter_qa', files=['prepare_feedback.sql'])
async def test_base(
        taxi_callcenter_qa,
        mock_tracker,
        mockserver,
        testpoint,
        pgsql,
        expected_ticket_data,
):
    @testpoint('feedbacks_aggregator::completed')
    def task_finished(data):
        pass

    async with taxi_callcenter_qa.spawn_task('distlock/feedbacks_aggregator'):
        await task_finished.wait_call()

    assert mock_tracker.create_issue.times_called == 1
    assert (
        mock_tracker.create_issue.next_call()['request'].json
        == expected_ticket_data
    )

    cursor = pgsql['callcenter_qa'].cursor()
    cursor.execute(
        'SELECT ticket_id, feedback_id'
        ' FROM callcenter_qa.mass_incident_links',
    )
    assert cursor.fetchall() == [
        ('ticket_test_1', 'id3'),
        ('CCMASSINCIDENT', 'id1'),
        ('CCMASSINCIDENT', 'id2'),
    ]
    cursor.close()
