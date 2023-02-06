# -*- coding: utf-8 -*-
from hamcrest import raises
from passport.backend.core.validators import Invalid


def raises_invalid():
    """Матчится, если вызванная функция бросает исключение Invalid

    :return: Оборачивает стандартный матчер ``raises`` ожидающий Invalid, простой шоткат
    """
    return raises(Invalid)
