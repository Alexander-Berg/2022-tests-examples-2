import pytest

from tests_cargo_crm import const


@pytest.fixture(name='blackbox_response')
def _blackbox_response():
    class Response:
        def __init__(self):
            self.user = {
                'uid': {'value': const.UID},
                'attributes': {'27': 'John', '28': 'Smith'},
                'phones': [{'attributes': {'102': const.PHONE, '108': '1'}}],
            }

        def add_user_phone(self, phone_attributes: dict):
            self.user['phones'].append({'attributes': phone_attributes})

        def add_user_confirmed_phone(self, number: str):
            self.add_user_phone({'102': number, '105': '1'})

        def switch_user_secured_phone(self, number: str):
            self.user['phones'] = []
            self.add_user_phone({'102': number, '108': '1'})

        def make(self, request):
            return {'users': [self.user]}

    return Response()


@pytest.fixture(name='blackbox', autouse=True)
def _blackbox(mockserver, blackbox_response):
    @mockserver.json_handler('/blackbox')
    def handler(request):
        return blackbox_response.make(request)

    return handler


@pytest.fixture(name='happy_path_events')
def _happy_path_events():
    return [
        {
            'event_id': 'ev_1',
            'created': '2021-06-20T10:00:00+00:00',
            'payload': {
                'kind': 'initial_form_request',
                'data': {
                    'operation_id': 'opid_1',
                    'revision': 0,
                    'requester_uid': const.UID,
                    'requester_login': const.LOGIN,
                    'form_data': {
                        'contact_phone': '',
                        'name': 'John',
                        'surname': 'Smith',
                    },
                    'form_pd': {'contact_phone_pd_id': const.PHONE_PD_ID},
                },
            },
        },
        {
            'event_id': 'ev_2',
            'created': '2021-06-20T10:00:01+00:00',
            'payload': {
                'kind': 'initial_form_result',
                'data': {'operation_id': 'opid_1'},
            },
        },
        {
            'event_id': 'ev_3',
            'created': '2021-06-20T10:02:00+00:00',
            'payload': {
                'kind': 'company_created_notification',
                'data': {
                    'form_data': {'corp_client_id': const.CORP_CLIENT_ID},
                    'form_pd': {},
                },
            },
        },
        {
            'event_id': 'ev_4',
            'created': '2021-06-20T10:03:00+00:00',
            'payload': {
                'kind': 'company_info_form_request',
                'data': {
                    'operation_id': 'opid_6',
                    'revision': 2,
                    'requester_uid': const.UID,
                    'requester_login': const.LOGIN,
                    'form_data': {
                        'name': 'Camomile Ltd.',
                        'country': 'ru',
                        'segment': 'Аптеки',
                        'city': 'moscow',
                        'email': '',
                        'phone': '',
                        'website': 'camomile.ru',
                    },
                    'form_pd': {
                        'phone_pd_id': const.PHONE_PD_ID,
                        'email_pd_id': const.EMAIL_PD_ID,
                    },
                },
            },
        },
        {
            'event_id': 'ev_5',
            'created': '2021-06-20T10:03:01+00:00',
            'payload': {
                'kind': 'company_info_form_result',
                'data': {'operation_id': 'opid_6'},
            },
        },
        {
            'event_id': 'ev_6',
            'created': '2021-06-20T10:04:00+00:00',
            'payload': {
                'kind': 'card_bound_notification',
                'data': {
                    'form_data': {
                        'corp_client_id': const.CORP_CLIENT_ID,
                        'yandex_uid': const.UID,
                        'card_id': const.CARD_ID,
                    },
                    'form_pd': {},
                },
            },
        },
        {
            'event_id': 'ev_7',
            'created': '2021-06-20T10:04:00+00:00',
            'payload': {
                'kind': 'resolution',
                'data': {'caused_by': 'phoenix:event:ev_6'},
            },
        },
    ]


@pytest.fixture(name='happy_path_offer_events')
def _happy_path_offer_events(happy_path_events):
    return happy_path_events[:-2] + [
        {
            'event_id': 'ev_6',
            'created': '2021-06-20T10:04:00+00:00',
            'payload': {
                'kind': 'offer_info_form_request',
                'data': {
                    'operation_id': 'opid_offer_6',
                    'revision': 5,
                    'requester_uid': const.UID,
                    'requester_login': const.LOGIN,
                    'form_data': {
                        'name': 'SuperCompanyName',
                        'longname': 'SuperCompanyLongname',
                        'postcode': '123456',
                        'postaddress': (
                            '123456; Super City, Super Street, 91/2, 10'
                        ),
                        'legaladdress': (
                            '123456; Super City, Super Street, 91/2, 10'
                        ),
                        'inn': '9234565432',
                        'bik': '044525225',
                        'account': '40703810938000010045',
                        'kind': 'rus',
                        'country': 'rus',
                    },
                    'form_pd': {},
                },
            },
        },
        {
            'event_id': 'ev_7',
            'created': '2021-06-20T10:04:01+00:00',
            'payload': {
                'kind': 'offer_info_form_result',
                'data': {
                    'operation_id': 'opid_offer_6',
                    'fail_reason': {
                        'code': 'error',
                        'details': {},
                        'message': 'error',
                    },
                },
            },
        },
        {
            'event_id': 'ev_extra_7',
            'created': '2021-06-20T10:04:02+00:00',
            'payload': {
                'kind': 'offer_info_form_request',
                'data': {
                    'operation_id': 'opid_offer_7',
                    'revision': 7,
                    'requester_uid': const.UID,
                    'requester_login': const.LOGIN,
                    'form_data': {
                        'name': 'CoolCompanyName',
                        'longname': 'CoolCompanyLongname',
                        'postcode': '123456',
                        'postaddress': (
                            '123456; Cool City, Cool Street, 91/2, 10'
                        ),
                        'legaladdress': (
                            '123456; Cool City, Cool Street, 91/2, 10'
                        ),
                        'inn': '1234565432',
                        'bik': '044525225',
                        'account': '40703810938000010045',
                        'kind': 'rus',
                        'country': 'rus',
                    },
                    'form_pd': {},
                },
            },
        },
        {
            'event_id': 'ev_extra_8',
            'created': '2021-06-20T10:04:03+00:00',
            'payload': {
                'kind': 'offer_info_form_result',
                'data': {'operation_id': 'opid_offer_7'},
            },
        },
        {
            'event_id': 'ev_8',
            'created': '2021-06-20T10:05:00+00:00',
            'payload': {
                'kind': 'balance_created_notification',
                'data': {
                    'form_data': {
                        'billing_id': const.BILLING_ID,
                        'person_id': const.PERSON_ID,
                        'contract': const.CONTRACT,
                    },
                    'form_pd': {},
                },
            },
        },
        {
            'event_id': 'ev_9',
            'created': '2021-06-20T10:06:00+00:00',
            'payload': {
                'kind': 'resolution',
                'data': {'caused_by': 'phoenix:event:ev_8'},
            },
        },
    ]


@pytest.fixture(name='initial_form')
def _initial_form(happy_path_events):
    for event in happy_path_events:
        if event['payload']['kind'] == 'initial_form_request':
            return event['payload']['data']['form_data']
    raise RuntimeError('never reach this line')


@pytest.fixture(name='company_created_form')
def _company_created_form(happy_path_events):
    for event in happy_path_events:
        if event['payload']['kind'] == 'company_created_notification':
            return event['payload']['data']['form_data']
    raise RuntimeError('never reach this line')


@pytest.fixture(name='company_info_form')
def _company_info_form(happy_path_events):
    for event in happy_path_events:
        if event['payload']['kind'] == 'company_info_form_request':
            return event['payload']['data']['form_data']
    raise RuntimeError('never reach this line')


@pytest.fixture(name='card_bound_form')
def _card_bound_form(happy_path_events):
    for event in happy_path_events:
        if event['payload']['kind'] == 'card_bound_notification':
            return event['payload']['data']['form_data']
    raise RuntimeError('never reach this line')


@pytest.fixture(name='offer_info_form')
def _offer_info_form(happy_path_offer_events):
    for event in happy_path_offer_events[::-1]:
        if event['payload']['kind'] == 'offer_info_form_request':
            return event['payload']['data']['form_data']
    raise RuntimeError('never reach this line')


@pytest.fixture(name='balance_created_form')
def _balance_created_form(happy_path_offer_events):
    for event in happy_path_offer_events:
        if event['payload']['kind'] == 'balance_created_notification':
            return event['payload']['data']['form_data']
    raise RuntimeError('never reach this line')


@pytest.fixture(name='offer_ticket_closed_state_expected')
def _offer_ticket_closed_state_expected(
        initial_form,
        company_created_form,
        company_info_form,
        offer_info_form,
        balance_created_form,
):
    return {
        'progress': {
            'last_modified_at': '2021-06-20T10:06:00+00:00',
            'resolution': {'caused_by': 'phoenix:event:ev_8'},
            'steps': [
                {
                    'name': 'initial_form',
                    'is_passed': True,
                    'last_modified_at': '2021-06-20T10:00:00+00:00',
                },
                {
                    'name': 'company_created_form',
                    'is_passed': True,
                    'last_modified_at': '2021-06-20T10:02:00+00:00',
                },
                {
                    'name': 'company_info_form',
                    'is_passed': True,
                    'last_modified_at': '2021-06-20T10:03:00+00:00',
                },
                {
                    'name': 'offer_info_form',
                    'is_passed': True,
                    'last_modified_at': '2021-06-20T10:04:02+00:00',
                },
                {
                    'name': 'balance_created_form',
                    'is_passed': True,
                    'last_modified_at': '2021-06-20T10:05:00+00:00',
                },
            ],
        },
        'forms': {
            'initial_form': {
                'contact_phone': const.PHONE,
                'name': 'John',
                'surname': 'Smith',
            },
            'company_created_form': company_created_form,
            'company_info_form': company_info_form,
            'offer_info_form': offer_info_form,
            'balance_created_form': balance_created_form,
        },
        'pending_operations': [],
        'next_step': {
            'disable_reason': {
                'code': 'ticket_closed',
                'message': 'Ticket is closed.',
                'details': {},
            },
        },
    }


@pytest.fixture(name='ticket_closed_state_expected')
def _ticket_closed_state_expected(
        initial_form, company_created_form, company_info_form, card_bound_form,
):
    return {
        'progress': {
            'last_modified_at': '2021-06-20T10:04:00+00:00',
            'resolution': {'caused_by': 'phoenix:event:ev_6'},
            'steps': [
                {
                    'name': 'initial_form',
                    'is_passed': True,
                    'last_modified_at': '2021-06-20T10:00:00+00:00',
                },
                {
                    'name': 'company_created_form',
                    'is_passed': True,
                    'last_modified_at': '2021-06-20T10:02:00+00:00',
                },
                {
                    'name': 'company_info_form',
                    'is_passed': True,
                    'last_modified_at': '2021-06-20T10:03:00+00:00',
                },
                {
                    'name': 'card_bound_form',
                    'is_passed': True,
                    'last_modified_at': '2021-06-20T10:04:00+00:00',
                },
            ],
        },
        'forms': {
            'initial_form': {
                'contact_phone': const.PHONE,
                'name': 'John',
                'surname': 'Smith',
            },
            'company_created_form': company_created_form,
            'company_info_form': company_info_form,
            'card_bound_form': card_bound_form,
        },
        'pending_operations': [],
        'next_step': {
            'disable_reason': {
                'code': 'ticket_closed',
                'message': 'Ticket is closed.',
                'details': {},
            },
        },
    }
