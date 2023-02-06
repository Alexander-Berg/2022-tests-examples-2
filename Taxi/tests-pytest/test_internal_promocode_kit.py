# -*- coding: utf-8 -*-

import datetime
import shutil
import tempfile

import pytest


from taxi.core import async
from taxi.core import db
from taxi.internal.promocode_kit import config
from taxi.internal.promocode_kit import coupon_classes
from taxi.internal.promocode_kit import coupon_generate
from taxi.internal.promocode_kit import coupon_handler
from taxi.internal.promocode_kit import promocode_const
from taxi.util import coupon as util_coupon


# TODO: Historically, coupon_manager (and promocode_kit, as its latest
# reincarnation) were tested in trial through corresponding handlers
# (couponcheck, routestats, order, taxionthway). One should consolidate
# core features tests here.

ORDER_ID = 'abc1234567890'
YANDEX_UID = 'user123'


@pytest.yield_fixture
def tmpdir():
    td = tempfile.mkdtemp()
    yield td
    shutil.rmtree(td)


@pytest.mark.parametrize(
    'num_digits, random_int, random_str', [
        (5, 12345, '12345'),
        (6, 123, '000123'),
])
def test_generate_random(patch, num_digits, random_int, random_str):
    @patch('random.randint')
    def _randint(a, b):
        assert a == 1
        assert str(b) == '9' * num_digits
        return random_int

    assert coupon_generate.generate_random(num_digits) == random_str


@pytest.mark.now('2016-05-31 15:30:00+03')
@pytest.inline_callbacks
def test_referrals_build_series_info(patch, sleep):
    @patch('taxi.internal.promocode_kit.config.get_referrals_config')
    @async.inline_callbacks
    def get_referrals_config():
        yield
        async.return_value({
            'enabled': True,
            'count': count,

            'creator': {
                'max_per_user': 1,
                'min_card_orders': 0,
                'promocodes': {
                    '__default__': {
                        'valid': True,
                        'value': 350,
                    },
                }
            },

            'consumer': {
                '__default__': {
                    'valid': True,
                    'duration': 30 * 86400,
                    'user_limit': 1,
                    'first_limit': 1,
                },
            }
        })

    now = datetime.datetime.utcnow()
    validation_data = coupon_classes.ValidationData(
        user_phone_id='user_phone_1',
        city_id=u'Москва',
        creditcard=False,
        application='android',
        app_version=(3, 32, 0),
        platform_version=None,
        card_object=None,
        device_id='fake_id',
        yandex_uid=None
    )

    promocode_doc = {
        '_id': 'referral1',
        'value': 350,
        'currency': 'RUB',
    }
    promocode_obj = coupon_classes.ReferralPromocode(
        'phone1', promocode_doc
    )
    assert promocode_obj.series_info is None

    for count in (3, 5, 7):
        yield promocode_obj.build_series_info(validation_data)
        si = promocode_obj.series_info
        assert si.series_id == 'referral1'
        assert si.value == 350
        assert si.currency == 'RUB'
        assert si.start == datetime.date(2016, 5, 31)
        assert si.finish == datetime.date(2016, 6, 30)
        assert si.user_limit == 1
        assert si.rides_total == 1
        assert si.first_limit == 1
        assert si.count == count
        assert si.country == 'rus'
        assert si.creditcard_only is True

        doc = yield db.promocode_refclaims.find_one({
            'series_id': 'referral1',
            'user_phone_id': 'user_phone_1'
        })
        assert doc is not None
        assert doc['created'] == now
        assert doc['updated'] == now

        yield sleep(2 * 86400)  # wait 2 days
        assert now != datetime.datetime.utcnow()


@pytest.mark.parametrize('city_id,enabled,valid,reason', [
    (u'Екатеринбург', True, True, None),
    (u'Екатеринбург', False, True, promocode_const.ERROR_INVALID_CODE),
    (u'Екатеринбург', True, False, promocode_const.ERROR_INVALID_CITY),
    (u'Екатеринбург', False, False, promocode_const.ERROR_INVALID_CODE),
])
@pytest.inline_callbacks
def test_referrals_precheck(city_id, enabled, valid, reason, patch):
    @patch('taxi.internal.promocode_kit.config.get_referrals_config')
    @async.inline_callbacks
    def get_referrals_config():
        yield
        async.return_value({
            'enabled': enabled,
            'count': 5,

            'creator': {
                'max_per_user': 1,
                'min_card_orders': 0,
                'promocodes': {
                    '__default__': {
                        'valid': True,
                        'value': 350,
                        # 'currency': 'RUB',
                    },
                }
            },

            'consumer': {
                '__default__': {
                    'valid': global_valid,
                    'duration': 30 * 86400,
                    'user_limit': 1,
                    'first_limit': 1,
                },
                city_id: {
                    'valid': valid
                }
            }
        })

    for global_valid in (True, False):
        global_cfg = yield config.get_referrals_config()
        area_cfg = config.get_referrals_area_config(
            global_cfg[config.REFERRALS_CONSUMER],
            city_id
        )
        print global_cfg['consumer']

        if reason is None:
            coupon_classes.ReferralPromocode._pre_check(global_cfg, area_cfg)
        else:
            with pytest.raises(coupon_classes.CouponCheckError) as exc:
                coupon_classes.ReferralPromocode._pre_check(
                    global_cfg, area_cfg
                )
            assert exc.value.error_info.reason == reason


@pytest.inline_callbacks
def test_cash_friendly_promocode():
    tests = [('clear', True), ('SAD', False), ('ФЫВАОЛДЖ', False)]
    for series, creditcard_only in tests:
        series_doc = {
            '_id': series.lower(),
            'creditcard_only': creditcard_only,
        }
        yield db.promocode_series.insert(series_doc)
        result = yield coupon_handler.cash_friendly_promocode(series)
        assert result is not None
        assert result is not creditcard_only


@pytest.inline_callbacks
def test_cash_friendly_promocode_for_referral_series():
    result = yield coupon_handler.cash_friendly_promocode(util_coupon.COUPON_SERIES_REFERRAL)
    assert result is not None
    assert result is False
