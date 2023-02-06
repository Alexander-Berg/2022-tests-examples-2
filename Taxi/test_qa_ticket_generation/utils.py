import datetime
from urllib import parse

import pytest

from tests_callcenter_stats.test_qa_ticket_generation import params


async def forward_stq(stq, stq_runner):
    stq_call = stq.operator_qa_ticket_generation.next_call()
    await stq_runner.operator_qa_ticket_generation.call(
        task_id=stq_call['id'],
        args=stq_call['args'],
        kwargs=stq_call['kwargs'],
    )


def to_datetime(string):
    return datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S+0000')


# timepoint - 1 minute
def pre_time_point(time_point):
    fmt = '%Y-%m-%dT%H:%M:%S+00:00'
    dtime = datetime.datetime.strptime(time_point, fmt)
    return datetime.datetime.strftime(
        dtime - datetime.timedelta(minutes=1), fmt,
    )


# first id from id_extractor must be call_link_id
def check_ticket(ticket, call_history_db, id_extractor, ml_rating=None):
    assert ticket['napravlenieSp'] == 'test_direction'
    assert ticket['type'] == 'prosluskaIOcenka'
    assert (
        ticket['queue'] == 'CALLS'
        or ticket['queue'] == 'CALLS_BEL'
        or ticket['queue'] == 'CALLS_INTERNAL'
    )
    assert ticket['summary'] == ' '.join(
        [ticket['imaOperatora'], ticket['RecTime'], ticket['RecDate']],
    ) or ticket['summary'] == ' '.join([ticket['RecTime'], ticket['RecDate']])

    assert (
        ticket['description'].find('Имя оператора: ' + ticket['imaOperatora'])
        != -1
    )
    assert ticket['description'].find('Логин: ' + ticket['login']) != -1
    assert (
        ticket['description'].find('Время звонка: ' + ticket['RecTime']) != -1
    )
    assert (
        ticket['description'].find('Дата звонка: ' + ticket['RecDate']) != -1
    )
    assert (
        ticket['description'].find(
            'Время в разговоре: ' + ticket['DialogTime'],
        )
        != -1
    )
    assert (
        ticket['description'].find(
            'Номер абонента: ' + ticket['PhoneNumberOktell'],
        )
        != -1
    )
    assert (
        ticket['description'].find('Номер линии: ' + ticket['nomerLinii'])
        != -1
    )
    assert ticket['description'].find('Город: ' + ticket['gorod']) != -1
    assert (
        ticket['description'].find('Имя очереди: ' + ticket['imaOceredi'])
        != -1
    )
    assert (
        ticket['description'].find('Ссылка на диалог: ' + ticket['RecURL'])
        != -1
    )
    assert ticket['components'] == params.OPERATOR_CALLCENTERS.get(
        ticket['login'],
    )
    assert (
        ticket['description'].find('Колл-центр: ' + ticket['components']) != -1
    )
    if ml_rating:
        assert ticket.get('mlRating')
        assert (
            ticket['description'].find(
                'Рейтинг ML: ' + str(ticket['mlRating']),
            )
            != -1
        )
    for i in range(1, 6):
        if ticket.get(f'ssylkaNaZakaz{i}'):
            assert (
                ticket['description'].find(
                    f'Ссылка на заказ {i}: ' + ticket[f'ssylkaNaZakaz{i}'],
                )
                != -1
            )
        else:
            assert ticket['description'].find(f'Ссылка на заказ {i}: ') == -1

    ids = id_extractor(ticket)

    expected_order_ids = params.ORDER_BY_CALL_LINK_ID.get(
        ids[0], params.ORDER_BY_CALL_LINK_ID['__default__'],
    )
    assert ticket['zakazOformlen'] == 'Да' if expected_order_ids else 'Нет'
    order_ids = set()
    for i in range(1, 6):
        if ticket.get(f'ssylkaNaZakaz{i}') and ticket[
                f'ssylkaNaZakaz{i}'
        ].startswith('order/'):
            encoded_order_id = ticket[f'ssylkaNaZakaz{i}'][6:]
            order_id = parse.unquote(encoded_order_id)
            assert order_id in expected_order_ids
            order_ids.add(order_id)
    import sys
    print(order_ids, expected_order_ids, file=sys.stderr)
    assert order_ids == expected_order_ids

    db_row = (
        *ids,
        ticket['imaOceredi'],
        datetime.datetime.fromisoformat(
            ticket['RecDate'] + 'T' + ticket['RecTime'] + '+03:00',
        ),
        params.OPERATOR_IDS.get(ticket['login']),
        params.PHONE_TO_PHONE_ID_MAPPING.get(ticket['PhoneNumberOktell']),
        ticket['nomerLinii'],
    )
    assert db_row in call_history_db

    assert (
        params.CC_PHONE_INFO_MAP.get(
            ticket['nomerLinii'], params.CC_PHONE_INFO_MAP['__default__'],
        )['city_name']
        == ticket['gorod']
    )


def mark_qa_ticket_gen_settings(settings_map):
    return pytest.mark.config(
        CALLCENTER_STATS_QA_TICKET_GENERATION_SETTINGS_MAP=settings_map,
    )
