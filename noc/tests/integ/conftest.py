import os

import pytest

from django.conf import settings


django_db_keepdb = True
django_db_createdb = False


@pytest.fixture(scope='session')
def django_db_setup(django_db_keepdb, django_db_createdb):
    settings.DATABASES['default'].update(NAME="piskunov_test_env_l3mgr")
