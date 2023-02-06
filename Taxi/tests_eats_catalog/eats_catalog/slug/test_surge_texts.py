from dateutil import parser
import pytest

from eats_catalog import configs
from eats_catalog import experiments
from eats_catalog import storage
from eats_catalog import surge_utils

DEFAULT_TEXTS = {
    'description': 'Повышенный спрос',
    'message': (
        'Заказов сейчас очень много — чтобы еда приехала '
        'в срок, стоимость доставки временно увеличена'
    ),
    'title': 'Повышенный спрос',
}

CUSTOM_TANKER_KEYS = {
    'title_key': 't_key',
    'message_key': 'm_key',
    'description_key': 'd_key',
}

DEFAULT_TANKER_TITLE_KEY = 'slug.surge.default_title'
DEFAULT_TANKER_MESSAGE_KEY = 'slug.surge.default_message'
DEFAULT_TANKER_DESCRIPTION_KEY = 'slug.surge.default_description'

CUSTOM_TRANSLATIONS = {
    'eats-catalog': {
        't_key': {'en': 'custom title'},
        'm_key': {'en': 'custom message'},
        'd_key': {'en': 'custom description'},
    },
}


@pytest.mark.now('2021-03-30T12:55:00+00:00')
@pytest.mark.parametrize(
    'expected_texts',
    [
        pytest.param(DEFAULT_TEXTS, id='no experiment'),
        pytest.param(
            {
                'description': 'custom description',
                'message': 'custom message',
                'title': 'custom title',
            },
            marks=[
                experiments.surge_texts(**CUSTOM_TANKER_KEYS),
                pytest.mark.translations(**CUSTOM_TRANSLATIONS),
            ],
            id='full and correct config',
        ),
        pytest.param(
            {
                'title': '__default from tanker1',
                'message': '__default from tanker2',
                'description': '__default from tanker3',
            },
            marks=[
                experiments.surge_texts(),
                pytest.mark.translations(
                    **{
                        'eats-catalog': {
                            DEFAULT_TANKER_TITLE_KEY: {
                                'en': '__default from tanker1',
                            },
                            DEFAULT_TANKER_MESSAGE_KEY: {
                                'en': '__default from tanker2',
                            },
                            DEFAULT_TANKER_DESCRIPTION_KEY: {
                                'en': '__default from tanker3',
                            },
                        },
                    },
                ),
            ],
            id='empty config and default (from Tanker) translations',
        ),
        pytest.param(
            DEFAULT_TEXTS,
            marks=[experiments.surge_texts(), pytest.mark.translations()],
            id='empty config and default (hardcoded) translations',
        ),
        pytest.param(
            {
                'description': '___',
                'message': DEFAULT_TEXTS['message'],
                'title': DEFAULT_TEXTS['title'],
            },
            marks=[
                experiments.surge_texts(description_key='__d'),
                pytest.mark.translations(
                    **{
                        'eats-catalog': {
                            DEFAULT_TANKER_TITLE_KEY: {
                                'en': DEFAULT_TEXTS['title'],
                            },
                            DEFAULT_TANKER_MESSAGE_KEY: {
                                'en': DEFAULT_TEXTS['message'],
                            },
                            '__d': {'en': '___'},
                        },
                    },
                ),
            ],
            id='only description from config key, others default from Tanker',
        ),
    ],
)
async def test_surge_texts(
        expected_texts, slug, eats_catalog_storage, mockserver,
):
    eats_catalog_storage.add_place(storage.Place(place_id=1, slug='place_1'))
    eats_catalog_storage.add_zone(
        storage.Zone(
            couriers_type=storage.CouriersType.Pedestrian,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-30T8:00:00+00:00'),
                    end=parser.parse('2021-03-30T23:00:00+00:00'),
                ),
            ],
        ),
    )

    @mockserver.json_handler(
        '/eda-delivery-price/v1/calc-delivery-price-surge',
    )
    def eda_delivery_price_surge(request):
        return {
            'calculation_result': {
                'calculation_name': 'testsuite',
                'result': {
                    'fees': [
                        {'delivery_cost': 0, 'order_price': 2000},
                        {'delivery_cost': 139, 'order_price': 500},
                        {'delivery_cost': 189, 'order_price': 0},
                    ],
                    'is_fallback': False,
                    'extra': {},
                },
            },
            'surge_extra': {},
            'surge_result': {
                'placeId': 1,
                'nativeInfo': {
                    'surgeLevel': 3,
                    'loadLevel': 97,
                    'deliveryFee': 99,
                },
            },
            'experiment_results': [],
            'experiment_errors': [],
            'meta': {},
        }

    response = await slug(
        'place_1',
        query={'latitude': 55.750028, 'longitude': 37.534397},
        headers={'X-Eats-Session': 'blablabla', 'X-Request-Language': 'en'},
    )

    assert eda_delivery_price_surge.times_called == 1
    assert response.status_code == 200
    # check all texts in response equal expected texts
    # запись вида a.items() <= b.items()
    # означает что мапа a это подмножество мапы b
    # где все значения одинаковые
    assert (
        expected_texts.items()
        <= response.json()['payload']['foundPlace']['surge'].items()
    )


RADIUS_LOCALIZATION = {
    'eats-catalog': {
        'common.today': {'ru': 'Сегодня'},
        'slug.surge.delivery_unavailable.title.custom': {
            'ru': 'Доставка Недоступна',
        },
        'slug.surge.preorder.title.custom': {
            'ru': 'Доставка Еды %(day)s %(time)s',
        },
        'slug.surge.delivery_unavailable.message.custom': {
            'ru': 'Текст про недоступность',
        },
        'slug.surge.preorder.message.custom': {'ru': 'Текст про предзаказ'},
    },
}


@pytest.mark.now('2021-11-17T12:10:00+03:00')
@experiments.SEND_SURGE_ON_RADIUS
@experiments.eats_catalog_surge_radius()
@experiments.eats_surge_planned(interval=60)
@pytest.mark.translations(**RADIUS_LOCALIZATION)
@experiments.surge_texts(
    delivery_unavailable_title_key=(
        'slug.surge.delivery_unavailable.title.custom'
    ),
    preorder_title_key='slug.surge.preorder.title.custom',
    delivery_unavailable_message_key=(
        'slug.surge.delivery_unavailable.message.custom'
    ),
    preorder_message_key='slug.surge.preorder.message.custom',
)
@pytest.mark.parametrize(
    'delivery_time,expected_surge',
    (
        pytest.param(
            None,
            {
                'title': 'Доставка Еды Сегодня 15:00',
                'description': 'Доставка Еды Сегодня 15:00',
                'message': 'Текст про предзаказ',
            },
            marks=configs.eats_catalog_delivery_feature(
                disable_by_surge_for_minutes=60,
            ),
            id='asap',
        ),
        pytest.param(
            None,
            {
                'title': 'Доставка Недоступна',
                'description': 'Доставка Недоступна',
                'message': 'Текст про недоступность',
            },
            marks=configs.eats_catalog_delivery_feature(
                disable_by_surge_for_minutes=5 * 60,
            ),
            id='asap_unavailable',
        ),
        pytest.param(
            '2021-11-17T12:30:00+03:00',
            {
                'title': 'Доставка Еды Сегодня 15:00',
                'description': 'Доставка Еды Сегодня 15:00',
                'message': 'Текст про предзаказ',
            },
            marks=configs.eats_catalog_delivery_feature(
                disable_by_surge_for_minutes=60,
            ),
            id='preorder_in_surge_planned',
        ),
        pytest.param(
            '2021-11-17T12:30:00+03:00',
            {
                'title': 'Доставка Недоступна',
                'description': 'Доставка Недоступна',
                'message': 'Текст про недоступность',
            },
            marks=configs.eats_catalog_delivery_feature(
                disable_by_surge_for_minutes=5 * 60,
            ),
            id='preorder_in_surge_planned_unavailable',
        ),
        pytest.param(
            '2021-11-17T15:30:00+03:00',
            None,
            marks=configs.eats_catalog_delivery_feature(
                disable_by_surge_for_minutes=60,
            ),
            id='preorder_out_surge_planned',
        ),
        pytest.param(
            '2021-11-17T15:30:00+03:00',
            None,
            marks=configs.eats_catalog_delivery_feature(
                disable_by_surge_for_minutes=5 * 60,
            ),
            id='preorder_out_surge_planned_unavailable',
        ),
    ),
)
async def test_surge_radius_texts(
        slug,
        eats_catalog_storage,
        surge_resolver,
        delivery_price,
        delivery_time,
        expected_surge,
):
    """
    Проверяет, что при сурже радиусом
    в заголовок сообщения о сурже попадает
    другое сообщение
    """

    eats_catalog_storage.add_place(storage.Place(place_id=1, slug='place_1'))
    eats_catalog_storage.add_zone(
        storage.Zone(
            couriers_type=storage.CouriersType.Pedestrian,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-11-17T12:00:00+03:00'),
                    end=parser.parse('2021-11-17T16:00:00+03:00'),
                ),
            ],
        ),
    )

    delivery_price.set_delivery_conditions(
        [{'order_price': 0, 'delivery_cost': 100}],
    )
    delivery_price.set_place_surge(
        {
            'placeId': 1,
            'nativeInfo': {
                'surgeLevel': 0,
                'loadLevel': 1,
                'show_radius': 1000.0,
                'deliveryFee': 10,
            },
        },
    )

    surge_resolver.place_radius = {1: surge_utils.SurgeRadius(pedestrian=1000)}

    params = {'latitude': 55.750028, 'longitude': 37.534397}
    if delivery_time:
        params['deliveryTime'] = delivery_time

    response = await slug(
        'place_1',
        query=params,
        headers={'X-Eats-Session': 'blablabla', 'X-Request-Language': 'ru'},
    )

    assert delivery_price.times_called == 1
    assert response.status_code == 200

    surge = response.json()['payload']['foundPlace']['surge']

    if expected_surge:
        expected_surge['deliveryFee'] = 0
    assert surge == expected_surge
