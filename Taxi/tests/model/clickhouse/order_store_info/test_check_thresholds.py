import pytest
from stall.model.clickhouse.order_store_info import OrderStoreInfo, Threshold


async def test_load_thresholds(tap, cfg):
    with tap.plan(1, 'Все конфиги должны загружаться'):
        thresholds = await Threshold.load(cfg('health_monitoring'))
        tap.ok(thresholds, 'Все конфиги загрузились')


async def test_load_custom_threshold(tap, cfg, uuid):
    # pylint: disable=protected-access
    with tap.plan(8, 'Загрузка конфигов'):
        config_name = uuid()
        cfg._lazy_load()
        cfg._db.o[config_name] = {
            'type_thresholds': {
                'order': {
                    'processing': {
                        'count': 5,
                        'duration_total': 100,
                        'duration_per_item': 1,
                        'duration_per_sku': 2,
                        'duration_per_suggest': 3,
                    }
                }
            }
        }

        thresholds = await Threshold.load(cfg(config_name))

        tap.eq(len(thresholds), 1, '1 конфиг')
        tap.eq(thresholds[0].type, 'order', 'type')
        tap.eq(thresholds[0].status, 'processing', 'status')
        tap.eq(thresholds[0].count, 5, 'count')
        tap.eq(thresholds[0].duration_total, 100, 'duration_total')
        tap.eq(thresholds[0].duration_per_item, 1, 'duration_per_item')
        tap.eq(thresholds[0].duration_per_sku, 2, 'duration_per_sku')
        tap.eq(thresholds[0].duration_per_suggest, 3, 'duration_per_suggest')


@pytest.mark.parametrize(
    'threshold_spec',
    (
        {'duration_total': 60},
        {'duration_per_item': 20},
        {'duration_per_sku': 15},
        {'duration_per_suggest': 10},
    )
)
async def test_thresholds(tap, uuid, threshold_spec):
    spec_name = list(threshold_spec.keys())[0]
    with tap.plan(4, f'Найдем проблему по {spec_name}'):
        thresholds = [
            Threshold(
                type='order',
                status='processing',
                **threshold_spec
            )
        ]
        order_id = uuid()
        orders_info = [
            OrderStoreInfo(
                company_id=uuid(),
                cluster_id=uuid(),
                head_supervisor_id=uuid(),
                supervisor_id=uuid(),
                store_id=uuid(),
                type='order',
                status='processing',
                order_id=order_id,
                duration=61,
                items_count=3,
                items_uniq=4,
                suggests_count=6,
            )
        ]
        order_problems = OrderStoreInfo.check_thresholds(
            orders_info,
            thresholds
        )
        tap.eq(len(order_problems), 1, '1 проблема')
        tap.eq(order_problems[0].reason, spec_name, 'Верная причина')
        tap.eq(order_problems[0].details[0].reason, spec_name, 'Верная причина')
        tap.eq(order_problems[0].details[0].order_id, order_id, 'order_id')


@pytest.mark.parametrize(
    'threshold_spec',
    (
        {'duration_total': 80},
        {'duration_per_item': 25},
        {'duration_per_sku': 20},
        {'duration_per_suggest': 15},
    )
)
async def test_thresholds_good(tap, uuid, threshold_spec):
    spec_name = list(threshold_spec.keys())[0]
    with tap.plan(1, f'По {spec_name} проблем нет'):
        thresholds = [
            Threshold(
                type='order',
                status='processing',
                **threshold_spec
            )
        ]
        orders_info = [
            OrderStoreInfo(
                company_id=uuid(),
                cluster_id=uuid(),
                head_supervisor_id=uuid(),
                supervisor_id=uuid(),
                store_id=uuid(),
                type='order',
                status='processing',
                order_id=uuid(),
                duration=61,
                items_count=3,
                items_uniq=4,
                suggests_count=6,
            )
        ]
        order_problems = OrderStoreInfo.check_thresholds(
            orders_info,
            thresholds
        )
        tap.eq(len(order_problems), 0, 'Проблем нет')


@pytest.mark.parametrize(
    'order_type, order_status',
    (
        ('order', 'request'),
        ('stowage', 'processing'),
    )
)
async def test_not_suitable_thresholds(tap, uuid, order_type, order_status):
    with tap.plan(1, 'Не подходящие пороги'):
        thresholds = [
            Threshold(
                type=order_type,
                status=order_status,
                duration_total=60,
            )
        ]
        orders_info = [
            OrderStoreInfo(
                company_id=uuid(),
                cluster_id=uuid(),
                head_supervisor_id=uuid(),
                supervisor_id=uuid(),
                store_id=uuid(),
                type='order',
                status='processing',
                order_id=uuid(),
                duration=200,
                items_count=0,
                items_uniq=0,
                suggests_count=0,
            )
        ]
        order_problems = OrderStoreInfo.check_thresholds(
            orders_info,
            thresholds
        )
        tap.eq(len(order_problems), 0, 'Проблем не найдено')


async def test_count(tap, uuid):
    with tap.plan(6, 'Найдем проблему: количество ордеров в статусе'):
        count_threshold = 1
        thresholds = [
            Threshold(
                type='order',
                status='processing',
                count=count_threshold,
            )
        ]
        store_id = uuid()
        order_id_1 = uuid()
        order_id_2 = uuid()
        store_info_raw = dict(
            company_id=uuid(),
            cluster_id=uuid(),
            head_supervisor_id=uuid(),
            supervisor_id=uuid(),
            store_id=store_id,
            type='order',
            status='processing',
            duration=0,
            items_count=0,
            items_uniq=0,
            suggests_count=0,
        )
        orders_info = [
            OrderStoreInfo(**store_info_raw, order_id=order_id_1),
            OrderStoreInfo(**store_info_raw, order_id=order_id_2),
        ]
        order_problems = OrderStoreInfo.check_thresholds(
            orders_info,
            thresholds
        )
        tap.eq(len(order_problems), 1, '1 проблема')
        tap.eq(
            order_problems[0].reason,
            'count',
            'У проблемы правильная причина'
        )
        tap.eq(
            order_problems[0].details[0].reason,
            'count',
            'У проблемы правильная причина'
        )
        tap.eq(
            order_problems[0].details[0].count,
            len(orders_info),
            'Найдено верное количество ордеров'
        )
        tap.eq(
            order_problems[0].details[0].order_ids,
            [order_id_1, order_id_2],
            'Найдено верное количество ордеров'
        )
        tap.eq(
            order_problems[0].details[0].count_threshold,
            count_threshold,
            'Записан верный лимит ордеров'
        )


async def test_two_orders(tap, uuid):
    with tap.plan(5, 'На два проблемных ордера должна получится одна проблема'):
        thresholds = [
            Threshold(
                type='order',
                status='processing',
                duration_per_suggest=15
            )
        ]
        order_id_1 = uuid()
        order_id_2 = uuid()
        raw = dict(
            company_id=uuid(),
            cluster_id=uuid(),
            head_supervisor_id=uuid(),
            supervisor_id=uuid(),
            store_id=uuid(),
            type='order',
            status='processing',
            duration=61,
            suggests_count=3,
        )
        orders_info = [
            OrderStoreInfo(dict(**raw, order_id=order_id_1)),
            OrderStoreInfo(dict(**raw, order_id=order_id_2)),
        ]
        order_problems = OrderStoreInfo.check_thresholds(
            orders_info,
            thresholds
        )

        tap.eq(len(order_problems), 1, '1 проблема')
        tap.eq(order_problems[0].reason, 'duration_per_suggest', 'reason')
        tap.eq(len(order_problems[0].details), 2, 'В проблеме 2 документа')
        tap.eq(
            order_problems[0].details[0].reason,
            'duration_per_suggest',
            'Причина в 1-м документе'
        )
        tap.eq(
            order_problems[0].details[1].reason,
            'duration_per_suggest',
            'Причина во 2-м документе'
        )
