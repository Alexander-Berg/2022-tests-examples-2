from __future__ import annotations

import datetime as dt
import decimal
import hashlib
import pydoc
from typing import Callable
from typing import Dict
from typing import Mapping
from typing import TypeVar
from typing import Union
from unittest import mock

from intervals import intervals
from taxi import billing
from taxi.billing.util import dates

from billing_functions import consts
from billing_functions.functions.core import support_info
from billing_functions.functions.core import types
from billing_functions.functions.core.subventions import netting
from billing_functions.repositories import migration_mode


def _make_money(money_json: Union[dict, str]) -> billing.Money:
    if isinstance(money_json, str):
        amount, currency = money_json.split(' ')
        return billing.Money(decimal.Decimal(amount), currency)
    return billing.Money(**money_json)


def _make_var(var_json: dict) -> support_info.Var:
    assert isinstance(var_json, dict)

    value = var_json['value']
    operations = var_json.get('mutations')
    if operations is None:
        operations = []

    mutations = [_make_operation(operation) for operation in operations]
    return support_info.Var(decimal.Decimal(value), mutations)


def _make_operation(operation_json: dict) -> support_info.Operation:
    assert isinstance(operation_json, dict)
    args = operation_json['args']
    reason = operation_json['reason']

    details = operation_json.get('details')
    if details is None:
        details = {}

    # expected format: "<operation> X = Y"
    operation, arg_value, _, value = args.split(' ')

    return support_info.Operation(
        op=operation,
        args=[decimal.Decimal(arg_value)],
        reason=reason,
        details=details,
        value=decimal.Decimal(value),
    )


Key = TypeVar('Key')
Value = TypeVar('Value')


def _key_mapper(
        mapper: Callable[[str], Key],
) -> Callable[[Dict[str, Value]], Mapping[Key, Value]]:
    def _mapper(json: Dict[str, Value]):
        return {mapper(key): value for key, value in json.items()}

    return _mapper


def _make_netting_config(netting_json: dict) -> netting.Config:
    attrs = {'default': netting.Config.Mode.NONE}
    attrs.update(
        **{k: netting.Config.Mode(v) for k, v in netting_json.items()},
    )
    return netting.Config(**attrs)


HOOKS = {
    '$antifraud_decision': consts.AntifraudDecision,
    '$billing_type': consts.BillingType,
    '$closed_open_interval': lambda json: intervals.closed_open(**json),
    '$commission_group': consts.CommissionGroup,
    '$date': dates.parse_date,
    '$decimal': decimal.Decimal,
    '$driver_mode': consts.DriverMode,
    '$entries_save_version': consts.EntriesSaveVersion,
    '$frozenset': frozenset,
    '$hiring_type': consts.HiringType,
    '$int_key_mapping': _key_mapper(int),
    '$iso_week_day': consts.ISOWeekDay,
    '$migration_mode': migration_mode.Mode,
    '$money': _make_money,
    '$payment_type': consts.PaymentType,
    '$profile_payment_type_rule': consts.ProfilePaymentTypeRule,
    '$int_or_reason': lambda json: types.IntOrReason(**json),
    '$true_or_reason': lambda json: types.TrueOrReason(**json),
    '$load_py_json': ...,  # load object from json by given path
    '$subvention_type': consts.SubventionType,
    '$time': dt.time.fromisoformat,
    '$timedelta': lambda json: dt.timedelta(**json),
    '$type': pydoc.locate,
    '$var': _make_var,
    '$md5': lambda seed: hashlib.md5(seed.encode('utf-8')).hexdigest(),
    '$any': lambda _: mock.ANY,
    '$netting_config': _make_netting_config,
}
