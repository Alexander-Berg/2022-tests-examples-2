import os

import metrika.admin.python.bishop.config_api.config_api.defaults as defaults


def pytest_configure():
    defaults.set_environment_variables_defaults()

    os.environ['APP_DIR'] = os.path.join(
        os.path.dirname(__file__),
        '..',
    )
    os.environ['DJANGO_SETTINGS_MODULE'] = 'metrika.admin.python.bishop.config_api.base.settings'

    import django
    django.is_in_test = True
    django.setup()


def pytest_unconfigure():
    import django
    del django.is_in_test
