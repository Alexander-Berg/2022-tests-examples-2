import pytest

from clownductor.generated.cron import run_cron
from clownductor.internal import service_issues


@pytest.fixture(name='duty_service_mock')
def _duty_service_mock(mockserver):
    @mockserver.json_handler('/duty-api/api/duty_group')
    def _duty_group_handler(request):
        group_id = request.query['group_id']
        if group_id == 'clowny_duty_group':
            return {
                'result': {
                    'data': {
                        'abcDutyId': 'taxidutyrtcsupport',
                        'calendarLayer': 0,
                        'currentEvent': {
                            'calendar_event_id': None,
                            'calendar_layer': 0,
                            'end': 'Thu, 17 Feb 2022 21:00:00 GMT',
                            'st_key': None,
                            'start': 'Tue, 15 Feb 2022 21:00:00 GMT',
                            'started': False,
                            'user': 'd1mbas',
                        },
                        'daysLong': 0,
                        'dutyGroupId': '',
                        'excludePeople': [],
                        'excludeWeekend': False,
                        'gaps': {},
                        'id': 'taxidutyrtcsupport',
                        'lastEvents': [],
                        'name': 'dummyname',
                        'people': [],
                        'plannedEvents': [
                            {
                                'calendar_event_id': None,
                                'calendar_layer': 0,
                                'end': 'Fri, 18 Feb 2022 21:00:00 GMT',
                                'st_key': None,
                                'start': 'Thu, 17 Feb 2022 21:00:00 GMT',
                                'started': False,
                                'user': 'vstimchenko',
                            },
                        ],
                        'rearrangeOnVacations': True,
                        'shiftStart': 0,
                        'stQueue': None,
                        'staffGroups': [],
                        'suggestedEvents': [
                            {
                                'calendar_event_id': None,
                                'calendar_layer': 0,
                                'end': 'Fri, 18 Feb 2022 21:00:00 GMT',
                                'st_key': None,
                                'start': 'Thu, 17 Feb 2022 21:00:00 GMT',
                                'started': False,
                                'user': 'vstimchenko',
                            },
                        ],
                    },
                    'error': None,
                    'ok': True,
                },
            }
        return {
            'result': {
                'data': {
                    'currentEvent': {},
                    'suggestedEvents': [],
                    'staffGroups': [],
                },
                'ok': True,
            },
        }

    return _duty_group_handler


@pytest.mark.features_on('enable_check_duty_for_service_issues_cron')
@pytest.mark.pgsql('clownductor', files=['add_test_db.sql'])
async def test_add_service_issue(web_context, patch):
    @patch('staff_api.components.StaffClient.get_persons')
    async def _get_persons(logins, fields, timeout):
        return [
            {'login': 'meow', 'official': {'is_dismissed': True}},
            {'login': 'azhuchkov', 'official': {'is_dismissed': False}},
        ]

    await run_cron.main(
        ['clownductor.crontasks.check_service_issues', '-t', '0'],
    )

    issues = (
        await web_context.service_manager.service_issues.get_by_service_id(1)
    )

    expected = [
        service_issues.ServiceIssue(
            id=1,
            service_id=1,
            issue_key='maintainer_dismiss',
            issue_parameters={'dismissed_maintainers': 'meow'},
        ),
        service_issues.ServiceIssue(
            id=2,
            service_id=1,
            issue_key='duty_group_missed',
            issue_parameters={},
        ),
    ]

    assert issues == expected
    assert len(_get_persons.calls) == 1


@pytest.mark.features_on('enable_check_duty_for_service_issues_cron')
@pytest.mark.pgsql('clownductor', files=['update_test_db.sql'])
async def test_update_service_issue(web_context, patch, duty_service_mock):
    @patch('staff_api.components.StaffClient.get_persons')
    async def _get_persons(logins, fields, timeout):
        return [
            {'login': 'meow', 'official': {'is_dismissed': True}},
            {'login': 'azhuchkov', 'official': {'is_dismissed': True}},
        ]

    await run_cron.main(
        ['clownductor.crontasks.check_service_issues', '-t', '0'],
    )

    issues = await web_context.service_manager.service_issues.get_all_issues()

    expected = [
        service_issues.ServiceIssue(
            id=1,
            service_id=1,
            issue_key='maintainer_dismiss',
            issue_parameters={'dismissed_maintainers': 'meow, azhuchkov'},
        ),
        service_issues.ServiceIssue(
            id=3,
            service_id=1,
            issue_key='duty_group_missed',
            issue_parameters={},
        ),
        service_issues.ServiceIssue(
            id=4,
            service_id=2,
            issue_key='maintainer_absence',
            issue_parameters={},
        ),
    ]

    assert issues == expected
    assert len(_get_persons.calls) == 1


@pytest.mark.pgsql('clownductor', files=['remove_test_db.sql'])
@pytest.mark.features_on('enable_check_duty_for_service_issues_cron')
async def test_remove_service_issue(web_context, patch, duty_service_mock):
    @patch('staff_api.components.StaffClient.get_persons')
    async def _get_persons(logins, fields, timeout):
        return [
            {'login': 'meow', 'official': {'is_dismissed': False}},
            {'login': 'azhuchkov', 'official': {'is_dismissed': False}},
        ]

    await run_cron.main(
        ['clownductor.crontasks.check_service_issues', '-t', '0'],
    )

    issues = (
        await web_context.service_manager.service_issues.get_by_service_id(1)
    )

    expected = [
        service_issues.ServiceIssue(
            id=4,
            service_id=1,
            issue_key='duty_group_is_empty',
            issue_parameters={},
        ),
    ]

    assert issues == expected
    assert len(_get_persons.calls) == 1
