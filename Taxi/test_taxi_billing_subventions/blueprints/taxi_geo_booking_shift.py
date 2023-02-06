import datetime as dt
import decimal

from taxi_billing_subventions.common.models.doc import _taxi_geo_booking_shift


def payment_meta(attrs: dict) -> _taxi_geo_booking_shift.GeoBookingPaymentMeta:
    default_kwargs: dict = {
        'billing_at': dt.datetime(
            2018, 12, 10, 14, 21, tzinfo=dt.timezone.utc,
        ),
        'budget_id': 'geo_booking_budget_id',
        'payment_ref': 'c4102437a1dec20bf234091b402b40',
        'tariff_zone': 'moscow',
        'time_zone': 'Europe/Moscow',
    }
    default_kwargs.update(attrs)
    return _taxi_geo_booking_shift.GeoBookingPaymentMeta(**default_kwargs)


def doc(attrs: dict) -> _taxi_geo_booking_shift.TaxiGeoBookingShift:
    default_kwargs: dict = {
        'payment_meta': payment_meta({}),
        'agreement': _taxi_geo_booking_shift.GeoBookingAgreement(
            ref='subvention_agreement/1/default/_id/12345678901234567890abcd',
            rule_data=_taxi_geo_booking_shift.GeoBookingRuleData(
                rule_type='add',
                currency='RUB',
                min_online_minutes=0,
                rate_on_order_per_minute=decimal.Decimal('5.5'),
                rate_free_per_minute=decimal.Decimal('15.0'),
            ),
        ),
        'driver': _taxi_geo_booking_shift.GeoBookingShiftDriver(
            clid='clid',
            driver_profile_id='uuid',
            park_id='db_id',
            unique_driver_id='111111111111111111111111',
        ),
        'shift': _taxi_geo_booking_shift.GeoBookingShift(
            start=dt.datetime(2018, 12, 9, 21, tzinfo=dt.timezone.utc),
            end=dt.datetime(2018, 12, 10, 21, tzinfo=dt.timezone.utc),
        ),
        'last_shift_date': dt.date(2018, 12, 10),
    }
    default_kwargs.update(attrs)
    data = _taxi_geo_booking_shift.TaxiGeoBookingShift.Data(**default_kwargs)
    return _taxi_geo_booking_shift.TaxiGeoBookingShift(
        data=data,
    )  # type: ignore
