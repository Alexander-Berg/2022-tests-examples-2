import pytest

from order_notify.generated.stq3 import stq_context
from order_notify.repositories.corp import corp_vars
from order_notify.repositories.order_info import OrderData


@pytest.fixture(name='mock_functions')
def mock_corp_send_functions(patch):
    class Counter:
        def __init__(self):
            self.times_called = 0

        def call(self):
            self.times_called += 1

    class Counters:
        def __init__(self):
            self.get_phone = Counter()

    counters = Counters()

    @patch('order_notify.repositories.personal.get_phone')
    async def _get_phone(context: stq_context.Context, personal_phone_id: str):
        assert personal_phone_id == 'n4mwhk8zn'
        counters.get_phone.call()
        return '+79701516448'

    return counters


@pytest.fixture(name='mock_server')
def mock_server_fixture(mockserver):
    @mockserver.json_handler('/corp-users/v1/ride_report/users')
    async def handler(request):
        assert request.method == 'GET'

        user_id = request.query['user_id']
        assert user_id in ('1', '2', '3')
        if user_id == '2':
            return mockserver.make_response(
                json={'id': '2', 'client_id': 'client_id', 'fullname': 'fill'},
                status=200,
            )
        if user_id == '3':
            return mockserver.make_response(
                json={
                    'id': '3',
                    'client_id': 'client_id',
                    'fullname': 'full',
                    'personal_phone_id': 'n4mwhk8zn',
                },
                status=200,
            )
        return mockserver.make_response(
            json={'message': 'not found'}, status=404,
        )

    return handler


@pytest.mark.parametrize(
    'o_request, expected_vars',
    [
        pytest.param({'s': 't'}, {}, id='no_corp'),
        pytest.param({'corp': {}}, {}, id='no_corp_user_id'),
        pytest.param({'corp': {'user_id': '1'}}, {}, id='no_corp_user_in_db'),
        pytest.param(
            {'corp': {'user_id': '2'}},
            {'phone_number': None, 'corp_user_fullname': 'fill'},
            id='no_personal_phone_id',
        ),
        pytest.param(
            {'corp': {'user_id': '3'}},
            {'phone_number': '+79701516448', 'corp_user_fullname': 'full'},
            id='corp_user_in_db',
        ),
    ],
)
async def test_get_corp_vars(
        stq3_context: stq_context.Context,
        mock_server,
        mock_functions,
        o_request,
        expected_vars,
):
    c_vars = await corp_vars.get_corp_vars(
        context=stq3_context,
        order_data=OrderData(
            brand='',
            country='',
            order={},
            order_proc={'order': {'request': o_request}},
        ),
    )
    assert c_vars == expected_vars
