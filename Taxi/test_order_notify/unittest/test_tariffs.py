import typing

import pytest

from generated.clients import taxi_tariffs
from generated.models import taxi_tariffs as taxi_tariffs_models
from taxi import memstorage

from order_notify.generated.stq3 import stq_context
from order_notify.repositories import tariffs


DEFAULT_CATEGORY_ARGS: dict = {
    'can_be_default': True,
    'client_constraints': [],
    'client_requirements': [],
    'is_default': True,
    'name': 'buisness',
    'only_for_soon_orders': True,
    'service_levels': [],
    'tanker_key': 'key.buisness',
}

DEFAULT_CATEGORY = taxi_tariffs_models.Category(**DEFAULT_CATEGORY_ARGS)


@pytest.fixture(name='mock_functions')
def mock_template_vars_functions(patch):
    class Counter:
        def __init__(self):
            self.times_called = 0

        def call(self):
            self.times_called += 1

    class Counters:
        def __init__(self):
            self.get_tariff_category = Counter()

    counters = Counters()

    @patch('order_notify.repositories.tariffs.get_tariff_category')
    async def _get_tariff_category(
            client_tariffs: taxi_tariffs.TaxiTariffsClient,
            zone: str,
            tariff_cls: str,
    ) -> typing.Optional[taxi_tariffs_models.Category]:
        counters.get_tariff_category.call()
        assert zone in ('moscow', 'minsk')
        assert tariff_cls in ('econom', 'buisness')
        if zone == 'moscow' and tariff_cls == 'econom':
            return None
        return DEFAULT_CATEGORY


@pytest.fixture(name='mock_server')
def mock_server_fixture(mockserver):
    @mockserver.json_handler('/taxi-tariffs/v1/tariff_settings/bulk_retrieve')
    def _tariff_zones(http_request):
        zones = []
        request_zones = http_request.query['zone_names']

        if 'kiev' in request_zones:
            zones.append(
                {'zone': 'kiev', 'tariff_settings': {'home_zone': 'kiev'}},
            )
        if 'minsk' in request_zones:
            zones.append({'zone': 'minsk'})
        if 'moscow' in request_zones:
            zones.append(
                {
                    'zone': 'moscow',
                    'tariff_settings': {
                        'home_zone': 'moscow',
                        'categories': [DEFAULT_CATEGORY_ARGS],
                    },
                },
            )
        return {'zones': zones}


@pytest.mark.parametrize(
    'zone, tariff_class, locale, expected_tariff',
    [
        pytest.param(None, None, 'ru', None, id='no_zone_and_tariff_cls'),
        pytest.param(None, 'econom', 'ru', None, id='no_zone'),
        pytest.param('moscow', None, 'ru', None, id='no_tariff_cls'),
        pytest.param('moscow', 'econom', 'ru', 'Эконом', id='no_category_ru'),
        pytest.param('moscow', 'econom', 'en', 'EC', id='no_category_en'),
        pytest.param('minsk', 'buisness', 'ru', 'Бызнэс', id='ru'),
        pytest.param('minsk', 'buisness', 'en', 'BSS', id='en'),
    ],
)
@pytest.mark.translations(
    tariff={
        'name.econom': {'ru': 'Эконом', 'en': 'EC'},
        'key.buisness': {'ru': 'Бызнэс', 'en': 'BSS'},
    },
)
async def test_get_tariff_name(
        stq3_context: stq_context.Context,
        mock_functions,
        zone,
        tariff_class,
        locale,
        expected_tariff,
):
    tariff = await tariffs.get_tariff_name(
        context=stq3_context,
        zone=zone,
        tariff_cls=tariff_class,
        locale=locale,
    )
    assert tariff == expected_tariff


@pytest.mark.parametrize(
    'zone, tariff_class, expected_category',
    [
        pytest.param('riga', 'econom', None, id='no_zone_in_zones'),
        pytest.param('minsk', 'econom', None, id='no_tariff_settings'),
        pytest.param('kiev', 'econom', None, id='no_categories'),
        pytest.param('moscow', 'econom', None, id='no_category'),
        pytest.param('moscow', 'buisness', DEFAULT_CATEGORY, id='exist'),
    ],
)
async def test_get_tariff_category(
        stq3_context: stq_context.Context,
        mock_server,
        zone,
        tariff_class,
        expected_category,
):
    memstorage.invalidate()

    category = await tariffs.get_tariff_category(
        client_tariffs=stq3_context.clients.taxi_tariffs,
        zone=zone,
        tariff_cls=tariff_class,
    )
    if expected_category is None:
        assert category is None
    else:
        assert category is not None
        assert category.serialize() == expected_category.serialize()
