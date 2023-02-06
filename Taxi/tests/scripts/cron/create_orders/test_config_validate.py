from stall import log
from scripts.cron.create_orders import create_orders_periodically as cop


async def test_success(tap, dataset):
    with tap.plan(10, 'Успешная валидация'):
        stores = [
            await dataset.store()
            for _ in range(3)
        ]
        tap.ok(all(stores), 'Создали склады')
        tap.eq(len(stores), 3, '3 штуки')

        products = [
            await dataset.product()
            for _ in range(4)
        ]
        tap.ok(all(products), 'Создали продукты')
        tap.eq(len(products), 4, '4 штуки')

        config = {
            'projects': [
                {
                    'project_name': 'first project',
                    'schedule': [
                        {
                            'hour': 12,
                        },
                        {
                            'weekday': 3,
                            'hour': 10,
                        }
                    ],
                    'external_store_ids': [
                        stores[0].external_id,
                        stores[1].external_id,
                    ],
                    'external_product_ids': [
                        products[0].external_id,
                        products[1].external_id,

                    ],
                    'order_type': 'check_product_on_shelf',
                    'shelf_types': ['kitchen_components'],
                },
                {
                    'project_name': 'second project',
                    'schedule': [
                        {
                            'hour': 10
                        }
                    ],
                    'external_store_ids': [
                        stores[0].external_id,
                        stores[2].external_id,
                    ],
                    'external_product_ids': [
                        products[2].external_id,
                        products[3].external_id,

                    ],
                    'order_type': 'check_product_on_shelf',
                    'shelf_types': ['store'],
                }
            ]
        }

        result = await cop.parse_and_validate_config(config)
        tap.ok(result, 'Конфиг получился')
        tap.eq(len(result), 3, 'Три склада')
        tap.in_ok('store', result[0], 'Появился склад')
        tap.eq(
            {config['store'].store_id for config in result},
            {store.store_id for store in stores},
            'Нужные склады',
        )
        first_store_config = next(
            config for config in result
            if config['store'].store_id == stores[0].store_id
        )
        projects = first_store_config['projects']
        tap.eq(len(projects), 2, 'Два проекта')

        first_project = next(
            project for project in projects
            if project['project_name'] == 'first project'
        )
        tap.eq(
            set(first_project['product_ids']),
            {products[0].product_id, products[1].product_id},
            'Продукты наши проставились',
        )


async def test_failure(tap, dataset, uuid, cfg):
    with tap.plan(12, 'Всякие ошибочные кнфиги'):
        log.setLevel('CRITICAL')
        stores = [
            await dataset.store()
            for _ in range(2)
        ]
        tap.ok(all(stores), 'Создали склады')
        tap.eq(len(stores), 2, '2 штуки')

        products = [
            await dataset.product()
            for _ in range(2)
        ]
        tap.ok(all(products), 'Создали продукты')
        tap.eq(len(products), 2, '2 штуки')

        config = {
            'projects': []
        }
        parsed_config = await cop.parse_and_validate_config(config)
        tap.eq(parsed_config, [], 'Нет проектов')

        config = {
            'projects': [
                {
                    'project_name': 'keklol',
                }
            ]
        }
        parsed_config = await cop.parse_and_validate_config(config)
        tap.eq(parsed_config, [], 'Невалидный конфиг')

        config = {
            'projects': [
                {
                    'project_name': 'first project',
                    'schedule': [
                        {
                            'hour': 12,
                        },
                        {
                            'weekday': 3,
                            'hour': 10,
                        }
                    ],
                    'external_store_ids': [
                        uuid(),
                    ],
                    'external_product_ids': [
                        products[0].external_id,
                        products[1].external_id,
                    ],
                    'order_type': 'check_product_on_shelf',
                    'shelf_types': ['kitchen_components'],
                },
            ]
        }
        parsed_config = await cop.parse_and_validate_config(config)

        tap.eq(parsed_config, [], 'У проекта нет правильных store_id')

        config = {
            'projects': [
                {
                    'project_name': 'first project',
                    'schedule': [
                        {
                            'hour': 12,
                        },
                        {
                            'weekday': 3,
                            'hour': 10,
                        }
                    ],
                    'external_store_ids': [
                        stores[0].external_id,
                    ],
                    'external_product_ids': [
                        products[0].external_id,
                        products[1].external_id,

                    ],
                    'order_type': 'random_name',
                    'shelf_types': ['kitchen_success_shelf'],
                },
            ]
        }
        parsed_config = await cop.parse_and_validate_config(config)
        tap.eq(parsed_config, [], 'Невалидный тип ордера, тип полок')

        config = {
            'projects': [
                {
                    'project_name': 'same project',
                    'schedule': [
                        {'hour': 12},
                    ],
                    'external_store_ids': [
                        stores[0].external_id,
                    ],
                    'external_product_ids': [
                        products[0].external_id,
                    ],
                    'order_type': 'check_product_on_shelf',
                    'shelf_types': ['store'],
                },
                {
                    'project_name': 'same project',
                    'schedule': [
                        {'hour': 13},
                    ],
                    'external_store_ids': [
                        stores[1].external_id,
                    ],
                    'external_product_ids': [
                        products[1].external_id,
                    ],
                    'order_type': 'check_product_on_shelf',
                    'shelf_types': ['store'],
                },
            ]
        }
        parsed_config = await cop.parse_and_validate_config(config)
        tap.eq(len(parsed_config), 1, 'Есть склад')
        tap.eq(parsed_config[0]['projects'], [], 'Проектов нет')

        config = {
            'projects': [
                {
                    'project_name': 'same project',
                    'schedule': [
                        {'hour': 12},
                    ],
                    'external_store_ids': [
                        stores[0].external_id,
                    ],
                    'external_product_ids': [
                        products[0].external_id,
                        uuid(),
                    ],
                    'order_type': 'check_product_on_shelf',
                    'shelf_types': ['store'],
                },
            ]
        }
        parsed_config = await cop.parse_and_validate_config(config)
        tap.eq(len(parsed_config), 1, 'Есть склад')
        tap.eq(parsed_config[0]['projects'], [], 'Проектов нет')

        log.setLevel(cfg('log.level'))
