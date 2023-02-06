import dataclasses
import re
from typing import Dict
from typing import List
from typing import Optional
from typing import Type

import pytest

import tests.plugins.common

TICKET_REGEX = re.compile(r'^[A-Z]{2,}-\d+$')


class StartrekException(NotImplementedError):
    pass


@dataclasses.dataclass
class TicketComments:
    comment_list: Optional[List[Dict[str, str]]] = None
    error_message: Optional[str] = None
    status_code: int = 200

    def as_response(
            self, response_cls: Type[tests.plugins.common.ResponseMock],
    ) -> tests.plugins.common.ResponseMock:
        if self.status_code < 400:
            return response_cls(
                json=self.comment_list, status_code=self.status_code,
            )
        return response_cls(
            text='',
            json={
                'errors': {},
                'errorMessages': [self.error_message],
                'statusCode': self.status_code,
            },
            status_code=self.status_code,
        )


# pylint: disable=too-many-instance-attributes
class Startrek:
    def __init__(self, patch_requests, mock):
        self._response = patch_requests.response
        self._base_url = 'https://st-api.test.yandex-team.ru/v2/'
        patch_requests(self._base_url)(self._request)
        self.taxirel_components = [
            {'name': 'backend-py2', 'id': 22},
            {'name': 'some-prefix-backend-py2', 'id': 222},
            {'name': 'backend-cpp', 'id': 33},
            {'name': 'antifraud', 'id': 35},
            {'name': 'surger', 'id': 36},
            {'name': 'taxi-adjust', 'id': 78},
            {'name': 'driver-authorizer', 'id': 93},
            {'name': 'driver-authorizer3', 'id': 95},
            {'name': 'protocol', 'id': 75},
            {'name': 'taxi-graph', 'id': 94},
            {'name': 'taxi-plotva-ml', 'id': 89},
            {'name': 'driver-protocol', 'id': 49},
            {'name': 'reposition', 'id': 58},
            {'name': 'lxc', 'id': 42},
            {'name': 'sandbox-resources', 'id': 41},
        ]
        self.component_opened = {}
        self.comments: Dict[str, TicketComments] = {}
        self.create_ticket = mock(self.create_ticket)
        self.create_comment = mock(self.create_comment)
        self.get_ticket = mock(self.get_ticket)
        self.update_ticket = mock(self.update_ticket)
        self.create_component = mock(self.create_component)
        self.get_opened_releases = mock(self.get_opened_releases)
        self.ticket_status = 'open'
        self.ticket_assignee = ''
        self.ticket_components = []

    # pylint: disable=method-hidden
    @staticmethod
    def create_ticket(json):  # type: ignore
        return {'key': 'TAXIREL-222'}

    @staticmethod
    def create_comment(json):
        return {}

    # pylint: disable=method-hidden
    def get_ticket(self, ticket):  # type: ignore
        ticket_info = {
            'key': 'TAXIREL-11585',
            'description': 'some\ntext',
            'summary': 'summary',
            'status': {'key': self.ticket_status},
            'components': self.ticket_components,
        }
        if self.ticket_assignee:
            ticket_info['assignee'] = {'id': self.ticket_assignee}
        return ticket_info

    def get_opened_releases(self, component):
        return self.component_opened.get(component, [])

    @staticmethod
    def create_component(json):
        return {'id': 100, 'name': json['name']}

    # pylint: disable=method-hidden
    @staticmethod
    def update_ticket(ticket, json):  # type: ignore
        return {'key': 'TAXIREL-11585'}

    def _request(self, method, url, **kwargs):
        path = url[len(self._base_url) :]

        if path == 'queues/TAXIREL/components':
            assert method.upper() == 'GET'
            return self._response(json=self.taxirel_components)

        component_path = (
            'issues?query=queue: TAXIREL and status: !closed and components: '
        )
        if path.startswith(component_path):
            assert method.upper() == 'GET'
            component = int(path[len(component_path) :])
            return self._response(json=self.get_opened_releases(component))

        if path == 'issues':
            assert method.upper() == 'POST'
            return self._response(201, json=self.create_ticket(kwargs['json']))

        if path == 'components':
            assert method.upper() == 'POST'
            return self._response(
                201, json=self.create_component(kwargs['json']),
            )
        issues_path = 'issues/'
        if path.startswith(issues_path):
            ticket = path.split('/')[1]
            assert TICKET_REGEX.match(ticket), f'Invalid ticket URL {path}'
            if path.endswith('/comments'):
                if method.upper() == 'POST':
                    return self._response(
                        json=self.create_comment(kwargs['json']),
                        status_code=201,
                    )
                if method.upper() == 'GET':
                    ticket_comments = self.comments.get(ticket, None)

                    if ticket_comments:
                        return ticket_comments.as_response(self._response)
                    return self._response(json=[], status_code=200)

            if method.upper() == 'GET':
                return self._response(json=self.get_ticket(ticket))
            if method.upper() == 'PATCH':
                return self._response(
                    json=self.update_ticket(ticket, kwargs['json']),
                )

        raise StartrekException(url)


@pytest.fixture
def startrek(monkeypatch, patch_requests, mock):
    monkeypatch.setenv('STARTREK_TOKEN', 'stoken')
    return Startrek(patch_requests, mock)
