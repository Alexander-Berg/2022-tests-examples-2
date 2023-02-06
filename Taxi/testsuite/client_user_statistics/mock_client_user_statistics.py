import pytest


@pytest.fixture(name='client_user_statistic')
def mock_client_user_statistic(mockserver):
    class Context:
        def __init__(self):
            self.error = None
            self.response = None
            self.mock_v1_orders = None
            self.mock_v1_recent_orders = None

        @staticmethod
        def _build_identity(**kwargs):
            list_correct_identity = [
                'phone_id',
                'yandex_uid',
                'card_persistent_id',
                'device_id',
            ]
            allowed_keys = list(
                filter(
                    lambda key: key in list_correct_identity, kwargs.keys(),
                ),
            )
            assert len(allowed_keys) == 1, 'allowed only one id'
            key = allowed_keys[0]
            value = kwargs[key]
            return {'type': key, 'value': value}

        @staticmethod
        def _build_user_statistics_response(**kwargs):
            identity = Context._build_identity(**kwargs)
            counters = []
            if kwargs.get('value', None) is not None:
                counters = [
                    {
                        'counted_from': kwargs.get(
                            'counted_from', '2019-04-07T13:22:37.142+0000',
                        ),
                        'counted_to': kwargs.get(
                            'counted_to', '2020-04-07T13:22:37.142+0000',
                        ),
                        'properties': kwargs.get('properties', []),
                        'value': kwargs['value'],
                    },
                ]
            return {'data': [{'counters': counters, 'identity': identity}]}

        @staticmethod
        def _function_for_throw_exception(mockserver, error):
            assert hasattr(
                mockserver, error,
            ), f'{error} - unexpected error for mock'
            raise getattr(mockserver, error)()

        def setup(self, response=None, error=None):
            if 'response_json' in response:
                self.response = response
            elif 'response_params' in response:
                self.response = Context._build_user_statistics_response(
                    **(response['response_params']),
                )
            else:
                assert False, (
                    '\'response_json\' or \'response_params\' '
                    'is required, see docs for '
                    'client-user-statistics mock'
                )
            self.error = (
                error
                if callable(error) or error is None
                else lambda mockserver: Context._function_for_throw_exception(
                    mockserver, error,
                )
            )

    context = Context()

    @mockserver.json_handler('/user-statistics/v1/orders')
    def mock_v1_orders(request):
        if context.error is not None:
            raise context.error(mockserver)
        return context.response

    @mockserver.json_handler('/user-statistics/v1/recent-orders')
    def mock_v1_recent_orders(request):
        if context.error is not None:
            raise context.error(mockserver)
        return context.response

    context.mock_v1_orders = mock_v1_orders
    context.mock_v1_recent_orders = mock_v1_recent_orders

    return context
