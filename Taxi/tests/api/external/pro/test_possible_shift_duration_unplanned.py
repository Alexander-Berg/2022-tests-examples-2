import datetime

from libstall.model import coerces
from stall.model.cluster import Cluster
from stall.model.courier import Courier
from stall.model.store import Store


async def test_common(tap, dataset, api, time_mock):
    with tap.plan(5, 'можно взять свободный слот'):
        time_mock.set(coerces.date_time('2022-06-20T00:00:00+00:00'))

        cluster: Cluster = await dataset.cluster(
            courier_shift_setup={
                'max_day_hours': 12,
            }
        )
        await dataset.store(cluster=cluster)

        courier: Courier = await dataset.courier(
            cluster=cluster,
            extra_vars={'can_take_unplanned_shift': True},
        )

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_possible_shift_duration_unplanned',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            }
        )
        t.status_is(200, diag=True)
        t.json_is('data.isPossible', True)
        t.json_is('data.maxPossibleDuration',
                  int(datetime.timedelta(hours=12).total_seconds()))
        t.json_is('data.maxAllowedDuration',
                  int(datetime.timedelta(hours=12).total_seconds()))


async def test_allowed_part_time(tap, dataset, api, time_mock):
    with tap.plan(5, 'есть остаток времени который можно взять'):
        time_mock.set(coerces.date_time('2022-06-20T00:00:00+00:00'))

        cluster: Cluster = await dataset.cluster(
            courier_shift_setup={
                'max_day_hours': 12,
            }
        )
        store: Store = await dataset.store(cluster=cluster)

        courier: Courier = await dataset.courier(
            cluster=cluster,
            extra_vars={'can_take_unplanned_shift': True},
        )

        await dataset.courier_shift(
            cluster=cluster, courier=courier, store=store,
            started_at=time_mock.now() + datetime.timedelta(hours=2),
            closes_at=time_mock.now() + datetime.timedelta(hours=6),
            status='waiting',
        )

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_possible_shift_duration_unplanned',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            }
        )
        t.status_is(200, diag=True)
        t.json_is('data.isPossible', True)
        t.json_is('data.maxPossibleDuration',
                  int(datetime.timedelta(hours=12).total_seconds()))
        t.json_is('data.maxAllowedDuration',
                  int(datetime.timedelta(hours=2).total_seconds()))


async def test_not_allowed(tap, dataset, api):
    with tap.plan(5, 'не разрешено брать свободные слоты'):
        cluster: Cluster = await dataset.cluster(
            courier_shift_setup={
                'max_day_hours': 12,
            }
        )
        await dataset.store(cluster=cluster)

        courier: Courier = await dataset.courier(cluster=cluster)

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_possible_shift_duration_unplanned',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            }
        )
        t.status_is(200, diag=True)
        t.json_is('data.isPossible', False)
        t.json_is('data.maxPossibleDuration',
                  int(datetime.timedelta(hours=12).total_seconds()))
        t.json_is('data.maxAllowedDuration',
                  int(datetime.timedelta(hours=0).total_seconds()))


async def test_no_time_left(tap, dataset, api, time_mock):
    with tap.plan(5, 'не осталось времени в день'):
        time_mock.set(coerces.date_time('2022-06-20T00:00:00+00:00'))

        cluster: Cluster = await dataset.cluster(
            courier_shift_setup={
                'max_day_hours': 12,
            }
        )
        store: Store = await dataset.store(cluster=cluster)

        courier: Courier = await dataset.courier(
            cluster=cluster,
            extra_vars={'can_take_unplanned_shift': True},
        )

        await dataset.courier_shift(
            cluster=cluster, courier=courier, store=store,
            started_at=time_mock.now() + datetime.timedelta(hours=2),
            closes_at=time_mock.now() + datetime.timedelta(hours=14),
            status='waiting',
        )

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_possible_shift_duration_unplanned',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            }
        )
        t.status_is(200, diag=True)
        t.json_is('data.isPossible', False)
        t.json_is('data.maxPossibleDuration',
                  int(datetime.timedelta(hours=12).total_seconds()))
        t.json_is('data.maxAllowedDuration',
                  int(datetime.timedelta(hours=0).total_seconds()))
