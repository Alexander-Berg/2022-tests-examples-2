import datetime
import decimal

import dateutil


def ensure_decimal(value):
    if value is not None and not isinstance(value, decimal.Decimal):
        value = decimal.Decimal(str(value))
    return value


def ensure_date(value):
    if value is not None and not isinstance(value, datetime.datetime):
        value = dateutil.parser.parse(str(value))
    return value


class Decimal:
    def __init__(self, value):
        self.value = ensure_decimal(value)

    def __repr__(self):
        return f'xcmp.Decimal(\'{str(self.value)}\')'

    def __eq__(self, value):
        return self.value == ensure_decimal(value)

    def __ne__(self, value):
        return self.value != ensure_decimal(value)

    def __lt__(self, value):
        return self.value < ensure_decimal(value)

    def __gt__(self, value):
        return self.value > ensure_decimal(value)

    def __le__(self, value):
        return self.value <= ensure_decimal(value)

    def __ge__(self, value):
        return self.value >= ensure_decimal(value)


class Date:
    def __init__(self, value):
        self.value = ensure_date(value)

    def __repr__(self):
        return f'xcmp.Date(\'{self.value.isoformat()}\')'

    def __eq__(self, value):
        return self.value == ensure_date(value)

    def __ne__(self, value):
        return self.value != ensure_date(value)

    def __lt__(self, value):
        return self.value < ensure_date(value)

    def __gt__(self, value):
        return self.value > ensure_date(value)

    def __le__(self, value):
        return self.value <= ensure_date(value)

    def __ge__(self, value):
        return self.value >= ensure_date(value)
