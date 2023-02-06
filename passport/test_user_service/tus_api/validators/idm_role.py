# coding=utf-8
import json

from formencode.validators import (
    FancyValidator,
    Invalid,
)


class IdmRoleValidator(FancyValidator):
    """Проверка запроса на наличие необходимых ключей"""

    @staticmethod
    def _to_python(value, state):
        role = json.loads(value)
        if 'tus_consumer' not in role or 'role' not in role:
            raise Invalid('Should be like {"tus_consumer": "some-consumer", "role": "tus-role"}', value, state)
        return role
