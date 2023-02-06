import pytest

DEFAULT_ZONE_NAME = 'bishkek'
GEOPOINTS = {
    DEFAULT_ZONE_NAME: [74.6, 42.866667],
    'moscow': [37.1946401739712, 55.478983901730004],
}


CURFEW_TEXT = (
    'Комендантский час: с 21:00 до 07:00 нельзя выходить из дома '
    'и ездить на такси.'
)
CURFEW_SHORT_TEXT = 'Поехать сейчас не получится: комендантский час'


# NOTE: there must be categories in db_tariffs.json with `dt` = 2 (or two
#  categories  with `dt` = 0 and 1) to support both workdays and weekend.
#  Otherwise, there would be `tariff has no categories` error in routestats
WEDNESDAY = '19'
THURSDAY = '20'
FRIDAY = '21'
SATURDAY = '22'
SUNDAY = '23'


def time(daytime, day=SATURDAY, tz='+06'):
    return f'2020-02-{day}T{daytime}:00{tz}00'


def now(daytime, **kwargs):
    return pytest.mark.now(time(daytime, **kwargs))


def make_rule(
        countries=None, zones=None, tariffs=None, intervals=None, enabled=True,
):
    rule = {
        'message_key': 'order_block.message.country.kgz',
        'enabled': enabled,
        'intervals': [{'from': '21:00', 'to': '07:00'}],
    }
    if countries:
        rule['countries'] = countries
    if zones:
        rule['zones'] = zones
    if tariffs:
        rule['tariffs'] = tariffs
    if intervals:
        rule['intervals'] = intervals
    return rule
