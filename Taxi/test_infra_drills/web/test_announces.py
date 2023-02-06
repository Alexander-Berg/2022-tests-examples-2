import pytest

from test_infra_drills import conftest as cfg


@pytest.mark.parametrize(
    'test_request,test_result,test_status',
    [
        (
            {
                'business_unit': 'taxi',
                'drill_date': '2032-01-20',
                'type': 'telegram',
            },
            {
                'type': 'telegram',
                'message': (
                    '🌶 #учения ДЦ IVA\n'
                    '2032-01-20: Учения ДЦ IVA\n'
                    'comment\n'
                    '- Такси/Доставка: c 16:00 до 19:00 // '
                    '[ticket](TAXIADMIN-102); '
                    '[событие в календаре]'
                    '(https://calendar.yandex-team.ru?event_id=123456))\n'
                    '- - -\n'
                    'Важно!\n'
                    '➤ Мы просим дежурных от групп критичных сервисов, '
                    'влияющих на цикл заказа, подключиться к ЗУМУ УЧЕНИЙ '
                    '(сделать ссылкой), дежурные некритичных сервисов '
                    'подключаются по желанию\n'
                    '➤ Подробная информация о том, что будет происходить '
                    'во время учений добавлена в описание тикета учений\n'
                    '➤ Базы и разработческие виртуалки выключать не будем\n'
                    'Подписаться на канал '
                    '[I LIKE TECHNO](https://t.me/+TkyY_A8Jt5pB5nJD)'
                ),
                'result': 'None',
            },
            200,
        ),
        (
            {
                'business_unit': 'taxi',
                'drill_date': '2032-01-20',
                'type': 'email',
            },
            {
                'type': 'email',
                'message': (
                    'Subject: Общеяндексовые учения с закрытием IVA\n'
                    'Body: 🌶 #учения ДЦ IVA\n'
                    '2032-01-20: Учения ДЦ IVA в '
                    'Такси/Доставка c 2032-01-20\n'
                    'comment\n'
                    '- Такси/Доставка: c 16:00 до 19:00 // '
                    '[ticket](TAXIADMIN-102); '
                    '[событие в календаре]'
                    '(https://calendar.yandex-team.ru?event_id=123456))\n'
                    '- - -\n'
                    'Важно!\n'
                    '➤ Мы просим дежурных от групп критичных сервисов, '
                    'влияющих на цикл заказа, подключиться к ЗУМУ УЧЕНИЙ '
                    '(сделать ссылкой), дежурные некритичных сервисов '
                    'подключаются по желанию\n'
                    '➤ Подробная информация о том, что будет происходить '
                    'во время учений добавлена в описание тикета учений\n'
                    '➤ Базы и разработческие виртуалки выключать не будем\n'
                    'Подписаться на канал '
                    '[I LIKE TECHNO](https://t.me/+TkyY_A8Jt5pB5nJD)'
                ),
                'result': 'None',
            },
            200,
        ),
    ],
)
@pytest.mark.usefixtures('taxi_infra_drills_mocks')
@pytest.mark.pgsql('infra_drills', files=['basic.sql'])
@pytest.mark.translations(infra_drills=cfg.TANKER)
async def test_drill_announce_get(
        web_app_client,
        staff_mockserver,
        test_request,
        test_result,
        test_status,
):
    staff_mockserver()

    path = '/infra-drills/v1/announce'
    params = {
        'business_unit': test_request['business_unit'],
        'drill_date': test_request['drill_date'],
        'type': test_request['type'],
    }

    response = await web_app_client.get(
        path=path, params=params, headers=cfg.HEADERS,
    )

    assert response.status == test_status
    response_json = await response.json()
    assert response_json == test_result
