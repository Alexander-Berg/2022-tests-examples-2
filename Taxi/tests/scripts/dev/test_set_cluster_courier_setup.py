import argparse

from scripts.dev.set_cluster_courier_setup import main


async def test_common(tap, dataset):
    with tap.plan(7, 'Управление настройками кластера и ограничение ролей'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'delivery_type_check_enable': False,
                'store_shifts_percent_limit': 50,
            },
            disabled_role_permits={
                'admin': ['couriers_load', 'courier_shifts_create'],
                'support': ['courier_shifts_save'],
                'city_head': ['courier_shifts_save'],
            }
        )
        tap.ok(
            not cluster.courier_shift_setup.delivery_type_check_enable,
            'delivery_type_check_enable is turned off'
        )

        await main(
            argparse.Namespace(
                cluster_id=cluster.cluster_id,
                update_setup='{"delivery_type_check_enable": true}',
                update_role_permits='{"admin":["couriers_load"],"support":[]}',
                apply=True,
            )
        )

        with await cluster.reload():
            setup = cluster.courier_shift_setup
            tap.eq(setup.delivery_type_check_enable, True, 'delivery check')
            tap.eq(setup.store_shifts_percent_limit, 50, 'percent limit')

            permits = cluster.disabled_role_permits
            tap.eq(permits['admin'], ["couriers_load"], 'обнов. целиком')
            tap.eq(permits['support'], [], 'ограничения сняты')
            tap.eq(permits['city_head'], ['courier_shifts_save'], 'остался')
            tap.eq(
                set(permits.keys()),
                {'admin', 'support', 'city_head'},
                'все 3 роли'
            )
