import datetime

import pytest

RESPONSE_PLUS_FIRST_ORDERS = {
    'bonuses': [{'cashback': [20.0, 10.0, 5.0]}],
    'description': (
        'Привлечь новых пользователей, '
        'предложив им повышенный кешбек '
        'за первые заказы.'
    ),
    'ends_at': '2021-11-25T15:43:00+00:00',
    'id': 7,
    'name': 'Повышенный кешбэк для новичков',
    'place_ids': [1, 2],
    'requirements': [{'min_order_price': 50.5}],
    'starts_at': '2020-11-25T15:43:00+00:00',
    'status': 'completed',
    'type': 'plus_first_orders',
}

RESPONSE_PLUS_HAPPY_HOURS = {
    'bonuses': [{'cashback': [20.0, 10.0, 5.0]}],
    'description': 'Предложите повышенный кешбек за заказ в мёртвые часы.',
    'ends_at': '2021-11-25T15:43:00+00:00',
    'id': 8,
    'name': 'Повышенный кешбэк в счастливые часы',
    'place_ids': [1, 2],
    'requirements': [{'min_order_price': 50.5}],
    'starts_at': '2020-11-25T15:43:00+00:00',
    'status': 'completed',
    'type': 'plus_happy_hours',
}

RESPONSE_FREE_DELIVERY = {
    'bonuses': [{}],
    'description': 'Предложите бесплатную доставку.',
    'ends_at': '2021-11-25T15:43:00+00:00',
    'id': 9,
    'name': 'Бесплатная доставка',
    'place_ids': [1, 2],
    'requirements': [{'min_order_price': 50.5}],
    'starts_at': '2020-11-25T15:43:00+00:00',
    'status': 'completed',
    'type': 'free_delivery',
}

RESPONSE_DISCOUNT = {
    'bonuses': [{}],
    'description': 'Увеличить выручку ресторана или поднять средний чек.',
    'ends_at': '2021-11-25T15:43:00+00:00',
    'id': 10,
    'name': 'Скидка на меню или некоторые позиции',
    'place_ids': [1, 2],
    'requirements': [{'min_order_price': 50.5}],
    'starts_at': '2020-11-25T15:43:00+00:00',
    'status': 'completed',
    'type': 'discount',
}

RESPONSE_ONE_PLUS_ONE = {
    'bonuses': [{}],
    'description': (
        'Увеличить количество заказов или познакомить '
        'пользователей c новыми блюдами.'
    ),
    'ends_at': '2021-11-25T15:43:00+00:00',
    'id': 11,
    'name': 'Два по цене одного',
    'place_ids': [1, 2],
    'requirements': [{'min_order_price': 50.5}],
    'starts_at': '2020-11-25T15:43:00+00:00',
    'status': 'completed',
    'type': 'one_plus_one',
}

RESPONSE_GIFT = {
    'bonuses': [{}],
    'description': (
        'Познакомить пользователей с новыми блюдами или поднять средний чек.'
    ),
    'ends_at': '2021-11-25T15:43:00+00:00',
    'id': 12,
    'name': 'Блюдо в подарок',
    'place_ids': [1, 2],
    'requirements': [{'min_order_price': 50.5}],
    'starts_at': '2020-11-25T15:43:00+00:00',
    'status': 'completed',
    'type': 'gift',
}


@pytest.mark.experiments3(filename='promos_settings.json')
async def test_promo_stop_autorization_403(
        taxi_eats_restapp_promo,
        mockserver,
        mock_authorizer_403,
        mock_partners_info_200,
):
    """
    Тест проверяет права на редакирование акций для набора ресторанов.
    Проверяется, что 403 ответ ручки
    eats-restapp-authorizer правильно обрабатывается.
    """
    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/stop',
        headers={'X-YaEda-PartnerId': '1'},
        json={'id': 1},
    )

    assert response.status_code == 403
    response = response.json()
    assert response == {'code': '403', 'message': 'Permission Denied'}


@pytest.mark.experiments3(filename='promos_settings.json')
async def test_promo_stop_autorization_400(
        taxi_eats_restapp_promo,
        mockserver,
        mock_authorizer_400,
        mock_partners_info_200,
):
    """
    Тест проверяет права на редакирование акций для набора ресторанов.
    Проверяется, что 400 ответ ручки
    eats-restapp-authorizer правильно обрабатывается.
    """
    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/stop',
        headers={'X-YaEda-PartnerId': '1'},
        json={'id': 1},
    )

    assert response.status_code == 400
    response = response.json()
    assert response == {'code': '400', 'message': 'Bad Request'}


@pytest.mark.experiments3(filename='promos_settings.json')
async def test_promo_stop_autorization_200(
        taxi_eats_restapp_promo,
        mock_authorizer_allowed,
        mock_partners_info_200,
):
    """
    Тест проверяет права на редакирование акций для набора ресторанов.
    Проверяется, что 200 ответ ручки
    eats-restapp-authorizer правильно обрабатывается.
    """
    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/stop',
        headers={'X-YaEda-PartnerId': '1'},
        json={'id': 1},
    )

    assert response.status_code == 200


@pytest.mark.experiments3(filename='promos_settings.json')
@pytest.mark.parametrize(
    ['promo_id', 'expected_code', 'expected_message'],
    [
        pytest.param(2, 404, 'Promo not found.', id='promo not found by id'),
        pytest.param(3, 500, 'Internal error', id='promo without discount_id'),
        pytest.param(
            4,
            400,
            'Incorrect current promo status.',
            id='promo with incorrect status completed',
        ),
        pytest.param(
            5,
            400,
            'Incorrect current promo status.',
            id='promo with incorrect status new',
        ),
        pytest.param(
            6,
            400,
            'Incorrect current promo status.',
            id='promo with incorrect status disabled',
        ),
    ],
)
async def test_promo_stop_validation_fails(
        taxi_eats_restapp_promo,
        mock_authorizer_allowed,
        promo_id,
        expected_code,
        expected_message,
        mock_partners_info_200,
):
    """
    Тест проверяет неуспешную валидацию акции на завершение.
    """
    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/stop',
        headers={'X-YaEda-PartnerId': '1'},
        json={'id': promo_id},
    )

    assert response.status_code == expected_code
    response = response.json()
    assert response == {
        'code': str(expected_code),
        'message': expected_message,
    }


@pytest.mark.experiments3(filename='promos_settings_one.json')
@pytest.mark.parametrize(
    ['promo_id', 'expected_code', 'expected_message'],
    [
        pytest.param(
            7,
            400,
            {
                'code': '400',
                'message': 'Promo type is not available for stop.',
            },
            id='plus first orders promo can not disable from config',
        ),
        pytest.param(
            8,
            400,
            {
                'code': '400',
                'message': 'Promo type is not available for stop.',
            },
            id='plus happy hours promo can not disable from config',
        ),
    ],
)
async def test_promo_stop_validation_settings(
        taxi_eats_restapp_promo,
        mock_authorizer_allowed,
        promo_id,
        expected_code,
        expected_message,
        mock_partners_info_200,
):
    """
    Тест проверяет валидацию акции на отключение.
    Проверяется, ошибка при отключении в конфиге
    флажка can_stop и вооще отсутсвии конфига
    для типа акции.
    """
    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/stop',
        headers={'X-YaEda-PartnerId': '1'},
        json={'id': promo_id},
    )

    assert response.status_code == expected_code
    response = response.json()
    assert response == expected_message


@pytest.mark.experiments3(filename='promos_settings.json')
@pytest.mark.parametrize(
    ['promo_id', 'expected_hierarchy', 'expected_code', 'expected_message'],
    [
        pytest.param(
            7,
            'place_cashback',
            200,
            RESPONSE_PLUS_FIRST_ORDERS,
            id='plus first orders promo successfully disabled',
        ),
        pytest.param(
            8,
            'place_cashback',
            200,
            RESPONSE_PLUS_HAPPY_HOURS,
            id='plus happy hours promo successfully disabled',
        ),
        pytest.param(
            9,
            'place_delivery_discounts',
            200,
            RESPONSE_FREE_DELIVERY,
            id='free delivery spromo successfully disabled',
        ),
    ],
)
async def test_promo_stop_success_disable(
        taxi_eats_restapp_promo,
        mock_authorizer_allowed,
        mockserver,
        pgsql,
        promo_id,
        expected_hierarchy,
        expected_code,
        expected_message,
        mock_partners_info_200,
):
    """
    Тест проверяет успешное завершение акции.
    """

    @mockserver.json_handler('/eats-discounts/v1/partners/discounts/finish')
    def _mock_eats_discounts(request):
        assert request.json == {
            'partner_user_id': '1',
            'discounts_data': [
                {
                    'hierarchy_name': expected_hierarchy,
                    'discount_id': 'aboba-biba-boba',
                },
            ],
        }
        return mockserver.make_response(status=200)

    cursor = pgsql['eats_restapp_promo'].cursor()
    cursor.execute(
        'SELECT updated_at FROM '
        'eats_restapp_promo.promos '
        f'WHERE promo_id = {promo_id}',
    )
    prev_updated_at = cursor.fetchone()[0]

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/stop',
        headers={'X-YaEda-PartnerId': '1'},
        json={'id': promo_id},
    )

    assert response.status_code == expected_code
    response = response.json()
    assert response == expected_message

    cursor.execute(
        'SELECT status, updated_at '
        'FROM eats_restapp_promo.promos '
        f'WHERE promo_id = {promo_id}',
    )

    promo_row = cursor.fetchone()
    assert promo_row[0] == 'completed'
    assert promo_row[1] > prev_updated_at


@pytest.mark.experiments3(filename='promos_settings.json')
@pytest.mark.parametrize(
    ['promo_id'],
    [
        pytest.param(10, id='discount'),
        pytest.param(11, id='one_plus_one'),
        pytest.param(12, id='gift'),
    ],
)
async def test_old_promo_stop_fails_on_old_platform(
        taxi_eats_restapp_promo,
        mock_authorizer_allowed,
        mock_partners_info_200,
        promo_id,
):
    """
    Тест проверяет выдачу ошибки на неподдерживаемые типы.
    """
    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/stop',
        headers={'X-YaEda-PartnerId': '1'},
        json={'id': promo_id},
    )

    assert response.status_code == 400
    response = response.json()
    assert response == {
        'code': '400',
        'message': 'Stop not implemented yet for this type of promos',
    }


@pytest.mark.experiments3(filename='activate_switching_to_new_platform.json')
@pytest.mark.experiments3(filename='promos_settings.json')
@pytest.mark.parametrize(
    ['promo_id', 'expected_response'],
    [
        pytest.param(10, RESPONSE_DISCOUNT, id='discount'),
        pytest.param(11, RESPONSE_ONE_PLUS_ONE, id='one_plus_one'),
        pytest.param(12, RESPONSE_GIFT, id='gift'),
    ],
)
async def test_old_promo_stop_success_on_new_platform(
        taxi_eats_restapp_promo,
        mock_authorizer_allowed,
        mock_partners_info_200,
        promo_id,
        expected_response,
):
    """
    Тест проверяет завершение старых акций на новой платформе.
    """
    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/stop',
        headers={'X-YaEda-PartnerId': '1'},
        json={'id': promo_id},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == expected_response


@pytest.mark.experiments3(filename='promos_settings.json')
@pytest.mark.parametrize(
    ['starts', 'ends', 'matcher'],
    [
        pytest.param(
            'now() - \'1 day\'::interval',
            'now() + \'1 day\'::interval',
            lambda ends, prev_ends, starts: starts < ends < prev_ends,
            id='stop running promo',
        ),
        pytest.param(
            'now() + \'1 day\'::interval',
            'now() + \'2 day\'::interval',
            lambda ends, prev_ends, starts: starts
            + datetime.timedelta(seconds=45)
            == ends
            < prev_ends,
            marks=[
                pytest.mark.config(
                    EATS_RESTAPP_PROMO_TIME_SHIFTS={'stop_shift': 45},
                ),
            ],
            id='stop planned promo',
        ),
        pytest.param(
            'now() - \'2 day\'::interval',
            'now() - \'1 day\'::interval',
            lambda ends, prev_ends, starts: starts < ends == prev_ends,
            id='stop promo with ends in past',
        ),
    ],
)
async def test_promo_stop_update_ends(
        taxi_eats_restapp_promo,
        mock_authorizer_allowed,
        mock_partners_info_200,
        mockserver,
        starts,
        ends,
        matcher,
        pgsql,
):
    """
    Тест проверяет изменение даты окончания при досрочном завершении.
    """
    promo_id = 9

    @mockserver.json_handler('/eats-discounts/v1/partners/discounts/finish')
    def _mock_eats_discounts(request):
        return mockserver.make_response(status=200)

    cursor = pgsql['eats_restapp_promo'].cursor()
    cursor.execute(
        'WITH updated AS ( '
        '  UPDATE eats_restapp_promo.promos '
        f'  SET starts = {starts}, '
        f'      ends = {ends} '
        f'  WHERE promo_id = {promo_id} '
        '  RETURNING * '
        ') SELECT ends '
        'FROM updated',
    )
    prev_ends = cursor.fetchone()[0]

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/stop',
        headers={'X-YaEda-PartnerId': '1'},
        json={'id': promo_id},
    )
    assert response.status_code == 200

    cursor.execute(
        'SELECT starts, ends '
        'FROM eats_restapp_promo.promos '
        f'WHERE promo_id = {promo_id}',
    )
    starts, ends = cursor.fetchone()
    assert matcher(ends, prev_ends, starts)


@pytest.mark.experiments3(filename='activate_switching_to_new_platform.json')
@pytest.mark.experiments3(filename='promos_settings.json')
async def test_check_stq_promo_finish(
        taxi_eats_restapp_promo,
        mock_authorizer_allowed,
        mock_partners_info_200,
        mockserver,
        stq,
):
    """
    Тест проверяет вызов stq при ошибках от discounts
    """

    @mockserver.json_handler('eats-discounts/v1/partners/discounts/finish')
    def _mock_finish_discounts(request):
        return mockserver.make_response(
            status=400, json={'code': '400', 'message': 'bad request'},
        )

    response = await taxi_eats_restapp_promo.post(
        '/4.0/restapp-front/promo/v1/promo/stop',
        headers={'X-YaEda-PartnerId': '1'},
        json={'id': 10},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == RESPONSE_DISCOUNT

    assert stq.eats_restapp_promo_promo_finish.times_called == 1
    arg = stq.eats_restapp_promo_promo_finish.next_call()
    assert arg['queue'] == 'eats_restapp_promo_promo_finish'
    assert arg['args'] == []
    assert arg['kwargs']['promo_id'] == 10
    assert arg['kwargs']['partner_id'] == 1
