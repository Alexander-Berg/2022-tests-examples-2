import hashlib
import hmac
from xml.etree import ElementTree

import jwt
import pytest

# pylint: disable=redefined-outer-name
import eats_tips_partners.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['eats_tips_partners.generated.service.pytest_plugins']


def create_jwt(user_id):
    return jwt.encode(
        {
            'user_id': str(user_id),
            'user_code': (str(user_id) + '0').zfill(7),
            'user_group': '1',
        },
        key='awesome_jwt_signature_key',
    ).decode()


def create_hmac(total_string, secret):
    return hmac.new(
        secret.encode('utf8'), total_string.encode('utf8'), hashlib.sha512,
    ).hexdigest()


def check_task_queued(stq, queue, kwargs, drop=()):
    task = queue.next_call()
    assert task.pop('eta')
    assert task.pop('id')
    assert task.pop('queue')
    for arg in drop:
        task['kwargs'].pop(arg)
    assert task == {'args': [], 'kwargs': kwargs}


@pytest.fixture(name='mock_tvm_rules', scope='function')
async def _mock_tvm_rules(taxi_config):
    taxi_config.set_values(
        {
            'TVM_RULES': [
                {'src': 'eats-tips-partners', 'dst': 'personal'},
                {'src': 'eats-tips-partners', 'dst': 'stq-agent'},
            ],
        },
    )


@pytest.fixture
def mock_limits(mock_sms_ru):
    def _wrapper(response):
        @mock_sms_ru('/my/limit')
        async def _handler(request):
            return response

        return _handler

    return _wrapper


@pytest.fixture
def mock_solomon(mockserver):
    def _wrapper():
        @mockserver.json_handler('/solomon/')
        async def _handler(request):
            return {}

        return _handler

    return _wrapper


def place_by_alias(alias, title, photo=None):
    place = {
        'alias': f'{alias}0'.zfill(7),
        'id': f'10000000-0000-0000-0000-{alias.zfill(12)}',
        'title': title,
        'mysql_id': alias,
    }
    if photo:
        place['photo'] = photo
    return place


PLACE_100 = place_by_alias('100', 'Деревня Вилларибо', 'фото_ресторана')
PLACE_101 = place_by_alias(
    '101', 'Деревня Виллабаджо', 'другое_фото_ресторана',
)
PLACE_102 = place_by_alias('102', 'Сам себе ресторан')
PLACE_104 = place_by_alias('104', '', None)
PLACE_106 = place_by_alias('106', 'Фиксики inside', 'фото_помогатора')
PLACE_107 = place_by_alias('107', '', None)


PARTNERS = {
    '10': {
        'id': '00000000-0000-0000-0000-000000000010',
        'alias': '0000100',
        'b2p_id': '10',
        'mysql_id': '10',
        'display_name': 'Васёк',
        'full_name': 'Чаевых Василий Вилларибо',
        'phone_id': '123456',
        'saving_up_for': 'трактор',
        'is_vip': False,
        'registration_date': '1970-01-01T03:00:01+03:00',
        'blocked': False,
        'best2pay_card_token': 'token1',
        'best2pay_card_pan': 'pan1',
        'best2pay_blocked': False,
        'is_admin_reg': False,
        'is_free_procent': False,
        'trans_guest': False,
        'trans_guest_block': True,
        'b2p_block_mcc': False,
        'b2p_block_full': False,
    },
    '11': {
        'id': '00000000-0000-0000-0000-000000000011',
        'display_name': 'Петро',
        'full_name': 'Чаевых Петр Вилларибо',
        'phone_id': '123456',
        'saving_up_for': '',
        'alias': '0000110',
        'b2p_id': '11',
        'mysql_id': '11',
        'photo': 'ссылка_на_s3',
        'is_vip': False,
        'registration_date': '1970-01-01T03:00:01+03:00',
        'blocked': False,
        'best2pay_card_token': 'token2',
        'best2pay_card_pan': 'pan2',
        'best2pay_blocked': False,
        'is_admin_reg': False,
        'is_free_procent': False,
        'trans_guest': False,
        'trans_guest_block': True,
        'b2p_block_mcc': True,
        'b2p_block_full': False,
    },
    '12': {
        'id': '00000000-0000-0000-0000-000000000012',
        'alias': '0000120',
        'b2p_id': '12',
        'mysql_id': '12',
        'display_name': 'Ванюха',
        'full_name': 'Чаевых Иван Вилларибо',
        'phone_id': '123456',
        'saving_up_for': '',
        'is_vip': False,
        'registration_date': '1970-01-01T03:00:01+03:00',
        'blocked': False,
        'best2pay_card_token': 'token3',
        'best2pay_card_pan': 'pan3',
        'best2pay_blocked': False,
        'is_admin_reg': False,
        'is_free_procent': False,
        'trans_guest': False,
        'trans_guest_block': True,
        'b2p_block_mcc': False,
        'b2p_block_full': True,
    },
    '13': {
        'id': '00000000-0000-0000-0000-000000000013',
        'alias': '0000130',
        'b2p_id': '13',
        'mysql_id': '13',
        'display_name': 'Стёпа',
        'full_name': 'Чаевых Степан Вилларибо',
        'phone_id': '123456',
        'saving_up_for': '',
        'is_vip': False,
        'registration_date': '1970-01-01T03:00:01+03:00',
        'blocked': False,
        'best2pay_card_token': 'token4',
        'best2pay_card_pan': 'pan4',
        'best2pay_blocked': False,
        'is_admin_reg': False,
        'is_free_procent': False,
        'trans_guest': False,
        'trans_guest_block': True,
        'b2p_block_mcc': False,
        'b2p_block_full': False,
    },
    '15': {
        'id': '00000000-0000-0000-0000-000000000015',
        'alias': '0000150',
        'b2p_id': '15',
        'mysql_id': '15',
        'display_name': 'Настюха',
        'full_name': 'Чаевых Анастасия Вилларибо',
        'phone_id': '123456',
        'saving_up_for': '',
        'is_vip': False,
        'registration_date': '1970-01-01T03:00:01+03:00',
        'blocked': False,
        'best2pay_card_token': 'token6',
        'best2pay_card_pan': 'pan6',
        'best2pay_blocked': False,
        'is_admin_reg': False,
        'is_free_procent': False,
        'trans_guest': False,
        'trans_guest_block': True,
        'b2p_block_mcc': False,
        'b2p_block_full': False,
    },
    '16': {
        'id': '00000000-0000-0000-0000-000000000016',
        'alias': '0000160',
        'b2p_id': '16',
        'mysql_id': '16',
        'display_name': '',
        'full_name': '',
        'phone_id': '',
        'saving_up_for': '',
        'is_vip': False,
        'registration_date': '0001-01-01T02:30:00+02:30',
        'blocked': False,
        'best2pay_blocked': False,
        'is_admin_reg': False,
        'is_free_procent': False,
        'trans_guest': False,
        'trans_guest_block': False,
        'b2p_block_mcc': False,
        'b2p_block_full': False,
    },
    '17': {
        'id': '00000000-0000-0000-0000-000000000017',
        'alias': '0000170',
        'b2p_id': '17',
        'mysql_id': '17',
        'display_name': '',
        'full_name': '',
        'phone_id': '',
        'saving_up_for': '',
        'is_vip': False,
        'registration_date': '0001-01-01T02:30:00+02:30',
        'blocked': False,
        'best2pay_blocked': False,
        'is_admin_reg': False,
        'is_free_procent': False,
        'trans_guest': False,
        'trans_guest_block': False,
        'b2p_block_mcc': False,
        'b2p_block_full': False,
    },
    '18': {
        'id': '00000000-0000-0000-0000-000000000018',
        'alias': '0000180',
        'b2p_id': '18',
        'mysql_id': '18',
        'display_name': '',
        'full_name': '',
        'phone_id': '',
        'saving_up_for': '',
        'is_vip': False,
        'registration_date': '0001-01-01T02:30:00+02:30',
        'blocked': False,
        'best2pay_blocked': False,
        'is_admin_reg': False,
        'is_free_procent': False,
        'trans_guest': False,
        'trans_guest_block': False,
        'b2p_block_mcc': False,
        'b2p_block_full': False,
    },
    '20': {
        'id': '00000000-0000-0000-0000-000000000020',
        'display_name': '',
        'full_name': '',
        'phone_id': '',
        'saving_up_for': '',
        'alias': '0000200',
        'b2p_id': '20',
        'is_vip': False,
        'registration_date': '0001-01-01T02:30:00+02:30',
        'blocked': False,
        'best2pay_blocked': False,
        'is_admin_reg': False,
        'is_free_procent': False,
        'trans_guest': False,
        'trans_guest_block': False,
        'b2p_block_mcc': False,
        'b2p_block_full': False,
    },
    '21': {
        'id': '00000000-0000-0000-0000-000000000021',
        'display_name': '',
        'full_name': '',
        'phone_id': '',
        'saving_up_for': '',
        'alias': '0000210',
        'b2p_id': '21',
        'is_vip': False,
        'registration_date': '0001-01-01T02:30:00+02:30',
        'blocked': False,
        'best2pay_blocked': False,
        'is_admin_reg': False,
        'is_free_procent': False,
        'trans_guest': False,
        'trans_guest_block': False,
        'b2p_block_mcc': False,
        'b2p_block_full': False,
    },
    '22': {
        'id': '00000000-0000-0000-0000-000000000022',
        'display_name': '',
        'full_name': 'Чаевых Ноунейм Вилларибо',
        'phone_id': '123456',
        'saving_up_for': '',
        'alias': '0000220',
        'b2p_id': '22',
        'mysql_id': '22',
        'is_vip': False,
        'registration_date': '1970-01-01T03:00:01+03:00',
        'best2pay_card_token': 'token8',
        'best2pay_card_pan': 'pan8',
        'blocked': False,
        'best2pay_blocked': False,
        'is_admin_reg': False,
        'is_free_procent': False,
        'trans_guest': False,
        'trans_guest_block': True,
        'b2p_block_mcc': False,
        'b2p_block_full': False,
    },
    '23': {
        'id': '00000000-0000-0000-0000-000000000023',
        'display_name': 'Тоха',
        'full_name': 'Чаевых Антон Вилларибо',
        'phone_id': '123456',
        'saving_up_for': 'машину',
        'alias': '0000230',
        'b2p_id': '23',
        'mysql_id': '23',
        'photo': 'красивое_фото',
        'is_vip': False,
        'registration_date': '1970-01-01T03:00:01+03:00',
        'best2pay_card_token': 'token9',
        'best2pay_card_pan': 'pan9',
        'blocked': False,
        'best2pay_blocked': False,
        'is_admin_reg': False,
        'is_free_procent': False,
        'trans_guest': False,
        'trans_guest_block': True,
        'b2p_block_mcc': False,
        'b2p_block_full': False,
    },
    '100': {
        'id': '00000000-0000-0000-0000-000000000100',
        'b2p_id': '100',
        'mysql_id': '100',
        'display_name': '',
        'full_name': 'Деревня Вилларибо',
        'phone_id': '123456',
        'photo': 'фото_ресторана',
        'saving_up_for': '',
        'is_vip': False,
        'registration_date': '1970-01-01T03:00:01+03:00',
        'best2pay_card_token': 'token10',
        'best2pay_card_pan': '',
        'blocked': False,
        'best2pay_blocked': False,
        'is_admin_reg': False,
        'is_free_procent': False,
        'trans_guest': False,
        'trans_guest_block': True,
        'b2p_block_mcc': False,
        'b2p_block_full': False,
    },
    '102': {
        'id': '00000000-0000-0000-0000-000000000102',
        'b2p_id': '102',
        'mysql_id': '102',
        'display_name': '',
        'full_name': 'Сам себе ресторан',
        'saving_up_for': '',
        'phone_id': '123456',
        'is_vip': False,
        'registration_date': '1970-01-01T03:00:01+03:00',
        'best2pay_card_token': 'token12',
        'best2pay_card_pan': '',
        'blocked': False,
        'best2pay_blocked': False,
        'is_admin_reg': False,
        'is_free_procent': False,
        'trans_guest': False,
        'trans_guest_block': True,
        'b2p_block_mcc': False,
        'b2p_block_full': False,
    },
    '104': {
        'id': '00000000-0000-0000-0000-000000000104',
        'b2p_id': '104',
        'mysql_id': '104',
        'display_name': '',
        'full_name': '',
        'phone_id': '',
        'saving_up_for': '',
        'is_vip': False,
        'registration_date': '0001-01-01T02:30:00+02:30',
        'blocked': False,
        'best2pay_blocked': False,
        'is_admin_reg': False,
        'is_free_procent': False,
        'trans_guest': False,
        'trans_guest_block': False,
        'b2p_block_mcc': False,
        'b2p_block_full': False,
    },
    '105': {
        'id': '00000000-0000-0000-0000-000000000105',
        'b2p_id': '105',
        'mysql_id': '105',
        'display_name': '',
        'full_name': '',
        'phone_id': '',
        'saving_up_for': '',
        'is_vip': False,
        'registration_date': '0001-01-01T02:30:00+02:30',
        'blocked': False,
        'best2pay_blocked': False,
        'is_admin_reg': False,
        'is_free_procent': False,
        'trans_guest': False,
        'trans_guest_block': False,
        'b2p_block_mcc': False,
        'b2p_block_full': False,
    },
    '106': {
        'id': '00000000-0000-0000-0000-000000000106',
        'b2p_id': '106',
        'mysql_id': '106',
        'display_name': '',
        'full_name': 'Фиксики inside',
        'phone_id': '123456',
        'photo': 'фото_помогатора',
        'saving_up_for': '',
        'is_vip': False,
        'registration_date': '1970-01-01T03:00:01+03:00',
        'blocked': False,
        'best2pay_card_token': 'token13',
        'best2pay_card_pan': '',
        'best2pay_blocked': False,
        'is_admin_reg': False,
        'is_free_procent': False,
        'trans_guest': False,
        'trans_guest_block': True,
        'b2p_block_mcc': False,
        'b2p_block_full': False,
    },
    '700': {
        'id': '00000000-0000-0000-0000-000000000700',
        'alias': '0007000',
        'b2p_id': '700',
        'mysql_id': '700',
        'display_name': '',
        'full_name': 'Важный админ',
        'phone_id': '123456',
        'saving_up_for': '',
        'is_vip': False,
        'registration_date': '1970-01-01T03:00:01+03:00',
        'blocked': False,
        'best2pay_card_token': 'token700',
        'best2pay_card_pan': 'pan700',
        'best2pay_blocked': False,
        'is_admin_reg': False,
        'is_free_procent': False,
        'trans_guest': False,
        'trans_guest_block': True,
        'b2p_block_mcc': False,
        'b2p_block_full': False,
    },
}
JWT_USER_11 = (
    'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiMT'
    'EiLCJ1c2VyX2NvZGUiOiIwMDAxMTAiLCJ1c2VyX2dyb3VwIjoiMSJ9.'
    '5uwH-7qCj4jJQLdn7hM05meeyUkddBTj73axto-WKIA'
)
JWT_USER_27 = (
    'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiMj'
    'ciLCJ1c2VyX2NvZGUiOiIwMDAyNzAiLCJ1c2VyX2dyb3VwIjoiNCJ9.'
    'ZOo9fgPP8PbwUE9nx78rAXqY3BzREcVR1Anz1c3YpEw'
)

SOME_B2P_ERROR_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?><error>
    <description>Ошибка: неверная цифровая подпись.</description>
    <code>109</code>
</error>"""

B2P_ALREADY_REGISTERED_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?><error>
    <description>Ошибка: Неверное значение параметра.</description>
    <code>139</code>
</error>"""


def dict_to_xml(xml_response: dict, tag='b2p_user'):
    elem = ElementTree.Element(tag)
    for key, val in xml_response.items():
        child = ElementTree.Element(key)
        child.text = str(val)
        elem.append(child)
    return elem


def b2p_user_answer(
        client_ref,
        first_name,
        second_name,
        last_name=None,
        pan=None,
        phone=None,
        reg_date='2022.04.29 14:18:53',
        sector='38',
        state='1',
        auth_state='0',
        active='0',
        status='OPEN',
        signature='ZmRjNjYwNTkxYzc4MzkxN2ZmYjUxY2Y3MWY2NjIwNTU=',
):
    b2p_dict = {
        'reg_date': reg_date,
        'sector': sector,
        'client_ref': client_ref,
        'state': state,
        'auth_state': auth_state,
        'active': active,
        'first_name': first_name,
        'second_name': second_name,
        'status': status,
        'signature': signature,
    }
    if last_name:
        b2p_dict['patronymic'] = last_name
    if pan:
        b2p_dict['pan'] = pan
    if phone:
        b2p_dict['phone'] = pan
    xml_element = dict_to_xml(b2p_dict)
    return ElementTree.tostring(xml_element, encoding='unicode')


def make_stat(labels: dict) -> dict:
    return {'kind': 'IGAUGE', 'labels': labels, 'timestamp': None, 'value': 1}
