from testsuite.utils import matching


class UuidDashedString(matching.RegexString):
    """Matches canonical lower-case hexadecimal uuid string."""

    def __init__(self):
        super().__init__(
            '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        )


class OrderCargoRefId(matching.RegexString):
    """
        Matches canonical lower-case hexadecimal uuid string
        with order/ prefix.
    """

    def __init__(self):
        super().__init__(
            '^order/'
            '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        )
