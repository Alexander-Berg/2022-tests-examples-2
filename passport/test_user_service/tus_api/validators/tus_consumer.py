# -*- coding: utf-8 -*-

import re

from formencode.validators import (
    FancyValidator,
    Invalid,
)


class TusConsumer(FancyValidator):
    """Проверка и форматирование консьюмера"""

    @staticmethod
    def _to_python(value, state):
        tus_consumer = value
        if re.match(r'^[a-z][a-z0-9_\-]{3,20}$', value):  # проверка на соответствие шаблону
            return tus_consumer
        else:
            raise Invalid('Should start with a letter, '
                          'contain lowercase Latin characters, numbers, \'_\', \'-\' and have length '
                          'from 3 to 30 characters', value, state)
