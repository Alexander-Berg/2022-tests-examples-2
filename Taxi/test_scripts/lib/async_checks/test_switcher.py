import pytest

from scripts.lib import db_utils
from scripts.lib.async_checks import switcher
from test_scripts import helpers


def mk_script(**updates):
    return db_utils.Script(None, helpers.get_script_doc(updates))


@pytest.mark.parametrize(
    'script, result',
    [
        pytest.param(
            mk_script(),
            False,
            marks=[pytest.mark.config(SCRIPTS_ASYNC_CHECKS_SWITCHER=[])],
            id='emptry config',
        ),
        pytest.param(
            mk_script(),
            False,
            marks=[
                pytest.mark.config(
                    SCRIPTS_ASYNC_CHECKS_SWITCHER=[
                        {
                            'service': '__ANY__',
                            'execute_type': '__ANY__',
                            'value': False,
                        },
                    ],
                ),
            ],
            id='config with negative any filter',
        ),
        pytest.param(
            mk_script(),
            True,
            marks=[
                pytest.mark.config(
                    SCRIPTS_ASYNC_CHECKS_SWITCHER=[
                        {
                            'service': '__ANY__',
                            'execute_type': '__ANY__',
                            'value': True,
                        },
                    ],
                ),
            ],
            id='config with positive any filter',
        ),
        pytest.param(
            mk_script(project='taxi_scripts', execute_type='pgmigrate'),
            True,
            marks=[
                pytest.mark.config(
                    SCRIPTS_ASYNC_CHECKS_SWITCHER=[
                        {
                            'service': 'taxi_scripts',
                            'execute_type': 'pgmigrate',
                            'value': True,
                        },
                        {
                            'service': '__ANY__',
                            'execute_type': '__ANY__',
                            'value': False,
                        },
                    ],
                ),
            ],
            id='config fully matching script',
        ),
        pytest.param(
            mk_script(project='taxi_scripts', execute_type='pgmigrate'),
            True,
            marks=[
                pytest.mark.config(
                    SCRIPTS_ASYNC_CHECKS_SWITCHER=[
                        {
                            'service': 'taxi_scripts',
                            'execute_type': '__ANY__',
                            'value': True,
                        },
                        {
                            'service': '__ANY__',
                            'execute_type': '__ANY__',
                            'value': False,
                        },
                    ],
                ),
            ],
            id='config partially matching script',
        ),
        pytest.param(
            mk_script(
                project='eda_eats-logistics-performer-payouts',
                execute_type='pgmigrate',
            ),
            False,
            marks=[
                pytest.mark.config(
                    SCRIPTS_ASYNC_CHECKS_SWITCHER=[
                        {
                            'execute_type': '__ANY__',
                            'service': 'taxi_api_admin',
                            'value': True,
                        },
                        {
                            'execute_type': '__ANY__',
                            'service': '__ANY__',
                            'value': False,
                        },
                    ],
                ),
            ],
            id='expects false by config',
        ),
    ],
)
async def test_switcher(scripts_app, script, result):
    await scripts_app.config.init_cache()
    assert switcher.use_async_check(scripts_app.config, script) is result
