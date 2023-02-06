# pylint: disable=no-member

import dataclasses
from typing import Dict
from typing import List
from typing import Sequence

import pytest


BASE_URL = 'http://configs-admin.taxi.yandex.net'


@dataclasses.dataclass
class SeanceItem:
    question: Dict = dataclasses.field(default_factory=dict)
    answer: Dict = dataclasses.field(default_factory=dict)
    is_failed: bool = False


@dataclasses.dataclass
class Seance:
    data: Sequence[SeanceItem] = dataclasses.field(default_factory=list)
    _iter: int = dataclasses.field(compare=False, default=0)

    def __iter__(self):
        self._iter = 0
        return self

    def __next__(self):
        if len(self.data) <= self._iter:
            raise StopIteration
        result = self.data[self._iter]  # pylint: disable=E1136
        self._iter += 1
        return result


@dataclasses.dataclass(eq=True)
class HistoryItem:
    path: str
    data: SeanceItem


@dataclasses.dataclass
class Parameters:
    groups: Seance = dataclasses.field(default_factory=Seance)
    definitions: Seance = dataclasses.field(default_factory=Seance)
    schemas: Seance = dataclasses.field(default_factory=Seance)
    history: List[Dict] = dataclasses.field(default_factory=list)

    def update_from_json(self, json_data):
        for handle, data in (
                ('groups', self.groups),
                ('definitions', self.definitions),
                ('schemas', self.schemas),
        ):
            self._update_from_json(
                handle=handle, seance=data, json_data=json_data,
            )

    def _update_from_json(self, handle: str, seance: Seance, json_data: Dict):
        if handle not in json_data:
            return

        section = json_data[handle]
        assert all(
            key in section for key in ('requests', 'responses', 'is_failed')
        ), (
            f'{handle}: all fields must be in static data - '
            f'`requests`, `responses`, `is_failed`. '
            f'Found: {sorted(section.keys())}'
        )
        requests = section['requests']
        responses = section['responses']
        assert len(requests) == len(
            responses,
        ), f'{handle}: count of requests must be equal count of responses'
        is_failed = section['is_failed']
        seance.data = [
            SeanceItem(question=req, answer=resp, is_failed=is_failed)
            for req, resp in zip(requests, responses)
        ]


@pytest.fixture
def configs_admin_mock(patch_requests, monkeypatch):
    monkeypatch.setenv('CONFIGS_ADMIN_URL', BASE_URL)

    prs = Parameters(
        groups=Seance(data=[SeanceItem()]),
        schemas=Seance(data=[SeanceItem()]),
        definitions=Seance(data=[SeanceItem()]),
    )

    @patch_requests(f'{BASE_URL}/v1/schemas/')
    def _send_schemas_group(method, url, **kwargs):
        if url.endswith('/actual_commit/all/'):
            assert method.upper() == 'GET'
            item = next(prs.groups)
            assert item.question == kwargs.get('params', {}), 'commits'
            prs.history.append(
                dataclasses.asdict(
                    HistoryItem(
                        f'{BASE_URL}/v1/schemas/actual_commit/all/', item,
                    ),
                ),
            )
            return patch_requests.response(json=item.answer)

        if kwargs.get('headers', {}).get('X-YaTaxi-Api-Key') != 'cool-token':
            return patch_requests.response(
                status_code=403,
                json={'code': 'auth_error', 'message': 'auth_error'},
            )
        if url.endswith('/definitions/'):
            assert method.upper() == 'POST'
            item = next(prs.definitions)
            received = {
                key: value
                for key, value in kwargs.get('json', {}).items()
                if key not in {'actual_commit', 'new_commit'}
            }
            assert item.question == received, 'definitions'
            prs.history.append(
                dataclasses.asdict(
                    HistoryItem(f'{BASE_URL}/v1/schemas/definitions/', item),
                ),
            )
            if item.is_failed:
                return patch_requests.response(
                    status_code=400, json=item.answer,
                )
            return patch_requests.response(json=item.answer)

        assert method.upper() == 'POST'
        item = next(prs.schemas)
        received = {
            key: value
            for key, value in kwargs.get('json', {}).items()
            if key not in {'actual_commit', 'new_commit'}
        }
        assert item.question == received, 'schemas'
        prs.history.append(
            dataclasses.asdict(HistoryItem(f'{BASE_URL}/v1/schemas/', item)),
        )
        if item.is_failed:
            return patch_requests.response(status_code=400, json=item.answer)
        return patch_requests.response(json=item.answer)

    return prs
