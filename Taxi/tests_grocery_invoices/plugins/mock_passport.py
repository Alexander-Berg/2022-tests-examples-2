import copy

import pytest

from tests_grocery_invoices import consts

USERINFO_RESPONSE = {
    'users': [
        {
            'id': '3000062912',
            'uid': {
                'value': '3000062912',
                'hosted': False,
                'domid': '',
                'domain': '',
                'mx': '',
                'domain_ena': '',
                'catch_all': '',
            },
            'login': 'test',
            'aliases': {'6': 'uid-sjywgxrn'},
            'karma': {'value': 85, 'allow-until': 1321965947},
            'karma_status': {'value': 3085},
            'public_id': 'mcat26m4cb7z951vv46zcbzgqt',
            'pin_status': True,
            'attributes': {'1007': consts.PASSPORT_CUSTOMER_NAME},
            'phones': [{'id': '2', 'attributes': {'6': '1412183145'}}],
            'emails': [{'id': '2', 'attributes': {'1': 'my_email@gmail.com'}}],
            'address-list': [
                {
                    'address': 'test@yandex.ru',
                    'validated': True,
                    'default': True,
                    'rpop': False,
                    'unsafe': False,
                    'native': True,
                    'born-date': '2011-11-16 00:00:00',
                },
            ],
        },
    ],
}


@pytest.fixture(name='passport', autouse=True)
def mock_personal(mockserver):
    class Context:
        def __init__(self):
            self.response = copy.deepcopy(USERINFO_RESPONSE)

        def set_no_customer_name(self):
            del self.response['users'][0]['attributes']['1007']

        def times_mock_blackbox_called(self):
            return mock_blackbox.times_called

        def flush(self):
            mock_blackbox.flush()

    context = Context()

    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        return context.response

    return context
