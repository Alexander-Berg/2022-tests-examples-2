# pylint: disable=redefined-outer-name
import decimal

import pytest

import eats_tips_withdrawal.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['eats_tips_withdrawal.generated.service.pytest_plugins']

# {'user_id': '1', 'user_code': '000010', 'user_group': '1'}
JWT_USER_1 = (
    'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiM'
    'SIsInVzZXJfY29kZSI6IjAwMDAxMCIsInVzZXJfZ3JvdXAiOiIxIn0'
    '.iyPeG0GUHJc1KptvQ1mgg5x4cb6yIk-NEZHddZ92umU'
)
# {'user_id': '2', 'user_code': '000020', 'user_group': '1'}
JWT_USER_2 = (
    'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiM'
    'iIsInVzZXJfY29kZSI6IjAwMDAyMCIsInVzZXJfZ3JvdXAiOiIxIn0'
    '.r6yQPPZuGp6rLxOT2U2IFSD2mJLXJfKlsl0EDKrezBM'
)
# {'exp': 1, 'user_id': '2', 'user_code': '000020', 'user_group': '1'}
JWT_USER_2_EXPIRED = (
    'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjEsInVzZ'
    'XJfaWQiOiIyIiwidXNlcl9jb2RlIjoiMDAwMDIwIiwidXNlcl9ncm9'
    '1cCI6IjEifQ.s_AEWiuVKkt_nqt8AgtmKHBItS-4OCjO_DEwEGqfYzA'
)
# {'user_id': '3', 'user_code': '000030', 'user_group': '2'}
JWT_USER_3 = (
    'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiM'
    'yIsInVzZXJfY29kZSI6IjAwMDAzMCIsInVzZXJfZ3JvdXAiOiIyIn0'
    '.SoqiXrnYeV1oFGVm4yNt2w3ikhOSSrqZE89TNgjTk_Y'
)
# {'user_id': '4', 'user_code': '000040', 'user_group': '1'}
JWT_USER_4 = (
    'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiN'
    'CIsInVzZXJfY29kZSI6IjAwMDA0MCIsInVzZXJfZ3JvdXAiOiIxIn0'
    '.S9rWLCsaMj2Q0rrtspKnnYaPTJU0ErHAme3jsHkyiYQ'
)
# {'user_id': '5', 'user_code': '000050', 'user_group': '1'}
JWT_USER_5 = (
    'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiN'
    'SIsInVzZXJfY29kZSI6IjAwMDA1MCIsInVzZXJfZ3JvdXAiOiIxIn0'
    '.dil9yKv5COYB2Z6neVPSU-VKF4uYQDCBTm0IGjQSRnE'
)
# {'user_id': '6', 'user_code': '000060', 'user_group': '1'}
JWT_USER_6 = (
    'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiN'
    'iIsInVzZXJfY29kZSI6IjAwMDA2MCIsInVzZXJfZ3JvdXAiOiIxIn0'
    '.qmGYa0zxMuiCRmLNWK0iKLC26EJnjCABaEczKgJSXPo'
)
# {'user_id': '11', 'user_code': '000110', 'user_group': '1'}
JWT_USER_11 = (
    'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiMT'
    'EiLCJ1c2VyX2NvZGUiOiIwMDAxMTAiLCJ1c2VyX2dyb3VwIjoiMSJ9.'
    '5uwH-7qCj4jJQLdn7hM05meeyUkddBTj73axto-WKIA'
)
# {'user_id': '20', 'user_code': '000200', 'user_group': '4'}
JWT_USER_20 = (
    'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiM'
    'jAiLCJ1c2VyX2NvZGUiOiIwMDAyMDAiLCJ1c2VyX2dyb3VwIjoiNCJ9'
    '.RyOFHVyQoE_EtMELbJGN3hGqLUQFqqegs7z18LFqWq0'
)
# {'user_id': '27', 'user_code': '000270', 'user_group': '4'}
JWT_USER_27 = (
    'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiMj'
    'ciLCJ1c2VyX2NvZGUiOiIwMDAyNzAiLCJ1c2VyX2dyb3VwIjoiNCJ9.'
    'ZOo9fgPP8PbwUE9nx78rAXqY3BzREcVR1Anz1c3YpEw'
)

USER_ID_1 = '19cf3fc9-98e5-4e3d-8459-179a602bd7a8'
USER_ID_2 = '19cf3fc9-98e5-4e3d-8459-179a602bd7a2'

PARTNER_1 = {
    'id': '00000000-0000-0000-0000-000000000001',
    'alias': '10',
    'b2p_id': '1',
    'mysql_id': '1',
    'display_name': '',
    'full_name': 'нормальный',
    'phone_id': '123456',
    'saving_up_for': '',
    'is_vip': False,
    'registration_date': '1970-01-01T03:00:00+03:00',
    'best2pay_card_token': 'token1',
    'best2pay_card_pan': 'some_pan',
    'best2pay_blocked': False,
    'is_admin_reg': False,
    'is_free_procent': False,
    'trans_guest': False,
    'trans_guest_block': False,
    'b2p_block_mcc': False,
    'b2p_block_full': False,
}
PARTNER_2 = {
    'id': '00000000-0000-0000-0000-000000000002',
    'alias': '20',
    'b2p_id': '2',
    'mysql_id': '2',
    'display_name': '',
    'full_name': 'заблоченный',
    'phone_id': '123456',
    'saving_up_for': '',
    'is_vip': False,
    'registration_date': '1970-01-01T03:00:00+03:00',
    'best2pay_card_token': 'token2',
    'best2pay_card_pan': 'some_pan',
    'best2pay_blocked': False,
    'is_admin_reg': False,
    'is_free_procent': False,
    'trans_guest': False,
    'trans_guest_block': False,
    'b2p_block_mcc': False,
    'b2p_block_full': False,
}
PARTNER_4 = {
    'id': '00000000-0000-0000-0000-000000000004',
    'alias': '40',
    'b2p_id': '4',
    'mysql_id': '4',
    'display_name': 'юзер кафе без имени',
    'full_name': '',
    'phone_id': '123456',
    'saving_up_for': '',
    'is_vip': False,
    'registration_date': '1970-01-01T03:00:00+03:00',
    'best2pay_card_token': 'token4',
    'best2pay_card_pan': 'some_pan',
    'best2pay_blocked': False,
    'is_admin_reg': False,
    'is_free_procent': False,
    'trans_guest': False,
    'trans_guest_block': False,
    'b2p_block_mcc': False,
    'b2p_block_full': False,
}
PARTNER_5 = {
    'id': '00000000-0000-0000-0000-000000000005',
    'alias': '50',
    'b2p_id': '5',
    'mysql_id': '5',
    'display_name': '',
    'full_name': 'заблоченный юзер кафе',
    'phone_id': '123456',
    'saving_up_for': '',
    'is_vip': False,
    'registration_date': '2021-10-7T18:09:49+03:00',
    'best2pay_card_token': 'token5',
    'best2pay_card_pan': 'some_pan',
    'best2pay_blocked': False,
    'is_admin_reg': False,
    'is_free_procent': False,
    'trans_guest': False,
    'trans_guest_block': False,
    'b2p_block_mcc': False,
    'b2p_block_full': False,
}
PARTNER_6 = {
    'id': '00000000-0000-0000-0000-000000000006',
    'alias': '60',
    'b2p_id': '6',
    'mysql_id': '6',
    'display_name': 'юзер кафе без имени с телефоном',
    'full_name': '',
    'phone_id': '123456',
    'saving_up_for': '',
    'is_vip': True,
    'registration_date': '1970-01-01T03:00:00+03:00',
    'best2pay_card_token': '',
    'best2pay_blocked': False,
    'is_admin_reg': False,
    'is_free_procent': False,
    'trans_guest': False,
    'trans_guest_block': False,
    'b2p_block_mcc': False,
    'b2p_block_full': False,
}
PARTNER_11 = {
    'id': '00000000-0000-0000-0000-000000000011',
    'alias': '110',
    'b2p_id': '11',
    'mysql_id': '11',
    'display_name': 'официант второго кафе',
    'full_name': 'официант',
    'phone_id': '123456',
    'saving_up_for': '',
    'is_vip': True,
    'registration_date': '1970-01-01T03:00:00+03:00',
    'best2pay_card_token': 'token11',
    'best2pay_card_pan': 'some_pan',
    'best2pay_blocked': False,
    'is_admin_reg': False,
    'is_free_procent': False,
    'trans_guest': False,
    'trans_guest_block': False,
    'b2p_block_mcc': False,
    'b2p_block_full': False,
}
PLACES = {
    '1': {
        'place_id': '1',
        'title': '',
        'address': '',
        'confirmed': True,
        'show_in_menu': True,
        'brand_slug': 'elite',
        'roles': [],
    },
    '2': {
        'place_id': '2',
        'title': '',
        'address': '',
        'confirmed': True,
        'show_in_menu': True,
        'brand_slug': 'not elite',
        'roles': [],
    },
    '3': {
        'place_id': '3',
        'title': '',
        'address': '',
        'confirmed': True,
        'show_in_menu': True,
        'roles': [],
    },
}
PARTNERS = {
    '00000000-0000-0000-0000-000000000001': PARTNER_1,
    '00000000-0000-0000-0000-000000000002': PARTNER_2,
    '00000000-0000-0000-0000-000000000004': PARTNER_4,
    '00000000-0000-0000-0000-000000000005': PARTNER_5,
    '00000000-0000-0000-0000-000000000006': PARTNER_6,
    '00000000-0000-0000-0000-000000000011': PARTNER_11,
}


def format_partner_response(partner_id, place_ids=None):
    if place_ids is None:
        place_ids = []
    result = {
        'info': {
            'id': partner_id,
            'b2p_id': PARTNERS[partner_id]['mysql_id'],
            'display_name': '',
            'full_name': '',
            'phone_id': 'phone_id_1',
            'saving_up_for': '',
            'best2pay_blocked': False,
            'registration_date': '1970-01-01T03:00:00+03:00',
            'is_vip': False,
            'blocked': False,
        },
        'places': [PLACES[place_id] for place_id in place_ids],
    }
    return result


def make_stat(labels: dict) -> dict:
    return {'kind': 'IGAUGE', 'labels': labels, 'timestamp': None, 'value': 1}


def check_task_rescheduled(stq, queue, eta):
    task = queue.next_call()
    assert task.pop('id')
    assert task.pop('queue')
    assert task == {
        'eta': eta.replace(tzinfo=None),
        'args': None,
        'kwargs': None,
    }
    assert stq.is_empty


def check_task_queued(stq, queue, kwargs, drop=()):
    task = queue.next_call()
    assert task.pop('eta')
    assert task.pop('id')
    assert task.pop('queue')
    for arg in drop:
        assert task['kwargs'].pop(arg)
    assert task == {'args': [], 'kwargs': kwargs}


def get_db_usage_exp(user_id: int, use_pg: bool):
    return pytest.mark.client_experiments3(
        consumer='eats-tips-withdrawal/what-db-use-for-user',
        experiment_name='eda_tips_withdrawals_what_db_use',
        args=[{'name': 'user_id', 'type': 'int', 'value': user_id}],
        value={'enabled': use_pg},
    )


async def check_pushes(
        expected_push_text,
        expected_push_title,
        expected_withdrawal_status,
        amount,
        stq,
        partner_id,
        success_status,
):
    if expected_push_text:
        expected_title = (
            expected_push_title.format(amount=decimal.Decimal(amount))
            if expected_withdrawal_status == success_status
            else expected_push_title
        )
        assert stq.eats_tips_partners_send_push.times_called == 1
        check_task_queued(
            stq,
            stq.eats_tips_partners_send_push,
            {
                'text': expected_push_text,
                'partner_id': partner_id,
                'title': expected_title,
                'intent': 'withdrawal',
            },
        )
    else:
        assert not stq.eats_tips_partners_send_push.times_called
