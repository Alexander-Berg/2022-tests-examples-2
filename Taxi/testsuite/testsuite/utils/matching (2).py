# pylint: disable=invalid-name
import re


class AnyString:
    """Matches any string."""

    def __repr__(self):
        return '<AnyString>'

    def __eq__(self, other):
        return isinstance(other, str)


class RegexString(AnyString):
    def __init__(self, pattern):
        self._pattern = re.compile(pattern)

    def __repr__(self):
        return f'<{self.__class__.__name__} pattern={self._pattern!r}>'

    def __eq__(self, other):
        if not super().__eq__(other):
            return False
        return self._pattern.match(other) is not None


class UuidString(RegexString):
    """Matches lower-case hexadecimal uuid string."""

    def __init__(self):
        super().__init__('^[0-9a-f]{32}$')


class ObjectIdString(RegexString):
    """Matches lower-case hexadecimal objectid string."""

    def __init__(self):
        super().__init__('^[0-9a-f]{24}$')


any_string = AnyString()
uuid_string = UuidString()
objectid_string = ObjectIdString()
