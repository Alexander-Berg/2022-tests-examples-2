import datetime

import pytest

from taxi.util import audit


@pytest.mark.config(
    ADMIN_AUDIT_TICKET_CONFIG={
        'enabled': True,
        'queues': {'TAXIRATE': {'statuses': ['approved']}},
    },
)
@pytest.mark.parametrize(
    'ticket_key, get_field_history, expected',
    [
        pytest.param(
            'TAXIRATE-123',
            [
                {
                    'fields': [
                        {
                            'field': {'id': 'status'},
                            'from': None,
                            'to': {'key': 'open'},
                        },
                    ],
                    'updatedAt': '2019-11-01T15:15:00.000+0000',
                    'updatedBy': {'id': 'user_updater'},
                },
                {
                    'fields': [
                        {
                            'field': {'id': 'status'},
                            'from': {'key': 'open'},
                            'to': {'key': 'approved'},
                        },
                    ],
                    'updatedAt': '2019-11-02T15:15:00.000+0000',
                    'updatedBy': {'id': 'user_updater'},
                },
            ],
            datetime.datetime(2019, 11, 2, 15, 15, 0),
            id='base_case',
        ),
        pytest.param(
            'TAXIRATE-123',
            [
                {
                    'fields': [
                        {
                            'field': {'id': 'status'},
                            'from': None,
                            'to': {'key': 'open'},
                        },
                    ],
                    'updatedAt': '2019-11-01T15:15:00.000+0000',
                    'updatedBy': {'id': 'user_updater'},
                },
                {
                    'fields': [
                        {
                            'field': {'id': 'status'},
                            'from': {'key': 'open'},
                            'to': {'key': 'approved'},
                        },
                    ],
                    'updatedAt': '2019-11-02T15:15:00.000+0000',
                    'updatedBy': {'id': 'user_updater'},
                },
                {
                    'fields': [
                        {
                            'field': {'id': 'status'},
                            'from': {'key': 'approved'},
                            'to': {'key': 'closed'},
                        },
                    ],
                    'updatedAt': '2019-11-03T15:15:00.000+0000',
                    'updatedBy': {'id': 'user_updater'},
                },
            ],
            datetime.datetime(2019, 11, 2, 15, 15, 0),
            id='changed after approve',
        ),
        pytest.param(
            'TAXIRATE-123',
            [
                {
                    'fields': [
                        {
                            'field': {'id': 'status'},
                            'from': None,
                            'to': {'key': 'open'},
                        },
                    ],
                    'updatedAt': '2019-11-01T15:15:00.000+0000',
                    'updatedBy': {'id': 'user_updater'},
                },
                {
                    'fields': [
                        {
                            'field': {'id': 'status'},
                            'from': {'key': 'open'},
                            'to': {'key': 'approved'},
                        },
                    ],
                    'updatedAt': '2019-11-02T15:15:00.000+0000',
                    'updatedBy': {'id': 'user_updater'},
                },
                {
                    'fields': [
                        {
                            'field': {'id': 'status'},
                            'from': {'key': 'approved'},
                            'to': {'key': 'closed'},
                        },
                    ],
                    'updatedAt': '2019-11-03T15:15:00.000+0000',
                    'updatedBy': {'id': 'user_updater'},
                },
                {
                    'fields': [
                        {
                            'field': {'id': 'status'},
                            'from': {'key': 'open'},
                            'to': {'key': 'approved'},
                        },
                    ],
                    'updatedAt': '2019-11-04T15:15:00.000+0000',
                    'updatedBy': {'id': 'user_updater'},
                },
                {
                    'fields': [
                        {
                            'field': {'id': 'status'},
                            'from': {'key': 'approved'},
                            'to': {'key': 'closed'},
                        },
                    ],
                    'updatedAt': '2019-11-05T15:15:00.000+0000',
                    'updatedBy': {'id': 'user_updater'},
                },
            ],
            datetime.datetime(2019, 11, 4, 15, 15, 0),
            id='multiple approve',
        ),
    ],
)
async def test_last_approved_at(
        test_taxi_app, ticket_key, get_field_history, expected,
):
    class StartrackAPIClientMock:
        async def get_field_history(
                self, ticket, field_name, page_size=100, log_extra=None,
        ):
            assert ticket == ticket_key
            return get_field_history

    checker = audit.TicketChecker(
        StartrackAPIClientMock(), test_taxi_app.config,
    )

    assert await checker.last_approved_at(ticket_key) == expected


@pytest.mark.config(
    ADMIN_AUDIT_TICKET_CHECK_AUTHOR=True,
    ADMIN_AUDIT_TICKET_CHECK_APPROVER=True,
    ADMIN_AUDIT_TICKET_CONFIG={
        'enabled': True,
        'queues': {
            'TAXIRATE': {
                'statuses': ['approved'],
                'approvers': ['good_approver'],
                'approvers_rules': ['not_in_performers'],
            },
        },
    },
)
@pytest.mark.parametrize(
    'ticket_key, get_ticket, get_field_history, expected',
    [
        pytest.param(
            'BLABLABLA-123',
            {},
            [],
            'Wrong ticket queue',
            id='Wrong ticket queue',
        ),
        pytest.param(
            'TAXIRATE-123',
            {
                'status': {'key': 'open'},
                'createdBy': {'id': 'user_creater'},
                'assignee': {'id': 'user_creater'},
            },
            [],
            'Wrong ticket status',
            id='Wrong ticket status',
        ),
        pytest.param(
            'TAXIRATE-123',
            {
                'status': {'key': 'approved'},
                'createdBy': {'id': 'user_action_performer'},
                'assignee': {'id': 'user_creater'},
            },
            [],
            'You cannot perform an action with ticket created by yourself',
            id='action with ticket created by yourself',
        ),
        pytest.param(
            'TAXIRATE-123',
            {
                'status': {'key': 'approved'},
                'createdBy': {'id': 'user_creater'},
                'assignee': {'id': 'user_creater'},
            },
            [
                {
                    'fields': [
                        {
                            'field': {'id': 'status'},
                            'from': None,
                            'to': {'key': 'open'},
                        },
                    ],
                    'updatedAt': '2019-11-01T15:15:00.000+0000',
                    'updatedBy': {'id': 'user_updater'},
                },
                {
                    'fields': [
                        {
                            'field': {'id': 'status'},
                            'from': {'key': 'open'},
                            'to': {'key': 'approved'},
                        },
                    ],
                    'updatedAt': '2019-11-02T15:15:00.000+0000',
                    'updatedBy': {'id': 'user_action_performer'},
                },
            ],
            'You cannot perform an action with ticket approved by yourself',
            id='action with ticket approved by yourself',
        ),
        pytest.param(
            'TAXIRATE-123',
            {
                'status': {'key': 'approved'},
                'createdBy': {'id': 'user_creater'},
                'assignee': {'id': 'user_creater'},
            },
            [
                {
                    'fields': [
                        {
                            'field': {'id': 'status'},
                            'from': None,
                            'to': {'key': 'open'},
                        },
                    ],
                    'updatedAt': '2019-11-01T15:15:00.000+0000',
                    'updatedBy': {'id': 'user_updater'},
                },
                {
                    'fields': [
                        {
                            'field': {'id': 'status'},
                            'from': {'key': 'open'},
                            'to': {'key': 'approved'},
                        },
                    ],
                    'updatedAt': '2019-11-02T15:15:00.000+0000',
                    'updatedBy': {'id': 'some_approver'},
                },
            ],
            (
                'You cannot perform an action with ticket approved by'
                ' non legitimate approver'
            ),
            id='non legitimate approver',
        ),
        pytest.param(
            'TAXIRATE-123',
            {
                'status': {'key': 'approved'},
                'createdBy': {'id': 'user_creater'},
                'assignee': {'id': 'good_approver'},
            },
            [
                {
                    'fields': [
                        {
                            'field': {'id': 'status'},
                            'from': None,
                            'to': {'key': 'open'},
                        },
                    ],
                    'updatedAt': '2019-11-01T15:15:00.000+0000',
                    'updatedBy': {'id': 'user_updater'},
                },
                {
                    'fields': [
                        {
                            'field': {'id': 'status'},
                            'from': {'key': 'open'},
                            'to': {'key': 'approved'},
                        },
                    ],
                    'updatedAt': '2019-11-02T15:15:00.000+0000',
                    'updatedBy': {'id': 'good_approver'},
                },
            ],
            'You cannot perform an action with ticket approved by assignee',
            id='approved by assignee',
        ),
        pytest.param(
            'TAXIRATE-123',
            {
                'status': {'key': 'approved'},
                'createdBy': {'id': 'user_creater'},
                'assignee': {},
            },
            [
                {
                    'fields': [
                        {
                            'field': {'id': 'status'},
                            'from': None,
                            'to': {'key': 'open'},
                        },
                    ],
                    'updatedAt': '2019-11-01T15:15:00.000+0000',
                    'updatedBy': {'id': 'user_updater'},
                },
                {
                    'fields': [
                        {
                            'field': {'id': 'status'},
                            'from': {'key': 'open'},
                            'to': {'key': 'approved'},
                        },
                    ],
                    'updatedAt': '2019-11-02T15:15:00.000+0000',
                    'updatedBy': {'id': 'good_approver'},
                },
            ],
            'You cannot perform an action with ticket without assignee',
            id='no assignee',
        ),
    ],
)
async def test_check(
        test_taxi_app, ticket_key, get_ticket, get_field_history, expected,
):
    """Very basic test cases for checker."""

    class StartrackAPIClientMock:
        async def get_ticket(self, ticket, log_extra=None):
            assert ticket == ticket_key
            return get_ticket

        async def get_field_history(
                self, ticket, field_name, page_size=100, log_extra=None,
        ):
            assert ticket == ticket_key
            return get_field_history

    checker = audit.TicketChecker(
        StartrackAPIClientMock(), test_taxi_app.config,
    )
    with pytest.raises(audit.TicketError) as excinfo:
        await checker.check(
            ticket_key, 'user_action_performer', should_check_ticket=True,
        )

    assert expected in str(excinfo.value)


@pytest.mark.parametrize(
    'ticket_data,parsed_key',
    [
        (None, None),
        ('', ''),
        ('https://st.test.yandex-team.ru', ''),
        ('https://st.test.yandex-team.ru/', ''),
        ('TAXIPLATFORM-123', 'TAXIPLATFORM-123'),
        ('/TAXIPLATFORM-123', '/TAXIPLATFORM-123'),
        ('TAXIPLATFORM-123/', 'TAXIPLATFORM-123/'),
        ('/TAXIPLATFORM-123/', '/TAXIPLATFORM-123/'),
        (
            'https://st.test.yandex-team.ru/TAXIPLATFORM-123',
            'TAXIPLATFORM-123',
        ),
        (
            'https://st.test.yandex-team.ru/TAXIPLATFORM-123/',
            'TAXIPLATFORM-123',
        ),
        (
            'https://st.not-yandex-team.ru/TAXIPLATFORM-123',
            'https://st.not-yandex-team.ru/TAXIPLATFORM-123',
        ),
        (
            'https://not-st.yandex-team.ru/TAXIPLATFORM-123',
            'https://not-st.yandex-team.ru/TAXIPLATFORM-123',
        ),
    ],
)
def test_parse_ticket_key_in_link(ticket_data, parsed_key):
    assert audit.parse_ticket_key_in_link(ticket_data) == parsed_key
