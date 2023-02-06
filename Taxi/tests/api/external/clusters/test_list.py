# pylint: disable=unused-variable

from easytap.pytest_plugin import PytestTap
import tests.dataset as dt


async def test_list_subscribe(tap: PytestTap, dataset: dt, api):
    with tap.plan(3, 'подписка по кластерам'):
        store = await dataset.store()
        zone = await dataset.zone(store=store)
        cluster = await dataset.cluster(zone=zone.zone)

        t = await api(role='token:web.external.tokens.0')
        cluster_list = []
        cluster_set = set()
        found_created_zone = False

        with tap.subtest(None, 'Дочитываем до конца') as taps:
            t.tap = taps
            cursor = None
            clusters = None
            while clusters is None or clusters:
                await t.post_ok(
                    'api_external_clusters_list',
                    json={
                        'cursor': cursor,
                        'subscribe': True,
                    }
                )

                t.status_is(200, diag=True)
                t.json_is('code', 'OK', 'ответ получен')
                t.json_has('cursor', 'Курсор присутствует')
                cursor = t.res['json']['cursor']
                clusters = t.res['json']['clusters']
                cluster_list.extend(clusters)
                cluster_set |= set(str(it) for it in clusters)
                found_created_zone |= any(
                    cluster.zone == it.get('zone')
                    for it in clusters
                    if it.get('zone')
                )

        t.tap = tap
        tap.eq_ok(len(cluster_list), len(cluster_set),
                  'Subscribe вернул каждый элемент 1 раз')
        tap.ok(found_created_zone, 'Найдена созданная зона')


async def test_list(tap: PytestTap, dataset: dt, api):
    with tap.plan(8, 'проход по кластерам'):
        _ = await dataset.cluster()

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_clusters_list',
            json={
                'cursor': None,
                'subscribe': False,
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'ответ получен')
        t.json_has('cursor', 'Курсор присутствует')
        t.json_has('clusters', 'Список присутствует')
        t.json_has('clusters.0', 'элементы есть')
        t.json_has('clusters.0.cluster_id')
        t.json_has('clusters.0.zone')
