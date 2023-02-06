import dataclasses
import typing

import pytest

from taxi_approvals.internal import models


@dataclasses.dataclass(frozen=True)
class CreateTestCase:
    attach_drafts: typing.Optional[list] = None
    description: typing.Optional[str] = None
    version: typing.Optional[int] = None
    tickets: typing.Optional[dict] = None

    @property
    def request_data(self):
        body = {'request_id': 'test_id', 'description': 'test_description'}
        if self.attach_drafts is not None:
            body['attach_drafts'] = self.attach_drafts
        if self.description is not None:
            body['description'] = self.description
        if self.version is not None:
            body['version'] = self.version
        if self.tickets is not None:
            body['tickets'] = self.tickets
        return body


@dataclasses.dataclass(frozen=True)
class CreateResponse:
    status: int
    version: int = 1
    draft_id: typing.Optional[int] = None
    responsibles: typing.Optional[list] = None
    error_code: typing.Optional[str] = None
    comments: typing.Optional[list] = None
    attach_drafts: typing.Optional[list] = None
    draft_status: typing.Optional[str] = None
    tickets: typing.Optional[list] = None
    approvals: typing.Optional[list] = None
    scheme_type: models.SchemeType = models.SchemeType.ADMIN

    @property
    def response_data(self):
        response = {
            'comments': [],
            'description': 'test_description',
            'tickets': [],
            'data': {},
            'draft_types': [
                {'api_path': 'test_api2', 'service_name': 'test_service2'},
            ],
            'created_by': 'test_user',
            'version': self.version,
            'scheme_type': self.scheme_type.value,
        }

        if self.attach_drafts is not None:
            response['attach_drafts'] = self.attach_drafts

        if self.comments is not None:
            response['comments'] = self.comments

        if self.responsibles is not None:
            response['responsibles'] = self.responsibles

        if self.draft_status is not None:
            response['status'] = self.draft_status

        if self.draft_id is not None:
            response['id'] = self.draft_id

        if self.tickets is not None:
            response['tickets'] = self.tickets
        if self.approvals is not None:
            response['approvals'] = self.approvals

        return response


@pytest.mark.parametrize(
    'draft_id,case,response_case',
    [
        (
            4,
            CreateTestCase(version=2, attach_drafts=[{'id': 6, 'version': 2}]),
            CreateResponse(status=400, error_code='ATTACH_DRAFTS_ERROR'),
        ),
        (
            4,
            CreateTestCase(
                version=2,
                attach_drafts=[
                    {'id': 3, 'version': 2},
                    {'id': 5, 'version': 2},
                ],
                tickets={'existed': ['TAXIRATE-35']},
            ),
            CreateResponse(
                status=200,
                draft_status='need_approval',
                version=4,
                draft_id=4,
                tickets=['TAXIRATE-35'],
                comments=[
                    {
                        'comment': 'test_user прикрепил тикет TAXIRATE-35',
                        'login': 'test_user',
                    },
                ],
                approvals=[],
            ),
        ),
        (
            4,
            CreateTestCase(
                version=2,
                attach_drafts=[
                    {'id': 1, 'version': 1},
                    {'id': 2, 'version': 2},
                ],
            ),
            CreateResponse(status=400, error_code='WRONG_STATUS_DRAFT'),
        ),
        (
            13,
            CreateTestCase(
                version=1,
                attach_drafts=[
                    {'id': 11, 'version': 1},
                    {'id': 12, 'version': 1},
                ],
                tickets={},
            ),
            CreateResponse(status=409, error_code='APPROVERS_GROUPS_ERROR'),
        ),
    ],
)
@pytest.mark.pgsql('approvals', files=['data.sql'])
@pytest.mark.now('2017-11-01T01:10:00+0300')
async def test_edit_multidraft(
        taxi_approvals_client, draft_id, case, response_case,
):
    response = await taxi_approvals_client.post(
        '/multidrafts/edit/',
        params={'id': draft_id},
        json=case.request_data,
        headers={'X-Yandex-Login': 'test_user'},
    )
    content = await response.json()
    assert response.status == response_case.status
    if response.status == 200:
        content.pop('created')
        content.pop('updated')
        assert content == response_case.response_data
    else:
        assert content['code'] == response_case.error_code
