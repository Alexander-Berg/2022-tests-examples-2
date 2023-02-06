# pylint: disable=redefined-outer-name
import pytest

import eats_order_integration.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['eats_order_integration.generated.service.pytest_plugins']


@pytest.fixture
def partner_mocks(mock_eats_partner_engine_yandex_eda, load_json, mockserver):
    @mock_eats_partner_engine_yandex_eda('/security/oauth/token')
    def fetch_token(request):
        expected_credentials = load_json('partner_mocks_data.json')[
            'credentials'
        ]
        token = load_json('partner_mocks_data.json')['access_token']

        assert request.method == 'POST'
        assert request.form['client_id'] == expected_credentials['client_id']
        assert (
            request.form['client_secret']
            == expected_credentials['client_secret']
        )
        assert request.form['scope'] == expected_credentials['scope']
        assert request.form['grant_type'] == 'client_credentials'

        return {'access_token': token}

    @mock_eats_partner_engine_yandex_eda('/order')
    def create_order(request):
        token = load_json('partner_mocks_data.json')['access_token']

        assert request.method == 'POST'
        assert request.headers['Authorization'] == f'Bearer {token}'

        return load_json('partner_mocks_data.json')['create_order_response']

    @mock_eats_partner_engine_yandex_eda(
        r'/order/(?P<order_id>\w+)$', regex=True,
    )
    def update_order(request, order_id):
        token = load_json('partner_mocks_data.json')['access_token']

        assert request.method == 'PUT'
        assert request.headers['Authorization'] == f'Bearer {token}'

        return load_json('partner_mocks_data.json')['update_order_response']

    def check_order_status(request):
        token = load_json('partner_mocks_data.json')['access_token']

        assert request.method == 'GET'
        assert request.headers['Authorization'] == f'Bearer {token}'

        return load_json('partner_mocks_data.json')[
            'check_order_status_response'
        ]

    def cancel_order(request):
        token = load_json('partner_mocks_data.json')['access_token']

        assert request.method == 'PUT'
        assert request.headers['Authorization'] == f'Bearer {token}'

        return mockserver.make_response(status=204)

    @mock_eats_partner_engine_yandex_eda(
        r'/order/(?P<order_id>\w+)/status', regex=True,
    )
    def order_status(request, order_id):
        if request.method == 'GET':
            return check_order_status(request)
        if request.method == 'PUT':
            return cancel_order(request)

        raise NotImplementedError

    return {
        'fetch_token': fetch_token,
        'create_order': create_order,
        'update_order': update_order,
        'order_status': order_status,
    }


@pytest.fixture
def processing_mocks(mock_processing, load_json, mockserver):
    def setup_mock(should_raise=False):
        @mock_processing('/v1/eda/orders_client/create-event')
        def create_event(request):  # pylint: disable=unused-variable
            if should_raise:
                return mockserver.make_response(
                    400, json={'code': 400, 'message': ''},
                )

            return load_json('processing.json')[request.json['order_event']]

    return setup_mock


class OrderIntegrationContext:
    def __init__(self):
        self.order_get_calls = 0
        self.order_post_calls = 0
        self.order_json_name = 'default'


@pytest.fixture(name='order_integration_context')
def _order_integration_context():
    return OrderIntegrationContext()


@pytest.fixture(name='order_integration_mock')
def _order_integration_mock(
        mock_eats_core_order_integration,
        order_integration_context,
        mockserver,
        load_json,
):
    class OrderMock:
        @staticmethod
        @mock_eats_core_order_integration('/v1/order')
        async def get_order_mock(request):
            if request.method == 'GET':
                order_integration_context.order_get_calls += 1
                return load_json('get_order.json')[
                    order_integration_context.order_json_name
                ]
            if request.method == 'POST':
                order_integration_context.order_post_calls += 1
                return mockserver.make_response(status=200, json='{}')

        @staticmethod
        @mock_eats_core_order_integration('/v1/order/add-send-mark')
        async def add_send_mark(request):  # pylint:disable=W0612
            return mockserver.make_response(status=200)

    return OrderMock()


@pytest.fixture(name='order_tech_info_mock')
def _order_tech_info_mock(mock_eats_core_orders, mockserver, load_json):
    @mock_eats_core_orders(
        r'/internal-api/v1/order/(?P<order_nr>\w+)/metainfo$', regex=True,
    )
    async def _order_get(request, order_nr):
        responses = load_json('order_tech_info.json')
        if order_nr in responses:
            return responses[order_nr]
        return responses['default']
