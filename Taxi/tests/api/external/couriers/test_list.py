# pylint: disable=unused-variable

import pytest


@pytest.mark.parametrize('subscribe', [True, False])
async def test_list(tap, dataset, api, subscribe):
    with tap.plan(11, f'{"подписка" if subscribe else "проход"} по курьерам'):
        courier = await dataset.courier()

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_couriers_list',
            json={
                'cursor': None,
                'subscribe': subscribe,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'ответ получен')
        t.json_has('cursor', 'Курсор присутствует')
        t.json_has('couriers', 'Список присутствует')
        t.json_has('couriers.0', 'элементы есть')
        t.json_has('couriers.0.courier_id')
        t.json_has('couriers.0.first_name')
        t.json_has('couriers.0.delivery_type')

        def courier_ok(s):
            fields = ('courier_id', 'first_name', 'delivery_type')

            for field in fields:
                if s[field] != courier.__getattribute__(field):
                    return False
            return True

        courier_found = False

        with tap.subtest(None, 'Дочитываем до конца') as taps:
            t.tap = taps

            while True:
                couriers = t.res['json']['couriers']
                if not couriers:
                    break

                if [s for s in t.res['json']['couriers'] if courier_ok(s)]:
                    courier_found = True
                    break

                await t.post_ok(
                    'api_external_couriers_list',
                    json={
                        'cursor': t.res['json']['cursor'],
                        'subscribe': subscribe,
                    }
                )
                t.status_is(200, diag=True)
                t.json_has('cursor', 'Курсор присутствует')
                t.json_has('couriers', 'Список присутствует')
                t.json_has('couriers.0', 'элементы есть')

        tap.ok(courier_found, 'Курьер найден')
