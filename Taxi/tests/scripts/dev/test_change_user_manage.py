import argparse
import csv
from scripts.dev.change_users_manage import change_user_manage


async def test_change_users_manage(tap, dataset):
    with tap.plan(1, 'Проверка изменения users_manage через cluster_id'):
        cluster = await dataset.cluster()
        store = await dataset.store(
            cluster_id=cluster.cluster_id,
            users_manage='internal',
        )

        args = argparse.Namespace(
            users_manage='external',
            clear=False,
            cluster_id=cluster.cluster_id,
            file_depot_id=None,
            apply=True,
        )
        await change_user_manage(args)
        await store.reload()

        tap.eq(store.users_manage,
               'external',
               'users_manage изменился',)


async def test_change_users_manage_file(tap, dataset):
    with tap.plan(1, 'Проверка изменения users_manage через file_depot_id'):
        store = await dataset.store(
            users_manage='internal',
        )

        with open('change_users_manage.csv', 'w', newline='') as f:
            writer = csv.writer(f, delimiter=';',)
            writer.writerow(['depot_id'])
            writer.writerow([store.external_id])

        args = argparse.Namespace(
            users_manage='external',
            clear=False,
            cluster_id=None,
            file_depot_id='change_users_manage.csv',
            apply=True,
        )
        await change_user_manage(args)
        await store.reload()

        tap.eq(store.users_manage,
               'external',
               'users_manage изменился')


async def test_clear_users_manage(tap, dataset):
    with tap.plan(1, 'Проверка изменения users_manage через clear'):
        cluster = await dataset.cluster()
        company = await dataset.company(
            users_manage='external',
        )

        store = await dataset.store(
            company_id=company.company_id,
            users_manage='internal',
            cluster_id=cluster.cluster_id,
        )

        args = argparse.Namespace(
            users_manage=False,
            clear=True,
            cluster_id=cluster.cluster_id,
            file_depot_id=None,
            apply=True,
        )
        await change_user_manage(args)
        await store.reload()

        tap.eq(store.users_manage,
               'external',
               'users_manage изменился',)
