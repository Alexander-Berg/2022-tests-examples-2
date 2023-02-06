# pylint: disable=redefined-outer-name, import-only-modules, too-many-lines
# flake8: noqa F401
import pytest
import datetime as dt

from tests_callcenter_qa.utils import get_aggregator_config


@pytest.mark.now('2020-07-19T11:14:00.00Z')
@pytest.mark.parametrize(
    'expected_tags',
    (
        pytest.param(
            [
                {
                    'blocked_until': str(
                        dt.datetime(
                            2020, 7, 20, 11, 14, tzinfo=dt.timezone.utc,
                        ),
                    ),
                    'personal_phone_id': 'test_phone_pd_id',
                    'project': 'test_project_1',
                    'reason': 'children',
                    'feedbacks': ['id1', 'id2'],
                },
                {
                    'blocked_until': str(
                        dt.datetime(
                            2020, 7, 20, 11, 14, tzinfo=dt.timezone.utc,
                        ),
                    ),
                    'personal_phone_id': 'test_phone_pd_id',
                    'project': 'test_project_2',
                    'reason': 'children',
                    'feedbacks': ['id3', 'id4'],
                },
            ],
            marks=pytest.mark.config(
                CALLCENTER_QA_FEEDBACKS_AGGREGATION_SETTINGS=get_aggregator_config(
                    feedback_type_to_settings={
                        'children': {
                            'thresholds': [],
                            'processors': [
                                {
                                    'type': 'tag_saver',
                                    'settings': {'ttl': 60 * 60 * 24},  # 1d
                                },
                            ],
                            'filters': [
                                {
                                    'keys': [
                                        {
                                            'path': (
                                                'call_info/personal_phone_id'
                                            ),
                                            'alias': 'phone_pd_id',
                                        },
                                        {
                                            'path': 'call_info/application',
                                            'alias': 'application',
                                        },
                                        {
                                            'path': 'feedback_info/project',
                                            'alias': 'project',
                                        },
                                    ],
                                    'values': [
                                        {
                                            'thresholds': [
                                                {'interval': 3000, 'limit': 2},
                                            ],
                                        },
                                    ],
                                },
                            ],
                        },
                    },
                ),
            ),
        ),
    ),
)
@pytest.mark.pgsql('callcenter_qa', files=['prepare_feedback.sql'])
async def test_base(
        taxi_callcenter_qa, mockserver, testpoint, pgsql, expected_tags,
):
    @testpoint('feedbacks_aggregator::completed')
    def task_finished(data):
        pass

    async with taxi_callcenter_qa.spawn_task('distlock/feedbacks_aggregator'):
        await task_finished.wait_call()

    cursor = pgsql['callcenter_qa'].cursor()
    cursor.execute(
        'SELECT uuid, blocked_until, personal_phone_id, project, reason'
        ' FROM callcenter_qa.tags ORDER BY project',
    )

    db_tags = list()
    for db_item in cursor.fetchall():
        db_tags.append(
            {
                'uuid': db_item[0],
                'blocked_until': str(db_item[1].astimezone(dt.timezone.utc)),
                'personal_phone_id': db_item[2],
                'project': db_item[3],
                'reason': db_item[4],
            },
        )

    uuids_to_feedbacks = dict()
    for db_tag, expected_tag in zip(db_tags, expected_tags):
        assert db_tag['blocked_until'] == expected_tag['blocked_until']
        assert db_tag['project'] == expected_tag['project']
        assert db_tag['reason'] == expected_tag['reason']
        assert db_tag['personal_phone_id'] == expected_tag['personal_phone_id']
        uuids_to_feedbacks[db_tag['uuid']] = expected_tag['feedbacks']

    cursor.execute('SELECT tag_uuid, feedback_id FROM callcenter_qa.tag_links')

    for db_link in cursor.fetchall():
        assert db_link[0] in uuids_to_feedbacks.keys()
        assert db_link[1] in uuids_to_feedbacks[db_link[0]]
    cursor.close()
