import datetime
import decimal

import dateutil.parser
import pytz


def normalize_timestring(timestring):
    timestamp = dateutil.parser.parse(timestring)
    return to_timestring(timestamp)


def to_timestamp(timestamp_or_timestring):
    if isinstance(timestamp_or_timestring, datetime.datetime):
        return timestamp_or_timestring
    timestring = timestamp_or_timestring
    stamp = dateutil.parser.parse(timestring).astimezone(pytz.utc)
    return stamp.replace(tzinfo=None)


def to_timestring(timestamp_or_timestring):
    if not isinstance(timestamp_or_timestring, datetime.datetime):
        return timestamp_or_timestring
    timestamp = timestamp_or_timestring
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=pytz.utc)
    return timestamp.astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S%z')


def normalize_money(value):
    return '%.4f' % decimal.Decimal(value)


def account_to_tuple(account):
    return (
        account.get('entity') or account['entity_external_id'],
        account.get('agreement') or account['agreement_id'],
        account['currency'],
        account['sub_account'],
    )
