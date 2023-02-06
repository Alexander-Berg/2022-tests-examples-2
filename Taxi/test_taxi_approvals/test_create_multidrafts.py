import dataclasses
import typing

import pytest

from taxi_approvals.internal import headers as headers_module
from taxi_approvals.internal import models


@dataclasses.dataclass(frozen=True)
class CreateTestCase:
    responsibles: typing.Optional[list] = None
    attach_tickets: typing.Optional[dict] = None
    attach_drafts: typing.Optional[list] = None
    is_platform: bool = False

    @property
    def request_data(self):
        body = {'request_id': 'test_id', 'description': 'test_description'}
        if self.responsibles is not None:
            body['responsibles'] = self.responsibles
        if self.attach_tickets is not None:
            body['tickets'] = self.attach_tickets
        if self.attach_drafts is not None:
            body['attach_drafts'] = self.attach_drafts
        return body


@dataclasses.dataclass(frozen=True)
class CreateResponse:
    status: int
    version: int = 1
    responsibles: typing.Optional[list] = None
    error_code: typing.Optional[str] = None
    comments: typing.Optional[list] = None
    attached_tickets: typing.Optional[list] = None
    draft_status: typing.Optional[str] = None
    approvals: typing.Optional[list] = None
    draft_types: typing.Optional[list] = None
    scheme_type: models.SchemeType = models.SchemeType.ADMIN

    @property
    def response_data(self):
        response = {
            'comments': [],
            'created': '2017-11-01T01:10:00+0300',
            'created_by': 'test_login',
            'description': 'test_description',
            'tickets': [],
            'data': {},
            'updated': '2017-11-01T01:10:00+0300',
            'version': self.version,
            'scheme_type': self.scheme_type.value,
        }

        if self.attached_tickets is not None:
            response['tickets'] = self.attached_tickets

        if self.comments is not None:
            response['comments'] = self.comments

        if self.responsibles is not None:
            response['responsibles'] = self.responsibles

        if self.draft_status is not None:
            response['status'] = self.draft_status
        if self.approvals is not None:
            response['approvals'] = self.approvals

        if self.draft_types is not None:
            response['draft_types'] = self.draft_types

        return response


@pytest.mark.parametrize(
    'case,response_case',
    [
        (
            CreateTestCase(
                attach_tickets={
                    'existed': ['TAXIRATE-35'],
                    'create_data': {
                        'summary': 'test_summary',
                        'description': 'test_description',
                    },
                },
            ),
            CreateResponse(
                status=200,
                version=3,
                comments=[
                    {
                        'comment': 'test_login прикрепил тикет TAXIRATE-35',
                        'login': 'test_login',
                    },
                    {
                        'comment': (
                            'test_login создал и '
                            'прикрепил тикет RUPRICING-100'
                        ),
                        'login': 'test_login',
                    },
                ],
                attached_tickets=['TAXIRATE-35', 'RUPRICING-100'],
                draft_status='need_approval',
            ),
        ),
        (
            CreateTestCase(
                responsibles=['test_login', 'test_login_1', 'test_login_2'],
            ),
            CreateResponse(
                status=200,
                responsibles=['test_login', 'test_login_2'],
                draft_status='need_approval',
            ),
        ),
        (
            CreateTestCase(
                attach_drafts=[
                    {'id': 3, 'version': 2},
                    {'id': 5, 'version': 2},
                ],
            ),
            CreateResponse(
                status=200,
                draft_status='need_approval',
                approvals=[],
                draft_types=[
                    {'api_path': 'test_api2', 'service_name': 'test_service2'},
                ],
            ),
        ),
        (
            CreateTestCase(
                attach_drafts=[
                    {'id': 1, 'version': 1},
                    {'id': 4, 'version': 2},
                ],
            ),
            CreateResponse(status=400, error_code='ATTACH_DRAFTS_ERROR'),
        ),
        (
            CreateTestCase(
                attach_drafts=[
                    {'id': 1, 'version': 1},
                    {'id': 2, 'version': 2},
                ],
            ),
            CreateResponse(status=400, error_code='WRONG_STATUS_DRAFT'),
        ),
        (
            CreateTestCase(attach_drafts=[], is_platform=True),
            CreateResponse(
                status=200,
                scheme_type=models.SchemeType.PLATFORM,
                draft_status='need_approval',
            ),
        ),
        (
            CreateTestCase(
                attach_drafts=[{'id': 19, 'version': 2}], is_platform=True,
            ),
            CreateResponse(
                status=200,
                scheme_type=models.SchemeType.PLATFORM,
                draft_status='need_approval',
                draft_types=[
                    {'api_path': 'test_api', 'service_name': 'good_service'},
                ],
                approvals=[],
            ),
        ),
        (
            CreateTestCase(
                attach_drafts=[{'id': 3, 'version': 2}], is_platform=True,
            ),
            CreateResponse(status=400, error_code='WRONG_SCHEME_TYPE'),
        ),
    ],
)
@pytest.mark.pgsql('approvals', files=['data.sql'])
@pytest.mark.now('2017-11-01T01:10:00+0300')
async def test_create_multidraft(
        taxi_approvals_client, case, response_case, grands_retrieve_mock,
):
    headers = {headers_module.X_YANDEX_LOGIN: 'test_login'}
    grands_retrieve_mock()
    if case.is_platform:
        headers[headers_module.X_MULTISERVICES_PLATFORM] = 'true'
    response = await taxi_approvals_client.post(
        '/multidrafts/create/', json=case.request_data, headers=headers,
    )
    content = await response.json()
    assert response.status == response_case.status, content
    if response.status == 200:
        content.pop('id')
        assert content == response_case.response_data
    else:
        assert content['code'] == response_case.error_code
