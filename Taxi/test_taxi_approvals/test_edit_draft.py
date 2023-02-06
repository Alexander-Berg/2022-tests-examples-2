import dataclasses
import json
import typing

import pytest

from taxi_approvals.internal import models


@dataclasses.dataclass(frozen=True)
class EditTestCase:
    draft_id: int
    service_name: str = 'test_service'
    api_path: str = 'test_api'
    run_manually: bool = True
    mode: str = 'push'
    lock_ids: typing.Optional[list] = None
    deferred_apply: typing.Optional[str] = None
    route_method: str = 'POST'
    route_headers: typing.Optional[typing.Dict[str, str]] = None
    route_params: typing.Optional[typing.Dict[str, str]] = None
    date_expired: typing.Optional[str] = None
    extra_headers: typing.Optional[typing.Dict[str, str]] = None

    @property
    def request_data(self):
        data = {
            'service_name': self.service_name,
            'api_path': self.api_path,
            'request_id': 'test_id',
            'run_manually': self.run_manually,
            'data': {'test_data_key_new': 'test_data_value_new'},
            'mode': self.mode,
        }
        if self.deferred_apply is not None:
            data['deferred_apply'] = self.deferred_apply

        if self.date_expired is not None:
            data['date_expired'] = self.date_expired
        return data


@dataclasses.dataclass(frozen=True)
class EditResponse:
    draft_id: int
    status_code: int
    service_name: str = 'test_service'
    api_path: str = 'test_api'
    run_manually: bool = True
    mode: str = 'push'
    error_code: typing.Optional[str] = None
    deferred_apply: typing.Optional[str] = None
    headers: typing.Optional[typing.Dict[str, str]] = None
    date_expired: typing.Optional[str] = None
    scheme_type: models.SchemeType = models.SchemeType.ADMIN
    tplatform_namespace: typing.Optional[str] = None

    @property
    def response_data(self):
        response = {
            'service_name': self.service_name,
            'api_path': self.api_path,
            'run_manually': self.run_manually,
            'data': {'test_data_key_new': 'test_data_value_new'},
            'mode': self.mode,
            'approvals': [],
            'status': 'need_approval',
            'ticket': 'TAXIRATE-35',
            'tickets': ['TAXIRATE-35'],
            'comments': [],
            'created': '2017-11-01T04:10:00+0300',
            'created_by': 'test_user',
            'id': self.draft_id,
            'change_doc_id': 'test_doc_id',
            'summary': {'current': {}, 'new': {}},
            'version': 2,
            'object_id': f'{self.service_name}:{self.api_path}',
            'errors': [],
            'headers': self.headers or {},
            'query_params': {},
            'scheme_type': self.scheme_type.value,
        }
        if self.deferred_apply is not None:
            response['deferred_apply'] = self.deferred_apply

        if self.date_expired is not None:
            response['date_expired'] = self.date_expired

        if self.tplatform_namespace:
            response['tplatform_namespace'] = self.tplatform_namespace
        return response


@pytest.mark.parametrize(
    'case,response_case',
    [
        (
            EditTestCase(
                draft_id=1,
                service_name='test_service',
                api_path='test_api',
                deferred_apply='2018-01-01T12:00:00+02:00',
                date_expired='2021-01-01T12:00:00+02:00',
                run_manually=False,
                route_headers={
                    'X-YaTaxi-Draft-Author': 'test_user',
                    'X-YaTaxi-Draft-DeferredApply': '2018-01-01T13:00:00+0300',
                    'X-YaTaxi-Draft-RunType': 'automatically',
                    'X-YaTaxi-Draft-Tickets': 'TAXIRATE-35',
                    'X-YaTaxi-Draft-Service-Name': 'test_service',
                    'X-YaTaxi-Draft-Api-Path': 'test_api',
                },
            ),
            EditResponse(
                draft_id=1,
                status_code=200,
                service_name='test_service',
                api_path='test_api',
                deferred_apply='2018-01-01T13:00:00+0300',
                run_manually=False,
                headers={},
                date_expired='2021-01-01T13:00:00+0300',
                tplatform_namespace='taxi',
            ),
        ),
        (
            EditTestCase(
                draft_id=1,
                deferred_apply='2016-01-01T12:00:00+02:00',
                run_manually=False,
            ),
            EditResponse(
                draft_id=1,
                status_code=400,
                error_code='DEFERRED_APPLY_TIME_ERROR',
            ),
        ),
        (
            EditTestCase(
                draft_id=1,
                deferred_apply='2018-01-01T12:00:00+02:00',
                run_manually=True,
            ),
            EditResponse(
                draft_id=1,
                status_code=400,
                error_code='DEFERRED_APPLY_MANUALLY_ERROR',
            ),
        ),
        (
            EditTestCase(
                draft_id=1,
                deferred_apply='2018-01-01T12:00:00+02:00',
                run_manually=False,
                mode='poll',
            ),
            EditResponse(
                draft_id=1,
                status_code=400,
                error_code='DEFERRED_APPLY_MODE_ERROR',
            ),
        ),
        (
            EditTestCase(
                draft_id=1,
                service_name='test_service',
                api_path='test_api',
                lock_ids=[
                    {'custom': False, 'id': 'lock_id_3'},
                    {'custom': False, 'id': 'lock_id_4'},
                ],
                route_headers={
                    'X-YaTaxi-Draft-Author': 'test_user',
                    'X-YaTaxi-Draft-RunType': 'manually',
                    'X-YaTaxi-Draft-Tickets': 'TAXIRATE-35',
                    'X-YaTaxi-Draft-Service-Name': 'test_service',
                    'X-YaTaxi-Draft-Api-Path': 'test_api',
                },
                extra_headers={},
            ),
            EditResponse(
                draft_id=1,
                status_code=200,
                service_name='test_service',
                api_path='test_api',
                headers={},
                tplatform_namespace='taxi',
            ),
        ),
        (
            EditTestCase(
                draft_id=1,
                service_name='test_service',
                api_path='test_api2',
                lock_ids=[
                    {'custom': False, 'id': 'lock_id_3'},
                    {'custom': False, 'id': 'lock_id_2'},
                ],
            ),
            EditResponse(
                draft_id=1,
                status_code=409,
                service_name='test_service',
                api_path='test_api2',
                error_code='EXISTED_LOCK',
            ),
        ),
        (
            EditTestCase(
                draft_id=3, service_name='test_service', api_path='test_api2',
            ),
            EditResponse(
                draft_id=3, status_code=400, error_code='WRONG_DRAFT_TYPE',
            ),
        ),
    ],
)
@pytest.mark.config(
    APPROVALS_NAMESPACES_CONFIG={'tariff_editor_namespaces': ['taxi']},
)
@pytest.mark.pgsql('approvals', files=['edit.sql'])
@pytest.mark.now('2017-11-01T01:10:00+0300')
async def test_edit_draft(
        taxi_approvals_client,
        case,
        response_case,
        check_route_mock,
        create_reports_mock,
):
    check_route_mock(
        change_doc_id='test_doc_id',
        lock_ids=case.lock_ids,
        route_method=case.route_method,
        route_headers=case.route_headers,
        route_params=case.route_params,
    )
    summary = {'current': {}, 'new': {}}
    create_reports_mock(
        response_case.draft_id,
        summary,
        response_case.service_name,
        response_case.api_path,
        ['TAXIRATE-35'],
        login='test_user',
    )

    headers = {'X-Yandex-Login': 'test_user'}
    if case.extra_headers:
        headers.update(case.extra_headers)
    response = await taxi_approvals_client.post(
        f'/drafts/{case.draft_id}/edit/',
        data=json.dumps(case.request_data),
        headers=headers,
    )
    content = await response.json()
    assert response.status == response_case.status_code
    if response_case.status_code != 200:
        assert content['code'] == response_case.error_code
    else:
        assert content.pop('updated')
        assert content == response_case.response_data
