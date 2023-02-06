# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)

from formencode.validators import (
    Int,
    Invalid,
)


class DeleteAfter(Int):
    MINUTE_IN_SECONDS = 60
    MONTH_IN_SECONDS = 2592000

    def _to_python(self, value, state):
        delete_after = super(DeleteAfter, self)._to_python(value, state)

        if delete_after in [-1, 0]:
            return None

        if not self.MINUTE_IN_SECONDS < delete_after < self.MONTH_IN_SECONDS:
            raise Invalid(
                'should be between 60 and 2592000 or one of [-1, 0], if account does not need to be deleted',
                value, state
            )
        return datetime.now() + timedelta(seconds=delete_after)
