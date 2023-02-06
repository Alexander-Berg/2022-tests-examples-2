import os

import metrika.admin.python.zooface.frontend.tests.helper as helper


def pytest_configure():
    helper.load_zk_data()

    os.environ['APP_DIR'] = os.path.join(
        os.path.dirname(__file__),
        '..',
    )
    os.environ['DJANGO_SETTINGS_MODULE'] = 'metrika.admin.python.zooface.frontend.base.settings'

    import django
    django.is_in_test = True
    django.setup()


def pytest_unconfigure():
    import django
    del django.is_in_test
