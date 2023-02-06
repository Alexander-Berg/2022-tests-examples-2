# -*- coding: utf-8 -*-

from formencode.validators import (
    FancyValidator,
    Invalid,
)


class TestPhone(FancyValidator):
    """Проверка телефона на наличие тестового префикса"""

    @staticmethod
    def _to_python(value, state):
        phone = value
        if not phone.startswith('+7000'):
            raise Invalid("Should start with '+7000'. TUS allows to bind only fake phone numbers", value, state)
        return phone
