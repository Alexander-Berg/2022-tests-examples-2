# pylint: disable=W0212
import pytest

from taxi import pro_app
from testsuite.utils import http

from taxi_selfreg.components import car_checker
from taxi_selfreg.generated.service.cities_cache import plugin as cities_cache
from taxi_selfreg.generated.web import web_context as context_module

TAXIMETER_USER_AGENT = 'Taximeter 9.61 (1234)'
TAXIMETER_APP = pro_app.app_from_user_agent(TAXIMETER_USER_AGENT)

CITY_MOSCOW = cities_cache.City(
    name='Москва', lat=55.45, lon=37.37, country_id='rus', geoarea='moscow',
)


async def test_car_checker_nodata(web_context: context_module.Context, patch):
    @patch(
        'taxi_selfreg.generated.service.cities_cache.plugin.'
        'CitiesCache.get_city',
    )
    def _get_city(city_name: str):
        assert city_name == 'Москва'

    checker = await web_context.car_checker.check(
        phone_pd_id='',
        app=TAXIMETER_APP,
        city_name='Москва',
        brand='',
        model='',
        year=2020,
    )
    assert isinstance(checker, car_checker.DataError)


@pytest.mark.parametrize('check_success', [True, False])
@pytest.mark.config(
    CLASSIFY_CAR_CLASSES_BY_ZONE_ID={
        '__default__': ['econom'],
        'moscow': ['econom', 'business'],
    },
)
async def test_car_checker(
        web_context: context_module.Context,
        patch,
        mock_get_nearest_zone,
        mock_cars_catalog,
        mock_classifier,
        check_success,
):
    @patch(
        'taxi_selfreg.generated.service.cities_cache.plugin.'
        'CitiesCache.get_city',
    )
    def _get_city(city_name: str):
        assert city_name == 'Москва'
        return CITY_MOSCOW

    @mock_cars_catalog('/v1/vehicles/check-stats')
    async def _check_stats(request: http.Request):
        assert dict(request.query) == {
            'mark': 'Ваз',
            'model': '2106',
            'year': '2020',
        }
        return {
            'mark_code': 'ВАЗ',
            'model_code': '2106',
            'year': 2020,
            'adjusted_age': 1,
            'price': '100500',
        }

    @mock_classifier('/v1/vehicle-classification-reject-reason')
    async def _reason(request: http.Request):
        assert request.query == {'zone_id': 'moscow'}
        assert request.json == {
            'brand_model': 'Ваз 2106',
            'car_number': '',
            'age': 1,
            'price': 100500,
            'required_classes': ['econom', 'business'],
        }
        if check_success:
            return {
                'tariffs_reject_reasons': [
                    {'reasons': [], 'tariff_id': 'tariff_1'},
                ],
            }
        return {
            'tariffs_reject_reasons': [
                {'reasons': ['MANUFACTURE_YEAR'], 'tariff_id': 'econom'},
                {
                    'reasons': ['MANUFACTURE_YEAR', 'PRICE'],
                    'tariff_id': 'business',
                },
            ],
        }

    error = await web_context.car_checker.check(
        phone_pd_id='some_phone',
        app=TAXIMETER_APP,
        city_name='Москва',
        brand='Ваз',
        model='2106',
        year=2020,
    )
    if check_success:
        assert error is None
    else:
        assert isinstance(error, car_checker.Rejected)
    assert _check_stats.has_calls
    assert _reason.has_calls
    assert mock_get_nearest_zone.has_calls


@pytest.mark.config(
    CLASSIFY_CAR_CLASSES_BY_ZONE_ID={
        '__default__': ['econom'],
        'moscow': ['econom', 'business'],
    },
)
async def test_car_checker_future_year(
        web_context: context_module.Context,
        patch,
        mock_get_nearest_zone,
        mock_cars_catalog,
):
    @patch(
        'taxi_selfreg.generated.service.cities_cache.plugin.'
        'CitiesCache.get_city',
    )
    def _get_city(city_name: str):
        assert city_name == 'Москва'
        return CITY_MOSCOW

    @mock_cars_catalog('/v1/vehicles/check-stats')
    async def _check_stats(request: http.Request):
        assert dict(request.query) == {
            'mark': 'Ваз',
            'model': '2106',
            'year': '2222',
        }
        return {
            'mark_code': 'ВАЗ',
            'model_code': '2106',
            'year': 2222,
            'adjusted_age': -1,
            'price': '100500',
        }

    error = await web_context.car_checker.check(
        phone_pd_id='some_phone',
        app=TAXIMETER_APP,
        city_name='Москва',
        brand='Ваз',
        model='2106',
        year=2222,
    )

    assert isinstance(error, car_checker.Rejected)
    assert _check_stats.has_calls
    assert mock_get_nearest_zone.has_calls


@pytest.mark.parametrize(
    'fallback',
    [
        pytest.param(
            'always-accept',
            marks=pytest.mark.client_experiments3(
                file_with_default_response='always_accept.json',
            ),
        ),
        pytest.param(
            'always-reject',
            marks=pytest.mark.client_experiments3(
                file_with_default_response='always_reject.json',
            ),
        ),
    ],
)
async def test_car_checker_fallback(
        web_context: context_module.Context, patch, fallback,
):
    @patch(
        'taxi_selfreg.generated.service.cities_cache.plugin.'
        'CitiesCache.get_city',
    )
    def _get_city(city_name: str):
        assert city_name == 'Москва'
        return CITY_MOSCOW

    error = await web_context.car_checker.check(
        phone_pd_id='some_phone',
        app=TAXIMETER_APP,
        city_name='Москва',
        brand='Ваз',
        model='2106',
        year=2020,
    )
    if fallback == 'always-accept':
        assert error is None
    else:
        assert isinstance(error, car_checker.Rejected)
