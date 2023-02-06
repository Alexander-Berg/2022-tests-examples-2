from collections import defaultdict
import functools
from urllib import parse

import pytest

from scripts.lib.vcs_utils import github_utils


@pytest.mark.parametrize(
    'url, error_cls, script_features',
    [
        pytest.param(
            'https://github.yandex-team.ru/taxi/tools-py3/blob/'
            '1acc419d4d6a9ce985db7be48c6349a0475975b5/check.py?at=master',
            None,
            defaultdict(lambda: True, {'check_py3_service_name': False}),
            id='disable github check_py3_service_name',
        ),
        pytest.param(
            'https://github.yandex-team.ru/taxi/tools-py3/blob/'
            '1acc419d4d6a9ce985db7be48c6349a0475975b5/check.py?at=master',
            github_utils.common.UrlParseError,
            defaultdict(lambda: True),
            id='enable github check_py3_service_name',
        ),
    ],
)
async def test_check_parsed_url(
        patch, github_client, url, error_cls, script_features,
):
    @patch('taxi.clients.github.GithubClient.get_branch')
    async def _get_branch(*args, **kwargs):
        raise (error_cls or Exception)

    call = functools.partial(
        github_utils.check_parsed_url,
        parsed=parse.urlparse(url),
        github_client=github_client,
        allowed_from_base=False,
        allowed_bases=['master'],
        script_features=script_features,
        allowed_custom_branch=False,
    )
    if error_cls:
        with pytest.raises(error_cls):
            await call()
    else:
        await call()
