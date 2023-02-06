# pylint: disable=wildcard-import, unused-wildcard-import, import-error

import json

import pytest

from eats_order_send_plugins import *  # noqa: F403 F401


@pytest.fixture(name='mock_core_send_to_place')
def _mock_core_send_to_place(mockserver):
    def _inner(order_nr, sync: False, idempotency_key):
        @mockserver.json_handler('/eats-core-order-send/send-to-place')
        def core_send_to_place_handler(request):
            assert request.json == {
                'order_id': order_nr,
                'sync': sync,
                'idempotency_key': idempotency_key,
            }
            return mockserver.make_response(status=200, json={})

        return core_send_to_place_handler

    return _inner


@pytest.fixture(name='mock_core_cancel')
def _mock_core_cancel(mockserver):
    def _inner(order_id):
        @mockserver.json_handler('/eats-core-order-send/cancel')
        def core_cancel_handler(request):
            assert request.json == {'order_id': order_id}
            return mockserver.make_response(status=200, json={})

        return core_cancel_handler

    return _inner


@pytest.fixture()
def add_sending(pgsql):
    def do_add_sending(need_sending_history, sending_task):
        task_id = add_sending_task(
            pgsql,
            sending_task['order_id'],
            sending_task['created_at'],
            sending_task['planned_on'],
            sending_task['is_canceled'],
            sending_task['reasons'],
        )

        if need_sending_history:
            add_sending_history(pgsql, sending_task['sent_at'], task_id)

    return do_add_sending


def add_sending_task(
        pgsql, order_id, created_at, planned_on, is_canceled, reasons,
):
    cursor = pgsql['eats_order_send'].cursor()
    cursor.execute(
        f"""INSERT INTO eats_order_send.sending_tasks (
            order_id,
            created_at,
            planned_on,
            is_canceled,
            reasons
        )
        VALUES (
            '{order_id}',
            '{created_at}',
            '{planned_on}',
            '{is_canceled}',
            '{json.dumps(reasons)}'
        )
        RETURNING id""",
    )
    return list(cursor)[0][0]


def add_sending_history(pgsql, sent_at, task_id):
    cursor = pgsql['eats_order_send'].cursor()
    cursor.execute(
        f"""INSERT INTO eats_order_send.sending_history (sent_at, task_id)
            VALUES ('{sent_at}', '{task_id}')
            RETURNING id""",
    )
    return list(cursor)[0][0]
