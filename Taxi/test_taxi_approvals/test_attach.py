import dataclasses
import typing

import pytest


@dataclasses.dataclass(frozen=True)
class AttachNewTicketTestCase:
    draft_id: int
    summary: typing.Optional[str] = 'test_summary'
    description: typing.Optional[str] = 'test_description'
    components: typing.Optional[typing.List] = dataclasses.field(
        default_factory=list,
    )
    tags: typing.Optional[typing.List] = dataclasses.field(
        default_factory=list,
    )
    relates: typing.Optional[typing.List] = dataclasses.field(
        default_factory=list,
    )

    @property
    def request_data(self):
        body = {}
        if self.summary is not None:
            body['summary'] = self.summary
        if self.description is not None:
            body['description'] = self.description
        if self.components is not None:
            body['components'] = self.components
        if self.tags is not None:
            body['tags'] = self.tags
        if self.relates is not None:
            body['relationships'] = {'relates': self.relates}
        return body


@dataclasses.dataclass(frozen=True)
class AttachExistedTicketTestCase:
    draft_id: int
    mock_check_ticket_exists: bool = False
    ticket: typing.Optional[str] = None

    @property
    def request_data(self):
        body = {}
        if self.ticket is not None:
            body['ticket'] = self.ticket
        return body


@dataclasses.dataclass(frozen=True)
class AttachResponse:
    status: int
    attached_ticket: typing.Optional[str] = None
    tickets: typing.Optional[typing.List[str]] = None
    comments: typing.Optional[typing.List[dict]] = None
    error_code: typing.Optional[str] = None

    @property
    def response_data(self):
        return {
            'tickets': self.tickets,
            'attached': self.attached_ticket,
            'comments': self.comments,
        }


def _create_comments(
        *, existed_tickets=None, new_ticket=None, extend_comments=None,
):
    comments = [] if not extend_comments else extend_comments
    if existed_tickets:
        tickets = ', '.join(existed_tickets)
        if len(existed_tickets) == 1:
            comment = f'test_login прикрепил тикет {tickets}'
        else:
            comment = f'test_login прикрепил тикеты {tickets}'
        comments.append({'login': 'test_login', 'comment': comment})

    if new_ticket:
        comments.append(
            {
                'login': 'test_login',
                'comment': f'test_login создал и прикрепил тикет {new_ticket}',
            },
        )
    return comments


@pytest.mark.parametrize(
    'case,response_case',
    [
        (
            AttachNewTicketTestCase(
                draft_id=2,
                components=[1],
                tags=['test_tag'],
                relates=['TESTTICKET-1', 'TESTTICKET-2'],
            ),
            AttachResponse(
                status=200,
                attached_ticket='RUPRICING-100',
                tickets=['RUPRICING-100'],
                comments=_create_comments(
                    new_ticket='RUPRICING-100',
                    extend_comments=[
                        {'login': 'test_login', 'comment': 'meow'},
                    ],
                ),
            ),
        ),
        (
            AttachNewTicketTestCase(
                draft_id=2, summary=None, description=None,
            ),
            AttachResponse(status=400, error_code='invalid-input'),
        ),
        (
            AttachNewTicketTestCase(draft_id=3),
            AttachResponse(
                status=200,
                attached_ticket='RUPRICING-100',
                tickets=['RUPRICING-100'],
                comments=_create_comments(new_ticket='RUPRICING-100'),
            ),
        ),
    ],
)
@pytest.mark.config(
    APPROVALS_NAMESPACES_CONFIG={'tariff_editor_namespaces': ['taxi']},
)
@pytest.mark.pgsql('approvals', files=['edit.sql'])
async def test_attach_new_ticket(taxi_approvals_client, case, response_case):
    response = await taxi_approvals_client.post(
        f'drafts/{case.draft_id}/attach_new_ticket/',
        json=case.request_data,
        headers={'X-Yandex-Login': 'test_login'},
    )

    content = await response.json()
    assert response.status == response_case.status, content
    if response_case.status == 200:
        assert content == response_case.response_data
    else:
        assert response_case.error_code == content['code']


@pytest.mark.parametrize(
    'case,response_case',
    [
        (
            AttachExistedTicketTestCase(draft_id=1, ticket='TAXIRATE-35'),
            AttachResponse(status=400, error_code='TICKET_ERROR'),
        ),
        (
            AttachExistedTicketTestCase(draft_id=1, ticket='TAXIRATE-36'),
            AttachResponse(
                status=200,
                attached_ticket='TAXIRATE-36',
                tickets=['TAXIRATE-35', 'TAXIRATE-36'],
                comments=_create_comments(existed_tickets=['TAXIRATE-36']),
            ),
        ),
        (
            AttachExistedTicketTestCase(draft_id=1, ticket='TAXIRATE-37'),
            AttachResponse(status=404, error_code='NOT_FOUND'),
        ),
        (
            AttachExistedTicketTestCase(draft_id=1, ticket=''),
            AttachResponse(status=400, error_code='TICKET_EMPTY'),
        ),
        (
            AttachExistedTicketTestCase(
                draft_id=1,
                mock_check_ticket_exists=True,
                ticket='TAXIRATE-35',
            ),
            AttachResponse(status=409, error_code='VERSION_ERROR'),
        ),
        (
            AttachExistedTicketTestCase(draft_id=1, ticket=None),
            AttachResponse(status=400, error_code='invalid-input'),
        ),
        (
            AttachExistedTicketTestCase(draft_id=3, ticket='TAXIRATE-36'),
            AttachResponse(
                status=200,
                attached_ticket='TAXIRATE-36',
                tickets=['TAXIRATE-36'],
                comments=_create_comments(existed_tickets=['TAXIRATE-36']),
            ),
        ),
    ],
)
@pytest.mark.config(
    APPROVALS_NAMESPACES_CONFIG={'tariff_editor_namespaces': ['taxi']},
)
@pytest.mark.pgsql('approvals', files=['edit.sql'])
async def test_attach_existed_ticket(
        patch, taxi_approvals_client, case, response_case,
):
    if case.mock_check_ticket_exists:

        @patch('taxi_approvals.api.drafts._check_tickets')
        def _check_tickets(*args, **kwargs):
            return

    response = await taxi_approvals_client.post(
        f'drafts/{case.draft_id}/attach_existed_ticket/',
        json=case.request_data,
        headers={'X-Yandex-Login': 'test_login'},
    )

    content = await response.json()
    assert response.status == response_case.status
    if response_case.status == 200:
        assert content == response_case.response_data
    else:
        assert response_case.error_code == content['code']
