# -*- coding: utf-8 -*-
import re

from formencode.validators import (
    FancyValidator,
    Invalid,
)


class TagsValidator(FancyValidator):
    """Проверка тегов на тег-пригодность"""

    not_empty = True
    if_missing = None
    strip = True

    @staticmethod
    def _to_python(value, state):
        tags = {tag for tag in value.split(',') if tag}
        if len(tags) > 10:
            raise Invalid('Number of tags should not exceed 10', value, state)
        for tag in tags:
            if not re.match(r'^[a-zA-Z][-_a-zA-Z0-9]{2,39}$', tag):
                raise Invalid('Should start with a letter, '
                              'contain Latin characters, numbers, \'_\', \'-\' and have length '
                              'from 3 to 40 characters', value, state)
        return list(tags)
