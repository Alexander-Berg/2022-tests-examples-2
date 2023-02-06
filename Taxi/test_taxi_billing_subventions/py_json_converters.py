# pylint: disable=too-many-lines
import copy
import datetime as dt
import decimal
import typing as tp

import bson
import dateutil.parser
import pytz

from taxi import billing
from taxi.billing.clients.models import (
    billing_commissions as billing_commissions_models,
)

from taxi_billing_subventions import eye
from taxi_billing_subventions.common import containers
from taxi_billing_subventions.common import db
from taxi_billing_subventions.common import intervals
from taxi_billing_subventions.common import models
from taxi_billing_subventions.common import views
from taxi_billing_subventions.common.models.doc import _order_ready_for_billing
from taxi_billing_subventions.personal_uploads import (
    finders as personal_finders,
)
from taxi_billing_subventions.personal_uploads import models as personal_models
from test_taxi_billing_subventions import factories
import test_taxi_billing_subventions.blueprints as blueprints


class _Converter:
    def __init__(self, type_):
        self._type = type_

    def __call__(self, attrs: dict):
        return self._type(**attrs)

    def __repr__(self):
        return f'_Converter({self._type})'


def _make_upload_in_status(status_str: str) -> personal_models.Upload:
    events: tp.List[personal_models.Event] = [
        personal_models.UploadStatusChanged(
            occurred_at=dt.datetime(2018, 1, 1, tzinfo=pytz.utc),
            status=personal_models.UploadStatus(status_str),
            reason=personal_models.UploadStatusChangedReason.CREATED,
            messages=[],
        ),
    ]

    upload_data = personal_models.UploadData(
        id_='some_upload_id',
        initiator=models.Initiator('svovchenko', 'TAXIRATE-666'),
        yt_path='//home/taxi/home/aershov182/some/path',
        events=events,
        version=1,
    )
    return personal_models.Upload(upload_data)


def _make_upload_status(status_str: str) -> personal_models.UploadStatus:
    return personal_models.UploadStatus(status_str)


def _make_status_changed_reason(
        reason_str: str,
) -> personal_models.UploadStatusChangedReason:
    return personal_models.UploadStatusChangedReason(reason_str)


def _make_date(date_string: str) -> dt.date:
    datetime = dt.datetime.strptime(date_string, '%Y-%m-%d')
    return datetime.date()


def _make_tzinfo(tz_name: str) -> dt.tzinfo:
    return pytz.timezone(tz_name)


def _make_money_var(money_str) -> models.Var:
    value = _make_money(money_str)
    return models.Var(value, [])


def _make_money(money_str) -> billing.Money:
    amount_str, currency = money_str.split()
    return billing.Money(decimal.Decimal(amount_str), currency)


def _make_geo_booking_workshift(attrs: dict) -> models.GeoBookingWorkshift:
    return models.GeoBookingWorkshift.from_dict(attrs)


def _make_amendment(attrs: dict) -> models.order.Amendment:
    return models.order.Amendment(value=attrs['value'], reason=attrs['reason'])


def _make_single_step_extra_bonus_calculator(attrs: dict):
    effective_attrs = {
        'num_orders_interval': intervals.at_least(1),
        'bonus_sum': billing.Money(decimal.Decimal('30'), 'RUB'),
        'group_member_id': None,
        'id': bson.ObjectId('123456789012345678901234'),
        'has_commission': False,
        'is_additive': False,
    }
    effective_attrs.update(attrs)
    bonus_calculator = models.ExtraBonusCalculator(  # type: ignore
        bonus_sum=effective_attrs['bonus_sum'],  # type: ignore
        has_commission=effective_attrs['has_commission'],  # type: ignore
        is_additive=effective_attrs['is_additive'],  # type: ignore
    )
    return models.BonusStep(  # type: ignore
        num_orders_interval=(
            effective_attrs['num_orders_interval']  # type: ignore
        ),
        bonus_calculator=bonus_calculator,
        id=effective_attrs['id'],
        group_member_id=effective_attrs['group_member_id'],  # type: ignore
    )


def _make_single_step_guarantee_bonus_calculator(attrs: dict):
    effective_attrs = {
        'num_orders_interval': intervals.at_least(1),
        'guarantee_sum': billing.Money(decimal.Decimal('30'), 'RUB'),
        'id': None,
        'group_member_id': None,
        'has_commission': False,
        'is_additive': True,
    }
    effective_attrs.update(attrs)
    bonus_calculator = models.GuaranteeBonusCalculator(  # type: ignore
        guarantee_sum=effective_attrs['guarantee_sum'],  # type: ignore
        has_commission=effective_attrs['has_commission'],  # type: ignore
        is_additive=effective_attrs['is_additive'],  # type: ignore
    )
    return models.BonusStep(  # type: ignore
        num_orders_interval=(
            effective_attrs['num_orders_interval']  # type: ignore
        ),
        bonus_calculator=bonus_calculator,  # type: ignore
        id=effective_attrs['id'],
        group_member_id=effective_attrs['group_member_id'],  # type: ignore
    )


def _blueprint_make_park(attrs: dict) -> models.Park:
    default_kwargs = {
        'id': 'some_park_id',
        'city_id': 'Москва',
        'automate_marketing_payments': True,
        'pay_donations_without_offer': True,
        'offer_confirmed_at': None,
        'cash_contract_currency': 'RUB',
        'card_contract_currency': 'RUB',
        'offer_contract_currency': 'RUB',
        'general_contracts': [],
        'spendable_contracts': [],
        'vat_history': models.VatHistory.from_list([]),
    }
    default_kwargs.update(attrs)
    return models.Park(**default_kwargs)  # type: ignore


def _make_moscow_zone(attrs: dict) -> models.Zone:
    del attrs  # unused
    return models.Zone(
        name='moscow',
        city_id='Москва',
        tzinfo=pytz.timezone('Europe/Moscow'),
        currency='RUB',
        locale='ru',
        vat=models.Vat.make_naive(12000),
        country='rus',
    )


def _make_list_from_range(range_attrs) -> tp.List:
    return list(range(*range_attrs))


def _make_order_info(attrs: dict) -> models.OrderInfo:
    converted_attrs = attrs.copy()
    converted_attrs['tags'] = frozenset(attrs['tags'])
    default_kwargs = {
        'driver_id': None,
        'db_id': None,
        'has_workshift': None,
        'has_driver_promocode': None,
        'profile_payment_type_restrictions': None,
        'available_tariff_classes': None,
        'order_payment_type': None,
    }
    default_kwargs.update(converted_attrs)
    return models.OrderInfo(**default_kwargs)  # type: ignore


def _make_order_ready_for_billing_doc(attrs):
    default_kwargs = {'order': _make_order({}), 'context': _make_context({})}
    default_kwargs.update(attrs)
    return models.doc.OrderReadyForBilling(**default_kwargs)


def _make_subventions_update_needed_park_data(attrs):
    default_data = {
        'city': {
            'id': 'Москва',
            'tzinfo': 'Europe/Moscow',
            'country_code': 'rus',
            'donate_multiplier': '1.06',
            'donate_discounts_multiplier': '1.00',
        },
        'contract_currency': 'RUB',
        'offer_confirmed_at': '2018-11-22T13:02:41.000000+00:00',
        'contract_currency_rate': '1',
        'offer_contract_currency': 'RUB',
        'automate_marketing_payments': True,
        'pay_donations_without_offer': True,
        'offer_contract_currency_rate': '1',
    }
    default_data.update(attrs)
    return default_data


def _make_subventions_input_data(attrs):
    default_data = {
        'base_doc_id': None,
        'dry_mode': True,
        'due': '2019-04-01T07:46:00.000000+00:00',
        'park': _make_subventions_update_needed_park_data({}),
        'billing_v2_id': None,
        'create_via_py2': False,
        'force_hold': False,
        'currency_data': {
            'for_contract': {'currency': 'RUB', 'rate_from_local': '1'},
            'for_offer_contract': {'currency': 'RUB', 'rate_from_local': '1'},
        },
        'rule_group': 'single_order',
        'tags': ['selfemployed'],
        'uuid': '24deba79c4efecc229acdb1e5017296d',
        'db_id': '7ad36bc7560449998acbe2c57a75c293',
        'value': '91.0 RUB',
        'comment': None,
        'park_id': '100500',
        'order_id': '14c5ae25ffb1148d80fad06ea2f89b10',
        'zone_name': 'narofominsk',
        'has_sticker': False,
        'hold_config': {'delay': 0},
        'has_lightbox': False,
        'rule_details': [
            {
                'extra': {},
                'limit_ref': None,
                'value': '91.0 RUB',
                'rule_id': {'id': '5800ee9321586f10fe17171e', 'group_id': ''},
                'payment_type': 'guarantee',
                'subvention_geoareas': [],
                'rule_type': None,
                'is_once': False,
            },
        ],
        'tariff_class': 'econom',
        'driver_license': '1234962123',
        'order_alias_id': '3ba696b11c891ee88c3150aaacba9d19',
        'sub_commission': '10.7380 RUB',
        'activity_points': 100,
        'has_co_branding': False,
        'discount_details': {'discount': '0 RUB', 'amendments': []},
        'order_payment_type': 'card',
        'subvention_geoareas': [],
        'accepted_by_driver_at': '2019-04-01T07:41:10.619000+00:00',
        'closed_without_accept': False,
        'completed_by_dispatcher': False,
        'unrealized_sub_commission': '0 RUB',
        'order_completed_at': '2019-04-01T07:46:00.000000+00:00',
        'is_cargo': False,
    }
    default_data.update(attrs)
    return default_data


def _make_subventions_update_needed_default_data():
    return {
        'due': '2019-04-01T07:46:00.000000+00:00',
        'rule_group': 'single_order',
        'tags': ['selfemployed'],
        'uuid': '24deba79c4efecc229acdb1e5017296d',
        'db_id': '7ad36bc7560449998acbe2c57a75c293',
        'value': '91.0 RUB',
        'park_id': '100500',
        'order_id': '14c5ae25ffb1148d80fad06ea2f89b10',
        'zone_name': 'narofominsk',
        'has_sticker': False,
        'has_lightbox': False,
        'rule_details': [
            {
                'extra': {},
                'value': '91.0 RUB',
                'rule_id': {'id': '5800ee9321586f10fe17171e', 'group_id': ''},
                'payment_type': 'guarantee',
                'subvention_geoareas': [],
                'is_once': False,
            },
        ],
        'tariff_class': 'econom',
        'order_alias_id': '3ba696b11c891ee88c3150aaacba9d19',
        'sub_commission': '10.7380 RUB',
        'activity_points': 100,
        'subvention_geoareas': [],
        'accepted_by_driver_at': '2019-04-01T07:41:10.619000+00:00',
        'closed_without_accept': False,
        'completed_by_dispatcher': False,
    }


def _make_subventions_update_needed_data(attrs):
    default_data = _make_subventions_update_needed_default_data()
    default_data.update(attrs)
    return default_data


def _make_subventions_update_needed_driver_referral_data(attrs):
    default_data = {
        'dry_mode': False,
        'accepted_by_driver_at': None,
        'activity_points': None,
        'closed_without_accept': None,
        'comment': {
            'invited_driver': 'Иванов Иван Петрович',
            'rule_kind': 'driver_referral',
        },
        'completed_by_dispatcher': None,
        'db_id': '7ad36bc7560449998acbe2c57a75c293',
        'discount_details': {'amendments': [], 'discount': '0 RUB'},
        'driver_license': 'AXH903VV',
        'due': '2019-04-01T07:46:00.000000+00:00',
        'has_co_branding': None,
        'has_lightbox': None,
        'has_sticker': None,
        'hold_config': None,
        'order_alias_id': 'ref/3ba696b11c891ee88c3150aaacba9d19',
        'order_id': 'ref/3ba696b11c891ee88c3150aaacba9d19',
        'order_payment_type': 'cash',
        'park': {
            'automate_marketing_payments': True,
            'city': {
                'country_code': 'rus',
                'donate_discounts_multiplier': '1.00',
                'donate_multiplier': '1.06',
                'id': 'Москва',
                'tzinfo': 'Europe/Moscow',
            },
            'contract_currency': 'RUB',
            'contract_currency_rate': '1',
            'offer_confirmed_at': '2018-11-22T13:02:41.000000+00:00',
            'offer_contract_currency': 'RUB',
            'offer_contract_currency_rate': '1',
            'pay_donations_without_offer': True,
        },
        'park_id': '100500',
        'rule_details': [
            {
                'extra': {},
                'payment_type': 'driver_referral',
                'rule_id': {'group_id': None, 'id': 'driver_referral'},
                'subvention_geoareas': [],
                'value': '6000 RUB',
            },
        ],
        'rule_group': 'driver_referral',
        'sub_commission': '0 RUB',
        'subvention_geoareas': [],
        'tags': [],
        'tariff_class': None,
        'tlog_due': None,
        'unrealized_sub_commission': '0 RUB',
        'uuid': '24deba79c4efecc229acdb1e5017296d',
        'value': '6000 RUB',
        'zone_name': None,
    }
    default_data.update(attrs)
    return _make_subventions_update_needed_data(default_data)


def _make_subventions_update_needed_data_with_currency(attrs):
    default_data = _make_subventions_update_needed_default_data()
    default_data.update(attrs)
    return default_data


def _make_subventions_update_needed_moscow_data(attrs):
    default_data = _make_subventions_update_needed_default_data()
    default_data['due'] = '2019-04-01T10:32:00.000000+00:00'
    default_data['tags'] = []
    default_data['uuid'] = '32cfe834188a4994907288b033a90c54'
    default_data['db_id'] = 'a3608f8f7ee84e0b9c21862beef7e48d'
    default_data['value'] = '133.7 RUB'
    default_data['park_id'] = '643753730232'
    default_data['order_id'] = '226788420ffa2c868c33fc2f249d20dc'
    default_data['zone_name'] = 'moscow'
    default_data['hold_config'] = {'delay': 86400}
    default_data['tariff_class'] = 'vip'
    default_data['driver_license'] = 'OXO000153'
    default_data['order_alias_id'] = 'a732878330b728a5856780cea8515ed0'
    default_data['sub_commission'] = '0 RUB'
    default_data['subvention_geoareas'] = ['msk-iter2-polygon4']
    default_data['accepted_by_driver_at'] = '2019-04-01T10:12:34.387000+00:00'
    default_data['discount_details'] = {
        'discount': '0.0 RUB',
        'amendments': [],
    }
    default_data['rule_details'] = [
        {
            'extra': {},
            'value': '133.7 RUB',
            'rule_id': {'id': '5ca1c023254e5eb96a1d905a', 'group_id': ''},
            'payment_type': 'add',
            'subvention_geoareas': [],
        },
    ]
    default_data.update(attrs)
    return default_data


def _make_geoarea_activity(attrs):
    return models.doc.GeoareaActivity(
        geoareas=frozenset(attrs['geoareas']), interval=attrs['interval'],
    )


def _make_driver_geoarea_activity(attrs):
    default_kwargs = {
        'unique_driver_id': '111111111111111111111111',
        'clid': 'clid',
        'db_id': 'db_id',
        'driver_uuid': 'uuid',
        'geoarea_activities': [],
        'activity_points': 100.0,
        'profile_payment_type_restrictions': None,
        'rule_types': [],
    }
    default_kwargs.update(attrs)
    default_kwargs['tags'] = attrs.get('tags', frozenset())
    default_kwargs['available_tariff_classes'] = attrs.get(
        'available_tariff_classes', frozenset(),
    )
    return models.doc.DriverGeoareaActivity(**default_kwargs)


def _make_antifraud_response(attrs):
    default_kwargs = {
        'antifraud_id': 'some_antifraud_id',
        'billing_id': 'some_billing_id',
        'action': models.doc.AntifraudAction.PAY,
        'till': None,
        'reason': None,
    }
    default_kwargs.update(attrs)
    return models.doc.AntifraudResponse(**default_kwargs)


def _make_antifraud_config(attrs):
    default_kwargs = {'min_travel_time': 90, 'min_travel_distance': 200}
    default_kwargs.update(attrs)
    return _order_ready_for_billing.AntifraudConfig(**default_kwargs)


def _make_driver_promocode_config(attrs):
    default_kwargs = {'enabled': True, 'min_commission': _make_money('1 RUB')}
    default_kwargs.update(attrs)
    return _order_ready_for_billing.DriverPromocodeConfig(**default_kwargs)


def _make_hold_config(attrs):
    default_kwargs = {'delay': 0}
    default_kwargs.update(attrs)
    return models.HoldConfig(**default_kwargs)


def _make_context(attrs):
    default_kwargs = {
        'antifraud_config': _make_antifraud_config({}),
        'driver_promocode_config': _make_driver_promocode_config({}),
        'hold_config': _make_hold_config({}),
        'use_separate_journal_topic': False,
        'based_on_doc_id': None,
        'apply_rebate_to_paid_orders_only': None,
        'order_park_commission_rule': None,
        'park_commission_rule_status': None,
    }
    default_kwargs.update(attrs)
    return _order_ready_for_billing.Context(**default_kwargs)


def _make_order(attrs):
    default_kwargs = {
        'id': 'some_order_id',
        'alias_id': 'some_alias_id',
        'zone_name': 'moscow',
        'subvention_geoareas': [],
        'driver_workshift_ids': [],
        'driver_promocode': None,
        'payment_type': 'cash',
        'closed_without_accept': False,
        'completed_by_dispatcher': False,
        'park_corp_vat': decimal.Decimal('1'),
        'park_brandings': [],
        'source': None,
        'performer': _blueprint_make_performer({}),
        'tariff': models.order.Tariff(
            minimal_cost=_make_money('99 RUB'),
            modified_minimal_cost=_make_money('99 RUB'),
            class_='econom',
        ),
        'due': dt.datetime(2018, 5, 11, 0, 0, 0, tzinfo=pytz.utc),
        'accepted_by_driver_at': dt.datetime(
            2018, 5, 10, 23, 59, 0, tzinfo=pytz.utc,
        ),
        'billing_at': dt.datetime(2018, 5, 10, 23, 59, 0, tzinfo=pytz.utc),
        'cost': _make_money('300 RUB'),
        'cost_details': models.order.CostDetails(
            cost_for_subvention_var=_make_money_var('300 RUB'),
            cost_for_commission_var=_make_money_var('300 RUB'),
            call_center_commission=_make_money('0 RUB'),
            discount_details=models.order.DiscountDetails(
                _make_money('0 RUB'), [],
            ),
            cost_for_driver=None,
        ),
        'discount': models.order.Discount(
            rate=decimal.Decimal(0),
            method='subvention-fix',
            value=_make_money('0 RUB'),
            declines=[],
            limit_id=None,
        ),
        'childseat_rental': None,
        'completed_at': dt.datetime(2018, 5, 11, 0, 23, 45, tzinfo=pytz.utc),
        'is_mqc': False,
        'rebate_rate': decimal.Decimal('0'),
        'status': 'finished',
        'taxi_status': 'complete',
        'travel_time': 1425,
        'travel_distance': 30000.5,
        'tzinfo': pytz.timezone('Europe/Moscow'),
        'created': dt.datetime(2018, 5, 11, 0, 22, 45, tzinfo=pytz.utc),
        'updated': dt.datetime(2018, 5, 11, 0, 23, 45, tzinfo=pytz.utc),
        'park_ride_sum': _make_money('0 RUB'),
        'toll_road_payment_price': None,
        'ind_bel_nds_rate': None,
        'coupon': _make_money('0 RUB'),
        'coupon_for_support': None,
        'currency_data': models.CurrencyData(
            for_contract=models.RatedCurrency('RUB', decimal.Decimal(1)),
            for_offer_contract=models.MaybeRatedCurrency(
                'RUB', decimal.Decimal(1),
            ),
        ),
        'cancelled_at': None,
        'cancel_distance': None,
        'cancelled_with_captcha': None,
        'netting_allowed': False,
        'donate_multiplier': None,
        'agglomeration': None,
        'fleet_subscription_level': None,
        'fine': None,
        'oebs_mvp_id': None,
        'geo_hierarchy': None,
        'cargo': None,
        'call_center': None,
        'is_cargo': False,
    }
    default_kwargs.update(attrs)
    return models.doc.Order(**default_kwargs)


def _make_discount(attrs):
    default_kwargs = {'value': None, 'declines': [], 'limit_id': None}
    default_kwargs.update(attrs)
    return models.order.Discount(**default_kwargs)


def _blueprint_make_discount_rule(attrs):
    default_kwargs = {
        'identity': models.rule.Identity(
            bson.ObjectId('000000000000000000000000'), 'discount',
        ),
        'idempotency_token': None,
        'matcher': blueprints.rules.moscow_matcher({}),
        'bonus_calculator': models.DiscountBonusCalculator('RUB'),
        'agreement_ref': models.AgreementRef.from_str(
            'subvention_agreement/1/default/_id/000000000000000000000000',
        ),
        'status': models.rule.Status.APPROVED,
    }
    default_kwargs.update(attrs)
    return models.DiscountRule(models.DiscountRule.Data(**default_kwargs))


def _blueprint_make_goal_rule(attrs):
    default_kwargs = {
        'identity': models.rule.Identity('goal_rule_id', 'goal_rule_group_id'),
        'matcher': blueprints.rules.moscow_matcher({}),
        'bonus_calculator': _make_goal_rule_steps_bonus_calculator({}),
        'agreement_ref': models.AgreementRef.from_str(
            'subvention_agreement/1/default/group_id/goal_rule_group_id',
        ),
        'days_span': 1,
        'display_in_taximeter': True,
        'budget': _make_subvention_budget({'id': 'goal_rule_budget_id'}),
    }
    default_kwargs.update(attrs)
    return models.GoalRule(models.GoalRule.Data(**default_kwargs))


def _blueprint_make_daily_guarantee_rule(attrs):
    default_identity = models.rule.Identity(
        'daily_guarantee_rule_id', 'daily_guarantee_rule_group_id',
    )
    identity: models.rule.Identity = attrs.get('identity', default_identity)
    default_kwargs = {
        'identity': identity,
        'matcher': blueprints.rules.moscow_matcher({}),
        'bonus_calculator': _make_daily_guarantee_rule_step_bonus_calculator(
            {},
        ),
        'data': models.DailyGuaranteeData(
            agreement_ref=models.AgreementRef.from_str(
                'subvention_agreement/1/default/group_id/' + identity.group_id,
            ),
            is_net=attrs.pop('is_net', False),
            status=models.rule.Status.APPROVED,
            is_test=False,
            budget=_make_subvention_budget(
                {'id': 'daily_guarantee_budget_id'},
            ),
            pattern_id=None,
        ),
    }
    default_kwargs.update(attrs)
    return models.DailyGuaranteeRule(**default_kwargs)


def _blueprint_make_single_order_goal_rule(attrs):
    default_kwargs = {
        'identity': models.rule.Identity(
            'single_order_goal_rule_id', 'single_order_goal_rule_group_id',
        ),
        'idempotency_token': None,
        'matcher': blueprints.rules.moscow_matcher({}),
        'bonus_calculator': (
            _make_single_order_goal_rule_steps_bonus_calculator({})
        ),
        'agreement_ref': models.AgreementRef.from_str(
            'subvention_agreement/1/default/group_id/'
            'single_order_goal_rule_group_id',
        ),
        'is_goal': True,
        'priority': 1000,
        'days_span': 1,
        'display_in_taximeter': True,
        'status': models.rule.Status.APPROVED,
        'budget': _make_subvention_budget(
            {'id': 'single_order_goal_budget_id'},
        ),
    }
    default_kwargs.update(attrs)
    return models.SingleOrderRule(
        models.SingleOrderRule.Data(**default_kwargs),
    )


def _blueprint_make_performer(attrs):
    default_kwargs = {
        'park_id': 'some_clid',
        'db_id': 'some_db_id',
        'uuid': 'some_uuid',
        'driver_license': 'some_driver_license',
        'driver_license_personal_id': '8hd93jdlakhf84030ejd9390z',
        'unique_driver_id': bson.ObjectId('5bab4bf979b9e5513fe5ec4a'),
        'has_sticker': False,
        'has_lightbox': False,
        'has_co_branding': False,
        'activity_points': 97,
        'tags': frozenset(),
        'hired_at': None,
        'hiring_type': None,
        'available_tariff_classes': frozenset(),
        'profile_payment_type_restrictions': None,
        'zone': 'driver_zone',
        'geo_hierarchy': None,
    }
    default_kwargs.update(attrs)
    default_kwargs['tags'] = frozenset(default_kwargs['tags'])
    default_kwargs['available_tariff_classes'] = frozenset(
        default_kwargs['available_tariff_classes'],
    )
    if default_kwargs['profile_payment_type_restrictions']:
        default_kwargs['profile_payment_type_restrictions'] = (
            models.ProfilePaymentTypeRestrictions(
                default_kwargs['profile_payment_type_restrictions'],
            )
        )
    return models.doc.Performer(**default_kwargs)


def _blueprint_make_driver(overrides):
    attrs = {
        'park_id': 'some_clid',
        'db_id': 'some_db_id',
        'uuid': 'some_uuid',
        'unique_driver_id': bson.ObjectId('5bab4bf979b9e5513fe5ec4a'),
    }
    attrs.update(overrides)
    return models.doc.Driver(**attrs)


def _blueprint_make_rule_event_handled(attrs):
    kwargs = {
        'journal_entries': [],
        'shift_ended_events': [],
        'full_subvention_details': [],
        'taxi_shifts': [],
    }
    kwargs.update(attrs)
    return models.RuleEventHandled(
        journal=models.doc.SubventionJournal(kwargs['journal_entries']),
        shift_ended_events=kwargs['shift_ended_events'],
        full_subvention_details=kwargs['full_subvention_details'],
        taxi_shifts=kwargs['taxi_shifts'],
    )


def _make_journal_entry_details(data):
    return models.doc.JournalEntryDetails(data)


def _make_commission_agreement(attrs):
    doc = {'cn': {'z': 'moscow', 'p': 'cash'}}
    doc.update(attrs)
    return db.commission.Converter.build_agreements_from_doc(doc)


def _make_commission_service_agreement(attrs):
    data = {
        'branding_discounts': [],
        'cancelation_settings': {
            'park_billable_cancel_interval': ['60', '0'],
            'pickup_location_radius': 300000,
            'user_billable_cancel_interval': ['120', '600'],
        },
        'cost_info': {
            'kind': 'boundaries',
            'max_cost': '15000',
            'min_cost': '0',
        },
        'effective_billing_type': 'normal',
        'vat': '1.2',
    }
    data.update(attrs)
    return billing_commissions_models.Agreement.from_json(data)


def _make_commission_input(attrs):
    default_kwargs = {
        'cost_for_client': _make_money('1000 RUB'),
        'cost_for_commission_var': models.Var(_make_money('1000 RUB'), []),
        'currency': 'RUB',
        'status': 'finished',
        'taxi_status': 'complete',
        'billing_type': 'normal_billing_type',
        'extra_commission': _make_money('20 RUB'),
        'cost_for_rebate': _make_money('0 RUB'),
        'rebate_rate': decimal.Decimal(0),
        'payment_type': 'cash',
        'marketing_level': frozenset(['co_branding', 'lightbox']),
        'source': None,
        'park_corp_vat': None,
        'due': dt.datetime(2018, 5, 11, 0, 0, 0, tzinfo=pytz.utc),
        'hired_at': None,
        'hiring_type': None,
        'with_driver_workshift': False,
        'with_driver_promocode': False,
        'with_increased_commission_for_rent': False,
        'driver_promocode_min_commission': _make_money('1 RUB'),
        'park_ride_sum': _make_money('1000 RUB'),
        'ind_bel_nds_rate': None,
        'childseat_rental': None,
        'cancelled_at': None,
        'cancel_distance': None,
        'cancelled_with_captcha': None,
        'completed_by_dispatcher': False,
        'apply_rebate_to_paid_orders_only': None,
        'ind_bel_nds_applied_to_all_commissions': None,
        'apply_promocode_with_rebate': None,
        'call_center_cost': None,
    }
    default_kwargs.update(attrs)
    return models.doc.CommissionInput(**default_kwargs)


def _make_goal_rule_steps_bonus_calculator(attrs):
    first_bonus_calculator = models.ExtraBonusCalculator(
        bonus_sum=_make_money('1000 RUB'),
        has_commission=False,
        is_additive=True,
    )

    second_bonus_calculator = models.ExtraBonusCalculator(
        bonus_sum=_make_money('2000 RUB'),
        has_commission=False,
        is_additive=True,
    )

    default_kwargs = {
        'steps': [
            models.BonusStep(
                num_orders_interval=intervals.closed_open(10, 20),
                bonus_calculator=first_bonus_calculator,
                id='goal_rule_id',
                group_member_id='goal_rule_id',
            ),
            models.BonusStep(
                num_orders_interval=intervals.at_least(20),
                bonus_calculator=second_bonus_calculator,
                id='goal_rule_second_id',
                group_member_id='goal_rule_second_id',
            ),
        ],
    }
    default_kwargs.update(attrs)
    return models.StepsBonusCalculator(**default_kwargs)


def _make_single_order_goal_rule_steps_bonus_calculator(attrs):
    first_bonus_calculator = models.GuaranteeBonusCalculator(
        guarantee_sum=_make_money('100 RUB'),
        has_commission=True,
        is_additive=False,
    )

    default_kwargs = {
        'steps': [
            models.BonusStep(
                num_orders_interval=intervals.at_least(10),
                bonus_calculator=first_bonus_calculator,
                id='single_order_goal_rule_id',
                group_member_id='single_order_goal_rule_id',
            ),
        ],
    }
    default_kwargs.update(attrs)
    return models.StepsBonusCalculator(**default_kwargs)


def _make_balances_by_id(identity_balances_pairs: list):
    balances_by_id: tp.Dict[models.rule.Identity, tp.List[models.Balance]] = {}
    for identity, balances in identity_balances_pairs:
        balances_by_id[identity] = balances
    return balances_by_id


def _make_daily_guarantee_rule_step_bonus_calculator(attrs):
    first_bonus_calculator = models.GuaranteeBonusCalculator(
        guarantee_sum=_make_money('1000 RUB'),
        has_commission=False,
        is_additive=True,
    )

    second_bonus_calculator = models.GuaranteeBonusCalculator(
        guarantee_sum=_make_money('2000 RUB'),
        has_commission=False,
        is_additive=True,
    )

    default_kwargs = {
        'steps': [
            models.BonusStep(
                num_orders_interval=intervals.closed_open(10, 20),
                bonus_calculator=first_bonus_calculator,
                id='daily_guarantee_rule_id',
                group_member_id='num_orders/10/week_days/1,2,3,4,5,6,7',
            ),
            models.BonusStep(
                num_orders_interval=intervals.at_least(20),
                bonus_calculator=second_bonus_calculator,
                id='daily_guarantee_rule_id_second',
                group_member_id='num_orders/20/week_days/1,2,3,4,5,6,7',
            ),
        ],
    }
    default_kwargs.update(attrs)
    return models.StepsBonusCalculator(**default_kwargs)


def _blueprint_make_steps_bonus_calculator(attrs):
    first_bonus_calculator = models.ExtraBonusCalculator(
        bonus_sum=_make_money('1000 RUB'),
        has_commission=False,
        is_additive=True,
    )

    second_bonus_calculator = models.ExtraBonusCalculator(
        bonus_sum=_make_money('2000 RUB'),
        has_commission=False,
        is_additive=True,
    )

    default_kwargs = {
        'steps': [
            models.BonusStep(
                num_orders_interval=intervals.closed_open(10, 20),
                bonus_calculator=first_bonus_calculator,
                id=None,
                group_member_id=None,
            ),
            models.BonusStep(
                num_orders_interval=intervals.at_least(20),
                bonus_calculator=second_bonus_calculator,
                id=None,
                group_member_id=None,
            ),
        ],
    }
    default_kwargs.update(attrs)
    return models.StepsBonusCalculator(**default_kwargs)


def _blueprint_make_calculators_order(attrs):
    currency_data = models.CurrencyData(
        for_contract=models.RatedCurrency('RUB', decimal.Decimal(1)),
        for_offer_contract=models.MaybeRatedCurrency(
            'RUB', decimal.Decimal(1),
        ),
    )
    default_kwargs = {
        'id': 'some_order_id',
        'payment_type': 'cash',
        'accepted_by_driver_at': dt.datetime(
            2018, 5, 10, 23, 59, 0, tzinfo=pytz.utc,
        ),
        'billing_at': dt.datetime(2018, 5, 10, 23, 59, 0, tzinfo=pytz.utc),
        'due': dt.datetime(2018, 5, 11, 0, 0, 0, tzinfo=pytz.utc),
        'completed_at': dt.datetime(2018, 5, 11, 0, 23, 45, tzinfo=pytz.utc),
        'status': 'finished',
        'taxi_status': 'complete',
        'zone_name': 'moscow',
        'source': None,
        'tariff': models.order.Tariff(
            minimal_cost=_make_money('99 RUB'),
            modified_minimal_cost=_make_money('99 RUB'),
            class_='econom',
        ),
        'price_modifiers': [],
        'cost_for_client': _make_money('300 RUB'),
        'cost_for_driver': _make_money('300 RUB'),
        'discount': models.order.Discount(
            rate=decimal.Decimal(0),
            method='full',
            value=_make_money('0 RUB'),
            declines=[],
            limit_id=None,
        ),
        'park_corp_vat': None,
        'coupon': _make_money('0 RUB'),
        'currency_data': currency_data,
        'tags': frozenset(),
        'profile_payment_type_restrictions': None,
        'available_tariff_classes': None,
        'fleet_subscription_level': None,
        'fine': None,
        'cargo': None,
        'call_center': None,
    }
    default_kwargs.update(attrs)
    return models.calculators.Order(**default_kwargs)


def _make_price_modifiers(attrs):
    return [
        models.calculators.PriceModifier(
            reason=item['reason'],
            value=decimal.Decimal(item['value']),
            type=item['type'],
            tariff_classes=item['tariff_classes'],
            has_subvention=item['has_subvention'],
        )
        for item in attrs
    ]


def _make_config(attrs):
    class MockConfig:
        pass

    config = MockConfig()
    for name, value in attrs.items():
        setattr(config, name, value)
    return config


def _make_interval(attrs):
    if 'end' in attrs:
        return intervals.closed_open(attrs['start'], attrs['end'])
    return intervals.at_least(attrs['start'])


def _make_datetime_interval(attrs):
    start = dateutil.parser.isoparse(attrs['start'])
    end = dateutil.parser.isoparse(attrs['end'])
    return intervals.closed_open(start, end)


def _make_order_subvention_changed_event(attrs):
    subvention_change: billing.Money = attrs['subvention_change']
    subvention_change_by_type = {}
    for key, value in attrs.get('subvention_change_by_type', {}).items():
        subvention_change_by_type[key] = decimal.Decimal(value)
    return models.OrderSubventionChangedEvent(
        subvention_change=attrs['subvention_change'],
        subvention_change_by_type=models.AmountByType(
            amounts=subvention_change_by_type,
            currency=subvention_change.currency,
        ),
        order_info=attrs['order_info'],
    )


def _make_full_subvention_details(attrs):
    matches = attrs.pop('matches')
    default = {'rule_type': None}
    default.update(**attrs)
    details = models.doc.SubventionDetails(**default)
    return models.doc.FullSubventionDetails(details=details, matches=matches)


def _make_subvention_details(attrs):
    default = {'rule_type': None, 'limit_ref': None}
    default.update(**attrs)
    return models.doc.SubventionDetails(**default)


def _make_subventions_park_data(attrs):
    default_kwargs = {
        'automate_marketing_payments': True,
        'pay_donations_without_offer': True,
        'offer_confirmed_at': dt.datetime(
            2018, 11, 22, 13, 2, 41, tzinfo=pytz.utc,
        ),
        'city': models.City(
            id='Москва',
            tzinfo=pytz.timezone('Europe/Moscow'),
            country_code='rus',
            donate_multiplier=decimal.Decimal('1.06'),
            donate_discounts_multiplier=decimal.Decimal('1.00'),
        ),
    }
    default_kwargs.update(**attrs)
    return models.subventions.ParkData(**default_kwargs)


def _make_subventions_input(attrs):
    default_kwargs = {
        'can_be_dry': True,
        'create_via_py2': False,
        'order_id': '14c5ae25ffb1148d80fad06ea2f89b10',
        'order_alias_id': '3ba696b11c891ee88c3150aaacba9d19',
        'order_payment_type': 'card',
        'due': dt.datetime(2019, 4, 1, 7, 46, tzinfo=pytz.utc),
        'tariff_class': 'econom',
        'zone_name': 'narofominsk',
        'park_id': '100500',
        'db_id': '7ad36bc7560449998acbe2c57a75c293',
        'uuid': '24deba79c4efecc229acdb1e5017296d',
        'activity_points': 100,
        'driver_license': '1234962123',
        'unique_driver_id': None,
        'has_lightbox': False,
        'has_sticker': False,
        'has_co_branding': False,
        'closed_without_accept': False,
        'completed_by_dispatcher': False,
        'accepted_by_driver_at': dt.datetime(
            2019, 4, 1, 7, 41, 10, 619000, tzinfo=pytz.utc,
        ),
        'subvention_geoareas': frozenset(),
        'tags': ['selfemployed'],
        'discount_details': models.order.DiscountDetails(
            discount=_make_money('0 RUB'), amendments=[],
        ),
        'hold_config': models.HoldConfig(delay=0),
        'force_hold': False,
        'comment': None,
        'value': _make_money('91.0 RUB'),
        'sub_commission': _make_money('10.7380 RUB'),
        'unrealized_sub_commission': _make_money('0 RUB'),
        'rule_details': [
            models.subventions.RuleDetails(
                rule_id=models.rule.Identity(
                    id_='5800ee9321586f10fe17171e', group_id='',
                ),
                value=_make_money('91.0 RUB'),
                payment_type=models.rule.PaymentType.GUARANTEE,
                subvention_geoareas=[],
                extra={},
                rule_type=None,
                is_once=False,
                limit_ref=None,
                contract_id=None,
            ),
        ],
        'park': _make_subventions_park_data({}),
        'rule_group': models.subventions.RuleGroup.SINGLE_ORDER,
        'currency_data': models.CurrencyData(
            for_contract=models.RatedCurrency('RUB', decimal.Decimal(1)),
            for_offer_contract=models.MaybeRatedCurrency(
                'RUB', decimal.Decimal(1),
            ),
        ),
        'billing_v2_id': None,
        'profile_payment_type_restrictions': None,
        'available_tariff_classes': None,
        'base_doc_id': None,
        'tlog_due': None,
        'order_completed_at': dt.datetime(2019, 4, 1, 7, 46, tzinfo=pytz.utc),
        'billing_client_id': None,
        'contract_id': None,
        'agglomeration': None,
        'related_orders_ids': None,
        'park_commission': None,
        'is_cargo': False,
    }
    default_kwargs.update(attrs)
    return models.subventions.Input(**default_kwargs)


def _blueprint_make_currency_data(attrs):
    default_kwargs = {
        'contract_currency': 'RUB',
        'contract_rate': decimal.Decimal(1),
        'offer_currency': 'RUB',
        'offer_rate': decimal.Decimal(1),
    }
    default_kwargs.update(attrs)
    for_contract = models.RatedCurrency(
        currency=default_kwargs['contract_currency'],
        rate_from_local=default_kwargs['contract_rate'],
    )
    for_offer_contract = models.MaybeRatedCurrency(
        currency=default_kwargs['offer_currency'],
        rate_from_local=(default_kwargs['offer_rate']),
    )
    return models.CurrencyData(
        for_contract=for_contract, for_offer_contract=for_offer_contract,
    )


def _make_subvention_antifraud_check_v2(attrs):
    default_kwargs = {
        'future_external_obj_id': 'alias_id/some_alias_id',
        'future_journal_external_obj_id': 'alias_id/some_alias_id',
        'antifraud_query': models.AntifraudQuery.for_order(
            data=models.AntifraudOrderData(
                order_id='some_order_id',
                driver_license='some_license',
                driver_license_personal_id='8hd93jdlakhf84030ejd9390z',
                due=dt.datetime(2019, 3, 2, 15, tzinfo=pytz.utc),
                hold_delay=0,
                city_id='Москва',
                tzinfo=None,
                zone_name='moscow',
                subvention=_make_money('50 RUB'),
            ),
            after=dt.datetime(2019, 3, 3, 12, 10, tzinfo=pytz.utc),
        ),
        'journal_entries': models.doc.AntifraudJournalEntries(
            block=[
                models.doc.AccountJournalEntry(
                    **{
                        'account_id': 1,
                        'amount': '100.0',
                        'event_at': '2019-03-02T15:00:00.000000+00:00',
                    },
                ),
            ],
            execute=[
                models.doc.AccountJournalEntry(
                    **{
                        'account_id': 2,
                        'amount': '100.0',
                        'event_at': '2019-03-02T15:00:00.000000+00:00',
                    },
                ),
            ],
            unhold_verification=[
                models.doc.AccountJournalEntry(
                    **{
                        'account_id': 3,
                        'amount': '-100.0',
                        'event_at': '2019-03-02T15:00:00.000000+00:00',
                    },
                ),
            ],
        ),
        'future_journal_tags': ['journal_ancestor_doc_id/12345'],
        'ancestor_doc_kind': 'order_ready_for_billing',
        'parent_doc_id': 12345,
        'forward': eye.Forward.empty(),
        'initial_check': True,
        'subventions_input': _make_subventions_input({}),
        'payout_info': None,
        'payout_info_if_fraud': None,
        'notifications': [],
        'antifraud_version': 2,
        'future_support_info': None,
        'future_support_info_if_fraud': None,
        'park_commission_rule': None,
        'park_commission_rule_status': None,
    }
    default_kwargs.update(attrs)
    return models.doc.AntifraudCheckV2(**default_kwargs)


def _make_subvention_antifraud_check_v2_data_2(attrs):
    default_kwargs = {
        'future_external_obj_id': 'alias_id/alias_id',
        'antifraud_query': {
            'kind': 'order',
            'data': {
                'driver_license': 'AXH903VV',
                'order_id': '123456789',
                'due': '2018-07-02T12:00:00+03:00',
                'hold_delay': 86400,
                'city_id': 'Москва',
                'zone_name': 'moscow',
                'tzinfo': 'Europe/Moscow',
            },
            'after': '2018-07-03T04:00:00.000000+03:00',
        },
        'ancestor_doc_kind': 'order_ready_for_billing',
        'journal_entries': {
            'block': [
                {
                    'account_id': 2,
                    'amount': '100',
                    'event_at': '2018-07-02T00:00:00.750000+00:00',
                },
            ],
            'execute': [
                {
                    'account_id': 3,
                    'amount': '100',
                    'event_at': '2018-07-02T00:00:00.750000+00:00',
                },
            ],
            'unhold_verification': [
                {
                    'account_id': 1,
                    'amount': '-100',
                    'event_at': '2018-07-02T00:00:00.750000+00:00',
                },
            ],
        },
        'ancestor_doc_id': 12345678,
        'parent_doc_id': 1234567,
        'initial_check': True,
        'antifraud_version': 2,
        'payout_info': None,
        'payout_info_if_fraud': None,
        'subventions_input': {
            'accepted_by_driver_at': '2018-07-02T00:30:00.750000+00:00',
            'activity_points': 0,
            'base_doc_id': 12345,
            'billing_v2_id': None,
            'billing_client_id': 'billing_client_id',
            'closed_without_accept': False,
            'comment': None,
            'completed_by_dispatcher': False,
            'create_via_py2': False,
            'currency_data': None,
            'db_id': 'db_id',
            'discount_details': {'amendments': [], 'discount': '0 RUB'},
            'driver_license': 'AXH903VV',
            'dry_mode': True,
            'due': '2018-07-02T00:00:00.750000+00:00',
            'force_hold': False,
            'has_co_branding': True,
            'has_lightbox': False,
            'has_sticker': False,
            'hold_config': {'delay': 0},
            'order_alias_id': 'alias_id',
            'order_id': '123456789',
            'order_payment_type': 'cash',
            'park': {
                'city': {
                    'id': 'Москва',
                    'tzinfo': 'Europe/Moscow',
                    'country_code': 'rus',
                    'donate_multiplier': '1.06',
                    'donate_discounts_multiplier': '1.00',
                },
                'contract_currency': 'RUB',
                'offer_confirmed_at': '2018-11-22T13:02:41.000000+00:00',
                'contract_currency_rate': '1',
                'offer_contract_currency': 'RUB',
                'automate_marketing_payments': True,
                'pay_donations_without_offer': True,
                'offer_contract_currency_rate': '1',
            },
            'park_id': 'clid',
            'rule_details': [
                {
                    'extra': {},
                    'payment_type': 'guarantee',
                    'rule_id': {
                        'group_id': 'some_group_id_144',
                        'id': 'p_9c61aeabbeb9bfe4751aa144',
                    },
                    'rule_type': 'mfg',
                    'subvention_geoareas': [],
                    'value': '100 RUB',
                },
            ],
            'rule_group': 'single_order',
            'sub_commission': '0 RUB',
            'subvention_geoareas': ['moscow'],
            'tags': ['some_tag'],
            'tariff_class': 'econom',
            'unrealized_sub_commission': '0 RUB',
            'uuid': 'uuid',
            'value': '100.0000 RUB',
            'zone_name': 'moscow',
            'is_cargo': False,
        },
    }
    default_kwargs.update(attrs)
    return default_kwargs


def _make_subvention_antifraud_complete_data(attrs):
    antifraud_response = {
        'action': 'pay',
        'antifraud_id': 'doc_id/0',
        'billing_id': 'antifraud_id/doc_id/0',
        'reason': None,
        'till': None,
    }
    subvention_update_needed_input = {
        'accepted_by_driver_at': '2018-07-02T00:30:00.750000+00:00',
        'activity_points': 0,
        'closed_without_accept': False,
        'completed_by_dispatcher': False,
        'db_id': 'db_id',
        'due': '2018-07-02T00:00:00.750000+00:00',
        'has_lightbox': False,
        'has_sticker': False,
        'order_alias_id': 'alias_id',
        'order_id': '123456789',
        'park_id': 'clid',
        'rule_details': [
            {
                'extra': {},
                'payment_type': 'guarantee',
                'rule_id': {
                    'group_id': 'some_group_id_144',
                    'id': 'p_9c61aeabbeb9bfe4751aa144',
                },
                'subvention_geoareas': [],
                'value': '100 RUB',
                'rule_type': 'mfg',
                'is_once': False,
            },
        ],
        'rule_group': 'single_order',
        'sub_commission': '0 RUB',
        'subvention_geoareas': ['moscow'],
        'tags': ['some_tag'],
        'tariff_class': 'econom',
        'uuid': 'uuid',
        'value': '100.0000 RUB',
        'zone_name': 'moscow',
    }
    default_kwargs = {
        'ancestor_doc_kind': 'order_ready_for_billing',
        'antifraud_response': antifraud_response,
        'future_journal_external_obj_id': 'alias_id/alias_id',
        'eye': {'forward': {'tags': []}},
        'future_documents': [
            {
                'data': {'rule_spec': {'kind': 'single_order'}},
                'event_at': '2018-11-30T19:31:35.000000+00:00',
                'external_event_ref': (
                    'subvention_antifraud_check/0/subvention_rules_restored'
                ),
                'external_obj_id': 'alias_id/alias_id',
                'journal_entries': [],
                'kind': 'subvention_rules_restored',
                'process_at': '2018-11-30T19:31:35.000000+00:00',
                'schedule_processing': True,
                'status': 'new',
                'tags': [],
            },
            {
                'data': subvention_update_needed_input,
                'event_at': '2018-11-30T19:31:35.000000+00:00',
                'external_event_ref': (
                    'subvention_antifraud_check/0/subventions_update_needed'
                ),
                'external_obj_id': 'alias_id/alias_id',
                'journal_entries': [],
                'kind': 'subventions_update_needed',
                'process_at': '2018-11-30T19:31:35.000000+00:00',
                'schedule_processing': True,
                'status': 'new',
                'tags': [],
            },
            {
                'event_at': '2018-11-30T19:31:35.000000+00:00',
                'process_at': '2018-11-30T19:31:35.000000+00:00',
                'external_event_ref': 'subvention_antifraud_check/0',
                'external_obj_id': (
                    'taxi/write_subvention_antifraud_entries/single_order/'
                    'alias_id/alias_id'
                ),
                'journal_entries': [],
                'kind': 'write_subvention_antifraud_entries',
                'schedule_processing': True,
                'status': 'new',
                'tags': [],
                'data': {
                    'antifraud_action': antifraud_response['action'],
                    'check_id': 'initial_antifraud_check_doc_id/0',
                    'subventions_input': None,
                    'due': '2018-07-02T00:00:00.750000+00:00',
                },
            },
        ],
        'future_journal_entries': [
            {
                'account_id': 1,
                'amount': '-100',
                'event_at': '2018-07-02T00:00:00.750000+00:00',
            },
            {
                'account_id': 3,
                'amount': '100',
                'event_at': '2018-07-02T00:00:00.750000+00:00',
            },
        ],
        'future_journal_tags': [],
    }
    default_kwargs.update(attrs)
    return default_kwargs


def _make_subvention_antifraud_check_v2_dict_doc(attrs):
    default_kwargs = {
        'data': _make_subvention_antifraud_check_v2_data_2({}),
        'event_at': '2018-11-30T19:31:35.000000+00:00',
        'external_event_ref': 'order_ready_for_billing/antifraud_request',
        'external_obj_id': 'antifraud_check/alias_id/alias_id',
        'journal_entries': [],
        'kind': 'subvention_antifraud_check',
        'process_at': '2018-07-03T05:00:00.000000+03:00',
        'service': 'billing-subventions',
        'doc_id': 0,
        'status': 'new',
    }
    default_kwargs.update(attrs)
    return default_kwargs


def _make_antifraud_action_data(attrs):
    default_kwargs = {
        'billing_request_id': 'doc_id/12345',
        'antifraud_response_id': 'some_antifraud_id',
        'action': 'block',
        'decision_time': '2019-06-25T18:37:00.000000+03:00',
        'reason': None,
    }
    default_kwargs.update(**attrs)
    return default_kwargs


def _make_subvention_antifraud_check_v2_data(attrs):
    default_kwargs = {
        'future_external_obj_id': 'alias_id/some_alias_id',
        'antifraud_query': {
            'kind': 'order',
            'data': {
                'order_id': 'some_order_id',
                'driver_license': 'some_license',
                'due': '2019-03-02T15:00:00.000000+00:00',
                'hold_delay': 0,
                'city_id': 'Москва',
                'zone_name': 'moscow',
                'subvention': {'amount': '30.0', 'currency': 'RUB'},
            },
            'after': '2019-03-03T12:10:00.000000+00:00',
        },
        'journal_entries': {
            'block': [
                {
                    'account_id': 1,
                    'amount': '100.0',
                    'event_at': '2019-03-02T15:00:00.000000+00:00',
                },
            ],
            'execute': [
                {
                    'account_id': 2,
                    'amount': '100.0',
                    'event_at': '2019-03-02T15:00:00.000000+00:00',
                },
            ],
            'unhold_verification': [
                {
                    'account_id': 3,
                    'amount': '-100.0',
                    'event_at': '2019-03-02T15:00:00.000000+00:00',
                },
            ],
        },
        'future_journal_tags': ['journal_ancestor_doc_id/12345'],
        'ancestor_doc_kind': 'order_ready_for_billing',
        'parent_doc_id': 12345,
        'initial_check': True,
        'subventions_input': _make_subventions_input_data({}),
        'antifraud_version': 2,
        'notifications': [],
    }
    default_kwargs.update(attrs)
    return default_kwargs


def _make_antifraud_response_data(attrs):
    default_kwargs = {
        'antifraud_id': 'some_antifraud_id',
        'billing_id': 'doc_id/12345',
        'action': 'pay',
        'till': None,
        'reason': None,
    }
    default_kwargs.update(attrs)
    return default_kwargs


def _make_antifraud_decision_data(attrs):
    default_kwargs = {
        'antifraud_response': _make_antifraud_response_data({}),
        'antifraud_query': {
            'after': '2019-03-03T12:10:00.000000+00:00',
            'data': {},
            'kind': 'noop',
        },
        'initial_check': False,
        'notifications': [],
    }
    default_kwargs.update(attrs)
    return _make_subvention_antifraud_check_v2_data(default_kwargs)


def _blueprint_make_order_completed_data(attrs):
    default_kwargs = {
        'accepted_by_driver_at': '2018-07-02T00:30:00.750Z',
        'billing_at': '2018-07-02T00:30:00.750Z',
        'alias_id': 'alias_id',
        'billing_contract_is_set': False,
        'childseat_rental': {'cost': '51', 'count': 1},
        'closed_without_accept': False,
        'completed_at': '2018-07-02T00:40:00.750Z',
        'completed_by_dispatcher': False,
        'cost': {'amount': None, 'currency': 'RUB'},
        'created': '2018-07-01T23:50:00.750Z',
        'discount': {'method': None, 'rate': None},
        'driver_cost': None,
        'due': '2018-07-02T00:00:00.750Z',
        'has_co_branding': True,
        'has_lightbox': False,
        'has_sticker': False,
        'order_id': '123456789',
        'park_ride_sum': '100',
        'payment_type': 'cash',
        'performer': {
            'activity_points': None,
            'db_id': 'db_id',
            'driver_id': 'clid_uuid',
            'driver_license': 'AXH903VV',
            'driver_license_personal_id': 'ec8beae3af8f4272b25b27997227ba86',
            'hired_at': '2018-07-01T00:00:00.750000+00:00',
            'hiring_type': 'commercial',
            'tariff_category_id': 'category_id',
            'unique_driver_id': '0123456789ab0123456789ab',
            'available_tariff_classes': ['econom'],
            'zone': 'driver_zone',
        },
        'price_modifiers': [
            {
                'has_subvention': False,
                'reason': None,
                'tariff_classes': ['econom'],
                'type': 'multiplier',
                'value': '1.020000',
            },
        ],
        'source': 'call_center',
        'is_mqc': False,
        'status': 'complete',
        'subvention_geoareas': [],
        'tags': ['some_tag'],
        'tariff_class': 'econom',
        'taxi_status': None,
        'total_distance': 123.0,
        'total_time': 60.0,
        'updated': '2018-07-02T00:40:00.750000+00:00',
        'zone': 'Moscow',
        'coupon': {
            'amount': '30',
            'currency': 'RUB',
            'netting_allowed': False,
            'for_support': None,
        },
        'park_corp_vat': None,
        'park': None,
        'billing_contract': None,
        'driver_workshift_ids': None,
        'cost_for_driver': None,
        'reason': {'kind': 'completed', 'data': {}},
    }
    default_kwargs.update(attrs)
    return models.doc.OrderCompletedData.from_json(default_kwargs)


def _blueprint_make_contract(attrs):
    default_kwargs = {
        'id': 665,
        'link_contract_id': None,
        'currency': 'RUB',
        'services': [111],
        'type': 9,
        'begin': dt.datetime(2000, 1, 1, tzinfo=dt.timezone.utc),
        'end': dt.datetime(3000, 1, 1, tzinfo=dt.timezone.utc),
        'is_signed': True,
        'is_faxed': False,
        'is_cancelled': False,
        'is_deactivated': False,
        'is_suspended': False,
    }
    default_kwargs.update(attrs)
    return models.Contract(**default_kwargs)


def _make_cost_details(attrs) -> models.order.CostDetails:
    if 'cost_for_subvention_var' not in attrs:
        attrs['cost_for_subvention_var'] = copy.deepcopy(
            attrs['cost_for_commission_var'],
        )
    return models.order.CostDetails(**attrs)


def _make_subvention_budget(attrs) -> models.Budget:
    default_kwargs = {'id': 'badc0de', 'weekly': '12345.6789'}
    default_kwargs.update(**attrs)
    return models.Budget.from_dict(default_kwargs)


CONVERTERS = {
    '$upload_in_status': _make_upload_in_status,
    '$upload': _Converter(personal_models.Upload),
    '$upload_data': _Converter(personal_models.UploadData),
    '$upload_status_changed': _Converter(personal_models.UploadStatusChanged),
    '$some_rules_saved': _Converter(personal_models.SomeRulesSaved),
    '$upload_started': _Converter(personal_models.UploadStarted),
    '$upload_status': personal_models.UploadStatus,
    '$upload_status_changed_reason': personal_models.UploadStatusChangedReason,
    '$date': _make_date,
    '$analytics_row': _Converter(personal_models.AnalyticsRow),
    '$time_interval': _Converter(personal_models.TimeInterval),
    '$oid': bson.ObjectId,
    '$tzinfo': _make_tzinfo,
    '$payment_type': models.rule.PaymentType,
    '$money': _make_money,
    '$agreement_ref': models.AgreementRef.from_str,
    '$moscow_rule_matcher': blueprints.rules.moscow_matcher,
    '$daily_guarantee_data': _Converter(models.DailyGuaranteeData),
    '$daily_guarantee_rule': _Converter(models.DailyGuaranteeRule),
    '$geo_booking_workshift': _make_geo_booking_workshift,
    '$geo_booking_rule_data': _Converter(models.GeoBookingRuleData),
    '$geo_booking_rule': _Converter(models.GeoBookingRule),
    '$blueprint:driver_fix_rule': blueprints.rules.driver_fix,
    '$blueprint:driver_fix_rule_data': (
        blueprints.driver_fix_rule.make_driver_fix_rule_data
    ),
    '$extra_bonus_calculator': _Converter(models.ExtraBonusCalculator),
    '$guarantee_bonus_calculator': _Converter(models.GuaranteeBonusCalculator),
    '$bonus_step': _Converter(models.BonusStep),
    '$steps_bonus_calculator': _Converter(models.StepsBonusCalculator),
    '$single_step_bonus_calculator': _Converter(models.BonusStep),
    '$single_step_extra_bonus_calculator': (
        _make_single_step_extra_bonus_calculator
    ),
    '$single_step_guarantee_bonus_calculator': (
        _make_single_step_guarantee_bonus_calculator
    ),
    '$identity': _Converter(models.rule.Identity),
    '$single_order_personal_rule': _Converter(personal_models.SingleOrderRule),
    '$single_order_rule': _Converter(models.SingleOrderRule),
    '$multi_order_rule': _Converter(personal_models.MultiOrderRule),
    '$driver': _Converter(personal_models.Driver),
    '$driver_data': _Converter(personal_models.DriverData),
    '$driver_rule': _Converter(personal_models.DriverRule),
    '$park': _Converter(models.Park),
    '$blueprint:park': _blueprint_make_park,
    '$city': _Converter(models.City),
    '$zone': _Converter(models.Zone),
    '$moscow_zone': _make_moscow_zone,
    '$zone_finder': _Converter(personal_finders.ZoneFinder),
    '$initiator': _Converter(models.Initiator),
    '$decimal': decimal.Decimal,
    '$float': float,
    '$frozenset': frozenset,
    '$daily_guarantee_input': _Converter(views.DailyGuaranteeInput),
    '$list_from_range': _make_list_from_range,
    '$timedelta': _Converter(dt.timedelta),
    '$date_range': _Converter(models.DateRange),
    '$order_info': _make_order_info,
    '$order_completed_event': _Converter(models.OrderCompletedEvent),
    '$order_subvention_changed_event': _make_order_subvention_changed_event,
    '$order_commission_changed_event': _Converter(
        models.OrderCommissionChangedEvent,
    ),
    '$document': _Converter(models.Document),
    '$entity': _Converter(models.Entity),
    '$universe': _Converter(containers.Universe),
    '$order_ready_for_billing_doc': _make_order_ready_for_billing_doc,
    '$geoarea_activity': _make_geoarea_activity,
    '$driver_geoarea_activity': _make_driver_geoarea_activity,
    '$blueprint:driver_geoarea_activity': (
        blueprints.driver_geoarea_activity.doc
    ),
    '$shift': _Converter(models.doc.Shift),
    '$shift_ended_rule_data': _Converter(models.doc.ShiftEndedRuleData),
    '$shift_ended': _Converter(models.doc.ShiftEnded),
    '$blueprint:manual_subvention:test_case': (
        blueprints.manual_subvention.test_case
    ),
    '$blueprint:shift_ended': blueprints.shift_ended.doc,
    '$blueprint:taxi_geo_booking_shift': blueprints.taxi_geo_booking_shift.doc,
    '$blueprint:geo_booking_payment_meta': (
        blueprints.taxi_geo_booking_shift.payment_meta
    ),
    '$commission_journal': _Converter(models.doc.CommissionJournal),
    '$subvention_journal': _Converter(models.doc.SubventionJournal),
    '$blueprint:support_info': blueprints.journal.make_support_info,
    '$blueprint:unfit_rule': blueprints.journal.make_unfit_rule,
    '$journal_entry': _Converter(models.doc.JournalEntry),
    '$tariff': _Converter(models.order.Tariff),
    '$antifraud_action': models.doc.AntifraudAction,
    '$blueprint:antifraud_response': _make_antifraud_response,
    '$antifraud_config': _make_antifraud_config,
    '$driver_promocode_config': _make_driver_promocode_config,
    '$hold_config': _Converter(models.HoldConfig),
    '$context': _make_context,
    '$order': _make_order,
    '$discount': _make_discount,
    '$order_discount': _Converter(models.doc.OrderDiscount),
    '$order_discount_decline': _Converter(models.doc.OrderDiscountDecline),
    '$blueprint:performer': _blueprint_make_performer,
    '$blueprint:driver': _blueprint_make_driver,
    '$blueprint:single_order_rule': blueprints.rules.single_order,
    '$blueprint:single_order_guarantee_rule': (
        blueprints.rules.single_order_guarantee
    ),
    '$blueprint:discount_rule': _blueprint_make_discount_rule,
    '$blueprint:goal_rule': _blueprint_make_goal_rule,
    '$blueprint:geo_booking_rule': blueprints.rules.geo_booking,
    '$blueprint:info_journal': blueprints.journal.make_info_journal,
    '$blueprint:daily_guarantee_rule': _blueprint_make_daily_guarantee_rule,
    '$blueprint:steps_bonus_calculator': (
        _blueprint_make_steps_bonus_calculator
    ),
    '$blueprint:single_order_goal_rule': (
        _blueprint_make_single_order_goal_rule
    ),
    '$blueprint:rule_event_handled': _blueprint_make_rule_event_handled,
    '$commission_contract': _make_commission_agreement,
    '$blueprint:billing_commissions:Agreement': (
        _make_commission_service_agreement
    ),
    '$commission_input': _make_commission_input,
    '$factory:unfit_reason': factories.make_unfit_reason,
    '$price_modifiers': _make_price_modifiers,
    '$balance_query': _Converter(models.BalanceQuery),
    '$balance': _Converter(models.Balance),
    '$balances_by_id': _make_balances_by_id,
    '$daily_guarantee_goal_fulfilled': _Converter(
        models.DailyGuaranteeGoalFulfilled,
    ),
    '$goal_rule_goal_fulfilled': _Converter(models.GoalRuleGoalFulfilled),
    '$driver_fix_goal_fulfilled': _Converter(models.DriverFixGoalFulfilled),
    '$payment_level': _Converter(models.PaymentLevel),
    '$blueprint:calculators.order': _blueprint_make_calculators_order,
    '$blueprint:CallCenter': models.CallCenter.from_json,
    '$amendment': _make_amendment,
    '$factory:grouped_thresholds': factories.make_grouped_thresholds,
    '$config': _make_config,
    '$journal_entry_details': _make_journal_entry_details,
    '$blueprint:cost_details': _make_cost_details,
    '$discount_details': _Converter(models.order.DiscountDetails),
    '$childseat_rental': _Converter(models.order.ChildSeatRental),
    '$factory:driver_entity': factories.make_driver_entity,
    '$set': set,
    '$dict': dict,
    '$interval': _make_interval,
    '$account_journal_entry': _Converter(models.doc.AccountJournalEntry),
    '$rule_event_handled': _Converter(models.RuleEventHandled),
    '$decline_reason': _Converter(models.doc.DeclineReason),
    '$subvention_details': _make_subvention_details,
    '$full_subvention_details': _make_full_subvention_details,
    '$datetime_interval': _make_datetime_interval,
    '$factory:datetime_interval': factories.make_datetime_interval,
    '$antifraud_order_data': _Converter(models.AntifraudOrderData),
    '$antifraud_driver_data': _Converter(models.AntifraudDriverData),
    '$antifraud_driver': _Converter(models.AntifraudDriverData.Driver),
    '$antifraud_rule': _Converter(models.AntifraudDriverData.Rule),
    '$antifraud_query': _Converter(models.AntifraudQuery),
    '$blueprint:antifraud_action_data': _make_antifraud_action_data,
    '$blueprint:subvention_antifraud_check_v2_data': (
        _make_subvention_antifraud_check_v2_data
    ),
    '$blueprint:antifraud_response_data': _make_antifraud_response_data,
    '$blueprint:antifraud_decision_data': _make_antifraud_decision_data,
    '$blueprint:subvention_antifraud_check_v2': (
        _make_subvention_antifraud_check_v2
    ),
    '$blueprint:subvention_antifraud_check_v2_data_2': (
        _make_subvention_antifraud_check_v2_data_2
    ),
    '$blueprint:subvention_antifraud_complete_data': (
        _make_subvention_antifraud_complete_data
    ),
    '$blueprint:subvention_antifraud_check_v2_dict_doc': (
        _make_subvention_antifraud_check_v2_dict_doc
    ),
    '$blueprint:subventions_park_data': _make_subventions_park_data,
    '$blueprint:subventions_input': _make_subventions_input,
    '$blueprint:subventions_update_needed_data': (
        _make_subventions_update_needed_data
    ),
    '$blueprint:subventions_update_needed_moscow_data': (
        _make_subventions_update_needed_moscow_data
    ),
    '$blueprint:new_billing_migration_config': (
        blueprints.config.new_billing_migration
    ),
    '$blueprint:rebill_order_doc': blueprints.docs.rebill_order,
    '$blueprint:created_docs_for_order_amended_test': (
        blueprints.docs.created_docs_for_order_amended_test
    ),
    '$blueprint:existing_docs_for_order_amended_test': (
        blueprints.docs.existing_docs_for_order_amended_test
    ),
    '$blueprint:subventions_update_needed_driver_referral_data': (
        _make_subventions_update_needed_driver_referral_data
    ),
    '$blueprint:subventions_update_needed_data_with_currency': (
        _make_subventions_update_needed_data_with_currency
    ),
    '$blueprint:subventions_input_data': _make_subventions_input_data,
    '$currency_data': _Converter(models.CurrencyData),
    '$blueprint:currency_data': _blueprint_make_currency_data,
    '$rated_currency': _Converter(models.RatedCurrency),
    '$notification_performer': _Converter(models.doc.NotificationPerformer),
    '$notification_rule': _Converter(
        models.doc.DailyGuaranteeNotification.Rule,
    ),
    '$goal_notification': _Converter(models.doc.GoalNotification),
    '$daily_guarantee_notification': _Converter(
        models.doc.DailyGuaranteeNotification,
    ),
    '$antifraud_document': _Converter(models.doc.AntifraudDocument),
    '$blueprint:order_completed_data': _blueprint_make_order_completed_data,
    '$blueprint:contract': _blueprint_make_contract,
    '$blueprint:shift_ended_results:daily_guarantee': (
        blueprints.shift_ended_results.daily_guarantee
    ),
    '$blueprint:shift_ended_results:goal': (
        blueprints.shift_ended_results.goal
    ),
    '$blueprint:order_commission_changed_doc': (
        blueprints.order_commission_changed.doc
    ),
    '$blueprint:order_subvention_changed_doc': (
        blueprints.order_subvention_changed.doc
    ),
    '$blueprint:order_commission_changed': (
        blueprints.order_commission_changed.model
    ),
    '$blueprint:order_subvention_changed': (
        blueprints.order_subvention_changed.model
    ),
    '$blueprint:order_commission_changed_doc_data': (
        blueprints.order_commission_changed.doc_data
    ),
    '$blueprint:daily_guarantee_db_dict': (
        blueprints.daily_guarantees.make_daily_guarantee_db_dict
    ),
    '$blueprint:api_discount_payback_rule': (
        blueprints.select_rules.api_discount_payback_rule
    ),
    '$blueprint:api_ridecount_rule': (
        blueprints.select_rules.api_ridecount_rule
    ),
    '$blueprint:api_mfg_geo_rule': (blueprints.select_rules.api_mfg_geo_rule),
    '$blueprint:api_on_top_geo_rule': (
        blueprints.select_rules.api_on_top_geo_rule
    ),
    '$blueprint:api_mfg_rule': (blueprints.select_rules.api_mfg_rule),
    '$blueprint:api_on_top_rule': (blueprints.select_rules.api_on_top_rule),
    '$blueprint:api_nmfg_rule': (blueprints.select_rules.api_nmfg_rule),
    '$blueprint:api_do_x_get_y_rule': (
        blueprints.select_rules.api_do_x_get_y_rule
    ),
    '$blueprint:select_rules_api_request': (
        blueprints.select_rules.api_request
    ),
    '$blueprint:journal_entry': blueprints.journal.make_journal_entry,
    '$eye_forward': _Converter(eye.Forward),
    '$eye_context': _Converter(eye.Context),
    '$rule_status': models.rule.Status,
    '$profile_payment_type_restrictions': (
        models.ProfilePaymentTypeRestrictions
    ),
    '$profile_payment_type_rule': models.ProfilePaymentTypeRule,
    '$subvention_type': models.rule.SubventionType,
    '$blueprint:driver_fix_input_dict': (
        blueprints.driver_fix_rule.make_driver_fix_input_dict
    ),
    '$blueprint:driver_fix_rate_input_dict': (
        blueprints.driver_fix_rule.make_driver_fix_rate_input_dict
    ),
    '$factory:driver_fix_rate_intervals': (
        factories.make_driver_fix_rate_intervals
    ),
    '$blueprint:subvention_payment': (
        blueprints.payments.make_subvention_payment
    ),
    '$blueprint:commission_payment': (
        blueprints.payments.make_commission_payment
    ),
    '$blueprint:payout_info': blueprints.payments.make_payout_info,
    '$blueprint:driver_income_info': (
        blueprints.payments.make_driver_income_info
    ),
    '$rule_group': models.subventions.RuleGroup,
    '$driver_mode_context': _Converter(models.DriverModeContext),
    '$driver_mode_context_sub': _Converter(
        models.DriverModeContext.Subscription,
    ),
    '$time': factories.make_time,
    '$blueprint:var:with_calculations': blueprints.var.with_calculations,
    '$blueprint:var:zero': blueprints.var.zero,
    '$blueprint:var:with_value': blueprints.var.with_value,
    '$blueprint:var:with_many_values': blueprints.var.with_many_values,
    '$blueprint:var:with_rebated_value': blueprints.var.with_rebated_value,
    '$blueprint:var:with_ind_bel_nds_value': (
        blueprints.var.with_ind_bel_nds_value
    ),
    '$blueprint:support_info:commission': blueprints.support_info.commission,
    '$calculation': _Converter(models.Calculation),
    '$commission_support_info': _Converter(models.CommissionSupportInfo),
    '$blueprint:billing_commissions:commission_match_response': (
        billing_commissions_models.CommissionsMatchResponse.from_json
    ),
    '$budget': _make_subvention_budget,
    '$vat_history': models.VatHistory.from_list,
    '$driver_promocode': _Converter(models.doc.DriverPromocode),
}
