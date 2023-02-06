# -*- coding: utf-8 -*-
import re

from formencode.validators import (
    FancyValidator,
    Invalid,
)
from passport.backend.qa.test_user_service.tus_api.fillers import normalize_login


class BaseLoginValidator(FancyValidator):
    """Проверка, что логин выглядит как логин. Возвращаем нормализованный логин"""

    @staticmethod
    def _to_python(value, state):
        normalized_login = normalize_login(value)
        is_valid = re.match('^[a-z][a-z0-9-@.]{3,60}$', normalized_login)
        if is_valid:
            return normalized_login
        else:
            raise Invalid('Should start with a letter, '
                          'contain Latin characters, numbers, ".", "-", "@" (only for external environment) '
                          'and have length from 3 to 60 characters', value, state)
