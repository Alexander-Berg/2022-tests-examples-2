import argparse

from scripts.dev.check_access_requests import get_selection


async def test_simple(tap):
    with tap.plan(1, 'Поиск запросов к серверу по коду ответа'):
        # Выполняем скрипт
        args = argparse.Namespace(
            code="401",
            input="tests/scripts/dev/data/nginx.log",
            output="tmp/",
        )
        counts = get_selection(args)

        tap.eq(
            counts,
            {
                '"GET /4.0/support_chat/v2/chats?services=lavka_storages'
                '&status=opened%2Cclosed&start_date=2021-03-02 HTTP/1.0"': 2,
                '"POST /api/disp/orders/load HTTP/1.0"': 1,
            },
            'Скрипт сработал',
        )
