import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from cargo_fiscal_plugins import *  # noqa: F403 F401

from tests_cargo_fiscal import const
from tests_cargo_fiscal import utils

EZ_AUTH_ERROR_RESPONSE = {
    'errNum': 1,
    'errMsg': 'your API KEY is not correct',
    'errMsgPretty': ['your API KEY is not correct'],
    'success': False,
    'unixtime': 1653547583,
}

EZ_PARK_TYPE_ERROR_RESPONSE = {
    'errNum': 50.1,
    'errMsg': 'company type mismatch you sent 3 but we have 2',
    'additionalErrData': {'validate_company_type': 3, 'u_comp_type': 2},
    'success': False,
    'unixtime': 1653243459,
}


@pytest.fixture(name='mock_ez')
def _mock_ez(mockserver):
    url = '/eazy-count-cargo/api/createDoc'

    @mockserver.json_handler(url)
    def handler(request):
        if (
                request.json['api_key']
                != '5460afaa648bc05e4056b7b51aedeb3a9e7ef63d'
        ):
            return mockserver.make_response(
                status=200, json=EZ_AUTH_ERROR_RESPONSE,
            )
        if request.json['validate_company_type'] == 3:
            return mockserver.make_response(
                status=200, json=EZ_PARK_TYPE_ERROR_RESPONSE,
            )
        return mockserver.make_response(
            status=200,
            json={
                'success': True,
                'pdf_link': (
                    'https://demo.ezcount.co.il/front/documents/get/3d0c6bd8'
                ),
            },
        )

    return handler


@pytest.fixture(name='mock_buhta')
def _mock_buhta(mockserver):
    url = '/buhta-kz-api/api/v1/kassa/yt/register_ride'

    @mockserver.json_handler(url)
    def handler(request):
        return mockserver.make_response(status=201, json={})

    return handler


@pytest.fixture(name='mock_buhta_bad')
def _mock_buhta_bad(mockserver):
    url = '/buhta-kz-api/api/v1/kassa/yt/register_ride'

    @mockserver.json_handler(url)
    def handler(request):
        return mockserver.make_response(
            status=400,
            json={
                'message': 'Службы такси с таким БИН не найдено',
                'code': 'PARTNER_NOT_FOUND',
            },
        )

    return handler


@pytest.fixture(name='py2_fiscal_data_response')
def _py2_fiscal_data_response(static_response_cls, load_json):
    return static_response_cls('py2_fiscal_data_response.json')


@pytest.fixture(name='mock_py2_fiscal_data')
def _mock_py2_fiscal_data(mockserver, py2_fiscal_data_response):
    url = '/py2-delivery/fetch-fiscal-data'

    @mockserver.json_handler(url)
    def handler(request):
        return py2_fiscal_data_response.make(request)

    return handler


@pytest.fixture(name='static_response_cls')
def _static_response_cls(mockserver, load_json):
    class Response:
        def __init__(self, filename):
            self.filename = filename
            self.data = None
            self.status = 200

        def make(self, response):
            if self.status == 200:
                if self.data is not None:
                    return self.data
                return load_json(self.filename)
            return mockserver.make_response(status=self.status, json={})

        def load(self):
            return load_json(self.filename)

    return Response


@pytest.fixture(autouse=True)
def make_receipt_record(pgsql):
    utils.create_record(pgsql)


@pytest.fixture(autouse=True)
def make_unready_receipt_record(pgsql):
    utils.create_unready_record(pgsql)


@pytest.fixture(name='create_context_record')
def _create_context_record(pgsql):
    cursor = pgsql['cargo_fiscal'].conn.cursor()

    # rus topic context

    cursor.execute(
        f"""
INSERT INTO
    cargo_fiscal.topic
        (id, consumer, domain, topic_id, context)
VALUES (1, 'delivery', 'orders', '{const.TOPIC_ID}',
'{{"service_rendered_at": "2021-05-31T19:00:00+00:00",
"title": "Услуги доставки", "country": "KAZ", "provider_inn": "12345"}}')""",
    )

    cursor.execute(
        f"""
INSERT INTO
    cargo_fiscal.transaction
        (topic_id, transaction_id, context)
VALUES (1, '{const.TRANSACTION_ID}',
'{{"transaction_id": "{const.TRANSACTION_ID}",
"is_refund": true, "price_details": {{
"total": "120.0"}} }}')""",
    )

    # kaz topic context

    cursor.execute(
        f"""
INSERT INTO
    cargo_fiscal.topic
        (id, consumer, domain, topic_id, context)
VALUES (2, 'delivery', 'orders', '{const.TOPIC_ID_2}',
'{{"service_rendered_at": "2021-05-31T19:00:00+00:00",
"title": "Услуги доставки", "country": "KAZ", "provider_inn": "12345"}}')""",
    )

    cursor.execute(
        f"""
INSERT INTO
    cargo_fiscal.transaction
        (topic_id, transaction_id, context)
VALUES (2, '{const.TRANSACTION_ID_2}',
'{{"transaction_id": "{const.TRANSACTION_ID_2}",
"is_refund": false, "price_details": {{
"total": "120.0"}} }}')""",
    )

    # rus transaction context

    cursor.execute(
        f"""
INSERT INTO
    cargo_fiscal.topic
        (id, consumer, domain, topic_id, context)
VALUES (14, 'delivery', 'orders', '{const.TOPIC_ID_01}',
null)""",
    )

    cursor.execute(
        f"""
INSERT INTO
    cargo_fiscal.transaction
        (topic_id, transaction_id, context)
VALUES (14, '{const.TRANSACTION_ID_01}',
'{{"transaction_id": "{const.TRANSACTION_ID_01}",
"is_refund": true, "price_details": {{
"total": "120.0"}}, "service_rendered_at": "2021-05-31T19:00:00+00:00",
"title": "Услуги доставки", "country": "KAZ", "provider_inn": "12345"}}')""",
    )

    # kaz transaction context

    cursor.execute(
        f"""
INSERT INTO
    cargo_fiscal.topic
        (id, consumer, domain, topic_id, context)
VALUES (24, 'delivery', 'orders', '{const.TOPIC_ID_21}',
null)""",
    )

    cursor.execute(
        f"""
INSERT INTO
    cargo_fiscal.transaction
        (topic_id, transaction_id, context)
VALUES (24, '{const.TRANSACTION_ID_21}',
'{{"transaction_id": "{const.TRANSACTION_ID_21}",
"is_refund": false, "price_details": {{
"total": "120.0"}}, "service_rendered_at": "2021-05-31T19:00:00+00:00",
"title": "Услуги доставки", "country": "KAZ", "provider_inn": "12345"}}')""",
    )

    # isr topic context

    cursor.execute(
        f"""
INSERT INTO
    cargo_fiscal.topic
        (id, consumer, domain, topic_id, context)
VALUES (9, 'delivery', 'orders', '{const.TOPIC_ID_3}',
'{{"service_rendered_at": "2021-05-31T19:00:00+00:00",
"title": "Delivery", "country": "ISR", "provider_inn": "12345"}}')""",
    )

    cursor.execute(
        f"""
INSERT INTO
    cargo_fiscal.transaction
        (topic_id, transaction_id, context)
VALUES (9, '{const.TRANSACTION_ID_3}',
'{{"transaction_id": "{const.TRANSACTION_ID_3}",
"is_refund": false, "price_details": {{
"total": "120.0"}}, "isr_data": {{"developer_email": "v@v.ru",
"customer_name": "Beloved Client",
"payment_type": 3, "cc_type": 2, "cc_type_name": "Visa",
"cc_number": "1234", "cc_deal_type": 1, "cc_num_of_payments": 1,
"cc_payment_num": 1, "item_amount": 1}} }}')""",
    )

    cursor.execute(
        f"""
INSERT INTO
    cargo_fiscal.register_delivery_orders_eazycount
        (updated_at, tin, access_token, refresh_token, is_valid, user_type)
VALUES ('2021-05-31T19:00:00+00:00', '12345',
'6UQWkfFuuI3tcZYp5I/yC+7u/tBJiH5P0/U++/njibxzu+KdoLfhuHKiB51Be390sO5h8KkX45L+9Bjgo6pfjw==',
'iUpTf6Uah2QIKkYX0G6xXnDM9KEtD/bt9mzdOHrieD5psYYrRGt19Ds5H0rETcXgLPIdsxgyaQYrirVydFCc6Q==',
true, 1)""",
    )

    cursor.execute(
        f"""
INSERT INTO
    cargo_fiscal.topic
        (id, consumer, domain, topic_id, context)
VALUES (11, 'delivery', 'orders', '{const.TOPIC_ID_4}',
'{{"service_rendered_at": "2021-05-31T19:00:00+00:00",
"title": "Delivery", "country": "ISR", "provider_inn": "123456"}}')""",
    )

    cursor.execute(
        f"""
INSERT INTO
    cargo_fiscal.transaction
        (topic_id, transaction_id, context)
VALUES (11, '{const.TRANSACTION_ID_4}',
'{{"transaction_id": "{const.TRANSACTION_ID_4}",
"is_refund": true, "price_details": {{
"total": "120.1"}}, "isr_data": {{"developer_email": "v@v.ru",
"customer_name": "Beloved Client",
"payment_type": 3, "cc_type": 2, "cc_type_name": "Visa",
"cc_number": "1234", "cc_deal_type": 1, "cc_num_of_payments": 1,
"cc_payment_num": 1, "item_amount": 1}} }}')""",
    )

    cursor.execute(
        f"""
INSERT INTO
    cargo_fiscal.topic
        (id, consumer, domain, topic_id, context)
VALUES (13, 'delivery', 'orders', '{const.TOPIC_ID_5}',
'{{"service_rendered_at": "2021-05-31T19:00:00+00:00",
"title": "Delivery", "country": "ISR", "provider_inn": "12345"}}')""",
    )

    cursor.execute(
        f"""
INSERT INTO
    cargo_fiscal.transaction
        (topic_id, transaction_id, context)
VALUES (13, '{const.TRANSACTION_ID_5}',
'{{"transaction_id": "{const.TRANSACTION_ID_5}",
"is_refund": false, "price_details": {{
"total": "120.0"}}, "isr_data": {{"developer_email": "v@v.ru",
"customer_name": "Beloved Client",
"payment_type": 1, "item_amount": 1}} }}')""",
    )

    cursor.execute(
        f"""
INSERT INTO
    cargo_fiscal.register_delivery_orders_eazycount
        (updated_at, tin, access_token, refresh_token, is_valid, user_type)
VALUES ('2021-05-31T19:00:00+00:00', '123456',
'iUpTf6Uah2QIKkYX0G6xXnDM9KEtD/bt9mzdOHrieD5psYYrRGt19Ds5H0rETcXgLPIdsxgyaQYrirVydFCc6Q==',
'iUpTf6Uah2QIKkYX0G6xXnDM9KEtD/bt9mzdOHrieD5psYYrRGt19Ds5H0rETcXgLPIdsxgyaQYrirVydFCc6Q==',
true, 3)""",
    )

    # isr transaction context

    cursor.execute(
        f"""
INSERT INTO
    cargo_fiscal.topic
        (id, consumer, domain, topic_id, context)
VALUES (131, 'delivery', 'orders', '{const.TOPIC_ID_6}',
'{{"service_rendered_at": "2021-05-31T19:00:00+00:00",
"title": "Delivery", "country": "ISR", "provider_inn":
"12345_park_type_1"}}')""",
    )

    cursor.execute(
        f"""
INSERT INTO
    cargo_fiscal.transaction
        (topic_id, transaction_id, context)
VALUES (131, '{const.TRANSACTION_ID_6}',
'{{"transaction_id": "{const.TRANSACTION_ID_6}",
"is_refund": true, "price_details": {{
"total": "120.0"}}, "isr_data": {{"developer_email": "v@v.ru",
"customer_name": "Beloved Client",
"payment_type": 1, "item_amount": 1}} }}')""",
    )

    cursor.execute(
        f"""
INSERT INTO
    cargo_fiscal.register_delivery_orders_eazycount
        (updated_at, tin, access_token, refresh_token, is_valid, user_type)
VALUES ('2021-05-31T19:00:00+00:00', '12345_park_type_1',
'iUpTf6Uah2QIKkYX0G6xXnDM9KEtD/bt9mzdOHrieD5psYYrRGt19Ds5H0rETcXgLPIdsxgyaQYrirVydFCc6Q==',
'iUpTf6Uah2QIKkYX0G6xXnDM9KEtD/bt9mzdOHrieD5psYYrRGt19Ds5H0rETcXgLPIdsxgyaQYrirVydFCc6Q==',
true, 1)""",
    )

    cursor.execute(
        f"""
INSERT INTO
    cargo_fiscal.topic
        (id, consumer, domain, topic_id, context)
VALUES (91, 'delivery', 'orders', '{const.TOPIC_ID_3_TC}',
null)""",
    )

    cursor.execute(
        f"""
INSERT INTO
    cargo_fiscal.transaction
        (topic_id, transaction_id, context)
VALUES (91, '{const.TRANSACTION_ID_3_TC}',
'{{"transaction_id": "{const.TRANSACTION_ID_3_TC}",
"is_refund": false, "price_details": {{
"total": "120.0"}}, "isr_data": {{"developer_email": "v@v.ru",
"customer_name": "Beloved Client",
"payment_type": 3, "cc_type": 2, "cc_type_name": "Visa",
"cc_number": "1234", "cc_deal_type": 1, "cc_num_of_payments": 1,
"cc_payment_num": 1, "item_amount": 1}},
"service_rendered_at": "2021-05-31T19:00:00+00:00",
"title": "Delivery", "country": "ISR", "provider_inn": "12345"}}')""",
    )

    cursor.execute(
        f"""
INSERT INTO
    cargo_fiscal.topic
        (id, consumer, domain, topic_id, context)
VALUES (111, 'delivery', 'orders', '{const.TOPIC_ID_4_TC}',
null)""",
    )

    cursor.execute(
        f"""
INSERT INTO
    cargo_fiscal.transaction
        (topic_id, transaction_id, context)
VALUES (111, '{const.TRANSACTION_ID_4_TC}',
'{{"transaction_id": "{const.TRANSACTION_ID_4_TC}",
"is_refund": true, "price_details": {{
"total": "120.1"}}, "isr_data": {{"developer_email": "v@v.ru",
"customer_name": "Beloved Client",
"payment_type": 3, "cc_type": 2, "cc_type_name": "Visa",
"cc_number": "1234", "cc_deal_type": 1, "cc_num_of_payments": 1,
"cc_payment_num": 1, "item_amount": 1}},
"service_rendered_at": "2021-05-31T19:00:00+00:00",
"title": "Delivery", "country": "ISR", "provider_inn": "123456"}}')""",
    )

    cursor.execute(
        f"""
INSERT INTO
    cargo_fiscal.topic
        (id, consumer, domain, topic_id, context)
VALUES (1311, 'delivery', 'orders', '{const.TOPIC_ID_5_TC}',
null)""",
    )

    cursor.execute(
        f"""
INSERT INTO
    cargo_fiscal.transaction
        (topic_id, transaction_id, context)
VALUES (1311, '{const.TRANSACTION_ID_5_TC}',
'{{"transaction_id": "{const.TRANSACTION_ID_5_TC}",
"is_refund": false, "price_details": {{
"total": "120.0"}}, "isr_data": {{"developer_email": "v@v.ru",
"customer_name": "Beloved Client",
"payment_type": 1, "item_amount": 1}},
"service_rendered_at": "2021-05-31T19:00:00+00:00",
"title": "Delivery", "country": "ISR", "provider_inn": "12345"}}')""",
    )

    cursor.close()


EZ_OAUTH_RESPONSE = {
    'access_token': '5460afaa648bc05e4056b7b51aedeb3a9e7ef63d',
    'expires_in': 630720000,
    'token_type': 'Bearer',
    'scope': 'CREATE_DOCS GET_USER_DATA',
    'refresh_token': '69bf9dca1771e712d7ea2bd62d818daf5d92cc07',
}
EZ_BAD_OAUTH_RESPONSE = {
    'error': 'invalid_grant',
    'error_description': (
        'Authorization code doesn\'t exist or is invalid for the client'
    ),
}

EZ_GOOD_QUERY = {
    'client_id': 'client_id',
    'client_secret': 'client_secret',
    'grant_type': 'authorization_code',
    'redirect_uri': 'example.com',
    'code': 'code_from_ez',
}

EZ_GOOD_REFRESH_QUERY = {
    'client_id': 'client_id',
    'client_secret': 'client_secret',
    'grant_type': 'refresh_token',
    'redirect_uri': 'example.com',
    'refresh_token': '5460afaa648bc05e4056b7b51aedeb3a9e7ef63d',
}


@pytest.fixture(name='mock_ez_auth')
def _mock_amo_auth(mockserver):
    @mockserver.json_handler('/eazy-count-cargo/general/oauth2/token')
    def mock(request):
        if request.json in (EZ_GOOD_QUERY, EZ_GOOD_REFRESH_QUERY):
            return mockserver.make_response(status=200, json=EZ_OAUTH_RESPONSE)
        return mockserver.make_response(status=400, json=EZ_BAD_OAUTH_RESPONSE)

    return mock


@pytest.fixture(name='mock_ez_user_type')
def _mock_ez_user_type(mockserver):
    @mockserver.json_handler('/eazy-count-cargo/api/users/getBusinessData')
    def mock(request):
        return mockserver.make_response(status=200, json={'u_comp_type': 1})

    return mock
