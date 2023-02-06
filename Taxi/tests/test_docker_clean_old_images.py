import dataclasses
from typing import Dict
from typing import List
from typing import Optional

import docker_clean_old_images
from tests.utils import pytest_wraps


@dataclasses.dataclass
class Params(pytest_wraps.Params):
    repositories: List[str]
    tags: Dict[str, List[str]] = dataclasses.field(default_factory=dict)
    num_deleted_tags: Optional[int] = None


LIMIT = docker_clean_old_images.LIMIT
PARAMS = [
    Params(pytest_id='no_repositories', repositories=[]),
    Params(
        pytest_id='delete_one_repo',
        repositories=['taxi/abt/testing', 'urllib/taxi/lefi'],
        tags={'taxi/abt/testing': [f'0.1.{i}' for i in range(LIMIT + 5)]},
    ),
    Params(
        pytest_id='check_regular_expressions',
        repositories=[
            'taxi/abt/testing',
            'taxi/abt-1/unstable',
            'taxi/taxi-integration/xenial/abt_none',
            'taxi/taxi-integration/bionic/b',
            'taxi/taxi-integration-xenial-env',
            'taxi/taxi-integration-bionic-env',
            'taxi/not valid/testing',
            'taxi/abt-1/production',
            'urllib/taxi/lefi',
        ],
        tags={
            'taxi/abt/testing': [f'0.1.{i}' for i in range(LIMIT + 1)],
            'taxi/abt-1/unstable': [f'0.1.{i}' for i in range(LIMIT + 2)],
            'taxi/taxi-integration/xenial/abt_none': [
                f'0.1.{i}' for i in range(LIMIT + 3)
            ],
            'taxi/taxi-integration/bionic/b': [
                f'0.{i}' for i in range(LIMIT + 4)
            ],
            'taxi/taxi-integration-xenial-env': [
                f'0.{i}' for i in range(LIMIT + 5)
            ],
            'taxi/taxi-integration-bionic-env': [
                f'0.{i}' for i in range(LIMIT + 6)
            ],
        },
    ),
    Params(
        pytest_id='delete_tags_only_from_different_groups',
        repositories=['taxi/abt/testing'],
        tags={
            'taxi/abt/testing': (
                [f'0.1.{i}' for i in range(LIMIT + 1)]
                + [f'r0.1.{i}' for i in range(LIMIT + 2)]
                + [f'0.1.1testing{i}' for i in range(LIMIT)]
                + [f'0.1.1unstable{i}' for i in range(LIMIT - 10)]
            ),
        },
        num_deleted_tags=3,
    ),
]


@pytest_wraps.parametrize(PARAMS)
def test_docker_clean_old_images(params: Params, monkeypatch, patch_requests):
    monkeypatch.setenv('YANDEX_TOKEN', 'yandex-token')
    monkeypatch.setattr(
        docker_clean_old_images, 'get_manifest', lambda x, y: '1',
    )
    api_url = docker_clean_old_images.API_URL

    @patch_requests(f'{docker_clean_old_images.API_URL}/_catalog')
    def get_repositories(method, url, **kwargs):
        return patch_requests.response(
            status_code=200, json={'repositories': params.repositories},
        )

    @patch_requests(docker_clean_old_images.API_URL)
    def get_tags(method, url, **kwargs):
        if url.endswith('sha256:1'):
            return patch_requests.response(status_code=200, json={})
        service = url[len(f'{api_url}/') :][: -len('/tags/list')]
        return patch_requests.response(
            status_code=200, json={'tags': params.tags[service]},
        )

    docker_clean_old_images.main(['--limit', '300'])
    assert len(get_repositories.calls) == 1
    num_delete_calls = num_get_tags_calls = 0
    for call in get_tags.calls:
        if call['url'].endswith('/tags/list'):
            num_get_tags_calls += 1
        else:
            num_delete_calls += 1
    assert num_get_tags_calls == len(params.tags)

    num_calls_manifest = 0
    for tags in params.tags.values():
        num_calls_manifest += max(len(tags) - LIMIT, 0)

    assert num_delete_calls == (params.num_deleted_tags or num_calls_manifest)
