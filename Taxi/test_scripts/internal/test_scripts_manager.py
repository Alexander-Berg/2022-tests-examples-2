# pylint: disable=protected-access,unused-variable
from collections import defaultdict

import pytest

from taxi import settings

from scripts.internal import scripts_manager


URL_PREFIX = 'https://github.yandex-team.ru'


@pytest.mark.parametrize(
    'env,should_check',
    [
        (settings.PRODUCTION, True),
        (settings.TESTING, False),
        (settings.UNSTABLE, False),
    ],
)
@pytest.mark.parametrize(
    'url,from_master,is_head',
    [
        (
            f'{URL_PREFIX}/taxi/tools/blob/'
            f'1acc419d4d6a9ce985db7be48c6349a0475975b5/script.py',
            False,
            False,
        ),
        (
            f'{URL_PREFIX}/taxi/tools/blob/'
            f'1acc419d4d6a9ce985db7be48c6349a0475975b5/script.py',
            True,
            False,
        ),
        (
            f'{URL_PREFIX}/taxi/tools/blob/'
            f'1acc419d4d6a9ce985db7be48c6349a0475975b5/script.py',
            True,
            True,
        ),
    ],
)
async def test_branch_checker(
        monkeypatch,
        patch,
        scripts_app,
        env,
        should_check,
        url,
        from_master,
        is_head,
):
    monkeypatch.setattr(settings, 'ENVIRONMENT', env)

    @patch('taxi.clients.github.GithubClient.compare_commits')
    async def commit_in_branch_mock(*args, **kwargs):
        if not from_master:
            return {'status': 'diverged'}
        if is_head:
            return {'status': 'identical'}
        return {'status': 'behind'}

    checker = scripts_manager.check_script(
        url,
        False,
        allowed_master=False,
        script_features=defaultdict(
            lambda: True,
            {'merge_check_enabled': True, 'convert_gh_to_bb': False},
        ),
        app=scripts_app,
        bitbucket_client=scripts_app.bitbucket,
        github_client=scripts_app.github,
        taximeter_client=scripts_app.taximeter,
    )
    if not should_check:
        await checker
        assert not commit_in_branch_mock.calls
    else:
        if not from_master:
            with pytest.raises(scripts_manager.CheckScriptError) as exc_info:
                await checker
            assert exc_info.value.code == 'commit_not_from_master'
        else:
            await checker
        assert len(commit_in_branch_mock.calls) == 1


@pytest.mark.parametrize(
    'url,error_cls',
    [
        (
            f'{URL_PREFIX}/taxi/tools/blob/'
            f'1acc419d4d6a9ce985db7be48c6349a0475975b5/script.py',
            None,
        ),
        (
            f'{URL_PREFIX}/taxi/tools/blob/'
            f'1acc419d4d6a9ce985db7be48c6349a0475975b5/../../script.py',
            scripts_manager.CheckScriptError,
        ),
    ],
)
async def test_url_with_parent_dirs(scripts_app, url, error_cls):
    coro = scripts_manager.check_script(
        url,
        False,
        allowed_master=False,
        script_features=defaultdict(lambda: True),
        app=scripts_app,
        bitbucket_client=scripts_app.bitbucket,
        github_client=scripts_app.github,
        taximeter_client=scripts_app.taximeter,
    )
    if error_cls is None:
        await coro
    else:
        with pytest.raises(error_cls):
            await coro
