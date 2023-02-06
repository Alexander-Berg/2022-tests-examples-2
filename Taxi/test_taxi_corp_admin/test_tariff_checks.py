# pylint:disable=redefined-outer-name

from unittest import mock

import pytest


@pytest.fixture
def web_request(db, taxi_corp_admin_app, taxi_corp_admin_client):
    from taxi.util import context_timings
    from taxi.util import performance
    context_timings.time_storage.set(performance.TimeStorage('test'))
    return mock.MagicMock(db=db, app=taxi_corp_admin_app)


@pytest.mark.parametrize(
    'tariff',
    [
        {'classes': [{'name': 'econom', 'inherited': True}]},
        {'classes': [{'name': 'econom', 'inherited': False, 'intervals': []}]},
    ],
)
def test_inherited_ok(tariff):
    from taxi_corp_admin.api.common import tariffs
    assert tariffs.validate_inherited(tariff) == []


def test_inherited_false():
    from taxi_corp_admin import web
    from taxi_corp_admin.api.common import tariffs

    tariff = {
        'classes': [{'name': 'econom', 'inherited': True, 'intervals': []}],
    }
    assert tariffs.validate_inherited(tariff) == [
        web.errors.TARIFF_CLASS_INHERITED.replace('econom'),
    ]


def test_non_inherited_false():
    from taxi_corp_admin import web
    from taxi_corp_admin.api.common import tariffs

    tariff = {
        'classes': [{'name': 'econom', 'inherited': False, 'policy': {}}],
    }

    assert tariffs.validate_inherited(tariff) == [
        web.errors.TARIFF_CLASS_NOT_INHERITED.replace('econom'),
    ]


@pytest.mark.config(
    CORP_CATEGORIES={
        '__default__': {
            'econom': 'name.econom',
            'comfort': 'name.comfort',
            'vip': 'name.vip',
        },
    },
)
def test_unique_class_names(web_request):
    from taxi_corp_admin import web
    from taxi_corp_admin.api.common import tariffs

    tariff = {
        'classes': [
            {'name': 'econom'},
            {'name': 'econom'},
            {'name': 'comfort'},
            {'name': 'comfort'},
            {'name': 'vip'},
        ],
    }

    assert tariffs.validate_classes(web_request, tariff) == [
        web.errors.TARIFF_NOT_UNIQUE_CLASS_NAME.replace('econom'),
        web.errors.TARIFF_NOT_UNIQUE_CLASS_NAME.replace('comfort'),
    ]


@pytest.mark.config(
    CORP_CATEGORIES={
        '__default__': {
            'econom': 'name.econom',
            'comfort': 'name.comfort',
            'vip': 'name.vip',
        },
    },
    CORP_CARGO_CATEGORIES={'__default__': {'cargocorp': 'name.cargocorp'}},
)
def test_corp_class_names(web_request):
    from taxi_corp_admin import web
    from taxi_corp_admin.api.common import tariffs

    tariff = {
        'classes': [
            {'name': 'econom'},
            {'name': 'comfort'},
            {'name': 'cargocorp'},
            {'name': 'unknown'},
        ],
    }

    assert tariffs.validate_classes(web_request, tariff) == [
        web.errors.TARIFF_NOT_CORP_CLASS.replace('unknown'),
    ]


async def test_intervals_ok():
    from taxi_corp_admin.api.common import tariffs

    tariff = {
        'classes': [
            {
                'name': 'econom',
                'inherited': False,
                'intervals': [
                    {
                        'category_type': 'application',
                        'day_type': 0,
                        'time_from': '00:00',
                        'time_to': '23:59',
                    },
                    {
                        'category_type': 'call_center',
                        'day_type': 0,
                        'time_from': '00:00',
                        'time_to': '23:59',
                    },
                    {
                        'category_type': 'application',
                        'day_type': 1,
                        'time_from': '00:00',
                        'time_to': '23:59',
                    },
                ],
            },
            {
                'name': 'comfort',
                'inherited': False,
                'intervals': [
                    {
                        'category_type': 'application',
                        'day_type': 0,
                        'time_from': '10:00',
                        'time_to': '23:59',
                    },
                    {
                        'category_type': 'application',
                        'day_type': 0,
                        'time_from': '00:00',
                        'time_to': '9:59',
                    },
                ],
            },
            {
                'name': 'vip',
                'inherited': False,
                'intervals': [
                    {
                        'category_type': 'application',
                        'day_type': 0,
                        'time_from': '20:00',
                        'time_to': '06:59',
                    },
                    {
                        'category_type': 'application',
                        'day_type': 0,
                        'time_from': '07:00',
                        'time_to': '19:59',
                    },
                ],
            },
        ],
    }

    assert await tariffs.validate_intervals(tariff) == []


async def test_intervals_not_enough():
    from taxi_corp_admin import web
    from taxi_corp_admin.api.common import tariffs

    tariff = {
        'classes': [
            {
                'name': 'econom',
                'inherited': False,
                'intervals': [
                    {
                        'category_type': 'application',
                        'day_type': 0,
                        'time_from': '00:00',
                        'time_to': '9:59',
                    },
                    {
                        'category_type': 'application',
                        'day_type': 0,
                        'time_from': '20:00',
                        'time_to': '23:59',
                    },
                ],
            },
        ],
    }

    assert await tariffs.validate_intervals(tariff) == [
        web.errors.TARIFF_CLASS_TIME_INTERVALS.replace('econom.application.0'),
    ]


@pytest.mark.parametrize(
    'meters,meter_id,errors_count',
    [([{}, {}], None, 0), ([{}, {}], 1, 0), ([], 0, 1), ([{}, {}], 2, 1)],
)
async def test_intervals_wrong_meters(meters, meter_id, errors_count):
    from taxi_corp_admin import web
    from taxi_corp_admin.api.common import tariffs

    tariff = {
        'classes': [
            {
                'name': 'econom',
                'inherited': False,
                'intervals': [
                    {
                        'category_type': 'application',
                        'day_type': 0,
                        'id': 'id_1',
                        'meters': meters,
                        'time_from': '00:00',
                        'time_to': '23:59',
                    },
                ],
            },
        ],
    }
    if meter_id is not None:
        interval = tariff['classes'][0]['intervals'][0]
        interval['paid_dispatch_distance_price_intervals_meter_id'] = meter_id
        price_list = [
            {
                'price': {
                    'time_price_intervals_meter_id': meter_id,
                    'distance_price_intervals_meter_id': meter_id,
                },
            },
        ]
        interval['zonal_prices'] = price_list
        interval['special_taximeters'] = price_list
    errors = await tariffs.validate_intervals(tariff)
    if errors_count:
        assert errors == [
            web.errors.INTERVAL_WRONG_METERS.replace('econom', 'id_1'),
        ]
    else:
        assert errors == []


async def test_intervals_overlap():
    from taxi_corp_admin import web
    from taxi_corp_admin.api.common import tariffs

    tariff = {
        'classes': [
            {
                'name': 'econom',
                'inherited': False,
                'intervals': [
                    {
                        'category_type': 'application',
                        'day_type': 0,
                        'time_from': '00:00',
                        'time_to': '9:59',
                    },
                    {
                        'category_type': 'application',
                        'day_type': 0,
                        'time_from': '9:00',
                        'time_to': '23:59',
                    },
                ],
            },
            {
                'name': 'comfort',
                'inherited': False,
                'intervals': [
                    {
                        'category_type': 'application',
                        'day_type': 0,
                        'category_name': 'comfort',
                        'time_from': '00:00',
                        'time_to': '23:59',
                    },
                    {
                        'category_type': 'application',
                        'day_type': 0,
                        'category_name': 'comfort',
                        'time_from': '9:00',
                        'time_to': '10:00',
                    },
                ],
            },
            {
                'name': 'vip',
                'inherited': False,
                'intervals': [
                    {
                        'category_type': 'application',
                        'day_type': 0,
                        'category_name': 'vip',
                        'time_from': '00:00',
                        'time_to': '23:59',
                    },
                    {
                        'category_type': 'application',
                        'day_type': 0,
                        'category_name': 'vip',
                        'time_from': '00:00',
                        'time_to': '23:59',
                    },
                ],
            },
        ],
    }

    assert await tariffs.validate_intervals(tariff) == [
        web.errors.TARIFF_CLASS_TIME_INTERVALS.replace('econom.application.0'),
        web.errors.TARIFF_CLASS_TIME_INTERVALS.replace(
            'comfort.application.0',
        ),
        web.errors.TARIFF_CLASS_TIME_INTERVALS.replace('vip.application.0'),
    ]


async def test_currencies_ok(web_request, territories_mock):
    from taxi_corp_admin.api.common import tariffs

    tariff = {
        'home_zone': 'moscow',
        'country': 'rus',
        'classes': [
            {
                'name': 'econom',
                'inherited': False,
                'intervals': [{'currency': 'RUB'}, {'currency': 'RUB'}],
            },
        ],
    }

    errors = await tariffs.validate_currencies(web_request, tariff)
    assert errors == []


async def test_currencies_fail(web_request, territories_mock):
    from taxi_corp_admin import web
    from taxi_corp_admin.api.common import tariffs

    tariff = {
        'home_zone': None,
        'country': 'rus',
        'classes': [
            {
                'name': 'econom',
                'inherited': False,
                'intervals': [
                    {'currency': 'RUB'},
                    {'currency': 'PND'},
                    {'currency': 'USD'},
                ],
            },
        ],
    }

    errors = await tariffs.validate_currencies(web_request, tariff)
    assert errors == [
        web.errors.CLASS_NOT_COUNTRY_CURRENCY.replace('PND'),
        web.errors.CLASS_NOT_COUNTRY_CURRENCY.replace('USD'),
    ]


async def test_country_ok(web_request, territories_mock):
    from taxi_corp_admin.api.common import tariffs

    tariff = {
        'home_zone': 'moscow',
        'country': 'pandora',
        'tariff_series_id': 'tariff_series_id_1',
    }
    countries = await tariffs.retrieve_countries(web_request)
    errors = await tariffs.validate_country(
        web_request, tariff, countries, tariff_series_id='tariff_series_id_2',
    )
    assert errors == []


async def test_country_not_found(web_request, territories_mock):
    from taxi_corp_admin import web
    from taxi_corp_admin.api.common import tariffs

    tariff = {'home_zone': 'moscow', 'country': 'unk'}
    countries = await tariffs.retrieve_countries(web_request)
    errors = await tariffs.validate_country(web_request, tariff, countries)
    assert errors == [web.errors.TARIFF_UNKNOWN_COUNTRY.replace('unk')]


async def test_country_not_allowed(web_request, territories_mock):
    from taxi_corp_admin import web
    from taxi_corp_admin.api.common import tariffs

    tariff = {
        'home_zone': 'moscow',
        'country': 'pandora',
        'tariff_series_id': 'tariff_series_id_1',
    }
    countries = await tariffs.retrieve_countries(web_request)
    errors = await tariffs.validate_country(
        web_request, tariff, countries, tariff_series_id='tariff_series_id_1',
    )
    assert errors == [web.errors.TARIFF_COUNTRY_CHANGE_NOT_ALLOWED]


async def test_validate_zonal_ok(web_request):
    from taxi_corp_admin.api.common import tariffs

    tariff = {
        'home_zone': 'moscow',
        'country': 'rus',
        'classes': [
            {
                'name': 'econom',
                'inherited': False,
                'intervals': [
                    {
                        'special_taximeters': [{'zone_name': 'moscow'}],
                        'zonal_prices': [
                            {'source': 'dme', 'destination': 'svo'},
                        ],
                    },
                ],
            },
        ],
    }
    areas = await tariffs.retrieve_geoareas(web_request)
    assert await tariffs.validate_zones(tariff, areas) == []


async def test_validate_multizonal_ok(web_request):
    from taxi_corp_admin.api.common import tariffs

    tariff = {
        'home_zone': None,
        'country': 'rus',
        'classes': [
            {
                'intervals': [
                    {
                        'special_taximeters': [
                            {'zone_name': None},
                            {'zone_name': 'suburb'},
                            {'zone_name': 'dme'},
                        ],
                        'zonal_prices': [
                            {'source': None, 'destination': 'svo'},
                        ],
                    },
                ],
            },
        ],
    }
    areas = await tariffs.retrieve_geoareas(web_request)
    assert await tariffs.validate_zones(tariff, areas) == []


async def test_validate_zonal_fail(web_request):
    from taxi_corp_admin import web
    from taxi_corp_admin.api.common import tariffs

    tariff = {
        'home_zone': 'zone1',
        'country': 'rus',
        'classes': [
            {
                'name': 'econom',
                'inherited': False,
                'intervals': [
                    {
                        'special_taximeters': [
                            {'zone_name': 'home'},
                            {'zone_name': None},
                        ],
                        'zonal_prices': [
                            {'source': 'home', 'destination': 'zone1'},
                        ],
                    },
                ],
            },
        ],
    }
    areas = await tariffs.retrieve_geoareas(web_request)
    errors = await tariffs.validate_zones(tariff, areas)
    excepted_errors = [
        web.errors.TARIFF_UNKNOWN_ZONE.replace('zone1'),
        web.errors.TARIFF_UNKNOWN_ZONE.replace('home'),
        web.errors.TARIFF_ZONE_NOT_ALLOWED.replace(None),
    ]
    assert sorted(errors) == sorted(excepted_errors)


async def test_validate_multizonal_fail(web_request):
    from taxi_corp_admin import web
    from taxi_corp_admin.api.common import tariffs

    tariff = {
        'home_zone': None,
        'country': 'rus',
        'classes': [
            {
                'name': 'econom',
                'inherited': False,
                'intervals': [
                    {
                        'special_taximeters': [{'zone_name': 'zone1'}],
                        'zonal_prices': [
                            {'source': None, 'destination': 'zone2'},
                        ],
                    },
                ],
            },
        ],
    }
    areas = await tariffs.retrieve_geoareas(web_request)
    errors = await tariffs.validate_zones(tariff, areas)
    excepted_errors = [
        web.errors.TARIFF_UNKNOWN_ZONE.replace('zone1'),
        web.errors.TARIFF_UNKNOWN_ZONE.replace('zone2'),
    ]
    assert sorted(errors) == sorted(excepted_errors)


@pytest.mark.translations(
    tariff={
        'name.econom': {'ru': 'Эконом'},
        'currency.rub': {'ru': 'руб.'},
        'service_name.yellowcarnumber': {'ru': 'Желтые номера'},
        'interval.day': {'ru': 'Тариф "Дневной"'},
    },
    geoareas={
        'moscow': {'ru': 'Москва'},
        'inside_suburb': {'ru': 'За пределами города'},
        'svo': {'ru': 'Аэропорт Шереметьево'},
        'dme': {'ru': 'Аэропорт Домодедово'},
    },
)
def test_translations_ok(web_request):
    from taxi_corp_admin.api.common import tariffs

    tariff = {
        'home_zone': 'moscow',
        'country': 'rus',
        'classes': [
            {
                'name': 'econom',
                'inherited': False,
                'intervals': [
                    {
                        'category_name': 'econom',
                        'name_key': 'interval.day',
                        'currency': 'RUB',
                        'special_taximeters': [{'zone_name': 'suburb'}],
                        'zonal_prices': [
                            {'source': 'svo', 'destination': 'dme'},
                        ],
                        'summable_requirements': [
                            {'max_price': 100, 'type': 'yellowcarnumber'},
                        ],
                    },
                ],
            },
        ],
    }

    assert tariffs.validate_translations(web_request, tariff) == []


@pytest.mark.translations(
    tariff={
        'name.econom': {'ru': 'Эконом'},
        'currency.rub': {'ru': 'руб.'},
        'service_name.yellowcarnumber': {'ru': 'Желтые номера'},
        'interval.day': {'ru': 'Тариф "Дневной"'},
    },
    geoareas={
        'moscow': {'ru': 'Москва'},
        'inside_suburb': {'ru': 'За пределами города'},
        'svo': {'ru': 'Аэропорт Шереметьево'},
        'dme': {'ru': 'Аэропорт Домодедово'},
    },
)
def test_translations_fail(web_request):
    from taxi_corp_admin import web
    from taxi_corp_admin.api.common import tariffs

    tariff = {
        'home_zone': 'zone1',
        'country': 'rus',
        'classes': [
            {
                'name': 'econom',
                'inherited': False,
                'intervals': [
                    {
                        'name_key': 'interval1',
                        'currency': 'cur1',
                        'special_taximeters': [{'zone_name': 'zone2'}],
                        'zonal_prices': [
                            {'source': 'zone3', 'destination': 'zone4'},
                        ],
                        'summable_requirements': [
                            {'max_price': 100, 'type': 'req1'},
                        ],
                    },
                ],
            },
        ],
    }

    assert tariffs.validate_translations(web_request, tariff) == [
        web.errors.UNTRANSLATED_KEY.replace('geoareas.zone1', 'ru'),
        web.errors.UNTRANSLATED_KEY.replace('tariff.interval1', 'ru'),
        web.errors.UNTRANSLATED_KEY.replace('tariff.currency.cur1', 'ru'),
        web.errors.UNTRANSLATED_KEY.replace('geoareas.inside_zone2', 'ru'),
        web.errors.UNTRANSLATED_KEY.replace('geoareas.zone3', 'ru'),
        web.errors.UNTRANSLATED_KEY.replace('geoareas.zone4', 'ru'),
        web.errors.UNTRANSLATED_KEY.replace('tariff.service_name.req1', 'ru'),
    ]


@pytest.mark.parametrize(
    'name, exists, current_series_id',
    [
        ('Тариф 0', False, None),
        ('Тариф 1', False, 'tariff_series_id_1'),
        ('Тариф 1', True, None),
    ],
)
async def test_name_already_exists(
        web_request, name, exists, current_series_id,
):
    from taxi_corp_admin import web
    from taxi_corp_admin.api.common import tariffs

    tariff = {'name': name}

    expected_errors = []
    if exists:
        expected_errors = [web.errors.TARIFF_EXISTS.replace(name)]

    errors = await tariffs.validate_name(
        web_request, tariff, tariff_series_id=current_series_id,
    )
    assert errors == expected_errors
