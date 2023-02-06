# -*- coding: utf-8 -*-

from formencode.validators import Int


class WeakUidValidator(Int):
    """Проверка что uid выглядит как uid"""
    strip = True
    not_empty = True
    min = 0
    max = 2 ** 63 - 2  # Все что больше ЧЯ не считает валидным UID-ом
