# -*- coding: utf-8 -*-
# isort:skip_file
import os

from passport.backend.utils.warnings import enable_strict_bytes_mode

os.environ['DJANGO_SETTINGS_MODULE'] = 'passport.backend.perimeter_api.tests.base.settings_test'

import django
django.setup()
enable_strict_bytes_mode()
