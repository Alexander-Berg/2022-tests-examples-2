# -*- coding: utf-8 -*-

import re


def sanitize_project_name(name):
    """
    Набор символов в имени проекта testpalm ограничен символами [a-z, 0-9, -, _]
    @see https://st.yandex-team.ru/FEI-8681

    :param name: имя проекта
    :type name: str|unicode
    :rtype: str|unicode
    """
    return re.sub(r'[^a-z0-9_\-]', '_', name)
