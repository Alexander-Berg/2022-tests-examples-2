import functools

import pytest


@pytest.fixture(name='magnit_loyalty_check_balance_mock')
def _magnit_loyalty_check_balance_mock(mockserver):
    def factory(valid, **response_data):

        if valid:
            default_response_data = {'balanceDecimal': 0.0}
        else:
            default_response_data = {'error': 'error'}

        @mockserver.handler(
            r'/loyalty/b2b/trnprocessor/identifiers/'
            r'no=(?P<card_number>\d+)/check-balance',
            regex=True,
        )
        def _check_balance(request, card_number):
            assert 'location' in request.json
            assert 'partner' in request.json
            assert 'products' in request.json

            return mockserver.make_response(
                json={**default_response_data, **response_data},
            )

        return _check_balance

    return factory


@pytest.fixture(name='magnit_loyalty_sales_mock')
def _magnit_loyalty_sales_mock(mockserver):
    class Context:
        def __init__(self, **response_data):
            self.sales = None
            self.is_card_blocked = False
            self.blocked_card_headers = {
                'X-CLM-Error': 'TRN_IDENTIFIER_INVALID_STATUS',
            }
            self.default_response_data = {
                'pointsDecimal': 123,
                'pointTypes': [
                    {
                        'mainBalance': True,
                        'pointType': 'DD_YAEDA',
                        'pointsDecimal': 100.00,
                    },
                ],
            }
            self.response_data = response_data

        def set_card_blocked(self, blocked):
            self.is_card_blocked = blocked

    context = Context()

    @mockserver.handler(
        '/loyalty/b2b/trnprocessor/identifiers/' 'no=card_number/sales',
    )
    def _sales(request):
        assert 'location' in request.json
        assert 'partner' in request.json
        assert 'products' in request.json

        return (
            mockserver.make_response(
                json=None, status=500, headers=context.blocked_card_headers,
            )
            if context.is_card_blocked
            else mockserver.make_response(
                json={
                    **context.default_response_data,
                    **context.response_data,
                },
            )
        )

    context.sales = _sales

    return context


@pytest.fixture
def magnit_loyalty_login_mock(mockserver):
    def factory(**response_data):

        default_response_data = {
            'access_token': 'eyJhbGciOiJ',
            'token_type': 'bearer',
            'expires_in': 24999,
        }

        @mockserver.handler('/loyalty/b2b/login')
        def _login(request):
            assert request.form == {
                'client_id': 'test_login',
                'client_secret': 'test_password',
                'grant_type': 'client_credentials',
                'scope': 'any',
                'channel': 'L',
            }
            assert (
                request.headers['Content-Type']
                == 'application/x-www-form-urlencoded'
            )
            return mockserver.make_response(
                json={**default_response_data, **response_data},
            )

    return factory


@pytest.fixture
def magnit_loyalty_mocks(  # pylint: disable=W0621
        magnit_loyalty_login_mock,
        magnit_loyalty_check_balance_mock,
        magnit_loyalty_sales_mock,
):

    return {
        'login': magnit_loyalty_login_mock(),
        'check_balance': magnit_loyalty_check_balance_mock(valid=True),
        'sales': magnit_loyalty_sales_mock,
    }


@pytest.fixture
def user_id():
    return 1288356


@pytest.fixture
def loyalty_web_app_client(web_app_client, user_id):  # pylint: disable=W0621
    for method in ('get', 'post', 'delete', 'put', 'patch', 'head'):
        setattr(
            web_app_client,
            method,
            functools.partial(
                getattr(web_app_client, method),
                headers={'X-Eats-User': f'user_id={user_id}'},
            ),
        )
    return web_app_client


@pytest.fixture
def loyalty_method():
    return '/v1/loyalty'


@pytest.fixture
async def loyalty_card(  # pylint: disable=W0621
        magnit_loyalty_mocks, loyalty_web_app_client, loyalty_method,
):
    card_number = '1544126'
    response = await loyalty_web_app_client.post(
        loyalty_method, json={'card_number': card_number},
    )
    assert response.status == 200
    return card_number
