import random

import pytest


@pytest.mark.parametrize('by', ['ids', 'product_ids'])
async def test_products_empty_found(tap, api, uuid, by):
    with tap.plan(5):
        t = await api()
        await t.set_role('admin')

        await t.post_ok('api_tsd_products',
                        json={by: [uuid(), uuid()]})
        t.status_is(200, diag=True)
        t.content_type_like(r'^application/json')
        t.json_is('code', 'OK')
        t.json_is('products', [])


@pytest.mark.parametrize('by', ['ids', 'product_ids'])
async def test_products(tap, api, dataset, uuid, by):
    with tap.plan(128, 'тестим отправку продукта в tsd'):
        products = [await dataset.product(barcode=[uuid()]) for _ in range(5)]

        special_uid = uuid()
        products.append(
            await dataset.product(
                barcode=[special_uid],
                vars={
                    'imported': {
                        'visual_control_images': [
                            {'image': 'orig1.png', 'thumbnail': 'thumb1.png'},
                            {'image': 'orig2.png', 'thumbnail': 'thumb2.png'},
                            {'image': 'orig3.png', 'thumbnail': 'thumb3.png'},
                        ],
                        'visual_control_titles': [
                            {'defect_title': 'Банан черный',},
                            {'defect_title': None,},
                            {'defect_title': 'Банан фиолетовый',},
                        ],
                        'visual_control_descriptions': [
                            {'defect_desc': 'Как это есть вообще?',},
                            {'defect_desc': None,},
                            {'defect_desc': 'Что за хрень?',},
                        ],
                        'true_mark': random.random() > 0.5,
                    }
                }
            )
        )
        child = await dataset.product(parent_id=products[4].product_id)
        products[4].vars['children_id'] = [child.product_id]

        visual_control_defects = [
            {
                'image': 'thumb1.png',
                'title': 'Банан черный',
                'desc': 'Как это есть вообще?',
            },
            {
                'image': 'thumb2.png',
                'title': None,
                'desc': None,
            },
            {
                'image': 'thumb3.png',
                'title': 'Банан фиолетовый',
                'desc': 'Что за хрень?',
            },
        ]

        tap.ok(products, 'пяток продуктов сгенерировано')

        t = await api()
        await t.set_role('admin')

        unknown = uuid()
        ids = [x.product_id for x in products]
        ids.append(unknown)
        products.sort(key=lambda x: x.product_id)

        await t.post_ok('api_tsd_products',
                        json={by: ids})
        t.status_is(200, diag=True)
        t.content_type_like(r'^application/json')
        t.json_is('code', 'OK')

        for i, p in enumerate(products):
            t.json_is(f'products.{i}.product_id', p.product_id)
            t.json_is(f'products.{i}.barcode', p.barcode)
            t.json_is(f'products.{i}.title', p.title)
            t.json_is(f'products.{i}.description', p.description)
            t.json_is(f'products.{i}.images', p.images, 'изображения')
            t.json_is(
                f'products.{i}.visual_control_images',
                p.vars('imported.visual_control_images.*.thumbnail', []),
                'изображения для визуального контроля',
            )
            t.json_is(
                f'products.{i}.visual_control_defects',
                visual_control_defects if p.barcode[0] == special_uid else [],
                'изображения и описания дефектов',
            )
            t.json_is(f'products.{i}.tags', p.tags, 'метки')
            t.json_is(
                f'products.{i}.true_mark', p.vars('imported.true_mark', False)
            )

            # LAVKADEV-1034
            t.json_is(f'products.{i}.external_id', p.external_id)
            t.json_is(f'products.{i}.long_title', p.long_title)
            t.json_is(f'products.{i}.valid', p.valid)
            t.json_is(f'products.{i}.write_off_before', p.write_off_before)

            # LAVKADEV-1411
            t.json_is(f'products.{i}.quants', p.quants)
            t.json_is(f'products.{i}.quant_unit', p.quant_unit)

            t.json_is(f'products.{i}.parent_id', p.parent_id)
            t.json_is(f'products.{i}.children_id', p.vars('children_id', None))
            t.json_is(f'products.{i}.lower_weight_limit', p.lower_weight_limit)
            t.json_is(f'products.{i}.upper_weight_limit', p.upper_weight_limit)
            t.json_is(f'products.{i}.type_accounting', p.type_accounting)

        t.json_is('errors.0.product_id', unknown)
        t.json_is('errors.0.code', 'ER_NOT_EXISTS')
        t.json_is('errors.0.message', 'Product not exists')


@pytest.mark.parametrize('lang', ('ru_RU', 'en_US'))
async def test_locales(tap, api, dataset, lang):
    with tap.plan(9, 'отдаем переводы с учетом языка пользователя'):
        user = await dataset.user(lang=lang)

        products = [
            await dataset.product(
                title='нет перевода'
            ),
            await dataset.product(
                title='есть перевод',
                vars={
                    'locales': {
                        'long_title': {lang: f'есть перевод {lang}'}
                    }
                },
            ),
        ]

        tap.ok(products, 'создали товары')

        t = await api(user=user)

        await t.post_ok(
            'api_tsd_products', json={'ids': [products[0].product_id]},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('products.0.title', 'нет перевода')

        await t.post_ok(
            'api_tsd_products', json={'ids': [products[1].product_id]},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('products.0.title', f'есть перевод {lang}')
