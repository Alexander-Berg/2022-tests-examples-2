import dataclasses
import typing

from taxi_approvals.internal import models


@dataclasses.dataclass(frozen=True)
class CreateTestCase:
    service_name: str = 'test_service'
    api_path: str = 'test_api'
    change_doc_id: str = 'test_doc_id'
    run_manually: bool = True
    mode: str = 'push'
    attach_tickets: typing.Optional[dict] = None
    summon_users: typing.Optional[list] = None
    lock_ids_from_check: typing.Optional[list] = None
    deferred_apply: typing.Optional[str] = None
    route_method: str = 'POST'
    route_headers: typing.Optional[typing.Dict[str, str]] = None
    extra_headers: typing.Optional[typing.Dict[str, str]] = None
    route_params: typing.Optional[typing.Dict[str, str]] = None
    ticket_data_from_check: typing.Optional[dict] = None
    summon_users_from_check: typing.Optional[list] = None
    check_mode: typing.Optional[str] = None
    data: typing.Optional[dict] = None
    description: typing.Optional[str] = None
    date_expired: typing.Optional[str] = None
    is_platform: bool = False
    is_bank: bool = False
    is_wfm_effrat: bool = False
    check_tplatform_namespace: typing.Optional[str] = None

    def request_data(self, data=None):
        body = {
            'service_name': self.service_name,
            'api_path': self.api_path,
            'request_id': 'test_id',
            'run_manually': self.run_manually,
            'data': data if data else {'test_data_key': 'test_data_value'},
            'description': 'just_random_comment',
            'mode': self.mode,
        }
        if self.attach_tickets is not None:
            body['tickets'] = self.attach_tickets
        if self.summon_users is not None:
            body['summon_users'] = self.summon_users
        if self.deferred_apply is not None:
            body['deferred_apply'] = self.deferred_apply
        if self.date_expired is not None:
            body['date_expired'] = self.date_expired
        return body


@dataclasses.dataclass(frozen=True)
class CreateResponse:
    status: int
    version: int = 1
    service_name: str = 'test_service'
    api_path: str = 'test_api'
    expected_change_doc_id: str = 'test_doc_id'
    run_manually: bool = True
    mode: str = 'push'
    error_code: typing.Optional[str] = None
    summoned_users: typing.Optional[list] = None
    comments: typing.Optional[list] = None
    attached_tickets: typing.Optional[list] = None
    deferred_apply: typing.Optional[str] = None
    headers: typing.Optional[typing.Dict[str, str]] = None
    query_params: typing.Optional[typing.Dict[str, str]] = None
    date_expired: typing.Optional[str] = None
    data: typing.Optional[dict] = None
    scheme_type: models.SchemeType = models.SchemeType.ADMIN
    tplatform_namespace: typing.Optional[str] = None

    @property
    def response_data(self):
        response = {
            'created_by': 'test_login',
            'description': 'description from service answer',
            'created': '2017-11-01T01:10:00+0300',
            'run_manually': self.run_manually,
            'service_name': self.service_name,
            'api_path': self.api_path,
            'data': (
                self.data
                if self.data
                else {'test_data_key': 'test_data_value'}
            ),
            'updated': '2017-11-01T01:10:00+0300',
            'approvals': [],
            'version': self.version,
            'comments': [],
            'mode': self.mode,
            'status': 'need_approval',
            'change_doc_id': self.expected_change_doc_id,
            'summoned_users': [],
            'summary': {},
            'object_id': f'{self.service_name}:{self.api_path}',
            'errors': [],
            'headers': self.headers or {},
            'query_params': self.query_params or {},
            'scheme_type': self.scheme_type.value,
        }

        if self.attached_tickets is not None:
            response['tickets'] = self.attached_tickets
            if response['tickets']:
                response['ticket'] = response['tickets'][0]

        if self.summoned_users is not None:
            response['summoned_users'] = self.summoned_users

        if self.comments is not None:
            response['comments'] = self.comments

        if self.deferred_apply is not None:
            response['deferred_apply'] = self.deferred_apply

        if self.date_expired is not None:
            response['date_expired'] = self.date_expired

        if self.tplatform_namespace:
            response['tplatform_namespace'] = self.tplatform_namespace

        return response
