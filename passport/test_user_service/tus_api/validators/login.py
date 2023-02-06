# -*- coding: utf-8 -*-

from formencode.validators import Invalid
from passport.backend.qa.test_user_service.tus_api.validators.base_login_validator import BaseLoginValidator


class TestLogin(BaseLoginValidator):
    """Проверка логина на наличие тестового префикса"""

    @staticmethod
    def _to_python(value, state):
        normalized_login = BaseLoginValidator._to_python(value, state)
        if not normalized_login.startswith('yndx-') and not normalized_login.startswith('yandex-team-') and not normalized_login.startswith('robot-'):
            raise Invalid('Should start with `yandex-team-` or `yndx-` or `robot-`', value, state)
        return value
