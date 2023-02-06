# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from taxi import config
from taxiadmin.api import apiutils


@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize(
    'applications, all_applications_config, is_error', (
        (['iphone', 'android'], ['iphone', 'android'], False),
        (['yango_iphone'], ['iphone'], True),
        (['yango_iphone'], ['iphone', 'yango_iphone'], False),
    ),
)
def test_applications_validator(
        applications, all_applications_config, is_error,
):
    config.ALL_APPLICATIONS.save(all_applications_config)

    @apiutils.applications_validator(applications_field='apps')
    def handler(request, data, *args, **kwargs):
        pass

    result = handler(None, {'apps': applications})
    assert bool(result) == is_error
