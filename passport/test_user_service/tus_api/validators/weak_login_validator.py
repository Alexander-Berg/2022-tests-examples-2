# -*- coding: utf-8 -*-

from passport.backend.qa.test_user_service.tus_api.validators.base_login_validator import BaseLoginValidator


class WeakLoginValidator(BaseLoginValidator):
    """Проверка, что логин выглядит как логин"""

    @staticmethod
    def _to_python(value, state):
        # Валидируем логин в базовом валидаторе
        BaseLoginValidator._to_python(value, state)
        # Возвращаем логин пришедший в запросе (ненормализованный), если логин прошёл валидацию
        return value
