import os


def pytest_configure():
    os.environ['APP_DIR'] = os.path.join(
        os.path.dirname(__file__),
        '..',
    )
    os.environ['DJANGO_SETTINGS_MODULE'] = 'metrika.admin.python.clickhouse_rbac.frontend.base.settings'

    import django
    django.is_in_test = True
    django.setup()
