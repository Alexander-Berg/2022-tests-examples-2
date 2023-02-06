import json

import pytest

ORDER_ID = '8c83b49edb274ce0992f337061047399'
CORP_PAYMENTMETHODS_PATH = '/corp_integration_api/corp_paymentmethods'


def _mock_surge(mockserver):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return {
            'zone_id': 'moscow',
            'classes': [
                {
                    'name': 'econom',
                    'value': 1.1,
                    'reason': 'pins_free',
                    'antisurge': False,
                    'value_raw': 1.0,
                    'value_smooth': 1.0,
                },
            ],
        }


def _mock_corp_paymentmethods(mockserver):
    @mockserver.json_handler(CORP_PAYMENTMETHODS_PATH)
    def mock_corp_paymentmethods(request):
        return {
            'methods': [
                {
                    'type': 'corp',
                    'id': 'corp-corp_client_id',
                    'label': '-',
                    'description': '-',
                    'can_order': True,
                    'cost_center': '',
                    'zone_available': True,
                    'hide_user_cost': False,
                    'user_id': 'corp_user_id',
                    'client_comment': 'corp_comment',
                    'currency': 'RUB',
                    'without_vat_contract': True,
                },
            ],
        }


@pytest.fixture()
def events_testpoint(testpoint):
    class Context:
        @testpoint('corp_integration_client_stat_counter')
        def corp_integration_client_stat_counter(put):
            pass

    return Context()


def wait_events_update(events_testpoint):
    wait_res = (
        events_testpoint.corp_integration_client_stat_counter.wait_call()
    )
    assert wait_res == {'put': 'ok'}


def test_not_a_corp(
        taxi_protocol, mockserver, load, db, now, pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    request = {'id': 'b300bda7d41b4bae8d58dfa93221ef16', 'orderid': ORDER_ID}

    _mock_surge(mockserver)
    response = taxi_protocol.post('3.0/ordercommit', request)
    assert response.status_code == 200

    response_json = response.json()
    proc = db.order_proc.find_one({'_id': response_json['orderid']})
    request = proc['order']['request']
    assert 'corp' not in request


def test_not_found(
        taxi_protocol, mockserver, load, db, now, pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    db.order_proc.update(
        {'_id': ORDER_ID}, {'$set': {'order.request.payment.type': 'corp'}},
    )

    request = {'id': 'b300bda7d41b4bae8d58dfa93221ef16', 'orderid': ORDER_ID}

    _mock_surge(mockserver)
    response = taxi_protocol.post('3.0/ordercommit', request)
    assert response.status_code == 406

    content = response.json()
    assert content['error']['code'] == 'NOT_CORP_CLIENT'
    assert content['error']['comment'] == 'payment_id not found'


def make_corp_order(db, order_id, cargo_ref_id=None):
    db.order_proc.update(
        {'_id': order_id},
        {
            '$set': {
                'order.request.payment.type': 'corp',
                'payment_tech.main_card_payment_id': 'corp-corp_client_id',
                'order.request.cargo_ref_id': cargo_ref_id,
            },
        },
    )


def set_order_classes(db, order_id, classes):
    db.order_proc.update(
        {'_id': order_id}, {'$set': {'order.request.class': classes}},
    )


@pytest.mark.config(CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True)
def test_found(
        taxi_protocol, mockserver, load, db, now, pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    make_corp_order(db, ORDER_ID)
    request = {'id': 'b300bda7d41b4bae8d58dfa93221ef16', 'orderid': ORDER_ID}

    _mock_surge(mockserver)
    _mock_corp_paymentmethods(mockserver)
    response = taxi_protocol.post('3.0/ordercommit', request)
    assert response.status_code == 200

    response_json = response.json()
    proc = db.order_proc.find_one({'_id': response_json['orderid']})
    request = proc['order']['request']

    assert 'corp' in request
    corp = request['corp']
    assert corp['client_id'] == 'corp_client_id'
    assert corp['client_comment'] == 'corp_comment'
    assert corp['user_id'] == 'corp_user_id'
    assert corp['without_vat_contract'] is True


@pytest.mark.filldb(users='with_ya_plus')
@pytest.mark.config(CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True)
def test_corp_disable_ya_plus(
        taxi_protocol, mockserver, load, db, now, pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')
    make_corp_order(db, ORDER_ID)

    request = {'id': 'b300bda7d41b4bae8d58dfa93221ef16', 'orderid': ORDER_ID}

    _mock_surge(mockserver)
    _mock_corp_paymentmethods(mockserver)
    response = taxi_protocol.post('3.0/ordercommit', request)
    assert response.status_code == 200

    response_json = response.json()
    order_proc = db.order_proc.find_one({'_id': response_json['orderid']})
    assert 'price_modifiers' not in order_proc

    request = order_proc['order']['request']

    assert 'corp' in request
    corp = request['corp']
    assert corp['client_id'] == 'corp_client_id'
    assert corp['client_comment'] == 'corp_comment'
    assert corp['user_id'] == 'corp_user_id'


RUS_POINT = {
    'country': 'Россия',
    'fullname': 'Россия, Москва, улица Тимура Фрунзе, 11к2',
    'geopoint': [37.58917997300821, 55.73341076871702],
}

KAZ_POINT = {
    'country': 'Казахстан',
    'fullname': 'Скорее всего Алматы',
    'geopoint': [77.012111, 43.346668],
}


def set_country_corp_reg(db, country):
    db.corp_clients.update(
        {'_id': 'corp_client_id'}, {'$set': {'country': country}},
    )


def get_point_by_country_code(country_code):
    if country_code == 'rus':
        return RUS_POINT
    if country_code == 'kaz':
        return KAZ_POINT
    assert False


def set_source_point(db, point):
    db.order_proc.update(
        {'_id': ORDER_ID}, {'$set': {'order.request.source': point}},
    )


def set_dest_point(db, point):
    one_point_array = [point] * 1
    db.order_proc.update(
        {'_id': ORDER_ID},
        {'$set': {'order.request.destinations': one_point_array}},
    )


@pytest.mark.config(CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True)
def test_corp_account_source_point_has_no_zone(
        taxi_protocol, mockserver, load, db, now, pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    """
    Тест проверяет, что если у первой точки пути не найдена геозона, то
    мы получаем ошибку
    """
    _mock_surge(mockserver)
    make_corp_order(db, ORDER_ID)
    request = {'id': 'b300bda7d41b4bae8d58dfa93221ef16', 'orderid': ORDER_ID}

    strange_point = {
        'fullname': 'Somewhere in the world',
        'geopoint': [0, 0],
        'country': 'SomewhereLand',
    }
    db.order_proc.update(
        {'_id': ORDER_ID}, {'$set': {'order.request.source': strange_point}},
    )

    response = taxi_protocol.post('3.0/ordercommit', request)
    assert response.status_code == 406
    assert response.json()['error']['code'] == 'CORP_CITY_DISABLED'


def make_order_response(taxi_protocol, mockserver, db, locale):
    make_corp_order(db, ORDER_ID)
    request = {'id': 'b300bda7d41b4bae8d58dfa93221ef16', 'orderid': ORDER_ID}

    _mock_surge(mockserver)
    return taxi_protocol.post(
        '3.0/ordercommit', request, headers={'Accept-Language': locale},
    )


def check_cost_center(
        taxi_protocol,
        mockserver,
        db,
        expected_order_proc_cost_center,
        expected_order_cost_center,
):
    response = make_order_response(taxi_protocol, mockserver, db, 'ru')
    assert response.status_code == 200

    response_json = response.json()

    db_order_proc = db.order_proc.find_one({'_id': response_json['orderid']})
    order_proc_request = db_order_proc['order']['request']

    assert 'corp' in order_proc_request
    order_proc_corp = order_proc_request['corp']
    if expected_order_proc_cost_center == 'not exists':
        assert order_proc_corp.get('cost_center') is None
    else:
        assert (
            order_proc_corp.get('cost_center')
            == expected_order_proc_cost_center
        )


def set_order_cost_center(db, order_cost_center, order_cost_centers=None):
    _set = {}

    if order_cost_center != 'not exists':
        _set.update({'order.request.corp.cost_center': order_cost_center})
    if order_cost_centers is not None:
        _set.update({'order.request.corp.cost_centers': order_cost_centers})

    if _set:
        db.order_proc.update({'_id': ORDER_ID}, {'$set': _set})


def set_user_cost_center(db, user_cost_center):
    if user_cost_center != 'not exists':
        db.corp_users.update(
            {'_id': 'corp_user_id'},
            {'$set': {'cost_center': user_cost_center}},
        )


COST_CENTER_CHECK_TABLE_CORP_PAYMENTHMETHODS = [
    ('not exists', 'user', 'user', 'user'),
    (None, 'user', 'user', 'user'),
    ('', 'user', 'user', 'user'),
    ('order', 'not exists', 'order', 'order'),
    ('order', None, 'order', 'order'),
    ('order', '', 'order', 'order'),
    ('order', 'user', 'order', 'order'),
]


@pytest.mark.parametrize(
    'order_cost_center, user_cost_center,'
    'expected_order_proc_cost_center,'
    'expected_order_cost_center',
    COST_CENTER_CHECK_TABLE_CORP_PAYMENTHMETHODS,
)
@pytest.mark.config(CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True)
def test_corp_cost_center_corp_paymentmethods(
        taxi_protocol,
        mockserver,
        load,
        db,
        now,
        order_cost_center,
        user_cost_center,
        expected_order_proc_cost_center,
        expected_order_cost_center,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')
    """
    проверка обработки cost_center получаемого от corp_paymentmethods
    """

    @mockserver.json_handler(CORP_PAYMENTMETHODS_PATH)
    def mock_paymentmethods(request):
        corp_responce = {
            'methods': [
                {
                    'type': 'corp',
                    'id': 'corp-corp_client_id',
                    'label': '-',
                    'description': '-',
                    'can_order': True,
                    'zone_available': True,
                    'hide_user_cost': False,
                    'user_id': 'corp_user_id',
                    'client_comment': 'corp_comment',
                    'currency': 'RUB',
                },
            ],
        }
        # corp_paymentmethods всегда возвращает cost_center. если нет данных
        # то пустую строку
        if user_cost_center is None or user_cost_center == 'not exists':
            corp_responce['methods'][0]['cost_center'] = ''
        else:
            corp_responce['methods'][0]['cost_center'] = user_cost_center
        return corp_responce

    set_order_cost_center(db, order_cost_center)
    check_cost_center(
        taxi_protocol,
        mockserver,
        db,
        expected_order_proc_cost_center,
        expected_order_cost_center,
    )


@pytest.mark.parametrize(
    'order_cost_center, user_cost_center,'
    'expected_order_proc_cost_center,'
    'expected_order_cost_center',
    COST_CENTER_CHECK_TABLE_CORP_PAYMENTHMETHODS,
)
@pytest.mark.config(CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True)
def test_corp_cost_center_corp_paymentmethods_with_old(
        taxi_protocol,
        mockserver,
        load,
        db,
        now,
        order_cost_center,
        user_cost_center,
        expected_order_proc_cost_center,
        expected_order_cost_center,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')
    """
    Проверка вычисления cost_center в режиме проверки результатов работы
    нового кода старым (эксперимент corp_info_use_corp_paymentmethods). Если
    новое значение не совпадает со старым возвращается старое.
    сorp_paymentmethods всегда возвращает cost_center, а если он не
    задан то пустую строку. Поэтому варианты значений cost_center
    полученные старым методом такие как 'нет
    поля', None и пустая строка считаются одинаковыми и фолбек не должен
    срабатыавть. Иначе фолбек будет срабатывать часто и среди таких логов
    сложно искать фолбеки с другими вариантами не совпадений.
    Результаты должны быть как в предыдушем тесте
    test_corp_cost_center_corp_paymentmethods
    """

    @mockserver.json_handler(CORP_PAYMENTMETHODS_PATH)
    def mock_paymentmethods(request):
        corp_responce = {
            'methods': [
                {
                    'type': 'corp',
                    'id': 'corp-corp_client_id',
                    'label': '-',
                    'description': '-',
                    'can_order': True,
                    'zone_available': True,
                    'hide_user_cost': False,
                    'user_id': 'corp_user_id',
                    'client_comment': 'corp_comment',
                    'currency': 'RUB',
                },
            ],
        }
        if user_cost_center is None or user_cost_center == 'not exists':
            corp_responce['methods'][0]['cost_center'] = ''
        else:
            corp_responce['methods'][0]['cost_center'] = user_cost_center
        return corp_responce

    set_order_cost_center(db, order_cost_center)
    set_user_cost_center(db, user_cost_center)
    check_cost_center(
        taxi_protocol,
        mockserver,
        db,
        expected_order_proc_cost_center,
        expected_order_cost_center,
    )


NEW_COST_CENTERS = [
    {'id': 'cost_center', 'title': 'Центр затрат', 'value': 'командировка'},
    {'id': 'ride_purpose', 'title': 'Цель поездки', 'value': 'из аэропорта'},
]


@pytest.mark.parametrize(
    ['test_params'],
    [
        pytest.param(
            dict(experiment_enabled=False), id='exp-disabled-no-cost-centers',
        ),
        pytest.param(
            dict(experiment_enabled=False, order_cost_center='some_value'),
            id='exp-disabled-no-cost-center-is-sent',
        ),
        pytest.param(
            dict(experiment_enabled=True), id='exp-enabled-no-cost-centers',
        ),
        pytest.param(
            dict(
                experiment_enabled=True,
                order_cost_center='some_value',
                expected_sent_cost_center='some_value',
            ),
            id='exp-enabled-old-cost-center-sent-from-order',
        ),
        pytest.param(
            dict(
                experiment_enabled=True,
                order_cost_centers=NEW_COST_CENTERS,
                expected_sent_cost_centers=NEW_COST_CENTERS,
            ),
            id='exp-enabled-new-cost-centers-sent-from-order',
        ),
        pytest.param(
            dict(
                experiment_enabled=False,
                order_cost_centers=NEW_COST_CENTERS,
                expected_sent_cost_centers=NEW_COST_CENTERS,
            ),
            id='exp-disabled-new-cost-centers-sent-from-order',
        ),
        pytest.param(
            dict(
                experiment_enabled=True,
                order_cost_center='some_value',
                expected_sent_cost_center='some_value',
                order_cost_centers=NEW_COST_CENTERS,
                expected_sent_cost_centers=NEW_COST_CENTERS,
            ),
            id='exp-enabled-all-cost-centers-sent-from-order',
        ),
        pytest.param(
            dict(
                experiment_enabled=False,
                order_cost_center='some_value',  # not sent as exp disabled
                order_cost_centers=NEW_COST_CENTERS,
                expected_sent_cost_centers=NEW_COST_CENTERS,
            ),
            id='exp-disabled-new-only-cost-centers-sent-from-order',
        ),
    ],
)
@pytest.mark.config(CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True)
def test_corp_cost_centers(
        test_params,
        mockserver,
        db,
        taxi_protocol,
        now,
        load_json,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')
    experiment_enabled = test_params['experiment_enabled']
    order_cost_center = test_params.get('order_cost_center')
    expected_sent_cost_center = test_params.get('expected_sent_cost_center')
    order_cost_centers = test_params.get('order_cost_centers')
    expected_sent_cost_centers = test_params.get('expected_sent_cost_centers')

    @mockserver.json_handler('/v1/experiments/updates')
    def experiments3_proxy(request):
        data = load_json('experiments3_cost_centers.json')
        data['experiments'][0]['match']['enabled'] = experiment_enabled
        return data

    taxi_protocol.tests_control(now, invalidate_caches=True)

    @mockserver.json_handler(CORP_PAYMENTMETHODS_PATH)
    def mock_paymentmethods(request):
        request_str = next(request.form.keys())
        sent_cost_center = json.loads(request_str).get('cost_center')
        assert sent_cost_center == expected_sent_cost_center
        sent_cost_centers = json.loads(request_str).get('cost_centers')
        assert sent_cost_centers == expected_sent_cost_centers
        return {
            'methods': [
                {
                    'type': 'corp',
                    'id': 'corp-corp_client_id',
                    'label': '-',
                    'description': '-',
                    'can_order': True,
                    'cost_center': '',
                    'cost_center_fields': [],  # is not used though
                    'zone_available': True,
                    'hide_user_cost': False,
                    'user_id': 'corp_user_id',
                    'client_comment': 'corp_comment',
                    'currency': 'RUB',
                },
            ],
        }

    set_order_cost_center(db, order_cost_center, order_cost_centers)
    response = make_order_response(taxi_protocol, mockserver, db, 'ru')
    assert response.status_code == 200


@pytest.mark.config(CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True)
def test_corp_combo_order(
        mockserver, db, taxi_protocol, now, pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    taxi_protocol.tests_control(now, invalidate_caches=True)

    combo_order = {'delivery_id': 'delivery1'}

    @mockserver.json_handler(CORP_PAYMENTMETHODS_PATH)
    def mock_paymentmethods(request):
        request_str = next(request.form.keys())
        sent_combo_order = json.loads(request_str).get('combo_order')
        assert sent_combo_order == combo_order
        return {
            'methods': [
                {
                    'type': 'corp',
                    'id': 'corp-corp_client_id',
                    'label': '-',
                    'description': '-',
                    'can_order': True,
                    'cost_center': '',
                    'cost_center_fields': [],  # is not used though
                    'zone_available': True,
                    'hide_user_cost': False,
                    'user_id': 'corp_user_id',
                    'client_comment': 'corp_comment',
                    'currency': 'RUB',
                },
            ],
        }

    set_mongo = {'order.request.corp.combo_order': combo_order}
    db.order_proc.update({'_id': ORDER_ID}, {'$set': set_mongo})

    response = make_order_response(taxi_protocol, mockserver, db, 'ru')

    assert response.status_code == 200


@pytest.mark.config(CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True)
def test_corp_no_user(
        mockserver, db, taxi_protocol, now, load_json, pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    taxi_protocol.tests_control(now, invalidate_caches=True)

    @mockserver.json_handler(CORP_PAYMENTMETHODS_PATH)
    def mock_paymentmethods(request):
        return {
            'methods': [
                {
                    'type': 'corp',
                    'id': 'corp-corp_client_id',
                    'label': '-',
                    'description': '-',
                    'can_order': True,
                    'cost_center': '',
                    'zone_available': True,
                    'hide_user_cost': False,
                    'client_comment': 'corp_comment',
                    'currency': 'RUB',
                },
            ],
        }

    response = make_order_response(taxi_protocol, mockserver, db, 'ru')
    assert response.status_code == 200

    response_json = response.json()
    db_order_proc = db.order_proc.find_one({'_id': response_json['orderid']})
    order_proc_request = db_order_proc['order']['request']
    assert 'corp' in order_proc_request
    assert 'user_id' not in order_proc_request['corp']


@pytest.mark.parametrize(
    'locale, error_text',
    [('ru', 'NOT_CORP_CLIENT_ru'), ('en', 'NOT_CORP_CLIENT_en')],
)
@pytest.mark.translations(
    client_messages={
        'common_errors.NOT_CORP_CLIENT': {
            'en': 'NOT_CORP_CLIENT_en',
            'ru': 'NOT_CORP_CLIENT_ru',
        },
    },
)
@pytest.mark.config(CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True)
def test_corp_paymentmethods_no_paymentmethods(
        taxi_protocol,
        mockserver,
        load,
        db,
        now,
        locale,
        error_text,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    @mockserver.json_handler(CORP_PAYMENTMETHODS_PATH)
    def mock_paymentmethods(request):
        return {'methods': []}

    response = make_order_response(taxi_protocol, mockserver, db, locale)
    assert response.status_code == 406

    content = response.json()
    assert content['error']['code'] == 'NOT_CORP_CLIENT'
    assert content['error']['text'] == error_text


@pytest.mark.translations(
    client_messages={
        'common_errors.CORP_CANNOT_ORDER': {
            'en': 'CORP_CANNOT_ORDER_en',
            'ru': 'CORP_CANNOT_ORDER_ru',
        },
    },
)
@pytest.mark.parametrize('locale', ['ru', 'en'])
@pytest.mark.config(CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True)
def test_corp_paymentmethods_cannot_order(
        taxi_protocol,
        mockserver,
        load,
        db,
        now,
        locale,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')
    order_disable_reason = 'order disable reason'

    @mockserver.json_handler(CORP_PAYMENTMETHODS_PATH)
    def mock_paymentmethods(request):
        return {
            'methods': [
                {
                    'type': 'corp',
                    'id': 'corp-corp_client_id',
                    'label': '-',
                    'description': '-',
                    'can_order': False,
                    'order_disable_reason': order_disable_reason,
                    'cost_center': '',
                    'zone_available': True,
                    'hide_user_cost': False,
                    'user_id': 'corp_user_id',
                    'client_comment': 'corp_comment',
                    'currency': 'RUB',
                },
            ],
        }

    response = make_order_response(taxi_protocol, mockserver, db, locale)
    assert response.status_code == 406

    content = response.json()
    assert content['error']['code'] == 'CORP_CANNOT_ORDER'
    # text не зависит от перевода - берется уже переведенный на нужный язык
    # ответ из  corp_paymentmethods
    assert content['error']['text'] == order_disable_reason


@pytest.mark.translations(
    client_messages={
        'common_errors.CORP_ZONE_UNAVAILABLE': {
            'en': 'CORP_ZONE_UNAVAILABLE_en',
            'ru': 'CORP_ZONE_UNAVAILABLE_ru',
        },
    },
)
@pytest.mark.parametrize('locale', ['ru', 'en'])
@pytest.mark.config(CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True)
def test_corp_paymentmethods_zone_disable(
        taxi_protocol,
        mockserver,
        load,
        db,
        now,
        locale,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')
    zone_disable_reason = 'zone disable reason'

    @mockserver.json_handler(CORP_PAYMENTMETHODS_PATH)
    def mock_paymentmethods(request):
        assert request.headers['Accept-Language'] == locale
        return {
            'methods': [
                {
                    'type': 'corp',
                    'id': 'corp-corp_client_id',
                    'label': '-',
                    'description': '-',
                    'can_order': True,
                    'cost_center': '',
                    'zone_available': False,
                    'zone_disable_reason': zone_disable_reason,
                    'hide_user_cost': False,
                    'user_id': 'corp_user_id',
                    'client_comment': 'corp_comment',
                    'currency': 'RUB',
                },
            ],
        }

    response = make_order_response(taxi_protocol, mockserver, db, locale)
    assert response.status_code == 406

    content = response.json()
    assert content['error']['code'] == 'CORP_ZONE_UNAVAILABLE'
    # text не зависит от перевода - берется уже переведенный на нужный язык
    # ответ из  corp_paymentmethods
    assert content['error']['text'] == zone_disable_reason


CORP_PAYMENTMETHODS_RESPONCES = [
    {
        'methods': [
            {
                'type': 'corp',
                'id': 'corp-corp_client_id',
                'label': '-',
                'description': '-',
                'cost_center': '',
                'can_order': True,
                'zone_available': True,
                'hide_user_cost': False,
                'user_id': 'corp_user_id',
                'client_comment': 'corp_comment',
                'currency': 'RUB',
            },
        ],
    },
    # фолбек - в ответе нет user_id
    {
        'methods': [
            {
                'type': 'corp',
                'id': 'corp-corp_client_id',
                'label': '-',
                'description': '-',
                'can_order': True,
                'zone_available': True,
                'hide_user_cost': False,
                'currency': 'RUB',
            },
        ],
    },
    # фолбек - в ответе нет обязательного поля - type
    {
        'methods': [
            {
                'id': 'corp-corp_client_id',
                'label': '-',
                'description': '-',
                'can_order': True,
                'zone_available': True,
                'hide_user_cost': False,
                'currency': 'RUB',
            },
        ],
    },
]


def get_corp_payment_response_fallback():
    return {
        'methods': [
            {
                'type': 'corp',
                'id': 'corp-payment-id-0',
                'label': 'Команда яндекс такси 0',
                'description': 'Осталось 0 из 6000 руб.',
                'order_disable_reason': 'Недостаточно средств на счете',
                'cost_center': 'TAXI',
                'zone_available': True,
                'hide_user_cost': False,
                'currency': 'RUB',
            },
            {
                'type': 'corp',
                'id': 'corp-payment-id-1',
                'label': 'Команда яндекс такси 1',
                'description': '',
                'cost_center': '',
                'hide_user_cost': False,
                'order_disable_reason': 'Некая причина',
                'zone_available': True,
                'currency': 'USD',
            },
        ],
    }


def check_corp_paymentmethods_found(
        taxi_protocol, mockserver, db, locale, expected_user_id='corp_user_id',
):
    response = make_order_response(taxi_protocol, mockserver, db, locale)
    assert response.status_code == 200

    response_json = response.json()
    proc = db.order_proc.find_one({'_id': response_json['orderid']})
    request = proc['order']['request']
    assert 'corp' in request
    corp = request['corp']

    assert corp['client_id'] == 'corp_client_id'
    assert corp['client_comment'] == 'corp_comment'
    assert corp['user_id'] == expected_user_id


@pytest.mark.parametrize('corp_response', CORP_PAYMENTMETHODS_RESPONCES)
@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'protocol', 'dst': 'corp-integration-api'}],
    CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True,
)
@pytest.mark.parametrize('multiclass_request_flow_enabled', (True, False))
@pytest.mark.parametrize('classes', (['econom'], ['econom', 'business']))
def test_corp_paymentmethods_found(
        taxi_protocol,
        mockserver,
        tvm2_client,
        load,
        db,
        now,
        multiclass_request_flow_enabled,
        corp_response,
        config,
        classes,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    locale = 'ru'
    ticket = 'ticket'
    tvm2_client.set_ticket(json.dumps({'24': {'ticket': ticket}}))

    set_order_classes(db, ORDER_ID, classes)

    if multiclass_request_flow_enabled:
        config.set_values(
            dict(CORP_INTEGRATION_MULTICLASS_CORP_FLOW_ENABLED=True),
        )

    @mockserver.json_handler(CORP_PAYMENTMETHODS_PATH)
    def mock_paymentmethods(request):
        data = json.loads(request.get_data())
        assert request.headers['X-Ya-Service-Ticket'] == ticket
        assert request.headers['Accept-Language'] == locale
        assert data['source']['app'] == 'yataxi_application'
        assert data['identity']['phone_id'] == '5714f45e98956f06baaae3d4'
        assert (
            data['identity']['personal_phone_id']
            == '1fab75363700481a9adf5e31c3b6e673'
        )
        assert data['identity']['uid'] == ''
        assert data['route'][0]['geopoint'] == RUS_POINT['geopoint']
        assert data['client_id'] == 'corp_client_id'
        if not multiclass_request_flow_enabled:
            assert data['class'] == classes[0]
        else:
            assert data['classes'] == classes

        return CORP_PAYMENTMETHODS_RESPONCES[0]

    check_corp_paymentmethods_found(taxi_protocol, mockserver, db, locale)


#########################################################################
# Проверяется результат работы старого или нового метода будет возвращен
# при разных экспериментах. Результаты работы нового и старого методов при
# этом не совпадают.


CORP_PAYMENTMETHODS_USER_ID = 'corp paymentmethods user id'

DIFFERENT_USER_ID_RESPONCE = [
    {
        'methods': [
            {
                'type': 'corp',
                'id': 'corp-corp_client_id',
                'label': '-',
                'description': '-',
                'cost_center': '',
                'can_order': True,
                'zone_available': True,
                'hide_user_cost': False,
                'user_id': CORP_PAYMENTMETHODS_USER_ID,
                'client_comment': 'corp_comment',
                'currency': 'RUB',
            },
        ],
    },
]


@pytest.mark.parametrize('corp_response', DIFFERENT_USER_ID_RESPONCE)
@pytest.mark.config(CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True)
def test_corp_paymentmethods_found_old_new_not_equal_1(
        taxi_protocol,
        mockserver,
        load,
        db,
        now,
        corp_response,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    @mockserver.json_handler(CORP_PAYMENTMETHODS_PATH)
    def mock_paymentmethods(request):
        return corp_response

    check_corp_paymentmethods_found(
        taxi_protocol, mockserver, db, 'ru', CORP_PAYMENTMETHODS_USER_ID,
    )


@pytest.mark.parametrize('corp_response', DIFFERENT_USER_ID_RESPONCE)
@pytest.mark.config(CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True)
def test_corp_paymentmethods_found_old_new_not_equal_2(
        taxi_protocol,
        mockserver,
        load,
        db,
        now,
        corp_response,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    @mockserver.json_handler(CORP_PAYMENTMETHODS_PATH)
    def mock_paymentmethods(request):
        return corp_response

    check_corp_paymentmethods_found(
        taxi_protocol, mockserver, db, 'ru', CORP_PAYMENTMETHODS_USER_ID,
    )


@pytest.mark.config(CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=False)
def test_corp_paymentmethods_config_disabled(
        taxi_protocol, mockserver, db, pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')
    response = make_order_response(taxi_protocol, mockserver, db, 'en')
    assert response.status_code == 406
    content = response.json()
    assert content['error']['code'] == 'CORP_SERVICE_ERROR'


#########################################################################
# Проверка срабатывания фолбека на таймаут corp_paymentmethods при разных
# экспериментах
@pytest.mark.now('2019-02-21T09:30:00+0000')
@pytest.mark.config(CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True)
@pytest.mark.parametrize('autofallback_state', ['ok', 'fail'])
def test_corp_paymentmethods_service_ok_autofallback_varies(
        taxi_protocol,
        mockserver,
        db,
        load_json,
        events_testpoint,
        autofallback_state,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    @mockserver.json_handler(CORP_PAYMENTMETHODS_PATH)
    def mock_paymentmethods(request):
        data = json.loads(request.get_data())
        assert data['source']['app'] == 'yataxi_application'
        assert data['identity']['phone_id'] == '5714f45e98956f06baaae3d4'
        assert data['identity']['uid'] == ''
        assert data['route'][0]['geopoint'] == RUS_POINT['geopoint']
        assert data['client_id'] == 'corp_client_id'
        assert data['class'] == 'econom'
        return CORP_PAYMENTMETHODS_RESPONCES[0]

    event_stats_values = load_json('event_stats_values.json')
    db.event_stats.update_one(
        {'name': 'corp_integration'},
        {'$set': event_stats_values[autofallback_state]},
    )
    event_base = db.event_stats.find_one({'name': 'corp_integration'})

    stat_base = event_base['detailed']['corp_integration_client'][
        'corp_paymentmethods'
    ]

    check_corp_paymentmethods_found(taxi_protocol, mockserver, db, 'ru')

    wait_events_update(events_testpoint)
    event = db.event_stats.find_one({'name': 'corp_integration'})
    stat = event['detailed']['corp_integration_client']['corp_paymentmethods']
    assert stat['error'] == stat_base['error']
    assert stat['success'] == stat_base['success'] + 1


@pytest.mark.now('2019-01-21T09:30:00+0000')
@pytest.mark.config(CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True)
@pytest.mark.parametrize('flap', [True, False])
def test_corp_paymentmethods_service_fail_autofallback_ok(
        taxi_protocol,
        mockserver,
        load_json,
        db,
        events_testpoint,
        flap,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    @mockserver.json_handler(CORP_PAYMENTMETHODS_PATH)
    def mock_corp_paymentmethods(request):
        if flap is True:
            return mockserver.make_response('', 500)
        else:
            return get_corp_payment_response_fallback()

    event_stats_values = load_json('event_stats_values.json')
    db.event_stats.update_one(
        {'name': 'corp_integration'}, {'$set': event_stats_values['ok']},
    )
    event_base = db.event_stats.find_one({'name': 'corp_integration'})
    stat_base = event_base['detailed']['corp_integration_client'][
        'corp_paymentmethods'
    ]

    response = make_order_response(taxi_protocol, mockserver, db, 'en')

    if flap is True:
        assert response.status_code == 500
    else:
        assert response.status_code == 406
        content = response.json()
        assert content['error']['code'] == 'CORP_SERVICE_ERROR'

    wait_events_update(events_testpoint)
    event = db.event_stats.find_one({'name': 'corp_integration'})
    stat = event['detailed']['corp_integration_client']['corp_paymentmethods']
    assert stat['error'] == stat_base['error'] + 1
    assert stat['success'] == stat_base['success']


@pytest.mark.now('2019-01-21T09:30:00+0000')
@pytest.mark.config(CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True)
def test_corp_paymentmethods_service_fail_autofallback_fail(
        taxi_protocol, mockserver, load, load_json, db, pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    @mockserver.json_handler(CORP_PAYMENTMETHODS_PATH)
    def mock_corp_paymentmethods(request):
        return mockserver.make_response('', 500)

    event_stats_values = load_json('event_stats_values.json')
    db.event_stats.update_one(
        {'name': 'corp_integration'}, {'$set': event_stats_values['fail']},
    )

    response = make_order_response(taxi_protocol, mockserver, db, 'en')

    assert response.status_code == 406
    content = response.json()
    assert content['error']['code'] == 'CORP_SERVICE_ERROR'


@pytest.mark.config(
    CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True,
    USE_TARIFFS_TO_FILTER_SUPPLY=True,
)
def test_save_virtual_tariffs(
        taxi_protocol, mockserver, load, db, now, pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    virtual_tariffs = [
        {
            'class': 'comfort',
            'special_requirements': [{'id': 'food_delivery'}],
        },
        {'class': 'econom', 'special_requirements': [{'id': 'food_delivery'}]},
    ]

    @mockserver.json_handler('/virtual_tariffs/v1/match')
    def mock_virtual_tariffs_view(request):
        assert json.loads(request.get_data()) == {
            'classes': [{'id': 'econom'}],
            'corp_client_id': 'corp_client_id',
            'zone_id': 'moscow',
        }
        return {'virtual_tariffs': virtual_tariffs}

    make_corp_order(db, ORDER_ID)
    request = {'id': 'b300bda7d41b4bae8d58dfa93221ef16', 'orderid': ORDER_ID}

    _mock_surge(mockserver)
    _mock_corp_paymentmethods(mockserver)
    response = taxi_protocol.post('3.0/ordercommit', request)
    assert response.status_code == 200
    order_proc = db.order_proc.find_one({'_id': ORDER_ID})
    assert order_proc['order']['virtual_tariffs'] == virtual_tariffs


@pytest.mark.config(
    CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True,
    USE_TARIFFS_TO_FILTER_SUPPLY=True,
)
def test_cargo_virtual_tariffs(
        taxi_protocol, mockserver, load, db, now, pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    @mockserver.json_handler('/virtual_tariffs/v1/match')
    def mock_virtual_tariffs_view(request):
        assert json.loads(request.get_data()) == {
            'classes': [{'id': 'econom'}],
            'corp_client_id': 'corp_client_id',
            'zone_id': 'moscow',
            'cargo_ref_id': 'some_cargo_ref_id',
        }
        return {'virtual_tariffs': []}

    make_corp_order(db, ORDER_ID, 'some_cargo_ref_id')
    request = {'id': 'b300bda7d41b4bae8d58dfa93221ef16', 'orderid': ORDER_ID}

    _mock_surge(mockserver)
    _mock_corp_paymentmethods(mockserver)
    response = taxi_protocol.post('3.0/ordercommit', request)
    assert response.status_code == 200


@pytest.mark.config(
    CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True,
    USE_TARIFFS_TO_FILTER_SUPPLY=True,
    FORCED_REQUIREMENTS={'__default__': {'econom': {'yellowcarnumber': True}}},
)
def test_forced_requirements(
        taxi_protocol, mockserver, load, db, now, pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    # make_corp_order(db, ORDER_ID, 'some_cargo_ref_id')
    request = {'id': 'b300bda7d41b4bae8d58dfa93221ef16', 'orderid': ORDER_ID}

    _mock_surge(mockserver)
    _mock_corp_paymentmethods(mockserver)
    response = taxi_protocol.post('3.0/ordercommit', request)
    assert response.status_code == 200
    order_proc = db.order_proc.find_one({'_id': ORDER_ID})
    assert order_proc['order']['request']['requirements'] == {
        'yellowcarnumber': True,
    }


@pytest.mark.config(
    CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True,
    USE_TARIFFS_TO_FILTER_SUPPLY=False,
)
def test_save_virtual_tariffs_fallback(
        taxi_protocol, mockserver, load, db, now, pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    @mockserver.json_handler('/virtual_tariffs/v1/match')
    def mock_virtual_tariffs_view(request):
        raise Exception()

    make_corp_order(db, ORDER_ID)
    request = {'id': 'b300bda7d41b4bae8d58dfa93221ef16', 'orderid': ORDER_ID}

    _mock_surge(mockserver)
    _mock_corp_paymentmethods(mockserver)
    response = taxi_protocol.post('3.0/ordercommit', request)
    assert response.status_code == 200
    order_proc = db.order_proc.find_one({'_id': ORDER_ID})
    assert 'virtual_tariffs' not in order_proc['order']
