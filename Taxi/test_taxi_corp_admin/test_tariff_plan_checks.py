# pylint:disable=redefined-outer-name

from unittest import mock

import pytest


@pytest.fixture
def web_request(db, taxi_corp_admin_app, taxi_corp_admin_client):
    from taxi.util import context_timings
    from taxi.util import performance
    context_timings.time_storage.set(performance.TimeStorage('test'))
    return mock.MagicMock(db=db, app=taxi_corp_admin_app)


async def test_validate_zones_ok(web_request):
    from taxi_corp_admin.api.common import tariff_plans

    tariff_plan = {'zones': [{'zone': 'moscow', 'tariff_series_id': 'moscow'}]}

    errors = await tariff_plans.validate_zones(web_request, tariff_plan)
    assert errors == []


async def test_validate_zones_fail(web_request):
    from taxi_corp_admin import web
    from taxi_corp_admin.api.common import tariff_plans

    tariff_plan = {'zones': [{'zone': 'zone1', 'tariff_series_id': 'moscow'}]}

    errors = await tariff_plans.validate_zones(web_request, tariff_plan)
    assert errors == [web.errors.TARIFF_UNKNOWN_ZONE.replace('zone1')]


async def test_validate_zones_duplicate_fail(web_request):
    from taxi_corp_admin import web
    from taxi_corp_admin.api.common import tariff_plans

    tariff_plan = {
        'zones': [
            {'zone': 'moscow', 'tariff_series_id': 'moscow'},
            {'zone': 'moscow', 'tariff_series_id': 'moscow'},
            {'zone': 'moscow', 'tariff_series_id': 'moscow'},
        ],
    }

    errors = await tariff_plans.validate_zones(web_request, tariff_plan)
    assert errors == [web.errors.TARIFF_DUPLICATE_ZONE.replace('moscow')]


async def test_validate_tariffs_ok(web_request, territories_mock):
    from taxi_corp_admin.api.common import tariff_plans

    tariff_plan = {
        'country': 'rus',
        'zones': [
            {'zone': 'moscow', 'tariff_series_id': 'moscow'},
            {'zone': 'balaha', 'tariff_series_id': 'multizonal'},
        ],
    }

    errors = await tariff_plans.validate_tariffs(web_request, tariff_plan)
    assert errors == []


async def test_validate_tariffs_fail(web_request, territories_mock):
    from taxi_corp_admin import web
    from taxi_corp_admin.api.common import tariff_plans

    tariff_plan = {
        'country': 'rus',
        'zones': [
            {'zone': 'moscow', 'tariff_series_id': 'unknown'},
            {'zone': 'avrora', 'tariff_series_id': 'moscow'},
            {'zone': 'balaha', 'tariff_series_id': 'balaha'},
        ],
    }

    errors = await tariff_plans.validate_tariffs(web_request, tariff_plan)
    assert errors == [
        web.errors.TARIFF_NOT_FOUND.replace('unknown'),
        web.errors.TARIFF_PLAN_DIFFERENT_ZONE.replace('moscow', 'avrora'),
        web.errors.TARIFF_PLAN_DIFFERENT_COUNTRY.replace('pandora', 'rus'),
    ]


@pytest.mark.parametrize(
    'name, exists, current_series_id',
    [
        ('Тарифный план 0', False, None),
        ('Тарифный план 1', False, 'tariff_plan_series_id_1'),
        ('Тарифный план 1', True, None),
    ],
)
async def test_name_already_exists(
        web_request, name, exists, current_series_id,
):
    from taxi_corp_admin import web
    from taxi_corp_admin.api.common import tariff_plans

    tariff_plan = {
        'name': name,
        'country': 'rus',
        'zones': [{'zone': 'zone1', 'tariff_series_id': 'moscow'}],
    }

    expected_errors = []
    if exists:
        expected_errors = [web.errors.TARIFF_PLAN_EXISTS.replace(name)]

    errors = await tariff_plans.validate_name(
        web_request, tariff_plan, tariff_plan_series_id=current_series_id,
    )
    assert errors == expected_errors


async def test_country_ok(web_request, territories_mock):
    from taxi_corp_admin.api.common import tariff_plans

    tariff_plan = {
        'name': 'Тарифный план 1 (новый)',
        'country': 'rus',
        'zones': [{'zone': 'moscow', 'tariff_series_id': 'moscow'}],
    }

    errors = await tariff_plans.validate_country(
        web_request,
        tariff_plan,
        tariff_plan_series_id='tariff_plan_series_id_1',
    )
    assert errors == []


async def test_country_not_found(web_request, territories_mock):
    from taxi_corp_admin import web
    from taxi_corp_admin.api.common import tariff_plans

    tariff_plan = {
        'name': 'Тарифный план 2',
        'country': 'unk',
        'zones': [{'zone': 'moscow', 'tariff_series_id': 'moscow'}],
    }

    errors = await tariff_plans.validate_country(web_request, tariff_plan)
    assert errors == [web.errors.TARIFF_UNKNOWN_COUNTRY.replace('unk')]


async def test_country_not_allowed(web_request, territories_mock):
    from taxi_corp_admin import web
    from taxi_corp_admin.api.common import tariff_plans

    tariff_plan = {
        'name': 'Тарифный план 1 (обновлен)',
        'country': 'pandora',
        'zones': [{'zone': 'balaha', 'tariff_series_id': 'balaha'}],
    }

    errors = await tariff_plans.validate_country(
        web_request,
        tariff_plan,
        tariff_plan_series_id='tariff_plan_series_id_1',
    )
    assert errors == [web.errors.TARIFF_PLAN_COUNTRY_CHANGE_NOT_ALLOWED]
