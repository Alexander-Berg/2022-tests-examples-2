import time
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Tuple
from typing import Union

import pytest

import docker_cleanup


class Params(NamedTuple):
    docker_calls: List[Tuple[str, Union[str, int]]]
    white_list: Optional[str] = None


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                docker_calls=[
                    ('docker ps -q', 0),
                    ('docker system prune --volumes --force', 0),
                    ('docker images', 0),
                ],
            ),
            id='no containers',
        ),
        pytest.param(
            Params(
                docker_calls=[
                    ('docker ps -q', '111'),
                    ('docker kill 111', 0),
                    ('docker ps -q', 0),
                    ('docker system prune --volumes --force', 0),
                    ('docker images', 0),
                ],
            ),
            id='one container',
        ),
        pytest.param(
            Params(
                docker_calls=[
                    ('docker ps -q', '111 222'),
                    ('docker kill 111 222', 0),
                    ('docker ps -q', 0),
                    ('docker system prune --volumes --force', 0),
                    ('docker images', 0),
                ],
            ),
            id='two containers',
        ),
        pytest.param(
            Params(
                docker_calls=[
                    ('docker ps -q', '111 222'),
                    ('docker kill 111 222', 0),
                    ('docker ps -q', '111'),
                    ('docker kill 111', 0),
                    ('docker ps -q', '111'),
                    ('docker kill 111', 0),
                    ('docker ps -q', '111'),
                    ('docker kill 111', 0),
                    ('docker ps -q', 0),
                    ('docker system prune --volumes --force', 0),
                    ('docker images', 0),
                ],
            ),
            id='long kill',
        ),
        pytest.param(
            Params(
                docker_calls=[
                    ('docker ps -q', '111 222'),
                    ('docker kill 111 222', 0),
                    ('docker ps -q', '111'),
                    ('docker kill 111', 0),
                    ('docker ps -q', '111'),
                    ('docker kill 111', 0),
                    ('docker ps -q', '111'),
                    ('docker kill 111', 0),
                    ('docker ps -q', '111'),
                    ('docker kill 111', 0),
                    ('docker ps -q', '111'),
                    ('docker kill 111', 0),
                    ('docker ps -q', '111'),
                    ('docker kill 111', 0),
                    ('docker ps -q', '111'),
                    ('docker kill 111', 0),
                    ('docker ps -q', '111'),
                    ('docker kill 111', 0),
                    ('docker ps -q', '111'),
                    ('docker kill 111', 0),
                    ('sudo service docker restart', 0),
                    ('docker ps -q', '111'),
                    ('docker kill 111', 0),
                    ('docker system prune --volumes --force', 0),
                    ('docker images', 0),
                ],
            ),
            id='broken docker',
        ),
        pytest.param(
            Params(
                docker_calls=[
                    ('docker ps -q', '111 222'),
                    ('docker kill 111 222', 1),
                    ('docker ps -q', '111'),
                    ('docker kill 111', 1),
                    ('docker ps -q', '111'),
                    ('docker kill 111', 1),
                    ('docker ps -q', '111'),
                    ('docker kill 111', 1),
                    ('docker ps -q', '111'),
                    ('docker kill 111', 1),
                    ('docker ps -q', '111'),
                    ('docker kill 111', 1),
                    ('docker ps -q', '111'),
                    ('docker kill 111', 1),
                    ('docker ps -q', '111'),
                    ('docker kill 111', 1),
                    ('docker ps -q', '111'),
                    ('docker kill 111', 1),
                    ('docker ps -q', '111'),
                    ('docker kill 111', 1),
                    ('sudo service docker restart', 0),
                    ('docker ps -q', '111'),
                    ('docker kill 111', 0),
                    ('docker system prune --volumes --force', 0),
                    ('docker images', 0),
                ],
            ),
            id='broken docker exceptions',
        ),
        pytest.param(
            Params(
                docker_calls=[
                    ('docker ps -q', ' '.join(map(str, range(55)))),
                    ('docker kill ' + ' '.join(map(str, range(10))), 0),
                    ('docker kill ' + ' '.join(map(str, range(10, 20))), 0),
                    ('docker kill ' + ' '.join(map(str, range(20, 30))), 0),
                    ('docker kill ' + ' '.join(map(str, range(30, 40))), 0),
                    ('docker kill ' + ' '.join(map(str, range(40, 50))), 0),
                    ('docker kill ' + ' '.join(map(str, range(50, 55))), 0),
                    ('docker ps -q', 0),
                    ('docker system prune --volumes --force', 0),
                    ('docker images', 0),
                ],
            ),
            id='chunk',
        ),
        pytest.param(
            Params(
                docker_calls=[
                    ('docker ps -q', 0),
                    ('docker system prune --volumes --force', 0),
                    (
                        'docker images',
                        'REPO TAG IMG some\n'
                        'registry.yandex.net/a   latest aaa bbb\n'
                        'registry.yandex.net/b 123 x y z',
                    ),
                    ('docker rmi registry.yandex.net/b:123', 0),
                ],
            ),
            id='registry images',
        ),
        pytest.param(
            Params(
                docker_calls=[
                    ('docker ps -q', 0),
                    ('docker system prune --volumes --force', 0),
                    (
                        'docker images',
                        'REPO TAG IMG some\n'
                        'my   latest aaa bbb\n'
                        'other 123 x y z\n'
                        'none <none> d d d',
                    ),
                    ('docker rmi my:latest none:latest other:123', 0),
                ],
            ),
            id='other images',
        ),
        pytest.param(
            Params(
                docker_calls=[
                    ('docker ps -q', 0),
                    ('docker system prune --volumes --force', 0),
                    (
                        'docker images',
                        'REPO TAG IMG some\n'
                        'my   latest    aaa      bbb\n'
                        '<none> <none> a b c\n'
                        '<none> latest a b c\n'
                        'latest <none> a b c\n'
                        'registry.yandex.net/a   latest aaa bbb\n'
                        'registry.yandex.net/b 123 x y z\n'
                        'other 123 x y z',
                    ),
                    (
                        'docker rmi latest:latest my:latest other:123 '
                        'registry.yandex.net/b:123',
                        0,
                    ),
                ],
            ),
            id='mixed images',
        ),
        pytest.param(
            Params(
                docker_calls=[
                    ('docker ps -q', 0),
                    ('docker system prune --volumes --force', 0),
                    (
                        'docker images',
                        'REPO TAG IMG some\n'
                        'registry.yandex.net/a   latest aaa bbb\n'
                        'registry.yandex.net/b   <none> x y z',
                    ),
                ],
            ),
            id='registry none images',
        ),
        pytest.param(
            Params(
                docker_calls=[
                    ('docker ps -q', 0),
                    ('docker system prune --volumes --force', 0),
                    (
                        'docker images',
                        'REPO TAG IMG some\n'
                        'registry.yandex.net/a  latest 123 bbb\n'
                        'registry.yandex.net/b  <none> 324 y z\n'
                        'registry.yandex.net/b  latest 222 y z\n'
                        'registry.yandex.net/b  <none> 111 y z\n'
                        'registry.yandex.net/a  123 abc y z\n'
                        'registry.yandex.net/c  latest 453 y z',
                    ),
                    (
                        'docker rmi registry.yandex.net/a:123 '
                        'registry.yandex.net/c:latest',
                        0,
                    ),
                ],
                white_list=(
                    'registry.yandex.net/a:latest\n'
                    'registry.yandex.net/b:latest'
                ),
            ),
            id='remove_all_images_except_whitelist',
        ),
        pytest.param(
            Params(
                docker_calls=[
                    ('docker ps -q', 0),
                    ('docker system prune --volumes --force', 0),
                    (
                        'docker images',
                        'REPO TAG IMG some\n'
                        'registry.yandex.net/a  latest 123 bbb\n'
                        'registry.yandex.net/b  <none> 324 y z\n'
                        'registry.yandex.net/b  latest 222 y z',
                    ),
                    (
                        'docker rmi registry.yandex.net/a:latest '
                        'registry.yandex.net/b:latest',
                        0,
                    ),
                ],
                white_list='_empty',
            ),
            id='remove_all_images_if_whitelist_is_empty',
        ),
        pytest.param(
            Params(
                docker_calls=[
                    ('docker ps -q', 0),
                    ('docker system prune --volumes --force', 0),
                    (
                        'docker images',
                        'REPO TAG IMG some\n'
                        'this_is_not_empty  latest 123 bbb',
                    ),
                    ('docker rmi this_is_not_empty:latest', 2),
                ],
                white_list='_empty',
            ),
            id='failed_remove_images',
        ),
    ],
)
def test_docker_cleanup(params: Params, commands_mock, monkeypatch) -> None:
    monkeypatch.setattr(time, 'sleep', lambda x: None)
    docker_results = (call[1] for call in params.docker_calls)
    if params.white_list:
        monkeypatch.setenv(
            'DOCKER_CLEANUP_PROTECTED_IMAGES', params.white_list,
        )

    @commands_mock('docker')
    @commands_mock('sudo')
    def docker(args, **kwargs):
        return next(docker_results)

    docker_cleanup.main()

    assert [call['args'] for call in docker.calls] == [
        call[0].split() for call in params.docker_calls
    ]
