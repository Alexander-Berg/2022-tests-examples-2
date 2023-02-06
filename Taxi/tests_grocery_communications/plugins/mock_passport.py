import pytest

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
            'regname': 'test',
            'display_name': {
                'name': 'Козьма Прутков',
                'public_name': 'Козьма П.',
                'avatar': {'default': '4000217463', 'empty': False},
                'social': {
                    'profile_id': '5328',
                    'provider': 'tw',
                    'redirect_target': (
                        '1323266014.26924.5328.'
                        '9e5e3b502d5ee16abc40cf1d972a1c17'
                    ),
                },
            },
            'public_id': 'mcat26m4cb7z951vv46zcbzgqt',
            'pin_status': True,
            'dbfields': {
                'accounts.login.uid': 'test',
                'userinfo.firstname.uid': None,
            },
            'attributes': {
                '25': '1:Девичья фамилия матери',
                '1': '1294999198',
                '27': 'Иван Иванович',
                '1015': '1',
            },
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
def mock_passport(mockserver):
    class Context:
        def __init__(self):
            self.response = USERINFO_RESPONSE

        def times_mock_blackbox_called(self):
            return mock_blackbox.times_called

        def flush(self):
            mock_blackbox.flush()

    context = Context()

    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        return context.response

    return context
