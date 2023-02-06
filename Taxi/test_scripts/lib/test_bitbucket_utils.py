from collections import defaultdict
import functools
from urllib import parse

import pytest

from scripts.lib.vcs_utils import bitbucket_utils


@pytest.mark.parametrize(
    'url, error_cls, allowed_master, script_features',
    [
        ('', bitbucket_utils.BaseError, False, defaultdict(lambda: True)),
        (
            'https://bb.yandex-team.ru/projects/EDA/repos/'
            'infrastructure_admin_scripts/raw/eda_scripts/'
            'test.py?at=cce6f0627dc4925c910a47997f160e27b5256e0e',
            None,
            False,
            defaultdict(lambda: True),
        ),
        (
            'https://bb.yandex-team.ru/projects/EDA/repos/'
            'infrastructure_admin_scripts/browse/eda_scripts/'
            'test.py?at=cce6f0627dc4925c910a47997f160e27b5256e0e',
            None,
            False,
            defaultdict(lambda: True),
        ),
        (
            'https://bb.yandex-team.ru/projects/SOME/repos/'
            'infrastructure_admin_scripts/browse/eda_scripts/'
            'test.py?at=cce6f0627dc4925c910a47997f160e27b5256e0e',
            None,  # cause project checks at upper level
            False,
            defaultdict(lambda: True),
        ),
        (
            'https://bb.yandex-team.ru/projects/EDA/repos/'
            'some_repo/browse/eda_scripts/'
            'test.py?at=cce6f0627dc4925c910a47997f160e27b5256e0e',
            None,  # cause repo checks at upper level
            False,
            defaultdict(lambda: True),
        ),
        (
            'https://bb.yandex-team.ru/projects/EDA/repos/'
            'infrastructure_admin_scripts/browse/eda_scripts/'
            'test.py?at=master',
            None,
            True,
            defaultdict(lambda: True),
        ),
        (
            'https://bb.yandex-team.ru/projects/EDA/repos/'
            'infrastructure_admin_scripts/browse/eda_scripts/'
            'test.py?at=master',
            bitbucket_utils.common.UrlParseError,
            False,
            defaultdict(lambda: True),
        ),
        (
            'https://bb.yandex-team.ru/projects/EDA/repos/'
            'infrastructure_admin_scripts/browse/eda_scripts/'
            'test.py?at=develop',
            bitbucket_utils.common.UrlParseError,
            False,
            defaultdict(lambda: True),
        ),
        pytest.param(
            'https://bb.yandex-team.ru/projects/EDA/repos/'
            'infrastructure_admin_scripts/browse/check.py?at=master',
            None,
            True,
            defaultdict(lambda: True, {'check_bitbucket_rootdir': False}),
            id='disable bitbucket check_bitbucket_rootdir',
        ),
        pytest.param(
            'https://bb.yandex-team.ru/projects/EDA/repos/'
            'infrastructure_admin_scripts/browse/check.py?at=master',
            bitbucket_utils.BadScriptPath,
            True,
            defaultdict(lambda: True),
            id='enable bitbucket check_bitbucket_rootdir',
        ),
    ],
)
async def test_check_parsed_url(
        bitbucket_client, url, error_cls, allowed_master, script_features,
):
    call = functools.partial(
        bitbucket_utils.check_parsed_url,
        parsed=parse.urlparse(url),
        bitbucket_client=bitbucket_client,
        allowed_from_base=allowed_master,
        allowed_base='master',
        script_features=script_features,
        allowed_custom_branch=False,
    )
    if error_cls:
        with pytest.raises(error_cls):
            await call()
    else:
        await call()
