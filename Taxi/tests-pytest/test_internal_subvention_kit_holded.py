import datetime
import json

from bson import json_util
import pytest

from taxi.internal import dbh
from taxi.internal.subvention_kit import holded
from taxi.util import dates
from taxi.util import decimal


@pytest.mark.parametrize(
    'zone_name,due,expected_result', [
        (
                'unknown_zone',
                datetime.datetime(2017, 11, 16),
                0,
        ),
        (
                'moscow',
                datetime.datetime(2016, 11, 16),
                0,
        ),
        (
                'moscow',
                datetime.datetime(2017, 11, 16),
                86400,
        ),
    ]
)
@pytest.mark.filldb(
    holded_subventions_config='for_test_get_hold_delay'
)
@pytest.inline_callbacks
def test_get_hold_delay(zone_name, due, expected_result):
    actual_result = yield holded.get_hold_delay(
        zone_name=zone_name,
        due=due,
    )
    assert actual_result == expected_result


@pytest.mark.parametrize('hold_delay,expected_result', [
    (0, False),
    (3, True),
])
@pytest.mark.filldb(_fill=False)
def test_needs_holding_holded_context(hold_delay, expected_result):
    args = len(dbh.holded_subventions.Context._fields) * [None]
    holded_context = dbh.holded_subventions.Context(*args)._replace(
        hold_delay=hold_delay,
    )
    assert holded_context.needs_holding == expected_result


@pytest.mark.filldb(_fill=False)
def test_needs_holding_real_context():
    args = len(dbh.subventions.Context._fields) * [None]
    real_context = dbh.subventions.Context(*args)
    assert not real_context.needs_holding


@pytest.mark.parametrize(
    'holded_subventions_dicts,real_subventions_dicts,expected_result', [
        (
                [{'hold_status': 'holded', 'v': 1}],
                [{}],
                False,
        ),
        (
                [
                    {'hold_status': 'cleared', 'v': 1},
                    {'hold_status': 'undo_holded', 'v': 2,
                     'undo_of_versions': [1]}
                ],
                [{}],
                False,
        ),
        (
                [
                    {'hold_status': 'holded', 'v': 1},
                    {'hold_status': 'undo_holded', 'v': 2,
                     'undo_of_versions': [1]}
                ],
                [{}],
                True,
        )
    ]
)
@pytest.mark.filldb(_fill=False)
def test_full_subvention_has_unfinished_holded_subventions(
        holded_subventions_dicts, real_subventions_dicts, expected_result):
    holded_subventions = map(
        dbh.holded_subventions.Doc, holded_subventions_dicts
    )
    real_subventions = map(
        dbh.subventions.Doc, real_subventions_dicts,
    )
    full_subvention = holded.FullSubvention(
        holded_subventions,
        real_subventions
    )
    assert full_subvention.has_unfinished_holded_subventions is expected_result


_NOW = datetime.datetime(2017, 12, 22, 8, 7, 0)


def _make_value(subvention):
    return dbh.subventions.Value(
        subvention=decimal.Decimal(subvention),
        cc_subvention=decimal.Decimal(subvention),
    )


def _make_decline_reasons(*decline_reasons_data):
    doc = dbh.holded_subventions.Doc()
    doc.decline_reasons = []
    for reason, value in decline_reasons_data:
        decline = doc.decline_reasons.new()
        decline.reason = reason
        decline.value = value
    return doc.decline_reasons


def _make_details(*details_data):
    doc = dbh.holded_subventions.Doc()
    doc.details_subvention = []
    for rule_id, value, type_, geoareas in details_data:
        detail = doc.details_subvention.new()
        detail.rule_id = rule_id
        detail.value = value
        detail.type = type_
        detail.geoareas = geoareas
        detail.extra = {}
    return doc.details_subvention


def _make_holded_doc(
        due, discount, pool_subvention, sub_commission, without_commission,
        details):
    doc = dbh.holded_subventions.Doc()
    doc.due = due
    doc.discount_str = discount
    doc.pool_subvention = pool_subvention
    doc.sub_commission_str = sub_commission
    doc.cur_value_without_commission_str = without_commission
    doc.details_subvention = details
    return doc


def _make_real_doc(due, discount, pool_subvention, decline_reasons, details):
    doc = dbh.subventions.Doc()
    doc.due = due
    doc.discount_str = discount
    doc.pool_subvention = pool_subvention
    doc.decline_reasons = decline_reasons
    doc.details_subvention = details
    return doc


def _make_detalization(
        sub_commission, numeric_discount, without_commission, pool_subvention,
        decline_reasons, details_subvention):
    return holded._Detalization(
        sub_commission=decimal.Decimal(sub_commission),
        unrealized_sub_commission='',
        numeric_discount=decimal.Decimal(numeric_discount),
        without_commission=decimal.Decimal(without_commission),
        pool_subvention=decimal.Decimal(pool_subvention),
        decline_reasons=decline_reasons,
        # is a list of dbh objects
        details_subvention=details_subvention,
    )


def _make_bulk_entries(entry_data):
    bulk_entries = []
    for item in entry_data:
        base_context = dbh.subventions.BaseContext(**item['base_context'])
        if item['hold_context']:
            subvention_class = dbh.holded_subventions.Doc
            context = dbh.holded_subventions.Context.from_base_context(
                base_context, **item['hold_context'])
        else:
            subvention_class = dbh.subventions.Doc
            context = dbh.subventions.Context.from_base_context(
                base_context, clear_of_versions=[], clear_of_ids=[],
            )
        entry = subvention_class.make_bulk_entry(
            order_id=item['order_id'],
            alias_id=item['alias_id'],
            value=dbh.subventions.Value(**item['subvention_value']),
            context=context,
        )
        bulk_entries.append(entry)
    return bulk_entries


def _prepare_subvention_data(docs):
    docs.sort(key=lambda sub: sub['v'])
    for doc in docs:
        if '_id' in doc:
            del doc['_id']
        if 'u' in doc:
            del doc['u']
        for field_name, field_value in doc.iteritems():
            if isinstance(field_value, datetime.datetime):
                doc[field_name] = field_value.replace(tzinfo=None)


def _object_hook(dct):
    if '$decimal' in dct:
        return decimal.Decimal(dct['$decimal'])
    elif '$date' in dct:
        return dates.parse_timestring(dct['$date'], 'UTC')
    else:
        return json_util.object_hook(dct)


def _load_json(data):
    return json.loads(data, object_hook=_object_hook)


def _by_rule_id(detail):
    return detail.rule_id
