# -*- coding: utf-8 -*-
# isort:skip_file
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'passport.backend.oauth.admin.tests.base.settings_test'

import django
django.setup()

from passport.backend.oauth.core.api.startup import configure_settings
configure_settings()
