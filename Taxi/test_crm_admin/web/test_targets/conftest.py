# pylint: disable=unused-variable

import pytest

from test_crm_admin.web.test_targets import utils


@pytest.fixture(autouse=True)
def fixed_salt(patch):
    @patch('crm_admin.entity.base.create_salt')
    def generate(*agrs, **kwargs):
        return utils.EVERY_SALT
