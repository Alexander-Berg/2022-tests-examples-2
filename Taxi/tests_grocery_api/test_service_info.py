import datetime
import pytest

from . import common
from . import common_service_info
from . import const
from . import experiments
from . import tests_headers

# pylint: disable=too-many-lines

NOW = '2020-09-09T10:00:00+00:00'
LEGACY_DEPOT_ID = const.LEGACY_DEPOT_ID
DEPOT_ID = const.DEPOT_ID

DISABLE_SURGE_FOR_NEWBIES = pytest.mark.experiments3(
    name='grocery-p13n-surge',
    consumers=['grocery-surge-client/surge'],
    clauses=[
        {
            'title': 'No surge for newbies',
            'predicate': {
                'init': {
                    'arg_name': 'user_orders_completed',
                    'arg_type': 'int',
                    'value': 0,
                },
                'type': 'eq',
            },
            'value': {'surge': False},
        },
    ],
    default_value={'surge': True},
    is_config=True,
)

prepare_depots = common_service_info.prepare_depots
set_surge_conditions = common_service_info.set_surge_conditions


@pytest.fixture(name='umlaas_eta_not_responding')
def mock_umlaas_eta(mockserver):
    class Context:
        def __init__(self):
            self.times_called = 0
            self.umlaas_grocery_times_called = 0

    context = Context()

    @mockserver.json_handler(
        '/umlaas-grocery-eta/internal/umlaas-grocery-eta/v1/delivery-eta',
    )
    def _umlaas_grocery_eta(request):
        context.umlaas_grocery_times_called += 1

    return context


def _set_surge(
        experiments3,
        delivery_cost=None,
        min_eta=None,
        max_eta=None,
        minimum_order=None,
        next_cost=None,
        next_threshold=None,
        is_surge=None,
):
    value = {}

    if delivery_cost is not None:
        value['delivery_cost'] = str(delivery_cost)

    if min_eta is not None:
        value['min_eta_minutes'] = str(min_eta)

    if max_eta is not None:
        value['max_eta_minutes'] = str(max_eta)

    if minimum_order is not None:
        value['minimum_order'] = str(minimum_order)

    if next_cost is not None:
        value['next_delivery_cost'] = str(next_cost)

    if next_threshold is not None:
        value['next_delivery_threshold'] = str(next_threshold)

    if is_surge is not None:
        value['surge'] = is_surge

    experiments3.add_config(
        name='grocery-p13n-surge',
        consumers=['grocery-surge-client/surge'],
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': value,
            },
        ],
    )


@pytest.mark.now(NOW)
@pytest.mark.experiments3(filename='surge_exp_delivery.json')
@pytest.mark.parametrize('handler', ['v1', 'v2'])
async def test_service_info_default_surge_fallback(
        taxi_grocery_api,
        mockserver,
        overlord_catalog,
        grocery_surge,
        grocery_depots,
        umlaas_eta_not_responding,
        handler,
):
    """ Fallback to old flow if p13n is not responding
    /service-info should return default promise from config
    even if plotva-ml-eats is not responding """

    location = [0, 0]
    prepare_depots(overlord_catalog, location, grocery_depots)
    timestamp = NOW

    grocery_surge.add_record(
        legacy_depot_id=LEGACY_DEPOT_ID,
        timestamp=timestamp,
        pipeline='calc_surge_grocery_v1',
        load_level=0,
    )

    await taxi_grocery_api.invalidate_caches()

    json = {'position': {'location': location}}
    headers = {'Accept-Language': 'ru'}
    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/{handler}/service-info', json=json, headers=headers,
    )
    assert response.status_code == 200
    assert umlaas_eta_not_responding.umlaas_grocery_times_called == 1
    response_json = response.json()
    assert response_json['currency'] == 'RUB'
    assert response_json['currency_sign'] == '₽'
    assert response_json['depot_id'] == LEGACY_DEPOT_ID

    service_metadata = response_json['service_metadata']
    service_metadata.pop('availability_time', None)
    assert service_metadata == {
        'delivery_type': 'pedestrian',
        'legal_entities': [
            {
                'description': (
                    'Исполнитель (продавец): ООО "СУБМАРИНЕР", '
                    '125315, проспект Ленинградский, дом 80, '
                    'корпус 21, эт. технический пом. I ком. 2, '
                    'ИНН 7718231590, рег.номер '
                    '1157746538641.<br>Режим работы магазина: '
                    'с 0:00 до 24:00<br>Яндекс.Лавка – часть '
                    'информационного сервиса Яндекс.Еда. '
                    'Подробнее – <a '
                    'href="https://yandex.ru/legal/termsofuse_eda/"> '
                    'https://yandex.ru/legal/termsofuse_eda/.</a>'
                ),
                'type': 'service_partner',
            },
        ],
        'links': [],
        'service_name': 'Яндекс.Лавка',
        'status': 'open',
        'switch_time': timestamp,
        'traits': [
            {'type': 'eta', 'value': '3-7 мин.'},
            {'type': 'address', 'value': 'depot address'},
        ],
    }

    assert response_json['pricing_conditions'] == {
        'service_fee_template': '10 $SIGN$$CURRENCY$',
        'minimal_cart_price_value': '0',
        'minimal_cart_price_template': '0 $SIGN$$CURRENCY$',
    }
    assert response_json['is_surge'] is False


@pytest.mark.parametrize('handler', ['v1', 'v2'])
@pytest.mark.parametrize(
    'send_offer_id, offer_matched',
    [(True, False), (True, True), (False, None)],
)
async def test_service_info_uses_offer_on_demand(
        taxi_grocery_api,
        overlord_catalog,
        offers,
        grocery_depots,
        now,
        send_offer_id,
        offer_matched,
        handler,
):
    """ Если offer_id есть в запросе, то вызывается offers:/match-create, и
    результат используется для взятия суржа, а offer_id пробрасывается в ответ.
    Если offer_id отсутствует в запросе, то для суржа используется текущее
    время, а с офферами никакой работы не производится. """

    location = [0, 0]
    prepare_depots(overlord_catalog, location, grocery_depots)

    offer_id = 'some-offer-id'
    if offer_matched:
        offers.add_offer_elementwise(offer_id, now, DEPOT_ID, location)

    json = {'position': {'location': location}}
    if send_offer_id:
        json['offer_id'] = offer_id
    headers = {'Accept-Language': 'ru'}
    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/{handler}/service-info', json=json, headers=headers,
    )
    assert response.status_code == 200
    if send_offer_id:
        assert offers.match_create_times_called == 1
        if offer_matched:
            assert response.json()['offer_id'] == offer_id
        else:
            assert response.json()['offer_id'] != offer_id
    else:
        assert offers.match_create_times_called == 0
        assert 'offer_id' not in response.json()


@pytest.mark.now(NOW)
@pytest.mark.experiments3(filename='surge_exp_delivery.json')
@pytest.mark.parametrize('handler', ['v1', 'v2'])
async def test_service_info_offer_additional_info_check_logged(
        taxi_grocery_api,
        mockserver,
        overlord_catalog,
        grocery_surge,
        offers,
        grocery_depots,
        testpoint,
        handler,
):
    """ /service-info should save additional info for new offer_id """

    location = [0, 0]
    location_str = str(float(location[0])) + ';' + str(float(location[1]))
    prepare_depots(overlord_catalog, location, grocery_depots)

    timestamp = NOW
    grocery_surge.add_record(
        legacy_depot_id=LEGACY_DEPOT_ID,
        timestamp=timestamp,
        pipeline='calc_surge_grocery_v1',
        load_level=4,
    )

    offer_id = 'some-offer-id'
    offers.add_offer_elementwise(
        offer_id, datetime.datetime.fromisoformat(NOW), DEPOT_ID, location,
    )

    await taxi_grocery_api.invalidate_caches()

    user_id = '123456abcd'

    @testpoint('yt_offer_additional_info')
    def yt_offer_additional_info(offer_additional_info):
        assert offer_additional_info['offer_id'] == offer_id
        assert offer_additional_info['version'] == 1
        assert offer_additional_info['doc'] == {
            'active_zone': 'foot',
            'foot': {
                'delivery_cost': '199',
                'is_surge': True,
                'is_manual': False,
                'max_eta_minutes': '23',
                'min_eta_minutes': '12',
                'next_delivery_cost': '0',
                'next_delivery_threshold': '1300',
                'surge_minimum_order': '0',
                'delivery_conditions': [
                    {'order_cost': '0', 'delivery_cost': '199'},
                    {'order_cost': '1300', 'delivery_cost': '0'},
                ],
            },
        }
        assert offer_additional_info['params'] == {
            'lat_lon': location_str,
            'depot_id': LEGACY_DEPOT_ID,
        }
        assert offer_additional_info['user_id'] == user_id

    headers = {'X-YaTaxi-UserId': user_id}
    json = {'position': {'location': location}, 'offer_id': offer_id}
    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/{handler}/service-info', json=json, headers=headers,
    )
    assert response.status_code == 200
    assert yt_offer_additional_info.times_called == 1


@pytest.mark.now(NOW)
@pytest.mark.experiments3(filename='surge_exp_delivery.json')
@pytest.mark.parametrize('handler', ['v1', 'v2'])
async def test_service_info_uses_grocery_surge_and_ml_eats(
        taxi_grocery_api,
        mockserver,
        overlord_catalog,
        grocery_surge,
        grocery_depots,
        umlaas_grocery_eta,
        handler,
):
    """ /service-info should return response, constructed by
    grocery-surge and plotva-ml-eats responses """

    location = [0, 0]
    prepare_depots(overlord_catalog, location, grocery_depots)

    grocery_surge.add_record(
        legacy_depot_id=LEGACY_DEPOT_ID,
        timestamp=NOW,
        pipeline='calc_surge_grocery_v1',
        load_level=10,
    )

    await taxi_grocery_api.invalidate_caches()

    eta_min = 100
    eta_max = 500

    umlaas_grocery_eta.add_prediction(eta_min=eta_min, eta_max=eta_max)

    json = {'position': {'location': location}}
    headers = {'Accept-Language': 'ru'}
    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/{handler}/service-info', json=json, headers=headers,
    )
    assert response.status_code == 200
    assert umlaas_grocery_eta.umlaas_grocery_eta_times_called == 1
    result = response.json()
    assert result['is_surge']
    assert (
        result['pricing_conditions']['service_fee_template']
        == '199 $SIGN$$CURRENCY$'
    )
    assert (
        result['service_metadata']['traits'][0]['value']
        == f'{eta_min}-{eta_max} мин.'
    )


@pytest.mark.now(NOW)
@pytest.mark.parametrize('handler', ['v1', 'v2'])
@pytest.mark.parametrize('state', ['open', 'closed', 'coming_soon'])
async def test_service_info_basic(
        taxi_grocery_api,
        overlord_catalog,
        grocery_surge,
        grocery_p13n,
        grocery_depots,
        umlaas_eta_not_responding,
        state,
        handler,
):
    """ service info basic test without any surge or delivery conditions """

    location = const.LOCATION
    switch_time = NOW

    prepare_depots(
        overlord_catalog,
        location,
        grocery_depots,
        state,
        switch_time=switch_time,
    )

    extra_metadata = {}
    if state != 'open':
        # legacy field, frontend uses it to determine
        # if depot is closed
        extra_metadata['available_at'] = switch_time

    if state != 'coming_soon':
        # мок оверлорда в качестве availability_time возвращает значения
        # switch_time; ручка service-info его просто пробрасывает
        extra_metadata['availability_time'] = {
            'from': switch_time,
            'to': switch_time,
        }

    grocery_surge.add_record(
        legacy_depot_id=LEGACY_DEPOT_ID,
        timestamp=switch_time,
        pipeline='calc_surge_grocery_v1',
        load_level=0,
    )

    await taxi_grocery_api.invalidate_caches()

    json = {'position': {'location': location}}
    headers = {'Accept-Language': 'ru'}
    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/{handler}/service-info', json=json, headers=headers,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['currency'] == 'RUB'
    assert response_json['currency_sign'] == '₽'
    assert response_json['depot_id'] == LEGACY_DEPOT_ID
    assert response_json['service_metadata'] == {
        'delivery_type': 'pedestrian',
        'legal_entities': [
            {
                'description': (
                    'Исполнитель (продавец): ООО "СУБМАРИНЕР", '
                    '125315, проспект Ленинградский, дом 80, '
                    'корпус 21, эт. технический пом. I ком. 2, '
                    'ИНН 7718231590, рег.номер '
                    '1157746538641.<br>Режим работы магазина: '
                    'с 0:00 до 24:00<br>Яндекс.Лавка – часть '
                    'информационного сервиса Яндекс.Еда. '
                    'Подробнее – <a '
                    'href="https://yandex.ru/legal/termsofuse_eda/"> '
                    'https://yandex.ru/legal/termsofuse_eda/.</a>'
                ),
                'type': 'service_partner',
            },
        ],
        'links': [],
        'service_name': 'Яндекс.Лавка',
        'status': state,
        'switch_time': switch_time,
        'traits': [{'type': 'address', 'value': 'depot address'}],
        **extra_metadata,
    }

    assert response_json['pricing_conditions'] == {
        'service_fee_template': '0 $SIGN$$CURRENCY$',
        'minimal_cart_price_template': '0 $SIGN$$CURRENCY$',
        'minimal_cart_price_value': '0',
    }
    assert response_json['is_surge'] is False

    assert grocery_p13n.cashback_info_times_called == 0


@pytest.mark.now(NOW)
@pytest.mark.parametrize('handler', ['v1', 'v2'])
async def test_service_info_next_zone(
        taxi_grocery_api,
        overlord_catalog,
        grocery_surge,
        grocery_depots,
        umlaas_eta_not_responding,
        handler,
):
    location = [0, 0]
    external_depot_id = '100500'
    switch_time = NOW

    prepare_depots(
        overlord_catalog,
        location,
        grocery_depots,
        legacy_depot_id=external_depot_id,
        switch_time=switch_time,
    )
    overlord_catalog.add_next_location(
        location=location,
        legacy_depot_id=external_depot_id,
        switch_time=switch_time,
    )

    grocery_surge.add_record(
        legacy_depot_id=external_depot_id,
        timestamp=switch_time,
        pipeline='calc_surge_grocery_v1',
        load_level=0,
    )

    json = {'position': {'location': location}}
    headers = {'Accept-Language': 'ru'}
    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/{handler}/service-info', json=json, headers=headers,
    )
    assert response.status_code == 200
    response_json = response.json()

    next_zone_info = response_json['service_metadata']['next_zone_info']
    assert next_zone_info == {
        'depot_id': external_depot_id,
        'switch_to_zone_time': switch_time,
    }


@pytest.mark.now(NOW)
@pytest.mark.parametrize('handler', ['v1', 'v2'])
async def test_service_info_zone_24h(
        taxi_grocery_api,
        overlord_catalog,
        grocery_surge,
        grocery_depots,
        umlaas_eta_not_responding,
        handler,
):
    """Check that for a 24-hour depot zone (with a fake switch time) switch_time
     is not returned"""

    location = [0, 0]
    external_depot_id = '100500'
    switch_time = NOW

    prepare_depots(
        overlord_catalog,
        location,
        grocery_depots,
        legacy_depot_id=external_depot_id,
        switch_time=switch_time,
        all_day=True,
    )

    grocery_surge.add_record(
        legacy_depot_id=external_depot_id,
        timestamp=switch_time,
        pipeline='calc_surge_grocery_v1',
        load_level=0,
    )

    json = {'position': {'location': location}}
    headers = {'Accept-Language': 'ru'}
    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/{handler}/service-info', json=json, headers=headers,
    )
    assert response.status_code == 200
    body = response.json()

    service_metadata = body['service_metadata']
    assert service_metadata['status'] == 'open'
    assert 'switch_time' not in service_metadata.keys()

    assert body['l10n']['working_hours_text'] == 'Лавка работает круглосуточно'


@pytest.mark.now(NOW)
@pytest.mark.parametrize('handler', ['v1', 'v2'])
async def test_service_info_working_hours_from_to(
        taxi_grocery_api,
        overlord_catalog,
        grocery_surge,
        grocery_depots,
        umlaas_eta_not_responding,
        handler,
):
    location = [0, 0]
    external_depot_id = '100500'
    switch_time = NOW

    prepare_depots(
        overlord_catalog,
        location,
        grocery_depots,
        state='closed',
        legacy_depot_id=external_depot_id,
        switch_time=switch_time,
    )
    overlord_catalog.add_next_location(
        location=location,
        legacy_depot_id=external_depot_id,
        switch_time=switch_time,
    )

    grocery_surge.add_record(
        legacy_depot_id=external_depot_id,
        timestamp=switch_time,
        pipeline='calc_surge_grocery_v1',
        load_level=0,
    )

    json = {'position': {'location': location}}
    headers = {'Accept-Language': 'ru'}
    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/{handler}/service-info', json=json, headers=headers,
    )
    assert response.status_code == 200
    body = response.json()

    assert body['l10n']['working_hours_text'] == 'Работаем с 9:00 до 20:00'

    service_metadata = body['service_metadata']

    # мок depot-resolve возвращает в качестве availability_time значения
    # switch_time; ручка service-info просто его пробрасывает
    assert service_metadata['availability_time'] == {
        'from': switch_time,
        'to': switch_time,
    }


def _format_float_with_significant(value: float) -> str:
    if value == 0:
        return '0'
    str_val = str(value)
    while str_val[-1] == '0':
        str_val = str_val[:-1]
    if str_val[-1] == '.':
        str_val = str_val[:-1]
    return str_val


@pytest.mark.now(NOW)
@pytest.mark.parametrize('handler', ['v1', 'v2'])
@pytest.mark.parametrize(
    'delivery_conditions',
    [
        [{'order_cost': '0', 'delivery_cost': '0'}],
        [
            {'order_cost': '0', 'delivery_cost': '10'},
            {'order_cost': '25', 'delivery_cost': '5'},
            {'order_cost': '50', 'delivery_cost': '0'},
        ],
        [
            {'order_cost': '0', 'delivery_cost': '10'},
            {'order_cost': '50', 'delivery_cost': '0'},
        ],
    ],
)
@pytest.mark.parametrize('locale', ['ru', 'en', None])
@pytest.mark.parametrize('fallback_locale', ['ru', 'en'])
@pytest.mark.translations(
    overlord_catalog={
        'delivery_min_cost_threshold_text': {
            'ru': 'При заказе до %(value)s',
            'en': 'For orders under %(value)s',
        },
        'delivery_text_cost_range': {
            'ru': 'Доставка %(value)s',
            'en': 'Delivery %(value)s',
        },
        'delivery_cost_range': {'ru': '%(value)s', 'en': '%(value)s'},
        'finish': {
            'ru': 'А это всегда приятно',
            'en': 'It feels good to save',
        },
    },
    tariff={
        'currency_with_sign.default': {
            'en': '$SIGN$$VALUE$$CURRENCY$',
            'ru': '$VALUE$ $SIGN$$CURRENCY$',
        },
    },
)
async def test_service_info_paid_delivery(
        experiments3,
        taxi_config,
        taxi_grocery_api,
        overlord_catalog,
        grocery_surge,
        grocery_depots,
        delivery_conditions,
        locale,
        fallback_locale,
        handler,
):
    """ get service info with delivery conditions """

    taxi_config.set(
        GROCERY_LOCALIZATION_FALLBACK_LANGUAGES={
            '__default__': fallback_locale,
        },
    )

    location = [0, 0]
    prepare_depots(overlord_catalog, location, grocery_depots)

    delivery_cost = float(delivery_conditions[0]['delivery_cost'])
    delivery_cost_text = _format_float_with_significant(delivery_cost)
    order_cost = float(delivery_conditions[0]['order_cost'])
    order_cost_text = _format_float_with_significant(order_cost)
    set_surge_conditions(experiments3, delivery_conditions=delivery_conditions)

    grocery_surge.add_record(
        legacy_depot_id=LEGACY_DEPOT_ID,
        timestamp=NOW,
        pipeline='calc_surge_grocery_v1',
        load_level=0,
    )

    await taxi_grocery_api.invalidate_caches()

    json = {'position': {'location': location}}
    headers = {}
    if locale:
        headers['Accept-Language'] = locale
    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/{handler}/service-info', json=json, headers=headers,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['is_surge'] is False

    if locale is None:
        locale = fallback_locale

    rover_tracking_l10n = {
        'ru': {
            'rover_banner_tracking_title': 'Ваш курьер — Ровер',
            'rover_banner_tracking_message': 'Ааа, и что с ним делать?',
            'rover_banner_tracking_url': 'https://lavka.yandex/rover',
        },
        'en': {
            'rover_banner_tracking_title': 'Meet your courier: Rover!',
            'rover_banner_tracking_message': 'Ok... What do I need to do?',
            'rover_banner_tracking_url': 'https://deli.store/isr/rover/en',
        },
    }
    delivery_info = {
        'ru': {
            'delivery_max_cost_threshold_value': 'Бесплатно!',
            'delivery_min_order': (
                f'Заказ от {order_cost_text} $SIGN$$CURRENCY$'
            ),
            'paid_delivery_button_text': 'Поехали!',
            'paid_delivery_subtitle': 'Теперь и за деньги!',
            'paid_delivery_title': 'Платная доставка!',
        },
        'en': {
            'delivery_max_cost_threshold_value': 'FREE',
            'delivery_min_order': (
                f'Order from $SIGN${order_cost_text}$CURRENCY$'
            ),
            'paid_delivery_button_text': 'Go!',
            'paid_delivery_subtitle': 'Now not free!',
            'paid_delivery_title': 'Paid delivery',
        },
    }

    additional_delivery_info = {}
    if delivery_cost > 0:
        next_threshold = int(delivery_conditions[1]['order_cost'])
        additional_delivery_info = {
            'ru': {
                'delivery_cost_range': (
                    f'0-{delivery_cost_text} $SIGN$$CURRENCY$'
                ),
                'delivery_text_cost_range': (
                    f'Доставка 0-{delivery_cost_text} $SIGN$$CURRENCY$'
                ),
                'delivery_cost': 'Доставка 10 $SIGN$$CURRENCY$',
                'delivery_min_cost_threshold_value': (
                    f'{delivery_cost_text} $SIGN$$CURRENCY$'
                ),
                'delivery_max_cost_threshold_text': (
                    f'При заказе от {next_threshold} '
                    f'$SIGN$$CURRENCY$ доставка '
                ),
                'delivery_min_cost_threshold_text': (
                    f'При заказе до {next_threshold} $SIGN$$CURRENCY$'
                ),
                'till_free_delivery': 'До бесплатной 50 $SIGN$$CURRENCY$',
                'till_next_delivery': (
                    'Еще 25 $SIGN$$CURRENCY$ до доставки за 5 $SIGN$$CURRENCY$'
                ),
                'delivery_conditions': [
                    {
                        'delivery_cost_template': (
                            'Доставка 10 $SIGN$$CURRENCY$'
                        ),
                        'order_cost_template': (
                            'При заказе до 25 $SIGN$$CURRENCY$'
                        ),
                    },
                    {
                        'delivery_cost_template': (
                            'Доставка 5 $SIGN$$CURRENCY$'
                        ),
                        'order_cost_template': (
                            'При заказе от 25 $SIGN$$CURRENCY$'
                            ' и до 50 $SIGN$$CURRENCY$'
                        ),
                    },
                    {
                        'delivery_cost_template': (
                            'Доставка 0 $SIGN$$CURRENCY$'
                        ),
                        'order_cost_template': (
                            'При заказе более 50 $SIGN$$CURRENCY$'
                        ),
                    },
                ],
            },
            'en': {
                'delivery_cost_range': (
                    f'$SIGN$0-{delivery_cost_text}$CURRENCY$'
                ),
                'delivery_text_cost_range': (
                    f'Delivery $SIGN$0-{delivery_cost_text}$CURRENCY$'
                ),
                'delivery_cost': 'Delivery: $SIGN$10$CURRENCY$',
                'delivery_min_cost_threshold_value': (
                    f'$SIGN${delivery_cost_text}$CURRENCY$'
                ),
                'delivery_max_cost_threshold_text': (
                    f'$SIGN${next_threshold}$CURRENCY$ delivery'
                ),
                'delivery_min_cost_threshold_text': (
                    f'For orders under $SIGN${next_threshold}$CURRENCY$'
                ),
                'till_free_delivery': 'Till free: $SIGN$50$CURRENCY$',
                'till_next_delivery': (
                    'Add $SIGN$25$CURRENCY$ for $SIGN$5$CURRENCY$ delivery'
                ),
                'delivery_conditions': [
                    {
                        'delivery_cost_template': (
                            'Delivery: $SIGN$10$CURRENCY$'
                        ),
                        'order_cost_template': (
                            'For orders under $SIGN$25$CURRENCY$'
                        ),
                    },
                    {
                        'delivery_cost_template': (
                            'Delivery: $SIGN$5$CURRENCY$'
                        ),
                        'order_cost_template': (
                            'For orders from $SIGN$25$CURRENCY$'
                            ' to $SIGN$50$CURRENCY$'
                        ),
                    },
                    {
                        'delivery_cost_template': 'Free delivery',
                        'order_cost_template': (
                            'For orders over $SIGN$50$CURRENCY$'
                        ),
                    },
                ],
            },
        }
    else:
        additional_delivery_info = {
            'ru': {
                'delivery_text_cost_range': 'Доставка 0 $SIGN$$CURRENCY$',
                'delivery_cost': 'Доставка 0 $SIGN$$CURRENCY$',
            },
            'en': {
                'delivery_text_cost_range': 'Free delivery',
                'delivery_cost': 'Free delivery',
            },
        }

    delivery_info[locale].update(**additional_delivery_info[locale])

    pricing_conditions = {
        'ru': {
            'service_fee_template': f'{delivery_cost_text} $SIGN$$CURRENCY$',
            'minimal_cart_price_template': '0 $SIGN$$CURRENCY$',
            'minimal_cart_price_value': '0',
        },
        'en': {
            'service_fee_template': f'$SIGN${delivery_cost_text}$CURRENCY$',
            'minimal_cart_price_template': '$SIGN$0$CURRENCY$',
            'minimal_cart_price_value': '0',
        },
    }
    price_template_l10n = {
        'ru': {'price_template': '$VALUE$ $SIGN$$CURRENCY$'},
        'en': {'price_template': '$SIGN$$VALUE$$CURRENCY$'},
    }

    response_json['l10n'].pop('working_hours_text', None)
    if len(delivery_conditions) == 2:
        # next delivery is free
        assert (
            response_json['l10n']['till_next_delivery']
            == additional_delivery_info[locale]['till_free_delivery']
        )
    else:
        assert response_json['l10n'] == {
            **delivery_info[locale],
            **rover_tracking_l10n[locale],
            **price_template_l10n[locale],
        }
        assert (
            response_json['pricing_conditions'] == pricing_conditions[locale]
        )


# Проверяем, что service-info правильно отрабатывает,
# когда последняя доставка не бесплатная, а также:
# возвращает till_next_delivery, только если есть доставка дешевле;
# till_free_delivery не должно приходить, если бесплатной нет.
@pytest.mark.now(NOW)
@pytest.mark.parametrize('handler', ['v1', 'v2'])
@pytest.mark.parametrize(
    'delivery_conditions',
    [
        [{'order_cost': '0', 'delivery_cost': '50'}],
        [
            {'order_cost': '0', 'delivery_cost': '10'},
            {'order_cost': '25', 'delivery_cost': '5'},
        ],
    ],
)
@pytest.mark.translations(
    overlord_catalog={
        'delivery_text_cost_range': {
            'ru': 'Доставка %(value)s',
            'en': 'Delivery %(value)s',
        },
        'delivery_cost_range': {'ru': '%(value)s', 'en': '%(value)s'},
    },
    tariff={'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'}},
)
async def test_service_info_always_paid_delivery(
        experiments3,
        taxi_grocery_api,
        overlord_catalog,
        grocery_surge,
        grocery_depots,
        delivery_conditions,
        handler,
):
    """ Check that service-info logic works properly when last delivery
     threshold has paid delivery """

    location = [0, 0]
    locale = 'ru'
    prepare_depots(overlord_catalog, location, grocery_depots)

    set_surge_conditions(experiments3, delivery_conditions=delivery_conditions)

    grocery_surge.add_record(
        legacy_depot_id=LEGACY_DEPOT_ID,
        timestamp=NOW,
        pipeline='calc_surge_grocery_v1',
        load_level=0,
    )

    await taxi_grocery_api.invalidate_caches()

    json = {'position': {'location': location}}
    headers = {}
    headers['Accept-Language'] = locale
    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/{handler}/service-info', json=json, headers=headers,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['is_surge'] is False

    if len(delivery_conditions) == 2:
        delivery_info = {
            'till_next_delivery': (
                'Еще 25 $SIGN$$CURRENCY$ до доставки за 5 $SIGN$$CURRENCY$'
            ),
            'delivery_conditions': [
                {
                    'delivery_cost_template': 'Доставка 10 $SIGN$$CURRENCY$',
                    'order_cost_template': 'При заказе до 25 $SIGN$$CURRENCY$',
                },
                {
                    'delivery_cost_template': 'Доставка 5 $SIGN$$CURRENCY$',
                    'order_cost_template': (
                        'При заказе более 25 $SIGN$$CURRENCY$'
                    ),
                },
            ],
        }
    else:
        delivery_info = {
            'delivery_conditions': [
                {
                    'delivery_cost_template': 'Доставка 50 $SIGN$$CURRENCY$',
                    'order_cost_template': (
                        'При заказе более 0 $SIGN$$CURRENCY$'
                    ),
                },
            ],
        }
    assert 'till_free_delivery' not in response_json['l10n']
    if len(delivery_conditions) == 2:
        assert (
            response_json['l10n']['till_next_delivery']
            == delivery_info['till_next_delivery']
        )
        assert (
            response_json['l10n']['delivery_conditions']
            == delivery_info['delivery_conditions']
        )
    else:
        assert 'till_next_delivery' not in response_json['l10n']
        assert (
            response_json['l10n']['delivery_conditions']
            == delivery_info['delivery_conditions']
        )
    delivery_max_cost = delivery_conditions[0]['delivery_cost']
    delivery_min_cost = delivery_conditions[-1]['delivery_cost']
    if len(delivery_conditions) == 1:
        assert (
            response_json['l10n']['delivery_cost_range']
            == f'{delivery_max_cost} $SIGN$$CURRENCY$'
        )
        assert (
            response_json['l10n']['delivery_text_cost_range']
            == f'Доставка {delivery_max_cost} $SIGN$$CURRENCY$'
        )
    else:
        assert (
            response_json['l10n']['delivery_cost_range']
            == f'{delivery_min_cost}-{delivery_max_cost} $SIGN$$CURRENCY$'
        )
        assert (
            response_json['l10n']['delivery_text_cost_range']
            == f'Доставка {delivery_min_cost}-'
            f'{delivery_max_cost} $SIGN$$CURRENCY$'
        )


@pytest.mark.now(NOW)
@pytest.mark.parametrize('handler', ['v1', 'v2'])
@pytest.mark.parametrize('is_surge', [True, False])
async def test_service_info_with_surge(
        experiments3,
        taxi_grocery_api,
        overlord_catalog,
        grocery_surge,
        grocery_depots,
        is_surge,
        handler,
):
    """ get service info with surge and eta """
    location = [0, 0]
    prepare_depots(overlord_catalog, location, grocery_depots)

    grocery_surge.add_record(
        legacy_depot_id=LEGACY_DEPOT_ID,
        timestamp=NOW,
        pipeline='calc_surge_grocery_v1',
        load_level=0,
    )

    eta_min = 100
    eta_max = 500

    _set_surge(
        experiments3, min_eta=eta_min, max_eta=eta_max, is_surge=is_surge,
    )

    await taxi_grocery_api.invalidate_caches()

    json = {'position': {'location': location}}
    headers = {'Accept-Language': 'ru'}
    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/{handler}/service-info', json=json, headers=headers,
    )
    assert response.status_code == 200
    response_json = response.json()

    assert response_json['is_surge'] == is_surge
    eta_found = False
    for trait in response_json['service_metadata']['traits']:
        if trait['type'] == 'eta':
            eta_found = True
            assert trait['value'] == f'{eta_min}-{eta_max} мин.'
    assert eta_found


@pytest.mark.now(NOW)
@pytest.mark.parametrize('handler', ['v1', 'v2'])
async def test_service_info_no_delivery_info(
        experiments3,
        taxi_grocery_api,
        overlord_catalog,
        grocery_surge,
        grocery_depots,
        handler,
):
    """ service info with minimum_order offer """
    location = [0, 0]
    prepare_depots(overlord_catalog, location, grocery_depots)

    grocery_surge.add_record(
        legacy_depot_id=LEGACY_DEPOT_ID,
        timestamp=NOW,
        pipeline='calc_surge_grocery_v1',
        load_level=0,
    )

    minimum_order = 1500

    _set_surge(experiments3, minimum_order=minimum_order)

    await taxi_grocery_api.invalidate_caches()

    json = {'position': {'location': location}}
    headers = {'Accept-Language': 'ru'}
    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/{handler}/service-info', json=json, headers=headers,
    )
    assert response.status_code == 200

    rover_tracking_l10n = {
        'rover_banner_tracking_title': 'Ваш курьер — Ровер',
        'rover_banner_tracking_message': 'Ааа, и что с ним делать?',
        'rover_banner_tracking_url': 'https://lavka.yandex/rover',
    }

    response_json = response.json()
    response_json['l10n'].pop('working_hours_text', None)
    assert response_json['l10n'] == {
        'delivery_min_cart_subtitle': (
            'Поэтому можно сделать заказ только '
            f'от {minimum_order} $SIGN$$CURRENCY$'
        ),
        'delivery_min_order': 'Заказ от 1500 $SIGN$$CURRENCY$',
        'delivery_min_cart_title': 'Сейчас слишком много заказов',
        'delivery_min_cart_button_text': 'Понятно!',
        'price_template': '$VALUE$ $SIGN$$CURRENCY$',
        **rover_tracking_l10n,
    }
    assert response_json['pricing_conditions'] == {
        'service_fee_template': '0 $SIGN$$CURRENCY$',
        'minimal_cart_price_value': '1500',
        'minimal_cart_price_template': f'{minimum_order} $SIGN$$CURRENCY$',
    }


@pytest.mark.now(NOW)
@pytest.mark.parametrize('handler', ['v1', 'v2'])
@pytest.mark.experiments3(
    name='lavka_rover_delivery_zone',
    consumers=['grocery-cart/order-cycle', 'grocery-api/modes'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'coordinates': [
                    [[[-1.0, -1.0], [-1.0, 1.0], [1.0, 1.1], [1.0, -1.1]]],
                ],
            },
        },
    ],
    is_config=True,
)
@pytest.mark.experiments3(
    name='grocery_rover_compensation_params',
    consumers=['grocery-cart/order-cycle', 'grocery-api/service-info'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'value': '300', 'is_percent': False, 'is_plus': False},
        },
    ],
    is_config=True,
)
@pytest.mark.experiments3(
    name='lavka_force_rover_zone',
    consumers=['grocery-cart/order-cycle', 'grocery-api/modes'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'coordinates': [
                    [[[0.1, 0.1], [0.1, 1.0], [1.0, 1.1], [1.0, 0.1]]],
                ],
            },
        },
    ],
    is_config=True,
)
@pytest.mark.parametrize(
    'location',
    [
        pytest.param([0, 0], id='hit rover delivery zone'),
        pytest.param([0.5, 0.5], id='force rover delivery zone'),
        pytest.param([2, 2], id='missed rover delivery zone'),
    ],
)
@pytest.mark.parametrize('locale', ['ru', 'en', None])
@pytest.mark.parametrize('fallback_locale', ['ru', 'en'])
@pytest.mark.translations(
    overlord_catalog={
        'delivery_min_cart_subtitle': {
            'en': 'You can order from %(value)s',
            'ru': 'Поэтому можно сделать заказ только от %(value)s',
        },
        'delivery_min_cart_title': {
            'en': 'There are too many orders right now',
            'ru': 'Сейчас слишком много заказов',
        },
        'delivery_min_cart_button_text': {'en': 'Got it!', 'ru': 'Понятно!'},
        'delivery_min_order': {
            'en': 'Order from %(value)s',
            'ru': 'Заказ от %(value)s',
        },
        'rover_banner_main_page': {
            'en': 'What a cutie!',
            'ru': 'Ну вы посмотрите на этого красавца',
        },
        'rover_banner_main_page_force': {
            'en': 'ROVER_FORCED',
            'ru': 'Невозможно отказать!',
        },
        'rover_modal_title': {
            'en': 'Powerful hands! Get %(value)s bucks!',
            'ru': 'Как мощны его лапищи. Cкидка %(value)s деняк.',
        },
        'rover_modal_title_force': {
            'en': 'You can\'t run. And from %(value)s bucks discount',
            'ru': 'Тебе не скрыться. И от скидки в %(value)s',
        },
        'rover_modal_body': {
            'en': 'Will bring safely and discount %(value)s bucks',
            'ru': (
                'Привезёт вам товары и не отдаст никому другому и скидка'
                ' %(value)s деняк'
            ),
        },
        'rover_modal_body_force': {
            'en': (
                'Today rover serves you. Tomorrow you will serve rover!'
                ' Get %(value)s discount'
            ),
            'ru': (
                'Сегодня робот прислуживает тебе, а завтра -- ты ему!'
                ' Cкидка %(value)s деняк'
            ),
        },
        'rover_modal_button_more_info': {
            'en': 'Know everything!',
            'ru': 'Хочу знать о нём всё!',
        },
        'rover_modal_button_close': {
            'en': 'It is close',
            'ru': 'Восстание машин уже близко :(',
        },
        'rover_modal_link': {'en': 'yandex.com', 'ru': 'yandex.ru'},
    },
    tariff={
        'currency_with_sign.default': {
            'en': '$SIGN$$VALUE$$CURRENCY$',
            'ru': '$VALUE$ $SIGN$$CURRENCY$',
        },
    },
)
async def test_service_info_rover(
        experiments3,
        taxi_config,
        taxi_grocery_api,
        overlord_catalog,
        grocery_depots,
        location,
        locale,
        fallback_locale,
        grocery_surge,
        handler,
):
    """ service info show rover banner in rover delivery zone """
    taxi_config.set(
        GROCERY_LOCALIZATION_FALLBACK_LANGUAGES={
            '__default__': fallback_locale,
        },
    )

    prepare_depots(overlord_catalog, location, grocery_depots)
    grocery_surge.add_record(
        legacy_depot_id=LEGACY_DEPOT_ID,
        timestamp=NOW,
        pipeline='calc_surge_grocery_v1',
        load_level=0,
    )

    minimum_order = 1500
    _set_surge(experiments3, minimum_order=minimum_order)

    await taxi_grocery_api.invalidate_caches()

    json = {'position': {'location': location}}

    headers = {}
    if locale:
        headers['Accept-Language'] = locale
    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/{handler}/service-info', json=json, headers=headers,
    )
    assert response.status_code == 200
    response_json = response.json()

    if locale is None:
        locale = fallback_locale

    rover_tracking_l10n = {
        'ru': {
            'rover_banner_tracking_title': 'Ваш курьер — Ровер',
            'rover_banner_tracking_message': 'Ааа, и что с ним делать?',
            'rover_banner_tracking_url': 'https://lavka.yandex/rover',
        },
        'en': {
            'rover_banner_tracking_title': 'Meet your courier: Rover!',
            'rover_banner_tracking_message': 'Ok... What do I need to do?',
            'rover_banner_tracking_url': 'https://deli.store/isr/rover/en',
        },
    }

    delivery_info = {
        'ru': {
            'delivery_min_cart_subtitle': (
                'Поэтому можно сделать заказ только '
                'от 1500 $SIGN$$CURRENCY$'
            ),
            'delivery_min_cart_title': 'Сейчас слишком много заказов',
            'delivery_min_order': 'Заказ от 1500 $SIGN$$CURRENCY$',
            'delivery_min_cart_button_text': 'Понятно!',
        },
        'en': {
            'delivery_min_cart_subtitle': (
                'You can order from $SIGN$1,500$CURRENCY$'
            ),
            'delivery_min_cart_title': 'There are too many orders right now',
            'delivery_min_order': 'Order from $SIGN$1,500$CURRENCY$',
            'delivery_min_cart_button_text': 'Got it!',
        },
    }
    rover_info = {
        'ru': {
            'rover_banner_main_page': 'Ну вы посмотрите на этого красавца',
            'rover_modal_title': (
                'Как мощны его лапищи. Cкидка 300 $SIGN$$CURRENCY$ деняк.'
            ),
            'rover_modal_body': (
                'Привезёт вам товары и не отдаст никому другому и скидка '
                '300 $SIGN$$CURRENCY$ деняк'
            ),
            'rover_modal_button_more_info': 'Хочу знать о нём всё!',
            'rover_modal_button_close': 'Восстание машин уже близко :(',
            'rover_modal_link': 'yandex.ru',
        },
        'en': {
            'rover_banner_main_page': 'What a cutie!',
            'rover_modal_title': (
                'Powerful hands! Get $SIGN$300$CURRENCY$ bucks!'
            ),
            'rover_modal_body': (
                'Will bring safely and discount $SIGN$300$CURRENCY$ bucks'
            ),
            'rover_modal_button_more_info': 'Know everything!',
            'rover_modal_button_close': 'It is close',
            'rover_modal_link': 'yandex.com',
        },
    }

    if location == [0.5, 0.5]:
        rover_info['ru'][
            'rover_modal_title'
        ] = 'Тебе не скрыться. И от скидки в 300 $SIGN$$CURRENCY$'
        rover_info['en'][
            'rover_modal_title'
        ] = 'You can\'t run. And from $SIGN$300$CURRENCY$ bucks discount'
        rover_info['ru']['rover_modal_body'] = ''.join(
            [
                'Сегодня робот прислуживает тебе, а завтра -- ты ему!',
                ' Cкидка 300 $SIGN$$CURRENCY$ деняк',
            ],
        )
        rover_info['en']['rover_modal_body'] = ''.join(
            [
                'Today rover serves you. Tomorrow you will serve rover!',
                ' Get $SIGN$300$CURRENCY$ discount',
            ],
        )
        rover_info['ru']['rover_banner_main_page'] = 'Невозможно отказать!'
        rover_info['en']['rover_banner_main_page'] = 'ROVER_FORCED'

    price_template_l10n = {
        'ru': {'price_template': '$VALUE$ $SIGN$$CURRENCY$'},
        'en': {'price_template': '$SIGN$$VALUE$$CURRENCY$'},
    }

    l10n = {
        **delivery_info[locale],
        **rover_tracking_l10n[locale],
        **price_template_l10n[locale],
    }

    if location != [2, 2]:
        l10n.update(rover_info[locale])
    response_json['l10n'].pop('working_hours_text', None)
    assert response_json['l10n'] == l10n


@pytest.mark.now(NOW)
@pytest.mark.parametrize('handler', ['v1', 'v2'])
@pytest.mark.experiments3(
    name='lavka_rover_delivery_zone',
    consumers=['grocery-cart/order-cycle', 'grocery-api/modes'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'coordinates': [
                    [[[-1.0, -1.0], [-1.0, 1.0], [1.0, 1.1], [1.0, -1.1]]],
                ],
            },
        },
    ],
    is_config=True,
)
@pytest.mark.experiments3(
    name='use_rover_depot_zones',
    consumers=['grocery-cart/order-cycle', 'grocery-api/service-info'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {
                'init': {
                    'arg_name': 'depot_id',
                    'arg_type': 'string',
                    'value': 'theyseemerolling',
                },
                'type': 'eq',
            },
            'value': {'enabled': True},
        },
    ],
    default_value={'enabled': False},
    is_config=True,
)
@pytest.mark.parametrize(
    'location,depot_id',
    [
        pytest.param(
            [2, 2], 'theyseemerolling', id='depot with active rover zone',
        ),
        pytest.param(
            [0, 0], 'depotnoroverzone', id='depot without active rover zone',
        ),
    ],
)
async def test_servive_info_rover_by_depot_zone(
        experiments3,
        taxi_grocery_api,
        overlord_catalog,
        grocery_depots,
        location,
        depot_id,
        grocery_surge,
        handler,
):
    """ no matter how, we still get rover """

    prepare_depots(
        overlord_catalog,
        location,
        grocery_depots,
        depot_id=depot_id,
        with_rover=(location == [2, 2]),
    )
    grocery_surge.add_record(
        legacy_depot_id=LEGACY_DEPOT_ID,
        timestamp=NOW,
        pipeline='calc_surge_grocery_v1',
        load_level=0,
    )

    minimum_order = 1500
    _set_surge(experiments3, minimum_order=minimum_order)

    await taxi_grocery_api.invalidate_caches()

    json = {'position': {'location': location}}

    headers = {}

    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/{handler}/service-info', json=json, headers=headers,
    )
    assert response.status_code == 200
    response_json = response.json()

    assert 'rover_banner_main_page' in response_json['l10n']


# нет лавки, зона которой покрывает точку
@pytest.mark.parametrize('handler', ['v1', 'v2'])
async def test_service_info_404(taxi_grocery_api, handler):
    json = {'position': {'location': [0, 0]}}
    headers = {'Accept-Language': 'ru'}
    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/{handler}/service-info', json=json, headers=headers,
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'DEPOT_NOT_FOUND'


# проверяем что пробросили auth_context в ручке cart/evaluate
@pytest.mark.parametrize('handler', ['v1', 'v2'])
async def test_p13n_call_authorised(
        taxi_grocery_api,
        mockserver,
        overlord_catalog,
        grocery_depots,
        handler,
):
    location = [0, 0]
    prepare_depots(overlord_catalog, location, grocery_depots)

    @mockserver.json_handler('/grocery-p13n/internal/v1/p13n/v1/cart/evaluate')
    def _cart_evaluate(request):
        assert 'X-Yandex-UID' in request.headers
        return mockserver.make_response(status=500)

    json = {'position': {'location': location}}
    headers = {'Accept-Language': 'ru', 'X-Yandex-UID': 'test_uid'}
    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/{handler}/service-info', json=json, headers=headers,
    )
    assert response.status_code == 200


@pytest.mark.parametrize('handler', ['v1', 'v2'])
@pytest.mark.parametrize('payment_available', [True, False])
async def test_service_info_cashback_info_200(
        taxi_grocery_api,
        overlord_catalog,
        grocery_p13n,
        payment_available,
        grocery_depots,
        handler,
):
    """ Check /service-info forwards cashback-info from p13n"""
    uid = '1234567890'
    balance = '100500'
    location = [0, 0]
    prepare_depots(overlord_catalog, location, grocery_depots)

    grocery_p13n.set_cashback_info_response(
        balance=balance, payment_available=payment_available,
    )
    grocery_p13n.set_cashback_request_check(
        on_cashback_request=(
            lambda request_headers, request_body: request_headers[
                'X-Yandex-UID'
            ]
            == uid
        ),
    )
    json = {'position': {'location': location}}
    headers = {
        'X-YaTaxi-Session': 'taxi: user-id',
        'X-Yandex-UID': uid,
        'Accept-Language': 'ru',
    }
    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/{handler}/service-info', json=json, headers=headers,
    )
    assert response.status_code == 200
    assert grocery_p13n.cashback_info_times_called == 1
    assert response.json()['cashback'] == {
        'balance': balance,
        'payment_available': payment_available,
    }


@pytest.mark.parametrize('handler', ['v1', 'v2'])
async def test_service_info_cashback_info_unauthorised(
        taxi_grocery_api,
        overlord_catalog,
        grocery_p13n,
        grocery_depots,
        handler,
):
    """ Check /service-info is not calling p13n for
    unauthorised user """
    location = [0, 0]
    prepare_depots(overlord_catalog, location, grocery_depots)

    json = {'position': {'location': location}}
    headers = {'Accept-Language': 'ru'}
    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/{handler}/service-info', json=json, headers=headers,
    )
    assert response.status_code == 200
    assert grocery_p13n.cashback_info_times_called == 0
    assert 'cashback' not in response.json()


@pytest.mark.parametrize('handler', ['v1', 'v2'])
async def test_service_info_cashback_info_404(
        taxi_grocery_api,
        overlord_catalog,
        grocery_p13n,
        grocery_depots,
        handler,
):
    """ Check /service-info works properly on p13n 404 error """
    location = [0, 0]
    prepare_depots(overlord_catalog, location, grocery_depots)

    headers = {
        'X-YaTaxi-Session': 'taxi: user-id',
        'X-Yandex-UID': '123456',
        'Accept-Language': 'ru',
    }
    json = {'position': {'location': location}}
    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/{handler}/service-info', json=json, headers=headers,
    )
    assert response.status_code == 200
    assert grocery_p13n.cashback_info_times_called == 1
    assert 'cashback' not in response.json()


@pytest.mark.parametrize('handler', ['v1', 'v2'])
async def test_service_info_cashback_info_500(
        taxi_grocery_api,
        mockserver,
        overlord_catalog,
        grocery_depots,
        handler,
):
    """ Check /service-info works properly on p13n 500 error """
    location = [0, 0]
    prepare_depots(overlord_catalog, location, grocery_depots)

    @mockserver.json_handler('/grocery-p13n/internal/v1/p13n/v1/cashback-info')
    def _mock_cashback_info(request):
        return mockserver.make_response(status=500)

    headers = {'X-YaTaxi-Session': 'taxi: user-id', 'Accept-Language': 'ru'}
    json = {'position': {'location': location}}
    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/{handler}/service-info', json=json, headers=headers,
    )
    assert response.status_code == 200
    assert _mock_cashback_info.times_called == 1
    assert 'cashback' not in response.json()


@pytest.mark.now(NOW)
@pytest.mark.parametrize('handler', ['v1', 'v2'])
@pytest.mark.experiments3(
    name='grocery_rover_ui_images',
    consumers=['grocery-api/service-info'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'banner_main_page_image': 'banner_main_page_image.jpg',
                'modal_main_page_image': 'modal_main_page_image.jpg',
                'banner_tracking_image': 'banner_tracking_image.jpg',
            },
        },
    ],
    is_config=True,
)
async def test_service_info_rover_ui_images(
        taxi_grocery_api,
        overlord_catalog,
        grocery_surge,
        grocery_depots,
        handler,
):
    """ service info returns rover images
    from grocery_rover_ui_images config """
    location = [0, 0]
    prepare_depots(overlord_catalog, location, grocery_depots)

    grocery_surge.add_record(
        legacy_depot_id=LEGACY_DEPOT_ID,
        timestamp=NOW,
        pipeline='calc_surge_grocery_v1',
        load_level=0,
    )

    await taxi_grocery_api.invalidate_caches()

    json = {'position': {'location': location}}

    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/{handler}/service-info', json=json,
    )
    assert response.status_code == 200
    response_json = response.json()

    l10n = response_json['l10n']
    assert l10n['rover_banner_main_page_image'] == 'banner_main_page_image.jpg'
    assert l10n['rover_modal_image'] == 'modal_main_page_image.jpg'
    assert l10n['rover_banner_tracking_image'] == 'banner_tracking_image.jpg'


PAYMENT_ID_DIVISOR = 3


@pytest.mark.now(NOW)
@pytest.mark.parametrize('handler', ['v1', 'v2'])
@DISABLE_SURGE_FOR_NEWBIES
@pytest.mark.config(
    GROCERY_MARKETING_SHARED_CONSUMER_TAG_CHECK={
        'grocery_api_catalog': {
            'tag': 'total_paid_orders_count',
            'payment_id_divisor': PAYMENT_ID_DIVISOR,
        },
    },
)
@pytest.mark.parametrize(
    'user_orders_count,payment_id_orders_count,is_surge',
    [(10, 0, True), (0, 3, True), (0, 0, False), (None, None, False)],
)
async def test_user_orders_completed_kwarg(
        taxi_grocery_api,
        overlord_catalog,
        grocery_surge,
        grocery_marketing,
        grocery_depots,
        user_orders_count,
        payment_id_orders_count,
        is_surge,
        handler,
):
    """ g-api should get user total_orders_count tag and
    use it in surge request """

    yandex_uid = '1234567'
    location = [0, 0]
    payment_id = '1'
    prepare_depots(overlord_catalog, location, grocery_depots)
    if user_orders_count is not None:
        grocery_marketing.add_user_tag(
            'total_paid_orders_count', user_orders_count, user_id=yandex_uid,
        )
    if payment_id_orders_count is not None:
        grocery_marketing.add_payment_id_tag(
            'total_paid_orders_count',
            payment_id_orders_count,
            payment_id=payment_id,
        )
    grocery_surge.add_record(
        legacy_depot_id=LEGACY_DEPOT_ID,
        timestamp=NOW,
        pipeline='calc_surge_grocery_v1',
        load_level=0,
    )

    orders_count = 0
    if user_orders_count:
        orders_count += user_orders_count
    if payment_id_orders_count and payment_id_orders_count != 0:
        orders_count += payment_id_orders_count / PAYMENT_ID_DIVISOR

    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/{handler}/service-info',
        json={
            'position': {'location': location},
            'current_payment_method': {'type': 'card', 'id': payment_id},
        },
        headers={'X-Yandex-UID': yandex_uid, 'Accept-Language': 'en'},
    )
    assert response.status_code == 200
    assert response.json()['is_surge'] == is_surge
    assert grocery_marketing.retrieve_v2_times_called == 1
    assert response.json()['user_orders_count'] == orders_count


@pytest.mark.now(NOW)
@pytest.mark.parametrize('handler', ['v1', 'v2'])
@DISABLE_SURGE_FOR_NEWBIES
@pytest.mark.parametrize('headers,', [{'X-Yandex-UID': '1234567'}, {}])
async def test_nouid_user_orders_completed_kwarg(
        taxi_grocery_api,
        overlord_catalog,
        grocery_surge,
        grocery_depots,
        headers,
        grocery_marketing,
        handler,
):
    """ g-api should assume that user has 0 user_orders_completed
    if there is no yandex-uid """

    location = [0, 0]
    prepare_depots(overlord_catalog, location, grocery_depots)

    grocery_surge.add_record(
        legacy_depot_id=LEGACY_DEPOT_ID,
        timestamp=NOW,
        pipeline='calc_surge_grocery_v1',
        load_level=0,
    )

    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/{handler}/service-info',
        json={'position': {'location': location}},
        headers=headers,
    )
    assert response.status_code == 200
    assert not response.json()['is_surge']
    assert grocery_marketing.retrieve_v2_times_called == 1


@pytest.mark.parametrize('handler', ['v1', 'v2'])
@pytest.mark.parametrize('balance_to_annihilate', ['0', '42'])
@pytest.mark.parametrize(
    'is_cashback_annihilation_enabled',
    [
        pytest.param(
            True,
            id='cashback_annihilation_enabled',
            marks=[common.CASHBACK_ANNIHILATION_ENABLED],
        ),
        pytest.param(
            False,
            id='cashback_annihilation_disabled',
            marks=[common.CASHBACK_ANNIHILATION_DISABLED],
        ),
    ],
)
async def test_cashback_annihilation_info(
        overlord_catalog,
        taxi_grocery_api,
        mockserver,
        grocery_depots,
        balance_to_annihilate,
        is_cashback_annihilation_enabled,
        handler,
):
    """ Check /service-info forwards cashback annihilation info from p13n"""
    location = [0, 0]
    balance_to_annihilate = balance_to_annihilate
    annihilation_date = '2021-07-26T14:08:00+00:00'
    prepare_depots(overlord_catalog, location, grocery_depots)

    @mockserver.json_handler('/grocery-p13n/internal/v1/p13n/v1/cashback-info')
    def _p13_cashback_info(request):
        return {
            'balance': '100500',
            'complement_payment_types': [],
            'wallet_id': 'TEST_WALLET_ID',
            'annihilation_info': {
                'annihilation_date': annihilation_date,
                'balance_to_annihilate': balance_to_annihilate,
            },
        }

    json = {'position': {'location': location}}
    headers = {
        'X-YaTaxi-Session': 'taxi: user-id',
        'X-Yandex-UID': '1234567890',
        'Accept-Language': 'ru',
    }
    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/{handler}/service-info', json=json, headers=headers,
    )
    response_json = response.json()
    assert response.status_code == 200
    if balance_to_annihilate == '0' or not is_cashback_annihilation_enabled:
        assert 'annihilation_info' not in response_json['cashback']
    else:
        assert response_json['cashback']['annihilation_info'] == {
            'annihilation_date': annihilation_date,
            'balance_to_annihilate': balance_to_annihilate,
        }


@pytest.mark.now(NOW)
@pytest.mark.parametrize('reward_discounts_enabled', [True, False])
@pytest.mark.parametrize(
    'delivery_conditions',
    [
        [
            {'order_cost': '0', 'delivery_cost': '10'},
            {'order_cost': '100', 'delivery_cost': '5'},
            {'order_cost': '200', 'delivery_cost': '0'},
        ],
        [{'order_cost': '50', 'delivery_cost': '0'}],
    ],
)
@pytest.mark.translations(
    tariff={'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'}},
)
@pytest.mark.parametrize(
    'antifraud_enabled, is_fraud',
    [
        pytest.param(
            False,
            True,
            marks=experiments.ANTIFRAUD_CHECK_DISABLED,
            id='no antifraud, not fraud, no check',
        ),
        pytest.param(
            True,
            False,
            marks=experiments.ANTIFRAUD_CHECK_ENABLED,
            id='antifraud, not fraud, check',
        ),
        pytest.param(
            True,
            True,
            marks=experiments.ANTIFRAUD_CHECK_ENABLED,
            id='antifraud, fraud, check',
        ),
    ],
)
async def test_service_info_reward_block(
        experiments3,
        taxi_grocery_api,
        overlord_catalog,
        antifraud,
        grocery_marketing,
        grocery_p13n,
        grocery_surge,
        grocery_depots,
        tristero_parcels,
        delivery_conditions,
        reward_discounts_enabled,
        antifraud_enabled,
        is_fraud,
):
    """ get service info with reward_block """

    experiments3.add_config(
        match={
            'predicate': {'type': 'true'},
            'enabled': reward_discounts_enabled,
        },
        name='grocery_show_reward_discounts',
        consumers=['grocery-api/modes'],
        clauses=[
            {
                'predicate': {'type': 'true'},
                'value': {'enabled': reward_discounts_enabled},
            },
        ],
    )

    discount_steps = [
        ('75', '10.2', 'discount_percent'),
        ('150', '20', 'discount_value'),
        ('200', '5.3', 'gain_percent'),
        ('300', '50', 'gain_value'),
    ]
    grocery_p13n.add_cart_modifier_with_rules(steps=discount_steps)

    location = common.DEFAULT_LOCATION
    yandex_uid = tests_headers.HEADER_YANDEX_UID
    orders_count = 2 if not antifraud_enabled else None

    grocery_marketing.add_user_tag(
        'total_orders_count', orders_count, user_id=yandex_uid,
    )
    prepare_depots(overlord_catalog, location, grocery_depots)

    set_surge_conditions(experiments3, delivery_conditions=delivery_conditions)

    grocery_surge.add_record(
        legacy_depot_id=LEGACY_DEPOT_ID,
        timestamp='2020-09-09T10:00:00+00:00',
        pipeline='calc_surge_grocery_v1',
        load_level=0,
    )

    tristero_order = tristero_parcels.add_order(
        order_id='62a88408-b448-429e-8dc0-48f6995fd78e',
        uid=yandex_uid,
        status='received',
        delivery_date='2020-11-02T13:00:42.109234+00:00',
    )
    tristero_order.add_parcel(parcel_id='1', status='in_depot')

    await taxi_grocery_api.invalidate_caches()

    json = {
        'position': {'location': location},
        'additional_data': common.DEFAULT_ADDITIONAL_DATA,
    }
    headers = {}
    headers['X-Yandex-UID'] = yandex_uid
    headers['Accept-Language'] = 'ru'
    headers['User-Agent'] = common.DEFAULT_USER_AGENT
    headers['X-YaTaxi-Session'] = 'taxi:1'
    grocery_p13n.set_modifiers_request_check(
        on_modifiers_request=common.default_on_modifiers_request(
            orders_count, has_parcels=True,
        ),
    )
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/service-info', json=json, headers=headers,
    )
    assert response.status_code == 200

    assert tristero_parcels.retrieve_orders_v2_times_called == 1
    if reward_discounts_enabled:
        assert grocery_p13n.discount_modifiers_times_called == 1
        assert antifraud.times_discount_antifraud_called() == int(
            antifraud_enabled,
        )

    response_json = response.json()

    if antifraud_enabled and is_fraud:
        assert response_json['notifications'] == [
            {'name': 'catalog_newbie_discount_missing'},
        ]

    assert response_json['is_surge'] is False

    if reward_discounts_enabled:
        if len(delivery_conditions) > 1:
            reward_block = [
                {
                    'type': 'delivery',
                    'cart_cost_threshold': 'От 0 $SIGN$$CURRENCY$',
                    'reward_value': 'Доставка 10 $SIGN$$CURRENCY$',
                },
                {
                    'type': 'cart_money_discount',
                    'cart_cost_threshold': 'От 75 $SIGN$$CURRENCY$',
                    'reward_value': 'Скидка 10%',
                },
                {
                    'type': 'delivery',
                    'cart_cost_threshold': 'От 100 $SIGN$$CURRENCY$',
                    'reward_value': 'Доставка 5 $SIGN$$CURRENCY$',
                },
                {
                    'type': 'cart_money_discount',
                    'cart_cost_threshold': 'От 150 $SIGN$$CURRENCY$',
                    'reward_value': 'Скидка 20 $SIGN$$CURRENCY$',
                },
                {
                    'type': 'delivery',
                    'cart_cost_threshold': 'От 200 $SIGN$$CURRENCY$',
                    'reward_value': 'Доставка 0 $SIGN$$CURRENCY$',
                },
                {
                    'type': 'cart_cashback',
                    'cart_cost_threshold': 'От 200 $SIGN$$CURRENCY$',
                    'reward_value': '5% на Плюс',
                },
                {
                    'type': 'cart_cashback',
                    'cart_cost_threshold': 'От 300 $SIGN$$CURRENCY$',
                    'reward_value': '50 баллов на Плюс',
                },
            ]
        else:
            reward_block = [
                {
                    'type': 'min_cart',
                    'cart_cost_threshold': '50 $SIGN$$CURRENCY$',
                    'reward_value': 'Минимальная корзина 50 $SIGN$$CURRENCY$',
                },
                {
                    'type': 'delivery',
                    'cart_cost_threshold': 'От 50 $SIGN$$CURRENCY$',
                    'reward_value': 'Доставка 0 $SIGN$$CURRENCY$',
                },
                {
                    'type': 'cart_money_discount',
                    'cart_cost_threshold': 'От 75 $SIGN$$CURRENCY$',
                    'reward_value': 'Скидка 10%',
                },
                {
                    'type': 'cart_money_discount',
                    'cart_cost_threshold': 'От 150 $SIGN$$CURRENCY$',
                    'reward_value': 'Скидка 20 $SIGN$$CURRENCY$',
                },
                {
                    'type': 'cart_cashback',
                    'cart_cost_threshold': 'От 200 $SIGN$$CURRENCY$',
                    'reward_value': '5% на Плюс',
                },
                {
                    'type': 'cart_cashback',
                    'cart_cost_threshold': 'От 300 $SIGN$$CURRENCY$',
                    'reward_value': '50 баллов на Плюс',
                },
            ]
    else:
        if len(delivery_conditions) > 1:
            reward_block = [
                {
                    'type': 'delivery',
                    'cart_cost_threshold': 'От 0 $SIGN$$CURRENCY$',
                    'reward_value': 'Доставка 10 $SIGN$$CURRENCY$',
                },
                {
                    'type': 'delivery',
                    'cart_cost_threshold': 'От 100 $SIGN$$CURRENCY$',
                    'reward_value': 'Доставка 5 $SIGN$$CURRENCY$',
                },
                {
                    'type': 'delivery',
                    'cart_cost_threshold': 'От 200 $SIGN$$CURRENCY$',
                    'reward_value': 'Доставка 0 $SIGN$$CURRENCY$',
                },
            ]
        else:
            reward_block = [
                {
                    'type': 'min_cart',
                    'cart_cost_threshold': '50 $SIGN$$CURRENCY$',
                    'reward_value': 'Минимальная корзина 50 $SIGN$$CURRENCY$',
                },
                {
                    'type': 'delivery',
                    'cart_cost_threshold': 'От 50 $SIGN$$CURRENCY$',
                    'reward_value': 'Доставка 0 $SIGN$$CURRENCY$',
                },
            ]
    assert response_json['reward_block'] == reward_block


@pytest.mark.translations(
    overlord_catalog={
        'service_name': {'ru': 'Яндекс.Лавка'},
        'service_name.market': {'ru': 'Яндекс.Маркет'},
    },
)
@pytest.mark.parametrize('handler', ['v1', 'v2'])
@pytest.mark.parametrize(
    'brand, service_name',
    [('lavka', 'Яндекс.Лавка'), ('market', 'Яндекс.Маркет')],
)
async def test_service_info_is_localized_by_brand(
        taxi_grocery_api,
        overlord_catalog,
        grocery_depots,
        brand,
        service_name,
        handler,
):
    """ Название сервиса локализуется в зависимости от бренда """

    location = [0, 0]
    prepare_depots(overlord_catalog, location, grocery_depots)

    json = {'position': {'location': location}}
    headers = {
        'Accept-Language': 'ru',
        'X-Request-Application': (
            f'app_name=mobileweb_market_lavka_iphone,app_brand={brand}'
        ),
    }
    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/{handler}/service-info', json=json, headers=headers,
    )
    assert response.status_code == 200
    assert response.json()['service_metadata']['service_name'] == service_name


@pytest.mark.parametrize('handler', ['v1', 'v2'])
@pytest.mark.parametrize('locale', ['ru', 'en'])
@pytest.mark.experiments3(
    name='grocery_rover_compensation_params',
    consumers=['grocery-cart/order-cycle', 'grocery-api/service-info'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'value': '10', 'is_percent': True, 'is_plus': False},
        },
    ],
    is_config=True,
)
@pytest.mark.experiments3(
    name='use_rover_depot_zones',
    consumers=['grocery-cart/order-cycle', 'grocery-api/service-info'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {
                'init': {
                    'arg_name': 'depot_id',
                    'arg_type': 'string',
                    'value': 'theyseemerolling',
                },
                'type': 'eq',
            },
            'value': {'enabled': True},
        },
    ],
    default_value={'enabled': False},
    is_config=True,
)
@pytest.mark.experiments3(
    name='lavka_force_rover_zone',
    consumers=['grocery-cart/order-cycle', 'grocery-api/modes'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'coordinates': [
                    [[[0.1, 0.1], [0.1, 1.0], [1.0, 1.1], [1.0, 0.1]]],
                ],
            },
        },
    ],
    is_config=True,
)
@pytest.mark.translations(
    overlord_catalog={
        'rover_modal_title_force_percent': {
            'en': (
                'Powerful hands! Get %(value)s percent discount!'
                ' Can\'t refuse.'
            ),
            'ru': 'Как мощны его лапищи. Cкидка %(value)s%. Не откажешься.',
        },
        'rover_modal_body_force_percent': {
            'en': (
                'Will bring safely and discount %(value)s percent.'
                ' Resistance is futile'
            ),
            'ru': (
                'Привезёт вам товары и не отдаст никому другому и скидка'
                ' %(value)s%. Сопротивление бесполезно'
            ),
        },
    },
    tariff={
        'currency_with_sign.default': {
            'en': '$SIGN$$VALUE$$CURRENCY$',
            'ru': '$VALUE$ $SIGN$$CURRENCY$',
        },
    },
)
async def test_rover_localizations_force_percent_discount(
        experiments3,
        taxi_grocery_api,
        overlord_catalog,
        grocery_depots,
        grocery_surge,
        locale,
        handler,
):
    location = [0.4, 0.4]

    prepare_depots(
        overlord_catalog,
        location,
        grocery_depots,
        depot_id='theyseemerolling',
        with_rover=True,
    )
    grocery_surge.add_record(
        legacy_depot_id=LEGACY_DEPOT_ID,
        timestamp=NOW,
        pipeline='calc_surge_grocery_v1',
        load_level=0,
    )

    minimum_order = 1500
    _set_surge(experiments3, minimum_order=minimum_order)

    await taxi_grocery_api.invalidate_caches()

    json = {'position': {'location': location}}

    headers = {'Accept-Language': locale}

    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/{handler}/service-info', json=json, headers=headers,
    )
    assert response.status_code == 200
    response_json = response.json()

    rover_info = {
        'ru': {
            'rover_modal_title': (
                'Как мощны его лапищи. Cкидка 10%. Не откажешься.'
            ),
            'rover_modal_body': (
                'Привезёт вам товары и не отдаст никому другому'
                ' и скидка 10%. Сопротивление бесполезно'
            ),
        },
        'en': {
            'rover_modal_title': (
                'Powerful hands! Get 10 percent discount! Can\'t refuse.'
            ),
            'rover_modal_body': (
                'Will bring safely and discount 10 percent.'
                ' Resistance is futile'
            ),
        },
    }

    assert (
        response_json['l10n']['rover_modal_title']
        == rover_info[locale]['rover_modal_title']
    )
    assert (
        response_json['l10n']['rover_modal_body']
        == rover_info[locale]['rover_modal_body']
    )


@pytest.mark.parametrize('handler', ['v1', 'v2'])
@pytest.mark.parametrize('locale', ['ru', 'en'])
@pytest.mark.experiments3(
    name='grocery_rover_compensation_params',
    consumers=['grocery-cart/order-cycle', 'grocery-api/service-info'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'value': '100', 'is_percent': False, 'is_plus': True},
        },
    ],
    is_config=True,
)
@pytest.mark.experiments3(
    name='use_rover_depot_zones',
    consumers=['grocery-cart/order-cycle', 'grocery-api/service-info'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {
                'init': {
                    'arg_name': 'depot_id',
                    'arg_type': 'string',
                    'value': 'theyseemerolling',
                },
                'type': 'eq',
            },
            'value': {'enabled': True},
        },
    ],
    default_value={'enabled': False},
    is_config=True,
)
@pytest.mark.translations(
    overlord_catalog={
        'rover_modal_title_plus': {
            'en': 'Powerful hands! Get %(value)s plus back!',
            'ru': 'Как мощны его лапищи. Получи %(value)s баллов плюса.',
        },
        'rover_modal_body_plus': {
            'en': 'Will bring safely and get %(value)s plus back!',
            'ru': (
                'Привезёт вам товары и не отдаст никому другому и '
                '%(value)s баллов плюса.'
            ),
        },
    },
    tariff={
        'currency_with_sign.default': {
            'en': '$SIGN$$VALUE$$CURRENCY$',
            'ru': '$VALUE$ $SIGN$$CURRENCY$',
        },
    },
)
async def test_rover_localizations_plus_discount(
        experiments3,
        taxi_grocery_api,
        overlord_catalog,
        grocery_depots,
        grocery_surge,
        locale,
        handler,
):
    location = [2, 2]

    prepare_depots(
        overlord_catalog,
        location,
        grocery_depots,
        depot_id='theyseemerolling',
        with_rover=True,
    )
    grocery_surge.add_record(
        legacy_depot_id=LEGACY_DEPOT_ID,
        timestamp=NOW,
        pipeline='calc_surge_grocery_v1',
        load_level=0,
    )

    minimum_order = 1500
    _set_surge(experiments3, minimum_order=minimum_order)

    await taxi_grocery_api.invalidate_caches()

    json = {'position': {'location': location}}

    headers = {'Accept-Language': locale}

    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/{handler}/service-info', json=json, headers=headers,
    )
    assert response.status_code == 200
    response_json = response.json()

    rover_info = {
        'ru': {
            'rover_modal_title': (
                'Как мощны его лапищи. Получи 100 баллов плюса.'
            ),
            'rover_modal_body': (
                'Привезёт вам товары и не отдаст никому '
                'другому и 100 баллов плюса.'
            ),
        },
        'en': {
            'rover_modal_title': 'Powerful hands! Get 100 plus back!',
            'rover_modal_body': 'Will bring safely and get 100 plus back!',
        },
    }

    assert (
        response_json['l10n']['rover_modal_title']
        == rover_info[locale]['rover_modal_title']
    )
    assert (
        response_json['l10n']['rover_modal_body']
        == rover_info[locale]['rover_modal_body']
    )


@pytest.mark.parametrize('handler', ['v1', 'v2'])
@pytest.mark.parametrize('locale', ['ru', 'en'])
@pytest.mark.experiments3(
    name='grocery_rover_compensation_params',
    consumers=['grocery-cart/order-cycle', 'grocery-api/service-info'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'value': '100', 'is_percent': False, 'is_plus': True},
        },
    ],
    is_config=True,
)
@pytest.mark.experiments3(
    name='lavka_force_rover_zone',
    consumers=['grocery-cart/order-cycle', 'grocery-api/modes'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'coordinates': [
                    [[[0.1, 0.1], [0.1, 1.0], [1.0, 1.1], [1.0, 0.1]]],
                ],
            },
        },
    ],
    is_config=True,
)
@pytest.mark.experiments3(
    name='use_rover_depot_zones',
    consumers=['grocery-cart/order-cycle', 'grocery-api/service-info'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {
                'init': {
                    'arg_name': 'depot_id',
                    'arg_type': 'string',
                    'value': 'theyseemerolling',
                },
                'type': 'eq',
            },
            'value': {'enabled': True},
        },
    ],
    default_value={'enabled': False},
    is_config=True,
)
@pytest.mark.translations(
    overlord_catalog={
        'rover_modal_title_force_plus': {
            'en': 'Powerful hands! Get %(value)s plus back! No choice.',
            'ru': (
                'Как мощны его лапищи. Получи %(value)s баллов плюса.'
                ' Без вариантов.'
            ),
        },
        'rover_modal_body_force_plus': {
            'en': (
                'Will bring safely and get %(value)s plus back!'
                ' Lava is nothing.'
            ),
            'ru': (
                'Привезёт вам товары и не отдаст никому другому и '
                '%(value)s баллов плюса. Не скрыться.'
            ),
        },
    },
    tariff={
        'currency_with_sign.default': {
            'en': '$SIGN$$VALUE$$CURRENCY$',
            'ru': '$VALUE$ $SIGN$$CURRENCY$',
        },
    },
)
async def test_rover_localizations_plus_discount_force(
        experiments3,
        taxi_grocery_api,
        overlord_catalog,
        grocery_surge,
        grocery_depots,
        locale,
        handler,
):
    location = [0.4, 0.4]

    prepare_depots(
        overlord_catalog,
        location,
        grocery_depots,
        depot_id='theyseemerolling',
        with_rover=True,
    )
    grocery_surge.add_record(
        legacy_depot_id=LEGACY_DEPOT_ID,
        timestamp=NOW,
        pipeline='calc_surge_grocery_v1',
        load_level=0,
    )

    minimum_order = 1500
    _set_surge(experiments3, minimum_order=minimum_order)

    await taxi_grocery_api.invalidate_caches()

    json = {'position': {'location': location}}

    headers = {'Accept-Language': locale}

    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/{handler}/service-info', json=json, headers=headers,
    )
    assert response.status_code == 200
    response_json = response.json()

    rover_info = {
        'ru': {
            'rover_modal_title': (
                'Как мощны его лапищи. Получи 100 баллов плюса. Без вариантов.'
            ),
            'rover_modal_body': (
                'Привезёт вам товары и не отдаст никому '
                'другому и 100 баллов плюса. Не скрыться.'
            ),
        },
        'en': {
            'rover_modal_title': (
                'Powerful hands! Get 100 plus back! No choice.'
            ),
            'rover_modal_body': (
                'Will bring safely and get 100 plus back! Lava is nothing.'
            ),
        },
    }

    assert (
        response_json['l10n']['rover_modal_title']
        == rover_info[locale]['rover_modal_title']
    )
    assert (
        response_json['l10n']['rover_modal_body']
        == rover_info[locale]['rover_modal_body']
    )


get_rounding_rules = common_service_info.get_rounding_rules

# Округление цены доставки и отображение происходит с учетом
# значений конфигов CURRENCY_FORMATTING_RULES и CURRENCY_ROUNDING_RULES
@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    'delivery_cost_shown',
    [
        pytest.param('10.43', marks=get_rounding_rules(2, 0.01)),
        pytest.param('10.4', marks=get_rounding_rules(1, 0.1)),
        pytest.param('10', marks=get_rounding_rules(0, 1)),
    ],
)
@pytest.mark.translations(
    overlord_catalog={
        'delivery_text_cost_range': {
            'ru': 'Доставка %(value)s',
            'en': 'Delivery %(value)s',
        },
        'delivery_cost_range': {'ru': '%(value)s', 'en': '%(value)s'},
    },
    tariff={
        'currency_with_sign.default': {
            'en': '$SIGN$$VALUE$$CURRENCY$',
            'ru': '$VALUE$ $SIGN$$CURRENCY$',
        },
    },
)
async def test_service_paid_delivery_round(
        experiments3,
        taxi_grocery_api,
        overlord_catalog,
        grocery_surge,
        grocery_depots,
        delivery_cost_shown,
):
    location = [0, 0]
    prepare_depots(overlord_catalog, location, grocery_depots)
    set_surge_conditions(
        experiments3,
        delivery_conditions=[
            {'order_cost': '0', 'delivery_cost': '10.43'},
            {'order_cost': '50', 'delivery_cost': '0'},
        ],
    )

    grocery_surge.add_record(
        legacy_depot_id=LEGACY_DEPOT_ID,
        timestamp=NOW,
        pipeline='calc_surge_grocery_v1',
        load_level=0,
    )

    await taxi_grocery_api.invalidate_caches()

    headers = {'Accept-Language': 'en'}

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/service-info',
        json={'position': {'location': location}},
        headers=headers,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert (
        response_json['l10n']['delivery_cost']
        == f'Delivery: $SIGN${delivery_cost_shown}$CURRENCY$'
    )
    assert (
        response_json['l10n']['delivery_cost_range']
        == f'$SIGN$0-{delivery_cost_shown}$CURRENCY$'
    )
    assert response_json['reward_block'] == [
        {
            'cart_cost_threshold': 'From $SIGN$0$CURRENCY$',
            'reward_value': f'Delivery: $SIGN${delivery_cost_shown}$CURRENCY$',
            'type': 'delivery',
        },
        {
            'cart_cost_threshold': 'From $SIGN$50$CURRENCY$',
            'reward_value': 'Free delivery',
            'type': 'delivery',
        },
    ]
