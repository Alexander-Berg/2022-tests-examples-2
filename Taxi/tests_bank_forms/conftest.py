import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from bank_audit_logger.mock_bank_audit import bank_audit  # noqa: F401
from bank_forms_plugins import *  # noqa: F403 F401


@pytest.fixture
def blackbox_mock(mockserver):
    def make_response_phone(yandex_uid):
        result = {
            '1234': {
                'users': [
                    {
                        'id': '1234',
                        'phones': [
                            {
                                'id': '1',
                                'attributes': {
                                    '4': '500',
                                    '102': '+79999999999',
                                    '104': '+7999*****99',
                                    '105': '1',
                                    '108': '1',
                                },
                            },
                            {
                                'id': '2',
                                'attributes': {
                                    '4': '1000',
                                    '102': '+79999999990',
                                    '104': '+7999*****90',
                                    '105': '1',
                                    '108': '1',
                                },
                            },
                        ],
                    },
                ],
            },
            '1233': {
                'users': [
                    {
                        'id': '1233',
                        'phones': [
                            {
                                'id': '1',
                                'attributes': {
                                    '4': '12344',
                                    '102': '+79999999999',
                                    '104': '+7999*****99',
                                    '105': '1',
                                },
                            },
                            {
                                'id': '2',
                                'attributes': {
                                    '4': '1567865',
                                    '102': '+79999999990',
                                    '104': '+7999*****90',
                                    '105': '1',
                                },
                            },
                            {
                                'id': '3',
                                'attributes': {
                                    '102': '+79999999991',
                                    '104': '+7999*****91',
                                },
                            },
                        ],
                    },
                ],
            },
            '1235': {
                'users': [
                    {
                        'id': '1235',
                        'phones': [
                            {
                                'id': '1',
                                'attributes': {
                                    '102': '+79999999999',
                                    '105': '1',
                                },
                            },
                        ],
                    },
                ],
            },
            '1236': {
                'users': [
                    {
                        'id': '1236',
                        'phones': [
                            {'id': '1', 'attributes': {'102': '+79999999999'}},
                        ],
                    },
                ],
            },
            '123': {'users': [{'id': '123'}]},
        }
        return result[yandex_uid]

    def make_response_userinfo(yandex_uid):
        result = {
            '1234': {
                'users': [
                    {
                        'id': '1234',
                        'attributes': {
                            '27': 'Пётр',
                            '28': 'Петров',
                            '30': '2000-07-02',
                        },
                    },
                ],
            },
            '1235': {
                'users': [
                    {
                        'id': '1235',
                        'attributes': {'27': 'Пётр', '28': 'Петров'},
                    },
                ],
            },
            '123': {'users': [{'id': '123'}]},
        }
        return result[yandex_uid]

    class Context:
        def __init__(self):
            self.blackbox_handler = None

    context = Context()

    @mockserver.json_handler('/blackbox/blackbox')
    def _mock_get_blackbox_info(request):
        assert request.query.get('method') == 'userinfo'
        if request.query.get(
                'phone_attributes',
        ) and '102' in request.query.get('phone_attributes'):
            return make_response_phone(request.query.get('uid'))
        if request.query.get('attributes') and '27' in request.query.get(
                'attributes',
        ):
            return make_response_userinfo(request.query.get('uid'))
        return mockserver.make_response(status=500)

    context.blackbox_handler = _mock_get_blackbox_info

    return context
