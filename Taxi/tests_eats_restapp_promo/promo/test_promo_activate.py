# flake8: noqa
# pylint: disable=too-many-lines

import datetime

import psycopg2
import pytest

FREE_DELIVERY_CREATE_SETTINGS_CHECK_OFF = {
    'name': 'Бесплатная доставка',
    'name_template': 'Бесплатная доставка от {min_price} руб.',
    'description': 'На первый заказ в этом ресторане',
    'description_template': (
        'На первый заказ от {min_price}₽ в этом ресторане.'
    ),
    'picture_uri': 'picture_uri',
    'disable_check': True,
}

PLUS_FIRST_ORDERS = pytest.param(
    {
        'type': 'plus_first_orders',
        'place_ids': [1, 2],
        'starts_at': '2021-10-01T00:00:00+0300',
        'ends_at': '2021-10-10T00:00:00+0300',
        'cashback': [15.0],
    },
)
PLUS_HAPPY_HOURS = pytest.param(
    {
        'type': 'plus_happy_hours',
        'place_ids': [1, 2],
        'starts_at': '2021-10-01T00:00:00+0300',
        'ends_at': '2021-10-10T00:00:00+0300',
        'cashback': [15.0],
        'schedule': [{'day': 2, 'from': 0, 'to': 1}],
    },
)
FREE_DELIVERY = pytest.param(
    {
        'type': 'free_delivery',
        'place_ids': [1, 2],
        'starts_at': '2021-10-01T00:00:00+0300',
        'ends_at': '2021-10-10T00:00:00+0300',
        'min_order_price': 10,
    },
)
DISCOUNT = pytest.param(
    {
        'type': 'discount',
        'place_ids': [1, 2],
        'starts_at': '2021-10-01T00:00:00+0300',
        'ends_at': '2021-10-10T00:00:00+0300',
        'discount': 5,
    },
)
GIFT = pytest.param(
    {
        'type': 'gift',
        'place_ids': [1, 2],
        'starts_at': '2021-10-01T00:00:00+0300',
        'ends_at': '2021-10-10T00:00:00+0300',
        'min_order_price': 1.0,
        'item_id': '1',
    },
)
ONE_PLUS_ONE = pytest.param(
    {
        'type': 'one_plus_one',
        'place_ids': [1, 2],
        'starts_at': '2021-10-01T00:00:00+0300',
        'ends_at': '2021-10-10T00:00:00+0300',
        'item_ids': ['1', '2', '3'],
    },
)
NEW_PROMOS = [PLUS_FIRST_ORDERS, PLUS_HAPPY_HOURS, FREE_DELIVERY]
OLD_PROMOS = [DISCOUNT, GIFT, ONE_PLUS_ONE]
ALL_PROMOS = OLD_PROMOS + NEW_PROMOS


@pytest.mark.experiments3(filename='promos_settings_unabled_promos.json')
@pytest.mark.experiments3(filename='activate_switching_to_new_platform.json')
@pytest.mark.parametrize(
    ['request_body', 'error_code', 'error_message'],
    [
        pytest.param(
            {
                'type': 'plus_happy_hours',
                'place_ids': [1, 2],
                'starts_at': '2021-10-01T00:00:00+0300',
                'ends_at': '2021-10-10T00:00:00+0300',
                'cashback': [1.0],
                'schedule': [{'day': 2, 'from': 0, 'to': 1}],
            },
            404,
            'Promo type not presented in config',
            id='all promos, promo not in experiments',
        ),
        pytest.param(
            {
                'type': 'free_delivery',
                'place_ids': [1, 2],
                'starts_at': '2021-10-01T00:00:00+0300',
                'ends_at': '2021-10-10T00:00:00+0300',
                'min_order_price': 29,
            },
            200,
            None,
            id='new promos, promo not enables for create',
        ),
    ],
)
async def test_all_promos_service_response_4xx_if_promo_is_not_enabled(
        taxi_eats_restapp_promo,
        mockserver,
        mock_partners_info,
        mock_authorizer_allowed,
        request_body,
        error_code,
        error_message,
):
    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo',
        headers={'X-YaEda-PartnerId': '1'},
        json=request_body,
    )

    assert response.status_code == error_code
    if response.status_code == 500:
        assert response.json() == {
            'code': str(error_code),
            'message': error_message,
        }


@pytest.mark.now('2021-09-01T00:00:00+0300')
@pytest.mark.experiments3(filename='promos_settings.json')
@pytest.mark.parametrize(['request_body'], OLD_PROMOS)
async def test_old_promos_service_response_403_if_marketing_response_403(
        taxi_eats_restapp_promo,
        mockserver,
        mock_partners_info,
        mock_authorizer_allowed,
        mock_marketing_403,
        request_body,
):
    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo',
        headers={'X-YaEda-PartnerId': '1'},
        json=request_body,
    )

    assert response.status_code == 403
    assert response.json() == {'code': '403', 'message': 'Marketing 403'}


@pytest.mark.experiments3(filename='promos_settings.json')
@pytest.mark.parametrize(['request_body'], OLD_PROMOS)
async def test_old_promos_service_response_400_if_marketing_response_error(
        taxi_eats_restapp_promo,
        mockserver,
        mock_partners_info,
        mock_authorizer_allowed,
        mock_marketing_400,
        request_body,
):
    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo',
        headers={'X-YaEda-PartnerId': '1'},
        json=request_body,
    )

    assert response.status_code == 400
    assert response.json() == {'code': '400', 'message': 'Marketing 400'}


@pytest.mark.now('2021-09-01T00:00:00+0300')
@pytest.mark.experiments3(filename='promos_settings.json')
@pytest.mark.experiments3(filename='activate_switching_to_new_platform.json')
@pytest.mark.pgsql(
    'eats_restapp_promo', files=('pg_eats_restapp_promo_new_promos.sql',),
)
@pytest.mark.parametrize(['request_body'], NEW_PROMOS)
async def test_new_promos_service_response_500_if_discount_response_error(
        taxi_eats_restapp_promo,
        mockserver,
        mock_partners_info,
        mock_authorizer_allowed,
        mock_discount_500,
        request_body,
):
    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo',
        headers={'X-YaEda-PartnerId': '1'},
        json=request_body,
    )

    assert response.status_code == 500
    assert response.json() == {'code': '500', 'message': 'Internal error'}


@pytest.mark.now('2021-09-01T00:00:00+0300')
@pytest.mark.experiments3(filename='promos_settings.json')
@pytest.mark.experiments3(filename='activate_switching_to_new_platform.json')
@pytest.mark.pgsql(
    'eats_restapp_promo', files=('pg_eats_restapp_promo_errors.sql',),
)
@pytest.mark.parametrize(
    ['request_body', 'error_code', 'error_message', 'detail_message'],
    [
        pytest.param(
            {
                'type': 'plus_first_orders',
                'place_ids': [1, 2],
                'starts_at': '2021-10-01T00:00:00+0300',
                'ends_at': '2021-10-10T00:00:00+0300',
                'cashback': [29.0, 1.2, 2.0],
            },
            400,
            'Некоректные параметры акции',
            'Validation request error: cashback is less than minimum',
            id='check cashback',
        ),
        pytest.param(
            {
                'type': 'plus_happy_hours',
                'place_ids': [1, 2],
                'starts_at': '2021-10-01T00:00:00+0300',
                'ends_at': '2021-10-10T00:00:00+0300',
                'cashback': [11.0],
                'schedule': [{'day': 2, 'from': 0, 'to': 1}],
            },
            400,
            'Некоректные параметры акции',
            'Some places has not active plus.',
            id='check active plus',
        ),
        pytest.param(
            {
                'type': 'plus_happy_hours',
                'place_ids': [3],
                'starts_at': '2021-10-01T00:00:00+0300',
                'ends_at': '2021-10-10T00:00:00+0300',
                'cashback': [11.0],
                'schedule': [{'day': 2, 'from': 0, 'to': 1}],
            },
            400,
            'Некоректные параметры акции',
            'Some places has not active plus.',
            id='chack active plus for all places',
        ),
        pytest.param(
            {
                'type': 'free_delivery',
                'place_ids': [1, 2],
                'starts_at': '2021-10-01T00:00:00+0300',
                'ends_at': '2021-10-10T00:00:00+0300',
            },
            400,
            'Некоректные параметры акции',
            'Validation request error: min_order_price is missing',
            id='only free delivery, missing min_order_price',
        ),
        pytest.param(
            {
                'type': 'free_delivery',
                'place_ids': [1, 2],
                'starts_at': '2021-10-01T00:00:00+0300',
                'ends_at': '2021-10-10T00:00:00+0300',
                'min_order_price': 31,
            },
            400,
            'Некоректные параметры акции',
            'Validation request error: min_order_price is greater than maximum',
            id='only free delivery, min_order_price > settings.max_order_price',
        ),
        pytest.param(
            {
                'type': 'free_delivery',
                'place_ids': [1, 2],
                'starts_at': '2021-10-01T00:00:00+0300',
                'ends_at': '2021-10-10T00:00:00+0300',
                'min_order_price': 1,
            },
            400,
            'Некоректные параметры акции',
            'Validation request error: min_order_price is less than minimum',
            id='only free delivery, min_order_price < settings.min_order_price',
        ),
        pytest.param(
            {
                'type': 'free_delivery',
                'place_ids': [],
                'starts_at': '2021-10-01T00:00:00+0300',
                'ends_at': '2021-10-10T00:00:00+0300',
                'min_order_price': 29,
            },
            400,
            'Некоректные параметры акции',
            'place_ids empty',
            id='check empty place ids',
        ),
        pytest.param(
            {
                'type': 'plus_happy_hours',
                'place_ids': [1],
                'starts_at': '2021-10-01T00:00:00+0300',
                'ends_at': '2124-10-10T00:00:00+0300',
                'cashback': [11.0],
                'schedule': [{'day': 2, 'from': 0, 'to': 1}],
            },
            400,
            'Некоректные параметры акции',
            'Plus active dates and promo dates are incorrect.',
            id='check plus active date and promos date',
        ),
    ],
)
async def test_all_promos_service_response_4xx_for_bad_request(
        taxi_eats_restapp_promo,
        mockserver,
        mock_partners_info,
        mock_authorizer_allowed,
        request_body,
        error_code,
        error_message,
        detail_message,
):
    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo',
        headers={'X-YaEda-PartnerId': '1'},
        json=request_body,
    )

    assert response.status_code == error_code
    expected = {'code': str(error_code), 'message': error_message}
    if detail_message:
        expected['details'] = {
            'errors': [{'code': '400', 'message': detail_message}],
        }
    assert response.json() == expected


@pytest.mark.now('2021-09-01T00:00:00+0300')
@pytest.mark.experiments3(filename='promos_settings.json')
@pytest.mark.parametrize(
    ['request_body'],
    [
        pytest.param(
            {
                'type': 'discount',
                'place_ids': [1, 2],
                'starts_at': '2021-08-11T00:00:00+0300',
                'ends_at': '2021-08-09T00:00:00+0300',
                'discount': 5,
            },
            id='old promos are not checked for dates',
        ),
        pytest.param(
            {
                'type': 'discount',
                'place_ids': [],
                'starts_at': '2021-10-01T00:00:00+0300',
                'ends_at': '2021-10-10T00:00:00+0300',
                'discount': 5,
            },
            id='old promos are not checked for place_ids',
        ),
    ],
)
async def test_some_params_are_not_checked_for_old_promos(
        taxi_eats_restapp_promo,
        mockserver,
        mock_partners_info,
        mock_authorizer_allowed,
        request_body,
):
    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo',
        headers={'X-YaEda-PartnerId': '1'},
        json=request_body,
    )

    assert response.status_code == 200


@pytest.mark.experiments3(filename='promos_settings_unabled_promos.json')
@pytest.mark.parametrize(['request_body'], OLD_PROMOS)
async def test_old_promos_are_not_checked_param_can_create(
        taxi_eats_restapp_promo,
        mockserver,
        mock_partners_info,
        mock_authorizer_allowed,
        request_body,
):
    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo',
        headers={'X-YaEda-PartnerId': '1'},
        json=request_body,
    )

    assert response.status_code == 200


@pytest.mark.experiments3(filename='promos_settings.json')
@pytest.mark.parametrize(['request_body'], OLD_PROMOS)
async def test_old_promos_service_response_404_if_marketing_response_404(
        taxi_eats_restapp_promo,
        mockserver,
        mock_partners_info,
        mock_authorizer_allowed,
        mock_marketing_404,
        request_body,
):
    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo',
        headers={'X-YaEda-PartnerId': '1'},
        json=request_body,
    )

    assert response.status_code == 404
    assert response.json() == {'code': '404', 'message': 'Marketing 404'}


@pytest.mark.now('2021-09-01T00:00:00+0300')
@pytest.mark.pgsql(
    'eats_restapp_promo',
    files=('pg_eats_restapp_promos_with_oveload_promo.sql',),
)
@pytest.mark.experiments3(filename='activate_switching_to_new_platform.json')
@pytest.mark.experiments3(filename='promos_settings.json')
async def test_new_promos_service_response_409_if_promo_intersects_with_another_promo(
        taxi_eats_restapp_promo,
        mockserver,
        mock_partners_info,
        mock_authorizer_allowed,
):
    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo',
        headers={'X-YaEda-PartnerId': '1'},
        json={
            'type': 'free_delivery',
            'place_ids': [1, 2],
            'starts_at': '2021-10-01T00:00:00+0300',
            'ends_at': '2021-10-10T00:00:00+0300',
            'min_order_price': 29,
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        'code': '409',
        'message': 'Период действия акции пересекается с уже существующей',
        'details': {
            'errors': [
                {
                    'code': '409',
                    'message': 'Promo intersects with another promo 1',
                },
            ],
        },
    }


def check_request(request, expected_request):
    assert request == expected_request


def make_request(
        promo_type,
        schedule,
        min_order_price,
        item_id,
        discount,
        category_ids,
        item_ids,
        cashback,
        order_indexes=None,
        days_from_last_order=None,
        shipping_types=None,
        place_ids=None,
):
    result = dict()
    result['type'] = promo_type
    result['starts_at'] = '2021-10-10T01:00:00+00:00'
    result['ends_at'] = '2021-10-11T00:00:00+00:00'
    if place_ids is None:
        result['place_ids'] = [1, 2]
    else:
        result['place_ids'] = place_ids
    if not min_order_price is None:
        result['min_order_price'] = min_order_price
    if not item_id is None:
        result['item_id'] = item_id
    if not discount is None:
        result['discount'] = discount
    if not category_ids is None:
        result['category_ids'] = category_ids
    if not item_ids is None:
        result['item_ids'] = item_ids
    if not cashback is None:
        result['cashback'] = cashback
    if not schedule is None:
        result['schedule'] = schedule
    if not order_indexes is None:
        result['order_indexes'] = order_indexes
    if not days_from_last_order is None:
        result['days_from_last_order'] = days_from_last_order
    if not shipping_types is None:
        result['shipping_types'] = shipping_types
    return result


def make_response(
        promo_type, name, description, schedule, requirements, bonuses,
):
    result = dict()
    result['status'] = 'new'
    if name:
        result['name'] = name
    else:
        result['name'] = 'Name'
    if description:
        result['description'] = description
    else:
        result['description'] = 'Description'
    result['place_ids'] = [1, 2]
    result['type'] = promo_type
    result['starts_at'] = '2021-10-10T01:00:00+00:00'
    result['ends_at'] = '2021-10-11T00:00:00+00:00'
    result['requirements'] = requirements
    result['bonuses'] = bonuses
    if schedule:
        result['schedule'] = schedule
    return result


def make_discount_response(
        promo_type, name, description, schedule, requirements, bonuses,
):
    result = make_response(
        promo_type, name, description, schedule, requirements, bonuses,
    )
    result['id'] = 100000000
    return result


# check old promos


@pytest.mark.now('2021-10-10T00:00:00+0000')
@pytest.mark.experiments3(filename='promos_settings.json')
@pytest.mark.parametrize(
    [
        'promo_type',
        'min_order_price',
        'item_id',
        'schedule',
        'discount',
        'category_ids',
        'item_ids',
        'requirements',
        'bonuses',
    ],
    [
        pytest.param(
            'gift',
            1.0,
            '1',
            None,
            None,
            None,
            None,
            [{'min_order_price': 1.0}],
            [{'item_id': '1'}],
            id='gift without unrequired params',
        ),
        pytest.param(
            'gift',
            1.0,
            '1',
            [{'day': 1, 'from': 1, 'to': 2}, {'day': 3, 'from': 2, 'to': 1}],
            None,
            None,
            None,
            [{'min_order_price': 1.0}],
            [{'item_id': '1'}],
            id='gift with unrequired params',
        ),
        pytest.param(
            'discount',
            None,
            None,
            None,
            7,
            None,
            None,
            [{'category_ids': [1, 2], 'item_ids': ['1', '2']}],
            [{'discount': 1}],
            id='discount without unrequired params (discount не прроверяется на кратность 5)',
        ),
        pytest.param(
            'discount',
            None,
            None,
            [{'day': 1, 'from': 1, 'to': 2}],
            7,
            [1, 3],
            ['3', '4', '5'],
            [{'category_ids': [1, 2], 'item_ids': ['1', '2']}],
            [{'discount': 1}],
            id='discount with unrequired params (discount не прроверяется на кратность 5)',
        ),
        pytest.param(
            'one_plus_one',
            None,
            None,
            [{'day': 1, 'from': 1, 'to': 2}],
            None,
            None,
            ['3', '4', '5'],
            [{'category_ids': [1, 2], 'item_ids': ['1', '2']}],
            [{'discount': 1}],
            id='one_plus_one without unrequired params',
        ),
        pytest.param(
            'one_plus_one',
            None,
            None,
            None,
            None,
            None,
            ['3', '4', '5'],
            [{'category_ids': [1, 2], 'item_ids': ['1', '2']}],
            [{'discount': 1}],
            id='one_plus_one with unrequired params',
        ),
    ],
)
async def test_old_promos(
        taxi_eats_restapp_promo,
        mockserver,
        mock_partners_info,
        mock_authorizer_allowed,
        promo_type,
        min_order_price,
        item_id,
        schedule,
        discount,
        category_ids,
        item_ids,
        requirements,
        bonuses,
):
    request_body = make_request(
        promo_type,
        schedule,
        min_order_price,
        item_id,
        discount,
        category_ids,
        item_ids,
        None,
    )
    response_body = make_response(
        promo_type, None, None, schedule, requirements, bonuses,
    )

    @mockserver.json_handler(
        '/eats-restapp-marketing/4.0/restapp-front/marketing/v1/promo',
    )
    def _mock_marketing(request):
        check_request(request.json, request_body)
        response_body['id'] = 1
        return mockserver.make_response(status=200, json=response_body)

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo',
        headers={'X-YaEda-PartnerId': '1'},
        json=request_body,
    )

    assert response.status_code == 200
    assert response.json() == response_body

    assert _mock_marketing.times_called == 1


# check new promos


def check_pg(pgsql, promo_type, requirements, bonuses, schedule):
    cursor = pgsql['eats_restapp_promo'].cursor()
    cursor.execute(
        'SELECT '
        'promo_id,'
        'place_ids,'
        'promo_type,'
        'status,'
        'starts,'
        'ends,'
        'requirements,'
        'bonuses,'
        'schedule,'
        'discount_task_id,'
        'discount_ids '
        'FROM eats_restapp_promo.promos;',
    )
    pg_result = cursor.fetchall()[0]
    assert pg_result[0] == 100000000
    assert pg_result[1] == ['1', '2']
    assert pg_result[2] == promo_type
    assert pg_result[3] == 'new'
    assert pg_result[4] == datetime.datetime(
        2021,
        10,
        10,
        1,
        0,
        tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None),
    )
    assert pg_result[5] == datetime.datetime(
        2021,
        10,
        11,
        0,
        0,
        tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None),
    )
    assert pg_result[6] == {'requirements': requirements}
    assert pg_result[7] == {'bonuses': bonuses}
    if schedule:
        assert pg_result[8] == {'schedule': schedule}
    else:
        assert pg_result[8] is None
    assert pg_result[9] == '12345678-1234-1234-1234-123412345678'
    assert pg_result[10] is None


def get_expected_discount_request(load_json, promo):
    return load_json('discount_request/' + promo + '.json')


@pytest.mark.now('2021-09-01T00:00:00+0300')
@pytest.mark.pgsql(
    'eats_restapp_promo', files=('pg_eats_restapp_promo_new_promos.sql',),
)
@pytest.mark.experiments3(filename='activate_switching_to_new_platform.json')
@pytest.mark.experiments3(filename='promos_settings.json')
@pytest.mark.parametrize(
    [
        'promo',
        'promo_type',
        'min_order_price',
        'cashback',
        'schedule',
        'pg_requirements',
        'response_requirements',
        'bonuses',
        'name',
        'description',
    ],
    [
        pytest.param(
            'plus_first_orders_without_unrequired_params',
            'plus_first_orders',
            None,
            [30, 11],
            None,
            [{'has_yaplus': 1}],
            [],
            [{'cashback': [30.0, 11.0]}],
            'Повышенный кешбэк для новичков',
            'Привлечь новых пользователей, предложив им повышенный кешбек за первые заказы.',
            id='plus_first_orders without unrequired params',
        ),
        pytest.param(
            'plus_first_orders_with_unrequired_params',
            'plus_first_orders',
            1,
            [11],
            None,
            [{'min_order_price': 1.0}, {'has_yaplus': 1}],
            [{'min_order_price': 1.0}],
            [{'cashback': [11.0]}],
            'Повышенный кешбэк для новичков',
            'Привлечь новых пользователей, предложив им повышенный кешбек за первые заказы.',
            id='plus_first_orders with unrequired params',
        ),
        pytest.param(
            'plus_happy_hours_without_unrequired_params',
            'plus_happy_hours',
            None,
            [11],
            [{'day': 1, 'from': 1, 'to': 2}, {'day': 3, 'from': 0, 'to': 24}],
            [{'has_yaplus': 1}],
            [],
            [{'cashback': [11.0]}],
            'Повышенный кешбэк в счастливые часы',
            'Предложите повышенный кешбек за заказ в мёртвые часы.',
            id='plus_happy_hours without unrequired params',
        ),
        pytest.param(
            'plus_happy_hours_with_unrequired_params',
            'plus_happy_hours',
            1,
            [11],
            [{'day': 1, 'from': 1, 'to': 2}, {'day': 3, 'from': 0, 'to': 24}],
            [{'min_order_price': 1.0}, {'has_yaplus': 1}],
            [{'min_order_price': 1.0}],
            [{'cashback': [11.0]}],
            'Повышенный кешбэк в счастливые часы',
            'Предложите повышенный кешбек за заказ в мёртвые часы.',
            id='plus_happy_hours with unrequired params',
        ),
        pytest.param(
            'free_delivery_without_unrequired_params',
            'free_delivery',
            5,
            None,
            None,
            [
                {'brand_orders_count': [{'end': 1, 'start': 0}]},
                {'min_order_price': 5.0},
                {'delivery_methods': ['pedestrian']},
            ],
            [{'order_indexes': [1]}, {'min_order_price': 5.0}],
            [],
            'Бесплатная доставка',
            'Предложите бесплатную доставку.',
            id='free_delivery without unrequired params',
        ),
        pytest.param(
            'free_delivery_with_unrequired_params',
            'free_delivery',
            5,
            None,
            [
                {'day': 1, 'from': 1, 'to': 2},
                {'day': 3, 'from': 0, 'to': 1440},
            ],
            [
                {'brand_orders_count': [{'end': 1, 'start': 0}]},
                {'min_order_price': 5.0},
                {'delivery_methods': ['pedestrian']},
            ],
            [{'order_indexes': [1]}, {'min_order_price': 5.0}],
            [],
            'Бесплатная доставка',
            'Предложите бесплатную доставку.',
            id='free_delivery with unrequired params',
        ),
        pytest.param(
            'free_delivery_without_unrequired_params_table',
            'free_delivery',
            5,
            None,
            None,
            [
                {'brand_orders_count': [{'end': 1, 'start': 0}]},
                {'min_order_price': 5.0},
                {'delivery_methods': ['pedestrian']},
            ],
            [{'order_indexes': [1]}, {'min_order_price': 5.0}],
            [],
            'Бесплатная доставка',
            'Предложите бесплатную доставку.',
            marks=[
                pytest.mark.config(
                    EATS_RESTAPP_PROMO_FREE_DELIVERY_CREATE_SETTINGS=FREE_DELIVERY_CREATE_SETTINGS_CHECK_OFF,
                ),
            ],
            id='free_delivery without unrequired params with table value',
        ),
        pytest.param(
            'free_delivery_with_unrequired_params_table',
            'free_delivery',
            5,
            None,
            [
                {'day': 1, 'from': 1, 'to': 2},
                {'day': 3, 'from': 0, 'to': 1440},
            ],
            [
                {'brand_orders_count': [{'end': 1, 'start': 0}]},
                {'min_order_price': 5.0},
                {'delivery_methods': ['pedestrian']},
            ],
            [{'order_indexes': [1]}, {'min_order_price': 5.0}],
            [],
            'Бесплатная доставка',
            'Предложите бесплатную доставку.',
            marks=[
                pytest.mark.config(
                    EATS_RESTAPP_PROMO_FREE_DELIVERY_CREATE_SETTINGS=FREE_DELIVERY_CREATE_SETTINGS_CHECK_OFF,
                ),
            ],
            id='free_delivery with unrequired params with table value',
        ),
    ],
)
async def test_new_promos(
        taxi_eats_restapp_promo,
        mockserver,
        mock_partners_info,
        mock_authorizer_allowed,
        pgsql,
        load_json,
        promo,
        promo_type,
        min_order_price,
        cashback,
        schedule,
        pg_requirements,
        response_requirements,
        bonuses,
        name,
        description,
):
    expected_discount_request = get_expected_discount_request(load_json, promo)

    @mockserver.json_handler('/eats-discounts/v1/partners/discounts/create')
    def _mock_eats_discounts(request):
        assert request.json == expected_discount_request
        response_body = {'task_id': '12345678-1234-1234-1234-123412345678'}
        return mockserver.make_response(status=200, json=response_body)

    request_body = make_request(
        promo_type,
        schedule,
        min_order_price,
        None,
        None,
        None,
        None,
        cashback,
    )
    response_body = make_discount_response(
        promo_type,
        name,
        description,
        schedule,
        response_requirements,
        bonuses,
    )

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo',
        headers={'X-YaEda-PartnerId': '1'},
        json=request_body,
    )

    assert response.status_code == 200
    assert response.json() == response_body

    assert _mock_eats_discounts.times_called == 1

    check_pg(pgsql, promo_type, pg_requirements, bonuses, schedule)


@pytest.mark.now('2021-09-01T00:00:00+0300')
@pytest.mark.pgsql(
    'eats_restapp_promo', files=('pg_eats_restapp_promo_new_promos.sql',),
)
@pytest.mark.experiments3(filename='promos_settings_with_max_order_price.json')
@pytest.mark.experiments3(filename='activate_switching_to_new_platform.json')
@pytest.mark.parametrize(
    [
        'promo_type',
        'min_order_price',
        'cashback',
        'schedule',
        'max_order_price',
    ],
    [
        pytest.param(
            'plus_first_orders', 1, [30], None, '15', id='plus_first_orders',
        ),
        pytest.param(
            'plus_happy_hours',
            1,
            [11],
            [{'day': 1, 'from': 1, 'to': 2}, {'day': 3, 'from': 0, 'to': 24}],
            '15',
            id='plus_happy_hours',
        ),
        pytest.param(
            'free_delivery', 5, None, None, '100', id='free_delivery',
        ),
    ],
)
async def test_new_promos_validate_max_order_price(
        taxi_eats_restapp_promo,
        mockserver,
        mock_partners_info,
        mock_authorizer_allowed,
        pgsql,
        promo_type,
        min_order_price,
        cashback,
        schedule,
        max_order_price,
):
    @mockserver.json_handler('/eats-discounts' '/v1/partners/discounts/create')
    def _mock_eats_discounts(request):
        for discount_data in request.json['discounts_data']:
            for role in discount_data['rules']:
                if role['condition_name'] == 'check':
                    assert role['values'][0]['end'] == max_order_price
        response_body = {'task_id': '12345678-1234-1234-1234-123412345678'}
        return mockserver.make_response(status=200, json=response_body)

    request_body = make_request(
        promo_type,
        schedule,
        min_order_price,
        None,
        None,
        None,
        None,
        cashback,
    )

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo',
        headers={'X-YaEda-PartnerId': '1'},
        json=request_body,
    )

    assert response.status_code == 200

    assert _mock_eats_discounts.times_called == 1


@pytest.mark.now('2021-09-01T00:00:00+0300')
@pytest.mark.pgsql(
    'eats_restapp_promo', files=('pg_eats_restapp_promo_new_promos.sql',),
)
@pytest.mark.experiments3(filename='activate_switching_to_new_platform.json')
@pytest.mark.experiments3(filename='promos_settings.json')
@pytest.mark.parametrize(
    ['promo_type', 'min_order_price', 'cashback', 'schedule'],
    [
        pytest.param(
            'plus_first_orders', 1, [30], None, id='plus_first_orders',
        ),
        pytest.param(
            'plus_happy_hours',
            1,
            [11],
            [{'day': 1, 'from': 1, 'to': 2}, {'day': 3, 'from': 0, 'to': 24}],
            id='plus_happy_hours',
        ),
        pytest.param('free_delivery', 5, None, None, id='free_delivery'),
    ],
)
async def test_new_promos_validate_max_order_price_if_it_not_in_settings(
        taxi_eats_restapp_promo,
        mockserver,
        mock_partners_info,
        mock_authorizer_allowed,
        pgsql,
        promo_type,
        min_order_price,
        cashback,
        schedule,
):
    @mockserver.json_handler('/eats-discounts' '/v1/partners/discounts/create')
    def _mock_eats_discounts(request):
        for discount_data in request.json['discounts_data']:
            for rule in discount_data['rules']:
                if rule['condition_name'] == 'check':
                    assert rule['values'][0]['end'] == '1000000'
        response_body = {'task_id': '12345678-1234-1234-1234-123412345678'}
        return mockserver.make_response(status=200, json=response_body)

    request_body = make_request(
        promo_type,
        schedule,
        min_order_price,
        None,
        None,
        None,
        None,
        cashback,
    )

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo',
        headers={'X-YaEda-PartnerId': '1'},
        json=request_body,
    )

    assert response.status_code == 200

    assert _mock_eats_discounts.times_called == 1


@pytest.mark.now('2021-09-01T00:00:00+0300')
@pytest.mark.pgsql(
    'eats_restapp_promo', files=('pg_eats_restapp_promo_new_promos.sql',),
)
@pytest.mark.experiments3(filename='activate_switching_to_new_platform.json')
@pytest.mark.experiments3(filename='promos_settings.json')
@pytest.mark.parametrize(
    [
        'promo_type',
        'min_order_price',
        'cashback',
        'request_schedule',
        'expected_schedule',
    ],
    [
        pytest.param(
            'plus_first_orders',
            1,
            [30],
            None,
            [[{'exclude': False, 'day': [1, 2, 3, 4, 5, 6, 7]}]],
            id='plus_first_orders without schedule',
        ),
        pytest.param(
            'free_delivery',
            5,
            None,
            None,
            [[{'exclude': False, 'day': [1, 2, 3, 4, 5, 6, 7]}]],
            id='free_delivery without schedule',
        ),
        pytest.param(
            'plus_first_orders',
            1,
            [30],
            [{'day': 1, 'from': 1, 'to': 2}, {'day': 3, 'from': 0, 'to': 24}],
            [[{'exclude': False, 'day': [1, 2, 3, 4, 5, 6, 7]}]],
            id='plus_first_orders return default schedule',
        ),
        pytest.param(
            'free_delivery',
            5,
            None,
            [{'day': 1, 'from': 1, 'to': 2}, {'day': 3, 'from': 0, 'to': 24}],
            [
                [
                    {'exclude': False, 'day': [3]},
                    {'exclude': False, 'daytime': [{'to': '00:24:00'}]},
                ],
                [
                    {'exclude': False, 'day': [1]},
                    {
                        'exclude': False,
                        'daytime': [{'from': '00:01:00', 'to': '00:02:00'}],
                    },
                ],
            ],
            id='free_delivery with from=0',
        ),
        pytest.param(
            'free_delivery',
            5,
            None,
            [{'day': 1, 'from': 5, 'to': 1440}],
            [
                [
                    {'exclude': False, 'day': [1]},
                    {
                        'exclude': False,
                        'daytime': [{'from': '00:05:00', 'to': '23:59:59'}],
                    },
                ],
            ],
            id='free_delivery with to=1440',
        ),
        pytest.param(
            'free_delivery',
            5,
            None,
            [{'day': 1, 'from': 1, 'to': 2}, {'day': 3, 'from': 1, 'to': 2}],
            [
                [
                    {'exclude': False, 'day': [1, 3]},
                    {
                        'exclude': False,
                        'daytime': [{'from': '00:01:00', 'to': '00:02:00'}],
                    },
                ],
            ],
            id='free_delivery grouped_schedule',
        ),
        pytest.param(
            'free_delivery',
            5,
            None,
            [{'day': 3, 'from': 0, 'to': 1440}],
            [
                [
                    {'exclude': False, 'day': [3]},
                    {'exclude': False, 'daytime': [{'to': '23:59:59'}]},
                ],
            ],
            id='free_delivery with to 1440 and from 0',
        ),
    ],
)
async def test_new_promos_validate_schedule(
        taxi_eats_restapp_promo,
        mockserver,
        mock_partners_info,
        mock_authorizer_allowed,
        pgsql,
        promo_type,
        min_order_price,
        cashback,
        request_schedule,
        expected_schedule,
):
    @mockserver.json_handler('/eats-discounts' '/v1/partners/discounts/create')
    def _mock_eats_discounts(request):
        for discount_data in request.json['discounts_data']:
            for schedule_id in range(
                    len(
                        discount_data['data']['discount'][
                            'values_with_schedules'
                        ],
                    ),
            ):
                assert (
                    discount_data['data']['discount']['values_with_schedules'][
                        schedule_id
                    ]['schedule']['intervals']
                    == expected_schedule[schedule_id]
                )
        response_body = {'task_id': '12345678-1234-1234-1234-123412345678'}
        return mockserver.make_response(status=200, json=response_body)

    request_body = make_request(
        promo_type,
        request_schedule,
        min_order_price,
        None,
        None,
        None,
        None,
        cashback,
    )

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo',
        headers={'X-YaEda-PartnerId': '1'},
        json=request_body,
    )

    assert response.status_code == 200

    assert _mock_eats_discounts.times_called == 1


@pytest.mark.now('2021-09-01T00:00:00+0300')
@pytest.mark.pgsql(
    'eats_restapp_promo', files=('pg_eats_restapp_promo_new_promos.sql',),
)
@pytest.mark.experiments3(filename='activate_switching_to_new_platform.json')
@pytest.mark.experiments3(filename='promos_settings.json')
@pytest.mark.parametrize(
    ['promo_type', 'min_order_price', 'cashback'],
    [
        pytest.param('plus_happy_hours', 1, [11], id='plus_happy_hours'),
        pytest.param('free_delivery', 5, None, id='free_delivery'),
    ],
)
async def test_new_promos_service_response_500_if_from_eq_to_in_schedule(
        taxi_eats_restapp_promo,
        mockserver,
        mock_partners_info,
        mock_authorizer_allowed,
        pgsql,
        promo_type,
        min_order_price,
        cashback,
):
    @mockserver.json_handler('/eats-discounts' '/v1/partners/discounts/create')
    def _mock_eats_discounts(request):
        response_body = {'task_id': '12345678-1234-1234-1234-123412345678'}
        return mockserver.make_response(status=200, json=response_body)

    schedule = [
        {'day': 1, 'from': 0, 'to': 1440},
        {'day': 3, 'from': 2, 'to': 2},
    ]
    request_body = make_request(
        promo_type,
        schedule,
        min_order_price,
        None,
        None,
        None,
        None,
        cashback,
    )

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo',
        headers={'X-YaEda-PartnerId': '1'},
        json=request_body,
    )

    assert response.status_code == 500


@pytest.mark.now('2021-09-01T00:00:00+0300')
@pytest.mark.experiments3(filename='promos_settings.json')
@pytest.mark.experiments3(filename='activate_switching_to_new_platform.json')
@pytest.mark.eats_catalog_storage_cache(
    file='eats_catalog_storage_cache_data.json',
)
@pytest.mark.parametrize(
    [
        'promo_type',
        'discounts_request',
        'schedule',
        'min_order_price',
        'item_id',
        'item_ids',
        'discount',
        'order_indexes',
        'days_from_last_order',
        'shipping_types',
        'requirements',
        'pg_requirements',
        'bonuses',
        'pg_bonuses',
        'name',
        'description',
    ],
    [
        pytest.param(
            'one_plus_one',
            'one_plus_one_without_unrequired_params',
            None,
            None,
            None,
            ['3', '4', '5', '7', '8'],
            None,
            None,
            None,
            None,
            [{'item_ids': ['3', '4', '5']}],
            [{'item_ids': ['3', '4', '5']}],
            [],
            [],
            'Два по цене одного',
            'Увеличить количество заказов или познакомить пользователей c новыми блюдами.',
            id='one_plus_one without unrequired params',
        ),
        pytest.param(
            'one_plus_one',
            'one_plus_one_with_unrequired_params',
            [{'day': 1, 'from': 15, 'to': 600}],
            None,
            None,
            ['3', '4', '5'],
            None,
            [1, 2, 3],
            5,
            ['delivery'],
            [
                {'days_from_last_order': 5},
                {'order_indexes': [1, 2, 3]},
                {'item_ids': ['3', '4', '5']},
                {'shipping_types': ['delivery']},
            ],
            [
                {'days_from_last_order': 5},
                {
                    'brand_orders_count': [
                        {'end': 1, 'start': 0},
                        {'end': 2, 'start': 1},
                        {'end': 3, 'start': 2},
                    ],
                },
                {'item_ids': ['3', '4', '5']},
                {'shipping_types': ['delivery']},
            ],
            [],
            [],
            'Два по цене одного',
            'Увеличить количество заказов или познакомить пользователей c новыми блюдами.',
            id='one_plus_one with unrequired params',
        ),
        pytest.param(
            'gift',
            'gift_without_unrequired_params',
            None,
            123.456,
            '1',
            None,
            None,
            None,
            None,
            None,
            [{'min_order_price': 123.46}],
            [{'min_order_price': 123.46}],
            [{'item_id': '1'}],
            [{'item_id': '1'}],
            'Блюдо в подарок',
            'Познакомить пользователей с новыми блюдами или поднять средний чек.',
            id='gift without unrequired params',
        ),
        pytest.param(
            'gift',
            'gift_with_unrequired_params',
            [{'day': 1, 'from': 15, 'to': 600}],
            123.0,
            '1',
            None,
            None,
            [1],
            7,
            ['pickup'],
            [
                {'min_order_price': 123.0},
                {'order_indexes': [1]},
                {'days_from_last_order': 7},
                {'shipping_types': ['pickup']},
            ],
            [
                {'min_order_price': 123.0},
                {'brand_orders_count': [{'end': 1, 'start': 0}]},
                {'days_from_last_order': 7},
                {'shipping_types': ['pickup']},
            ],
            [{'item_id': '1'}],
            [{'item_id': '1'}],
            'Блюдо в подарок',
            'Познакомить пользователей с новыми блюдами или поднять средний чек.',
            id='gift with unrequired params',
        ),
        pytest.param(
            'discount',
            'discount_without_unrequired_params',
            None,
            None,
            None,
            None,
            7,
            None,
            None,
            None,
            [],
            [],
            [{'discount': 7}],
            [{'discount': 7, 'type': 'fraction'}],
            'Скидка на меню или некоторые позиции',
            'Увеличить выручку ресторана или поднять средний чек.',
            id='discount without unrequired params',
        ),
        pytest.param(
            'discount',
            'discount_with_unrequired_params',
            [{'day': 1, 'from': 15, 'to': 600}],
            None,
            None,
            ['3', '4', '5'],
            7,
            None,
            4,
            None,
            [{'item_ids': ['3', '4', '5']}, {'days_from_last_order': 4}],
            [{'item_ids': ['3', '4', '5']}, {'days_from_last_order': 4}],
            [{'discount': 7}],
            [{'discount': 7, 'type': 'fraction'}],
            'Скидка на меню или некоторые позиции',
            'Увеличить выручку ресторана или поднять средний чек.',
            id='discount with unrequired params',
        ),
    ],
)
async def test_promos_new_platform(
        taxi_eats_restapp_promo,
        mockserver,
        mock_partners_info,
        mock_authorizer_allowed,
        mock_eats_restapp_core,
        pgsql,
        load_json,
        promo_type,
        discounts_request,
        schedule,
        min_order_price,
        item_id,
        item_ids,
        discount,
        order_indexes,
        days_from_last_order,
        shipping_types,
        requirements,
        pg_requirements,
        bonuses,
        pg_bonuses,
        name,
        description,
):
    expected_discount_request = get_expected_discount_request(
        load_json, discounts_request,
    )

    @mockserver.json_handler('/eats-discounts/v1/partners/discounts/create')
    def _mock_eats_discounts(request):
        assert request.json == expected_discount_request
        response_body = {'task_id': '12345678-1234-1234-1234-123412345678'}
        return mockserver.make_response(status=200, json=response_body)

    request_body = make_request(
        promo_type,
        schedule,
        min_order_price,
        item_id,
        discount,
        None,
        item_ids,
        None,
        order_indexes,
        days_from_last_order,
        shipping_types,
    )
    response_body = make_discount_response(
        promo_type, name, description, schedule, requirements, bonuses,
    )

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo',
        headers={'X-YaEda-PartnerId': '1'},
        json=request_body,
    )

    assert response.status_code == 200
    assert response.json() == response_body

    assert _mock_eats_discounts.times_called == 1

    check_pg(pgsql, promo_type, pg_requirements, pg_bonuses, schedule)


@pytest.mark.now('2021-09-01T00:00:00+0300')
@pytest.mark.experiments3(filename='promos_settings.json')
@pytest.mark.experiments3(filename='promos_checks_settings.json')
@pytest.mark.experiments3(filename='activate_switching_to_new_platform.json')
@pytest.mark.parametrize(
    [
        'promo_type',
        'schedule',
        'min_order_price',
        'item_id',
        'item_ids',
        'discount',
        'order_indexes',
        'days_from_last_order',
        'shipping_types',
        'message',
        'details_message',
    ],
    [
        pytest.param(
            'one_plus_one',
            [{'day': 1, 'from': 15, 'to': 600}],
            None,
            None,
            ['3', '4', '5'],
            None,
            [1, 2, 4, 3],
            None,
            None,
            'Некоректные параметры акции',
            'Invalid brand_orders_count: brand_order_count=4, available brand_orders_count=[1, 2, 3]',
            id='one_plus_one with invalid order_indexes',
        ),
        pytest.param(
            'gift',
            [{'day': 1, 'from': 15, 'to': 600}],
            123.0,
            '1',
            None,
            None,
            [4],
            None,
            None,
            'Некоректные параметры акции',
            'Invalid brand_orders_count: brand_order_count=4, available brand_orders_count=[1, 2, 3]',
            id='gift with invalid order_indexes',
        ),
        pytest.param(
            'discount',
            [{'day': 1, 'from': 15, 'to': 600}],
            None,
            None,
            ['3', '4', '5'],
            7,
            [1, 2, 4],
            None,
            None,
            'Некоректные параметры акции',
            'Invalid brand_orders_count: brand_order_count=4, available brand_orders_count=[1, 2, 3]',
            id='discount with invalid order_indexes',
        ),
        pytest.param(
            'one_plus_one',
            [{'day': 1, 'from': 15, 'to': 600}],
            None,
            None,
            ['3', '4', '5'],
            None,
            None,
            8,
            None,
            'Некоректные параметры акции',
            'Invalid days_from_last_ordert: day=8, available days=[4, 5, 7]',
            id='one_plus_one with invalid days_from_last_order',
        ),
        pytest.param(
            'gift',
            [{'day': 1, 'from': 15, 'to': 600}],
            123.0,
            '1',
            None,
            None,
            None,
            3,
            None,
            'Некоректные параметры акции',
            'Invalid days_from_last_ordert: day=3, available days=[4, 5, 7]',
            id='gift with invalid days_from_last_order',
        ),
        pytest.param(
            'discount',
            [{'day': 1, 'from': 15, 'to': 600}],
            None,
            None,
            ['3', '4', '5'],
            7,
            None,
            6,
            None,
            'Некоректные параметры акции',
            'Invalid days_from_last_ordert: day=6, available days=[4, 5, 7]',
            id='discount with invalid days_from_last_order',
        ),
        pytest.param(
            'one_plus_one',
            [{'day': 1, 'from': 15, 'to': 600}],
            None,
            None,
            ['3', '4', '5'],
            None,
            None,
            None,
            ['delivery', 'pickup', 'other'],
            'Некоректные параметры акции',
            'Invalid shipping_type: shipping_type=other, available sipping_types=[pickup, delivery]',
            id='one_plus_one with invalid shipping_types',
        ),
        pytest.param(
            'gift',
            [{'day': 1, 'from': 15, 'to': 600}],
            123.0,
            '1',
            None,
            None,
            None,
            None,
            ['other'],
            'Некоректные параметры акции',
            'Invalid shipping_type: shipping_type=other, available sipping_types=[pickup, delivery]',
            id='gift with invalid shipping_types',
        ),
        pytest.param(
            'discount',
            [{'day': 1, 'from': 15, 'to': 600}],
            None,
            None,
            ['3', '4', '5'],
            7,
            None,
            None,
            ['other', 'pickup'],
            'Некоректные параметры акции',
            'Invalid shipping_type: shipping_type=other, available sipping_types=[pickup, delivery]',
            id='discount with invalid shipping_types',
        ),
        pytest.param(
            'discount',
            [{'day': 1, 'from': 15, 'to': 600}],
            None,
            None,
            ['3', '4', '5'],
            4,
            None,
            None,
            None,
            'Некоректные параметры акции',
            'Validation request error: discount is less than minimum',
            id='discount with invalid discount',
        ),
        pytest.param(
            'discount',
            [{'day': 1, 'from': 15, 'to': 600}],
            None,
            None,
            ['3', '4', '6'],
            6,
            None,
            None,
            None,
            'Некоректные параметры акции',
            'Not enough items in enabled categories, count=2',
            id='discount with invalid items',
        ),
        pytest.param(
            'gift',
            [{'day': 1, 'from': 15, 'to': 600}],
            123.0,
            '6',
            None,
            None,
            None,
            None,
            None,
            'Некоректные параметры акции',
            'Not enough items in enabled categories, count=0',
            id='gift with invalid items',
        ),
        pytest.param(
            'one_plus_one',
            [{'day': 1, 'from': 15, 'to': 600}],
            None,
            None,
            ['3', '4', '6'],
            None,
            None,
            None,
            None,
            'Некоректные параметры акции',
            'Not enough items in enabled categories, count=2',
            id='one_plus_one with invalid items',
        ),
        pytest.param(
            'gift',
            [{'day': 1, 'from': 15, 'to': 600}],
            1001.0,
            '1',
            None,
            None,
            None,
            None,
            None,
            'Некоректные параметры акции',
            'Place avarege cheque is less then min_order_price',
            id='gift with invalid min_order_price',
        ),
        pytest.param(
            'gift',
            [{'day': 1, 'from': 15, 'to': 600}],
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            'Некоректные параметры акции',
            'Validation request error: min_order_price is missing',
            id='gift with missing min_order_price',
        ),
        pytest.param(
            'gift',
            [{'day': 1, 'from': 15, 'to': 600}],
            1001.0,
            None,
            None,
            None,
            None,
            None,
            None,
            'Некоректные параметры акции',
            'Validation request error: item_id is missing',
            id='gift with missing item_id',
        ),
        pytest.param(
            'one_plus_one',
            [{'day': 1, 'from': 15, 'to': 600}],
            None,
            None,
            ['3', '4', '5'],
            None,
            [],
            None,
            None,
            'Некоректные параметры акции',
            'Validation request error: order_indexes size is less than minimum',
            id='one_plus_one with invalid order_indexes size',
        ),
        pytest.param(
            'one_plus_one',
            [{'day': 1, 'from': 15, 'to': 600}],
            None,
            None,
            ['3', '4', '5'],
            None,
            None,
            -1,
            None,
            'Некоректные параметры акции',
            'Validation request error: days_from_last_order is less than minimum',
            id='one_plus_one with invalid days_from_last_orders',
        ),
        pytest.param(
            'one_plus_one',
            [{'day': 1, 'from': 15, 'to': 600}],
            None,
            None,
            ['3', '4', '5'],
            None,
            None,
            None,
            [],
            'Некоректные параметры акции',
            'Validation request error: shipping_types size is less than minimum',
            id='one_plus_one with invalid shipping_types size',
        ),
        pytest.param(
            'one_plus_one',
            [{'day': 1, 'from': 15, 'to': 600}],
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            'Некоректные параметры акции',
            'Validation request error: item_ids is missing',
            id='one_plus_one with missing item_ids',
        ),
        pytest.param(
            'one_plus_one',
            [{'day': 1, 'from': 15, 'to': 600}],
            None,
            None,
            ['3', '4'],
            None,
            None,
            None,
            None,
            'Некоректные параметры акции',
            'Validation request error: item_ids size is less than minimum',
            id='one_plus_one with invalid item_ids size',
        ),
        pytest.param(
            'one_plus_one',
            [{'day': 1, 'from': 15, 'to': 600}],
            None,
            None,
            ['7', '8', '9'],
            None,
            None,
            None,
            None,
            'Некоректные параметры акции',
            'No available items',
            id='one_plus_one with empty available items',
        ),
        pytest.param(
            'discount',
            [{'day': 1, 'from': 15, 'to': 600}],
            None,
            None,
            ['3', '4', '6'],
            None,
            None,
            None,
            None,
            'Некоректные параметры акции',
            'Validation request error: discount is missing',
            id='discount with missed discount',
        ),
        pytest.param(
            'discount',
            [{'day': 1, 'from': 15, 'to': 600}],
            None,
            None,
            None,
            4,
            None,
            None,
            None,
            'Некоректные параметры акции',
            'Validation request error: discount is less than minimum',
            id='discount with discount less than minimum',
        ),
        pytest.param(
            'discount',
            [{'day': 1, 'from': 15, 'to': 600}],
            None,
            None,
            None,
            42,
            None,
            None,
            None,
            'Некоректные параметры акции',
            'Validation request error: discount is greater than maximum',
            id='discount with discount greater than maximum',
        ),
    ],
)
async def test_promos_new_platform_check_validation_errors(
        taxi_eats_restapp_promo,
        mockserver,
        mock_partners_info,
        mock_authorizer_allowed,
        mock_eats_restapp_core,
        pgsql,
        load_json,
        promo_type,
        schedule,
        min_order_price,
        item_id,
        item_ids,
        discount,
        order_indexes,
        days_from_last_order,
        shipping_types,
        message,
        details_message,
):
    @mockserver.json_handler('/eats-discounts/v1/partners/discounts/create')
    def _mock_eats_discounts(request):
        response_body = {'task_id': '12345678-1234-1234-1234-123412345678'}
        return mockserver.make_response(status=200, json=response_body)

    request_body = make_request(
        promo_type,
        schedule,
        min_order_price,
        item_id,
        discount,
        None,
        item_ids,
        None,
        order_indexes,
        days_from_last_order,
        shipping_types,
    )

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo',
        headers={'X-YaEda-PartnerId': '1'},
        json=request_body,
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': message,
        'details': {'errors': [{'code': '400', 'message': details_message}]},
    }


@pytest.mark.now('2021-09-01T00:00:00+0300')
@pytest.mark.experiments3(filename='promo_settings_validation_place_ids.json')
@pytest.mark.experiments3(filename='activate_switching_to_new_platform.json')
@pytest.mark.parametrize(
    [
        'promo_type',
        'schedule',
        'min_order_price',
        'item_id',
        'item_ids',
        'place_ids',
        'message',
        'details_message',
    ],
    [
        pytest.param(
            'gift',
            [{'day': 1, 'from': 15, 'to': 600}],
            99.0,
            '1',
            None,
            [],
            'Некоректные параметры акции',
            'place_ids empty',
            id='promo with empty place_ids',
        ),
        pytest.param(
            'one_plus_one',
            [{'day': 1, 'from': 15, 'to': 600}],
            None,
            None,
            ['3', '4', '5'],
            [1, 2],
            'Некоректные параметры акции',
            'promo for multiple places is disables',
            id='promo with some place_ids if multiply place is invailable',
        ),
    ],
)
async def test_promos_new_platform_check_place_ids_size(
        taxi_eats_restapp_promo,
        mockserver,
        mock_partners_info,
        mock_authorizer_allowed,
        mock_eats_restapp_core,
        pgsql,
        load_json,
        promo_type,
        schedule,
        min_order_price,
        item_id,
        item_ids,
        place_ids,
        message,
        details_message,
):

    request_body = make_request(
        promo_type,
        schedule,
        min_order_price,
        item_id,
        None,
        None,
        item_ids,
        None,
        None,
        None,
        None,
        place_ids,
    )

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo',
        headers={'X-YaEda-PartnerId': '1'},
        json=request_body,
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': message,
        'details': {'errors': [{'code': '400', 'message': details_message}]},
    }


@pytest.mark.now('2022-01-01T00:00:00+0300')
@pytest.mark.pgsql(
    'eats_restapp_promo',
    files=('pg_eats_restapp_promos_with_oveload_promo.sql',),
)
@pytest.mark.experiments3(filename='promos_settings.json')
@pytest.mark.experiments3(filename='activate_switching_to_new_platform.json')
@pytest.mark.parametrize(
    [
        'promo_type',
        'place_ids',
        'starts_at',
        'ends_at',
        'item_ids',
        'status_code',
        'message',
        'details_message',
    ],
    [
        pytest.param(
            'one_plus_one',
            [1, 2],
            '2022-01-30T00:00:00+0300',
            '2022-02-22T00:00:00+0300',
            ['3', '4', '5'],
            200,
            None,
            None,
            id='one_plus_one should not conflict',
        ),
        pytest.param(
            'discount',
            [1, 2],
            '2022-01-30T00:00:00+0300',
            '2022-02-22T00:00:00+0300',
            ['3', '4', '5'],
            200,
            None,
            None,
            id='discount should not conflict',
        ),
        pytest.param(
            'gift',
            [1, 2],
            '2022-01-30T00:00:00+0300',
            '2022-02-01T00:00:00+0300',
            ['3', '4', '5'],
            200,
            None,
            None,
            id='gift should not conflict for period before',
        ),
        pytest.param(
            'gift',
            [1, 2],
            '2022-02-20T00:00:00+0300',
            '2022-02-21T00:00:00+0300',
            ['3', '4', '5'],
            200,
            None,
            None,
            id='gift should not conflict for period after',
        ),
        pytest.param(
            'gift',
            [1, 2],
            '2022-02-01T00:00:00+0300',
            '2022-02-11T00:00:00+0300',
            ['3', '4', '5'],
            200,
            None,
            None,
            id='gift should not conflict if intersects with completed',
        ),
        pytest.param(
            'gift',
            [4, 5],
            '2022-02-13T00:00:00+0300',
            '2022-02-22T00:00:00+0300',
            ['3', '4', '5'],
            200,
            None,
            None,
            id='gift should not conflict for different places',
        ),
        pytest.param(
            'gift',
            [1, 2],
            '2022-02-13T00:00:00+0300',
            '2022-02-22T00:00:00+0300',
            ['3', '4', '5'],
            409,
            'Период действия акции пересекается с уже существующей',
            'Promo intersects with another promo 3',
            id='gift should conflict if intersects with enabled',
        ),
        pytest.param(
            'discount',
            [1, 2],
            '2022-03-01T00:00:00+0300',
            '2022-03-02T00:00:00+0300',
            None,
            409,
            'Период действия акции пересекается с уже существующей',
            'Promo intersects with another promo 4',
            id='discount should conflict if request_item_ids empty and pg_item_ids empty',
        ),
        pytest.param(
            'discount',
            [1, 2],
            '2022-03-01T00:00:00+0300',
            '2022-03-02T00:00:00+0300',
            ['3', '4', '5'],
            409,
            'Период действия акции пересекается с уже существующей',
            'Promo intersects with another promo 4',
            id='discount should conflict if request_item_ids not empty and pg_item_ids empty',
        ),
        pytest.param(
            'discount',
            [1, 2],
            '2022-03-03T00:00:00+0300',
            '2022-03-04T00:00:00+0300',
            None,
            409,
            'Период действия акции пересекается с уже существующей',
            'Promo intersects with another promo 5',
            id='one_plus_one should conflict if request_item_ids empty and pg_item_ids not empty',
        ),
        pytest.param(
            'one_plus_one',
            [1, 2],
            '2022-03-01T00:00:00+0300',
            '2022-03-02T00:00:00+0300',
            ['3', '4', '10'],
            409,
            'Период действия акции пересекается с уже существующей',
            'Promo intersects with another promo 6',
            id='one_plus_one should conflict if item_ids intersects',
        ),
        pytest.param(
            'one_plus_one',
            [1, 2],
            '2022-03-01T00:00:00+0300',
            '2022-03-02T00:00:00+0300',
            ['3', '4', '5'],
            200,
            None,
            None,
            id='one_plus_one should not conflict if item_ids not intersects',
        ),
    ],
)
async def test_promos_new_platform_response_409_if_intersects_with_enabled(
        taxi_eats_restapp_promo,
        mockserver,
        mock_partners_info,
        mock_authorizer_allowed,
        mock_eats_restapp_core,
        promo_type,
        place_ids,
        starts_at,
        ends_at,
        item_ids,
        status_code,
        message,
        details_message,
):
    request_body = {
        'type': promo_type,
        'place_ids': place_ids,
        'starts_at': starts_at,
        'ends_at': ends_at,
        'min_order_price': 100,
        'item_id': '1',
        'discount': 20,
    }
    if not item_ids is None:
        request_body['item_ids'] = item_ids
    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo',
        headers={'X-YaEda-PartnerId': '1'},
        json=request_body,
    )

    assert response.status_code == status_code
    if message:
        assert response.json() == {
            'code': '409',
            'message': message,
            'details': {
                'errors': [{'code': '409', 'message': details_message}],
            },
        }


@pytest.mark.now('2021-09-01T00:00:00+0300')
@pytest.mark.experiments3(filename='promos_settings_custom_titles.json')
@pytest.mark.experiments3(filename='activate_switching_to_new_platform.json')
async def test_promos_custom_titles(
        taxi_eats_restapp_promo,
        mockserver,
        mock_partners_info,
        mock_authorizer_allowed,
        mock_eats_restapp_core,
        pgsql,
        load_json,
):
    expected_discount_request = get_expected_discount_request(
        load_json, 'gift_with_custom_titles',
    )

    @mockserver.json_handler('/eats-discounts/v1/partners/discounts/create')
    def _mock_eats_discounts(request):
        assert request.json == expected_discount_request
        response_body = {'task_id': '12345678-1234-1234-1234-123412345678'}
        return mockserver.make_response(status=200, json=response_body)

    request_body = make_request(
        'gift', None, 123.456, '1', None, None, None, None, None, None, None,
    )
    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo',
        headers={'X-YaEda-PartnerId': '1'},
        json=request_body,
    )
    assert response.status_code == 200
    assert _mock_eats_discounts.times_called == 1


@pytest.mark.experiments3(filename='promos_settings.json')
@pytest.mark.experiments3(filename='activate_switching_to_new_platform.json')
@pytest.mark.parametrize(['request_body'], ALL_PROMOS)
async def test_all_promos_service_response_403_with_places_if_authorizer_response_403(
        taxi_eats_restapp_promo,
        mockserver,
        mock_partners_info,
        mock_authorizer_403,
        request_body,
):
    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo',
        headers={'X-YaEda-PartnerId': '1'},
        json=request_body,
    )

    assert response.status_code == 403
    assert response.json() == {
        'code': '403',
        'message': 'Недостаточно прав',
        'details': {
            'errors': [
                {
                    'code': '403',
                    'message': 'User 1 does not have access to places [1,2]',
                },
            ],
        },
    }


@pytest.mark.experiments3(filename='promos_settings.json')
@pytest.mark.experiments3(filename='activate_switching_to_new_platform.json')
@pytest.mark.parametrize(['request_body'], ALL_PROMOS)
async def test_all_promos_service_response_403_with_permissions_if_authorizer_response_403(
        taxi_eats_restapp_promo,
        mockserver,
        mock_partners_info,
        mock_authorizer_403_no_perm,
        request_body,
):
    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo',
        headers={'X-YaEda-PartnerId': '1'},
        json=request_body,
    )

    assert response.status_code == 403
    assert response.json() == {
        'code': '403',
        'message': 'Недостаточно прав',
        'details': {
            'errors': [
                {
                    'code': '403',
                    'message': 'User 1 does not have permissions ["permission.promo.edit"]',
                },
            ],
        },
    }


@pytest.mark.experiments3(filename='promos_settings_one.json')
@pytest.mark.experiments3(filename='activate_switching_to_new_platform.json')
@pytest.mark.parametrize(['request_body'], [DISCOUNT, GIFT, ONE_PLUS_ONE])
async def test_all_promos_service_response_404_for_promo_not_in_config(
        taxi_eats_restapp_promo,
        mockserver,
        mock_partners_info,
        mock_authorizer_allowed,
        request_body,
):
    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo',
        headers={'X-YaEda-PartnerId': '1'},
        json=request_body,
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'Неизвестный тип акции',
        'details': {
            'errors': [
                {
                    'code': '404',
                    'message': 'Promo type not presented in config',
                },
            ],
        },
    }
