import pytest

from aiohttp import web

from ymlcfg.jpath import JPath
from mouse.exception import ErValidate
from libstall.model.coerces import maybe_decimal
# pylint: disable=protected-access, too-many-lines


async def test_prepare_product(tap, load_json, uuid, prod_sync):
    with tap.plan(24, 'основные поля продукта'):
        a_product = load_json('data/product.pigeon.json')
        a_product['skuId'] = uuid()

        product = await prod_sync.prepare_obj(JPath(a_product))
        await product.save()

        tap.ok(product.product_id, 'Product saved')
        tap.eq_ok(product.groups, [], 'group')
        tap.eq_ok(product.barcode, ['8003868831238'], 'barcode',)
        tap.eq_ok(product.title, 'short name batoncheg', 'title')
        tap.eq_ok(product.long_title, 'длинное имя батончега', 'long_title')
        tap.eq_ok(product.description, 'все про батончег', 'description')
        tap.eq_ok(product.status, 'active', 'status')
        tap.eq_ok(product.order, 100, 'order')
        tap.eq_ok(product.legal_restrictions, [], 'legal_restrictions')
        tap.eq_ok(product.products_scope, ['russia'], 'products_scope')
        tap.eq_ok(product.amount, 120.000, 'amount')
        tap.eq_ok(product.amount_unit, 'г', 'amount_unit')
        tap.eq_ok(product.tags, ['refrigerator'], 'tags')
        tap.eq_ok(product.valid, 120, 'valid')
        tap.eq_ok(product.write_off_before, 3, 'write_off_before')
        tap.eq_ok(product.verification_period, 3, 'verification_period')
        tap.eq_ok(product.quants, 1, 'quants')
        tap.eq_ok(product.quant_unit, None, 'quant_unit')
        tap.eq_ok(product.parent_id, None, 'parent_id')
        tap.eq_ok(product.type_accounting, 'weight', 'type_accounting')
        tap.eq_ok(product.upper_weight_limit, None, 'upper_weight_limit')
        tap.eq_ok(product.lower_weight_limit, None, 'lower_weight_limit')
        tap.eq_ok(product.vat, None, 'vat is not set')
        tap.eq(product.vars.keys(), {'imported', 'locales', 'errors'}, 'vars')


# pylint: disable=too-many-statements
async def test_prepare_vars_imported(tap, load_json, uuid, prod_sync):
    with tap.plan(5, 'дополнительные поля продукта'):
        a_product = load_json('data/product.pigeon.json')
        a_product['skuId'] = uuid()
        product = await prod_sync.prepare_obj(JPath(a_product))

        imported = product.vars('imported')

        with tap.subtest(1, 'массив для синка картинок') as subtap:
            subtap.eq_ok(
                imported['images'],
                [
                    {'image': 'image.jpg', 'thumbnail': None},
                    {'image': 'image2.jpg', 'thumbnail': None}
                ],
                'images'
            )

        with tap.subtest(32, 'поля для external api') as subtap:
            subtap.eq_ok(imported['calorie'], 342, 'calorie')
            subtap.eq_ok(imported['protein'], 27, 'protein')
            subtap.eq_ok(imported['fat'], 26, 'fat')
            subtap.eq_ok(imported['carbohydrate'], 0.5, 'carbohydrate')
            subtap.eq_ok(imported['ingredients'],
                         'шейка выдержанная: свинина шейка, соль,'
                         ' глюкоза, натуральные ароматизаторы,', 'ingredients')
            subtap.eq_ok(
                imported['shelf_life_after_open'],
                0,
                'shelf_life_after_open',
            )
            subtap.eq_ok(imported['country'], None, 'country')
            subtap.eq_ok(imported['country_iso'], [], 'country_iso')
            subtap.eq_ok(imported['brand'], 'LA FELINESE', 'brand')
            subtap.eq_ok(imported['checkout_limit'], None, 'checkout_limit')
            subtap.eq_ok(imported['product_kind'], 'general', 'product_kind')
            subtap.eq_ok(imported['is_meta'], True, 'is_meta')
            subtap.eq_ok(
                imported['store_conditions'],
                'от +2°С до +4°С',
                'store_conditions',
            )
            subtap.eq_ok(
                imported['storage_low_temp'], 2, 'storage_low_temp',
            )
            subtap.eq_ok(
                imported['storage_high_temp'], 4, 'storage_high_temp',
            )
            subtap.eq_ok(imported['width'], 215, 'width')
            subtap.eq_ok(imported['height'], 40, 'height')
            subtap.eq_ok(imported['depth'], 20, 'depth')
            subtap.eq_ok(imported['brutto_weight'], 120, 'brutto_weight')
            subtap.eq_ok(imported['netto_weight'], 120, 'netto_weight')
            subtap.eq_ok(imported['grade_values'], [], 'grades')
            subtap.eq_ok(imported['grade_order'], 0, 'grade_order')
            subtap.eq_ok(imported['grade_size'], None, 'grade_size')
            subtap.eq_ok(imported['nonsearchable'], False, 'nonsearchable')
            subtap.eq_ok(imported['orders'], [300, 301], 'orders')

            subtap.eq_ok(
                imported['important_ingredients'],
                None,
                'important_ingredients',
            )
            subtap.eq_ok(
                imported['main_allergens'],
                ['fish', 'cat'],
                'main_allergens',
            )
            subtap.eq_ok(
                imported['nomenclature_type'],
                'product',
                'nomenclature_type',
            )
            subtap.eq_ok(imported['photo_stickers'], ['hot'], 'photo_stickers')
            subtap.eq_ok(
                imported['custom_tags'], ['halal', 'kosher'], 'custom_tags'
            )
            subtap.eq_ok(
                imported['logistic_tags'], ["hot", "fragile"], 'logistic_tags'
            )
            subtap.eq_ok(
                imported['client_attributes'],
                {
                    'main_allergens': ['fish', 'cat'],
                    'photo_stickers': ['hot'],
                    'custom_tags': ['halal', 'kosher']
                },
                'client_attributes'
            )

        with tap.subtest(5, 'поля для фров') as subtap:
            subtap.eq_ok(imported['visual_control'], False, 'visual_control')
            subtap.eq_ok(imported['visual_control_images'], [],
                         'visual_control_images')
            subtap.eq_ok(imported['visual_control_titles'], [],
                         'visual_control_titles')
            subtap.eq_ok(imported['visual_control_descriptions'], [],
                         'visual_control_descriptions')
            subtap.eq_ok(imported['leftover_for_visual_control'], 10,
                         'leftover_for_visual_control')

        with tap.subtest(18, 'поля для аналитиков') as subtap:
            subtap.eq_ok(imported['virtual_product'],
                         False, 'virtual_product')
            subtap.eq_ok(imported['farm_goods'], None, 'farm_goods')
            subtap.eq_ok(
                imported['warehouse_group'],
                'Мясная гастрономия, Полуфабрикаты,'
                ' Рыбные изделия, Консервация','warehouse_group',
            )
            subtap.eq_ok(
                imported['warehouse_group_list'],
                'myasnaya_gastronomiya_'
                'polufabrikaty_rybnye_izdeliya_konservacziya',
                'warehouse_group_list',
            )
            subtap.eq_ok(
                imported['competitor_url_perek_moscow'],
                'url',
                'competitor_url_perek_moscow',
            )
            subtap.eq_ok(
                imported['competitor_url_perek_piter'],
                None,
                'competitor_url_perek_piter',
            )
            subtap.eq_ok(
                imported['competitor_url_samokat_moscow'],
                None,
                'competitor_url_samokat_moscow',
            )
            subtap.eq_ok(
                imported['competitor_url_ozon_moscow'],
                None,
                'competitor_url_ozon_moscow',
            )
            subtap.eq_ok(
                imported['competitor_url_av_moscow'],
                None,
                'competitor_url_av_moscow',
            )
            subtap.eq_ok(
                imported['competitor_url_utkonos_moscow'],
                None,
                'competitor_url_utkonos_moscow',
            )
            subtap.eq_ok(
                imported['competitor_url_okey_moscow'],
                None,
                'competitor_url_okey_moscow',
            )
            subtap.eq_ok(
                imported['competitor_url_okey_piter'],
                None,
                'competitor_url_okey_piter',
            )
            subtap.eq_ok(imported['role_co'], 'BB', 'role_co')
            subtap.eq_ok(imported['abc'], None, 'abc')
            subtap.eq_ok(imported['private_label'], False, 'private_label')
            subtap.eq_ok(
                imported['stavit_drug_na_druga'],
                True,
                'stavit_drug_na_druga',
            )
            subtap.eq_ok(
                imported['preheat'],
                None,
                'preheat',
            )
            subtap.eq_ok(
                imported['category_manager'],
                'Бабкин',
                'category_manager',
            )

        with tap.subtest(4, 'прочее') as subtap:
            subtap.eq_ok(imported['manufacturer'], None, 'manufacturer')
            subtap.eq_ok(imported['substitution_products'], [],
                         'substitution_products')
            subtap.eq_ok(
                imported['created'],
                1574395672,
                'created',
            )
            subtap.eq_ok(
                imported['updated'],
                1628498436,
                'updated',
            )


async def test_prepare_vars_locales(tap, load_json, uuid, prod_sync):
    with tap.plan(6, 'локализованные поля продукта'):
        a_product = load_json('data/product.pigeon.json')
        a_product['skuId'] = uuid()

        product = await prod_sync.prepare_obj(JPath(a_product))

        locales = product.vars('locales')

        tap.eq(
            locales['title'],
            {
                'ru_RU': 'короткое имя батончега',
                'en_US': 'short name batoncheg',
            },
            'title',
        )
        tap.eq(
            locales['long_title'],
            {'ru_RU': 'длинное имя батончега'},
            'long_title',
        )
        tap.eq(
            locales['description'],
            {
                "ru_RU": "короткое описание батончега из голубя",
                "en_US": "deprecated description of snack"
            },
            'description',
        )
        tap.eq(
            locales['ingredients'],
            {
                "ru_RU": "сотав батончега",
                "en_US": "snack ingredients from pig"
            },
            'ingredients',
        )
        tap.eq(
            locales.get('brand', None),
            None,
            'brand'
        )
        tap.eq(locales['synonyms'], {}, 'synonyms')


# pylint: disable=too-many-locals
async def test_product_groups(tap, dataset, load_json, uuid, prod_sync):
    with tap:
        master_group = await dataset.product_group()
        front_group = await dataset.product_group()

        ext_products = dict()
        for ext_p in load_json('data/products.pigeon.json'):
            ext_id = uuid()
            ext_p['skuId'] = ext_id
            ext_p['masterCategory'] = master_group.external_id
            ext_p['frontCategories'] = [front_group.external_id]
            ext_products[ext_id] = ext_p

        new, updated, removed, not_updated = await prod_sync.run_pim(
            ext_products, {},
        )

        tap.eq(len(new), 4, 'добавили 4 товара')
        tap.eq(len(updated + removed + not_updated), 0, 'в бд их не было')

        expected_groups = {master_group.group_id, front_group.group_id}
        for p in new:
            tap.eq(set(p.groups), expected_groups, 'группы корректные')


@pytest.mark.parametrize(
    'test_input,expected',
    [
        ('holodilnik', ['refrigerator']),
        ('morozilnik', ['freezer']),
        ('holodilnik2', ['freezer2_2']),
        ('him', ['domestic']),
        ('freezer24', ['freezer24']),
        ('safe', ['safe']),
        ('spam', []),
    ]
)
async def test_product_tags(
        tap, load_json, uuid, test_input, expected, prod_sync):
    with tap:
        a_product = load_json('data/product.pigeon.json')
        a_product['skuId'] = uuid()
        a_product['attributes']['oblastHran'] = test_input

        product = await prod_sync.prepare_obj(JPath(a_product))
        tap.eq_ok(product.tags, expected, 'tags')


@pytest.mark.parametrize(
    'amount,expected',
    [
        (None, '1'),
        (-1, '1'),
        (0, '1'),
        (0.0001, '1'),
        (1, '1'),
        (1.5, '1.5'),
        (1.00051, '1.001'),
    ]
)
async def test_product_amount_nonpositive(
        tap, load_json, amount, expected, prod_sync,
):
    with tap.plan(2, 'Неположительные эмаунты запрещены'):
        a_product = load_json('data/product.pigeon.json')
        a_product['amount'] = amount
        product = await prod_sync.prepare_obj(JPath(a_product))
        tap.ok(product, 'Продукт создан')
        tap.eq_ok(
            product.amount, maybe_decimal(expected), 'amount равен 1.000',
        )


# pylint: disable=invalid-name
@pytest.mark.parametrize(
    'test_input,expected',
    [
        (['16'], ['RU_16+']),
        ([], []),
    ]
)
async def test_product_legal_restrictions(
        tap, load_json, uuid, test_input, expected, prod_sync
):
    with tap:
        a_product = load_json('data/product.pigeon.json')
        a_product['skuId'] = uuid()
        a_product['legalRestrictions'] = test_input

        product = await prod_sync.prepare_obj(JPath(a_product))

        tap.eq_ok(
            product.legal_restrictions, expected, 'legal_restrictions'
        )


async def test_product_status(tap, load_json, uuid, prod_sync):
    with tap:
        a_product = load_json('data/product.pigeon.json')
        a_product['skuId'] = uuid()

        # first time

        a_product['updated'] = '0'
        a_product['status'] = 'active'

        product = await prod_sync.prepare_obj(JPath(a_product))
        tap.eq_ok(product.status, 'active', 'status')

        await product.save()

        # second time disabled

        a_product['updated'] = '0'
        a_product['status'] = 'disabled'

        product = await prod_sync.prepare_obj(JPath(a_product))
        tap.eq_ok(product.status, 'disabled', 'status')

        await product.save()

        # third time enabled one more time

        a_product['updated'] = '0'
        a_product['status'] = 'active'

        product = await prod_sync.prepare_obj(JPath(a_product))
        tap.eq_ok(product.status, 'active', 'status')


async def test_product_write_off_before(tap, load_json, uuid, prod_sync):
    with tap.plan(4):
        a_product = load_json('data/product.pigeon.json')
        a_product['skuId'] = uuid()
        a_product['attributes']['expiredCount'] = 1

        product = await prod_sync.prepare_obj(JPath(a_product))
        tap.eq_ok(product.write_off_before, 1, 'если в поле все ок')

        a_product['attributes']['expiredCount'] = None
        product = await prod_sync.prepare_obj(JPath(a_product))
        tap.eq_ok(product.write_off_before, 0, 'если в поле пусто')

        del a_product['attributes']['expiredCount']
        product = await prod_sync.prepare_obj(JPath(a_product))
        tap.eq_ok(product.write_off_before, 0, 'если нет поля')

        a_product['attributes']['expiredCount'] = -1
        with tap.raises(ErValidate, 'Ошибка, если отрицательное'):
            await prod_sync.prepare_obj(JPath(a_product))


# pylint: disable=invalid-name
@pytest.mark.parametrize(
    'test_input,expected',
    [
        (None, 1),
        ('0', 1),
        ('3', 3),
    ]
)
async def test_product_quants(
        tap, load_json, uuid, test_input, expected, prod_sync
):
    with tap:
        a_product = load_json('data/product.pigeon.json')
        a_product['skuId'] = uuid()
        a_product['attributes']['portions'] = test_input

        product = await prod_sync.prepare_obj(JPath(a_product))
        tap.eq_ok(product.quants, expected, 'quants')


async def test_product_quants_change(tap, load_json, dataset, prod_sync):
    with tap.plan(2, 'Смена количества квантов'):
        product = await dataset.product(quants=300)
        tap.ok(product, 'Продукт создан')

        a_product = load_json('data/product.pigeon.json')
        a_product['skuId'] = product.external_id
        a_product['attributes']['portions'] = 301

        product = await prod_sync.prepare_obj(JPath(a_product))
        tap.ok(
            product.vars['errors'][0]['code'],
            'quants_changed'
            'Ошибка попытка смены квантов'
        )


async def test_product_title(tap, load_json, uuid, prod_sync):
    with tap:
        a_product = load_json('data/product.pigeon.json')
        a_product['skuId'] = uuid()

        a_product['title'] = {
            'ru_RU': 'короткое имя батончега',
            'en_US': 'short name batoncheg',
        }

        product = await prod_sync.prepare_obj(JPath(a_product))

        tap.eq_ok(
            product.title, 'short name batoncheg', 'инглиш ферст',
        )

        a_product['title'] = {
            'ru_RU': 'короткое имя батончега',
            'he_IL': 'in hebrew',
        }

        product = await prod_sync.prepare_obj(JPath(a_product))

        tap.eq_ok(
            product.title, 'короткое имя батончега', 'рашн',
        )

        a_product['title'] = {'he_IL': 'in hebrew'}

        product = await prod_sync.prepare_obj(JPath(a_product))

        tap.eq(product, None, 'нет названия вообще')


@pytest.mark.parametrize(
    'test_input,expected',
    [
        (
            {
                'he_HE': 'xxx',
                'ru_RU': 'берем ру',
            },
            'берем ру',
        ),
        (
            {
                'en_US': 'take en',
                'ru_RU': 'берем ру',
            },
            'take en',
        ),
        (
            {
                'xx_XX': 'xx',
                'yy_YY': 'yy',
            },
            None,
        ),
    ]
)
async def test_product_long_title(
        tap, load_json, uuid, test_input, expected, prod_sync):
    with tap:
        a_product = load_json('data/product.pigeon.json')
        a_product['skuId'] = uuid()
        a_product['longTitle'] = test_input

        product = await prod_sync.prepare_obj(JPath(a_product))
        tap.eq_ok(product.long_title, expected, 'long_title')


async def test_product_vat_not_changed(tap, dataset, load_json, prod_sync):
    with tap:
        product = await dataset.product(vat='15.67')
        tap.ok(product.product_id, 'сохранили товары в бд')

        a_product = load_json('data/product.pigeon.json')
        a_product['skuId'] = product.external_id
        a_product['vat'] = '20'

        updated_product = await prod_sync.prepare_obj(JPath(a_product))
        tap.eq_ok(str(updated_product.vat), '15.67', 'vat')


@pytest.mark.parametrize(
    ['type_accounting', 'expected'],
    [
        ('byWeight', 'weight'),
        ('byUnit', 'unit'),
        (None, 'unit'),
    ]
)
async def test_product_type_accounting(
        tap, load_json, type_accounting, expected, uuid, prod_sync
):
    with tap:
        a_product = load_json('data/product.pigeon.json')
        a_product['skuId'] = uuid()
        a_product['attributes']['typeAccounting'] = type_accounting

        product = await prod_sync.prepare_obj(JPath(a_product))
        tap.eq(
            product.type_accounting, expected, f'type_accounting = {expected}',
        )


async def test_product_parent_no_grade_values(
        tap, dataset, load_json, uuid, prod_sync,
):
    with tap:
        parent_product = await dataset.product()

        a_product = load_json('data/product.pigeon.json')
        a_product['skuId'] = uuid()
        a_product['attributes']['parentItem'] = parent_product.external_id

        child_product = await prod_sync.prepare_obj(JPath(a_product))
        tap.eq(child_product, None, 'у родителя нет grade_values')


async def test_product_parent_not_exists(tap, load_json, uuid, prod_sync):
    with tap:
        a_product = load_json('data/product.pigeon.json')
        a_product['skuId'] = uuid()
        a_product['attributes']['parentItem'] = uuid()

        product = await prod_sync.prepare_obj(JPath(a_product))
        tap.is_ok(product, None, 'у ребенка нет родителя')


async def test_product_parent_empty(tap, load_json, uuid, prod_sync):
    with tap:
        a_product = load_json('data/product.pigeon.json')
        a_product['skuId'] = uuid()
        a_product['attributes']['parentItem'] = None

        product = await prod_sync.prepare_obj(JPath(a_product))
        tap.is_ok(product.parent_id, None, 'parent_id is None')


# pylint: disable=too-many-branches,too-many-locals,too-many-statements
@pytest.mark.parametrize(
    [
        'lower', 'upper', 'lower_expected', 'upper_expected'
    ],
    [
        (1200, 1300, 1200, 1300),
        (None, None, None, None)
    ],
)
async def test_product_weight_bounds(
        tap, load_json, lower, upper, lower_expected, upper_expected, uuid,
        prod_sync,
):
    with tap:
        a_product = load_json('data/product.pigeon.json')
        a_product['skuId'] = uuid()
        a_product['attributes']['lowerWeightLimit'] = lower
        a_product['attributes']['upperWeightLimit'] = upper

        product = await prod_sync.prepare_obj(JPath(a_product))
        tap.eq(
            product.lower_weight_limit,
            lower_expected,
            f'lower_weight_limit = {lower_expected}',
        )
        tap.eq(
            product.upper_weight_limit,
            upper_expected,
            f'upper_weight_limit = {upper_expected}',
        )


@pytest.mark.parametrize(
    ['lower', 'upper', 'expected'],
    [
        (1200, None, 1),
        (None, 1300, 1),
        (1300, 1200, 0),
        (-1, 100, 0),
        (100, -1, 0),
        (100, 100, 1),
    ],
)
async def test_product_incorrect_weight_bounds(
        tap, load_json, lower, upper, uuid, prod_sync, expected
):
    with tap.plan(1, 'тест на неправильные веса'):
        a_product = load_json('data/product.pigeon.json')
        a_product['skuId'] = uuid()
        a_product['attributes']['lowerWeightLimit'] = lower
        a_product['attributes']['upperWeightLimit'] = upper

        product = await prod_sync.prepare_obj(JPath(a_product))

        if expected:
            tap.ok(product, 'сохранился товар')
        else:
            tap.ok(product is None, 'не сохранился товар')


@pytest.mark.skip(reason="removing removing")
async def test_removed(tap, dataset, uuid, prod_sync, load_json):
    with tap.plan(14):
        ext_products = dict()
        for ext_p in load_json('data/products.pigeon.json'):
            ext_id = uuid()
            ext_p['skuId'] = ext_id
            ext_products[ext_id] = ext_p
        tap.ok(ext_products, 'создали product 1, 2, 3')
        new, updated, removed, not_updated = await prod_sync.run_pim(
            ext_products, {}
        )
        prod = [await dataset.Product.load(by='external', key=k)
                for k in ext_products]
        tap.ok(new, 'смогли засинкать новые продукты')
        tap.ok(all(i.status == 'active' for i in prod), 'статус active')
        tap.eq_ok(
            len(prod),
            len(ext_products),
            'сохранили'
        )
        new, updated, removed, not_updated = await prod_sync.run_pim(
            ext_products, {}
        )
        prod = [await dataset.Product.load(by='external', key=k)
                for k in ext_products]
        tap.ok(all(i.status == 'active' for i in prod), 'статус active')
        tap.eq_ok(
            len(new + updated + removed),
            0,
            'не обновились товары при аналогичном запросе'
        )
        prod_sync.pim_update_limit = 25
        tap.note('Подняли предел для синка')
        new, updated, removed, not_updated = await prod_sync.run_pim(
            {},
            ext_products.keys()
        )
        prod = [await dataset.Product.load(by='external', key=k)
                for k in ext_products]
        tap.ok(all(i.status == 'removed' for i in prod), 'статус removed')
        tap.ok(all(i.status for i in prod), 'сменили статусы')
        tap.eq_ok(
            len(new + updated + not_updated),
            0,
            'проставили removed'
        )
        new, updated, removed, not_updated = await prod_sync.run_pim(
            {},
            ext_products.keys()
        )
        prod = [await dataset.Product.load(by='external', key=k)
                for k in ext_products]
        tap.ok(all(i.status == 'removed' for i in prod), 'статус removed')
        tap.eq_ok(
            len(new + updated + removed),
            0,
            'ничего не изменилось при аналогичном запросе'
        )
        tap.eq_ok(
            len(not_updated),
            len(ext_products),
            'ничего не изменилось при аналогичном запросе'
        )
        new, updated, removed, not_updated = await prod_sync.run_pim(
            {},
            [uuid(), uuid()],
        )
        prod = [await dataset.Product.load(by='external', key=k)
                for k in [uuid(), uuid()]]
        tap.ok(all(i is None for i in prod), 'статус removed')
        tap.eq_ok(
            len(new + updated + removed + not_updated),
            0,
            'ничего не изменилось при пробросе мусора'
        )


async def test_true_mark(tap, uuid, prod_sync, load_json):
    with tap.plan(4, 'тестируем импорт честного знака'):
        a_product = load_json('data/product.pigeon.json')
        a_product['skuId'] = uuid()

        product = await prod_sync.prepare_obj(JPath(a_product))
        tap.ok(not product.vars('imported.true_mark'), 'нет знака')
        await product.save()

        a_product['attributes']['trueMark'] = True

        product = await prod_sync.prepare_obj(JPath(a_product))
        tap.ok(product.vars('imported.true_mark'), 'есть знак')
        await product.save()

        a_product['attributes']['trueMark'] = False

        product_new = await prod_sync.prepare_obj(JPath(a_product))
        tap.eq(
            product_new.vars['errors'][0]['code'],
            'true_mark_shutdown',
            'Ошибка попытка выключить чз'
        )

        await product.reload()
        tap.ok(product.vars('imported.true_mark'), 'воистину честный знак')


async def test_vars_error(tap, dataset, prod_sync, load_json, uuid):
    with tap.plan(3, 'Проверяем ошибки в vars'):

        product = await dataset.product(
            true_mark=True,
            parent_id=uuid()
        )
        parent_product = await dataset.product(
            vars={
                'imported': {
                    'grade_values': [False]
                }
            }
        )
        other_parent = await dataset.product()

        a_product = load_json('data/product.pigeon.json')
        a_product['title'] = {}
        a_product['skuId'] = product.external_id

        a_product['attributes']['upperWeightLimit'] = 6
        a_product['attributes']['lowerWeightLimit'] = 9

        a_product['attributes']['portions'] = 2

        a_product['attributes']['parentItem'] = uuid()

        new_product = await prod_sync.prepare_obj(JPath(a_product))

        tap.eq(
            new_product.vars('errors'),
            [
                {
                    'code': 'no_title',
                    'message': 'product has no title'
                },
                {
                    'code': 'incorrect_weight',
                    'message': 'product has incorrect weight',
                    'more_info': {
                        'upper_weight_limit': 6,
                        'lower_weight_limit': 9
                    }
                },
                {
                    'code': 'quants_changed',
                    'message': 'Attempt to change quants',
                    'more_info': {
                        'old_quants': product.quants,
                        'new_quants': 2
                    }
                },
                {
                    'code': 'true_mark_shutdown',
                    'message': 'Attempt to shutdown true mark'
                },
                {
                    'code': 'parent_not_found',
                    'message': 'Parent not found',
                    'more_info': {
                        'parent_external_id': a_product[
                            'attributes']['parentItem']
                    }
                },
                {
                    'code': 'current_parent_not_found',
                    'message': 'Current parent not found',
                    'more_info': {
                        'parent_id': product.parent_id
                    }
                },
                {
                    'code': 'parent_changed',
                    'message': 'Attempt to change parent',
                    'more_info': {
                        'old_parent_id': product.parent_id,
                        'new_parent_id': None
                    }
                }
            ],
            'Первая порция ошибок'
        )

        a_product = load_json('data/product.pigeon.json')
        product = await dataset.product(parent_id=other_parent.product_id)
        a_product['attributes']['parentItem'] = other_parent.external_id
        a_product['skuId'] = product.external_id

        new_product = await prod_sync.prepare_obj(JPath(a_product))

        tap.eq(
            new_product.vars('errors'),
            [
                {
                    'code': 'parent_grade_not_found',
                    'message': 'Parent grade not found',
                    'more_info': {
                        'parent_external_id': other_parent.external_id
                    }
                }
            ],
            'Ошибка parent_grade_not_found'
        )

        product = await dataset.product(parent_id=parent_product.product_id)
        a_product['attributes']['parentItem'] = parent_product.external_id
        a_product['skuId'] = product.external_id

        new_product = await prod_sync.prepare_obj(JPath(a_product))

        tap.eq(
            new_product.vars('errors'),
            [
                {
                    'code': 'grade_value_not_found',
                    'message': 'Grade value not found',
                    'more_info': {
                        'parent_external_id': parent_product.external_id,
                        'grade_key': False,
                        'grade_value': None
                    }
                }
            ],
            'Ошибка grade_value_not_found'
        )


async def test_no_error_after_fix(tap, dataset, prod_sync, load_json):
    with tap.plan(4, 'Убираем ошибки после фикса'):
        product = await dataset.product(true_mark=True)

        a_product = load_json('data/product.pigeon.json')
        a_product['title'] = {}
        a_product['skuId'] = product.external_id
        a_product['attributes']['trueMark'] = True

        new_product = await prod_sync.prepare_obj(JPath(a_product))
        tap.eq(
            new_product.vars('errors'),
            [
                {
                    'code': 'no_title',
                    'message': 'product has no title'
                }
            ],
            'Есть ошибка'
        )
        product.vars['errors'] = [
            {
                'code': 'no_title',
                'message': 'product has no title'
            }
        ]
        tap.eq(product, new_product, 'Продукты одинаковые')

        a_product['title'] = {
            'ru_RU': 'короткое имя батончега',
            'he_IL': 'in hebrew',
        }

        await new_product.save()

        new_product = await prod_sync.prepare_obj(JPath(a_product))
        tap.eq(new_product.vars('errors'), [], 'Ошибок больше нет')
        product.vars['errors'] = []
        tap.ne(product, new_product, 'Уже не одинаковые')


async def test_no_new_product_errors(tap, prod_sync, load_json, uuid):
    with tap.plan(1, 'Продукт не создается, если есть ошибки'):
        a_product = load_json('data/product.pigeon.json')
        a_product['skuId'] = uuid()
        a_product['title'] = {}

        new_product = await prod_sync.prepare_obj(JPath(a_product))

        tap.eq(new_product, None, 'Не создали продукт')


async def test_update_client_attributes(tap, prod_sync, load_json, uuid):
    # pylint: disable=unused-variable
    with tap.plan(4, 'Проверяем обновление client_attributes'):
        ext_products = dict()
        ids = []
        for ext_p in load_json('data/products.pigeon.json'):
            ext_id = uuid()
            ids.append(ext_id)
            ext_p['skuId'] = ext_id
            ext_products[ext_id] = ext_p

        new, updated, removed, not_updated = await prod_sync.run_pim(
            ext_products,
            {}
        )
        tap.eq(len(new), 4, 'Добавили новые продукты')

        ext_products[ids[0]]['clientAttributes'] = {
            'custom_tags': ['halal', 'kosher'],
            'main_allergens': ['fish', 'cat'],
            'photo_stickers': ['hot'],
        }

        new, updated, removed, not_updated = await prod_sync.run_pim(
            ext_products,
            {}
        )
        tap.eq(len(updated), 0, 'Продукты не обновили')

        ext_products[ids[0]]['clientAttributes'] = {
            'custom_tags': ['halal', 'kosher'],
            'main_allergens': ['fish', 'cat'],
            'photo_stickers': ['hot'],
            'some_slovar': {
                'tishka': 'saint laurent',
                'visit': 'na mne'
            }
        }

        new, updated, removed, not_updated = await prod_sync.run_pim(
            ext_products,
            {}
        )
        tap.eq(len(updated), 1, 'Обновили 1 продукт')

        ext_products[ids[0]]['clientAttributes'] = {
            'custom_tags': ['halal', 'kosher'],
            'main_allergens': ['fish', 'cat'],
            'photo_stickers': ['hot'],
            'some_slovar': {
                'visit': 'na mne',
                'tishka': 'saint laurent',
            }
        }

        new, updated, removed, not_updated = await prod_sync.run_pim(
            ext_products,
            {}
        )
        tap.eq(len(updated), 0, 'Обновлений не было')


async def test_sort_products(tap, prod_sync, load_json):
    with tap.plan(1, 'Проверяем порядок продуктов'):
        ext_objs = load_json('data/products.pigeon.json')
        ext_objs[0]['attributes']['parentItem'] = ext_objs[2]['skuId']
        ext_objs[2]['attributes']['parentItem'] = ext_objs[1]['skuId']
        ext_objs[1]['attributes']['parentItem'] = ext_objs[3]['skuId']
        sort_objs = prod_sync._sort_objs(ext_objs)
        product_keys = ['18472', '18596', '18383', '2594']
        tap.eq(list(sort_objs.keys()), product_keys, 'Правильный порядок')


async def test_stash_errors(
        tap, prod_sync_client, ext_api, load_json, uuid, dataset):
    with tap.plan(2, 'Проверяем наличие стеша с ошибками'):

        ext_objs = load_json('data/products.pigeon.json')
        for obj in ext_objs:
            obj['skuId'] += ':' + uuid()

        ext_objs[0]['title'] = {}

        stash = await dataset.Stash.stash(
            name=prod_sync_client.not_updated_stash_name,
            objs=[]
        )

        stash.value['objs'] = []
        await stash.save()

        async def handler_pigeon(req):
            data = {
                'lastCursor': 2,
                'items': []
            }
            if 'actual-products' in req.path:
                data['items'] = ext_objs[0:2]
            return web.json_response(
                status=200,
                data=data
            )

        async def new_handler(req):
            data = {
                'lastCursor': 2,
                'items': []
            }
            if 'actual-products' in req.path:
                data['items'] = ext_objs
            return web.json_response(
                status=200,
                data=data
            )

        async with await ext_api(
            prod_sync_client.pim_client, handler_pigeon
        ):
            await prod_sync_client.run()

        await stash.reload()

        tap.eq(
            len(stash.value.get('objs')), 1, 'Есть ошибки'
        )

        ext_objs[0]['title'] = {
            "ru_RU": "Шпек и шейка La Felinese «Ассорти»"
        }

        async with await ext_api(
            prod_sync_client.pim_client, new_handler
        ):
            await prod_sync_client.run()

        await stash.reload()

        tap.eq(
            len(stash.value.get('objs')), 0, 'Ошибок нет'
        )


async def test_fix_child_errors(
        tap, prod_sync_client, load_json, dataset, uuid, ext_api):
    with tap.plan(2, 'Ребенок синхронизируется без ошибок'):
        ext_objs = load_json('data/products.pigeon.json')
        ext_objs[0]['skuId'] = uuid()
        ext_objs[0]['attributes']['parentItem'] = None
        ext_objs[1]['skuId'] = uuid()
        ext_objs[1]['attributes']['parentItem'] = ext_objs[0]['skuId']

        stash = await dataset.Stash.stash(
            name=prod_sync_client.not_updated_stash_name,
            objs=[]
        )

        stash.value['objs'] = []
        await stash.save()

        async def first_handler(req):
            data = {
                'lastCursor': 2,
                'items': []
            }
            if 'actual-products' in req.path:
                data['items'] = [ext_objs[1]]
            return web.json_response(
                status=200,
                data=data
            )

        async def second_handler(req):
            data = {
                'lastCursor': 3,
                'items': []
            }
            if 'actual-products' in req.path:
                data['items'] = [ext_objs[0]]
            return web.json_response(
                status=200,
                data=data
            )

        async with await ext_api(
            prod_sync_client.pim_client, first_handler
        ):
            await prod_sync_client.run()

        await stash.reload()

        tap.eq(
            len(stash.value.get('objs')), 1, 'Есть ошибки'
        )

        async with await ext_api(
            prod_sync_client.pim_client, second_handler
        ):
            await prod_sync_client.run()

        await stash.reload()

        tap.eq(
            len(stash.value.get('objs')), 0, 'Ошибки нет'
        )


async def test_no_change_vars(tap, dataset, prod_sync, load_json):
    with tap.plan(1, 'Меняет ли голубь vars'):
        a_product = load_json('data/product.pigeon.json')
        product = await dataset.product(vars={'supplier_tin': '777'})

        a_product['skuId'] = product.external_id

        product = await prod_sync.prepare_obj(JPath(a_product))
        await product.save()
        tap.eq(product.vars['supplier_tin'], '777', 'Не поменялись')


async def test_new_img_url(
        tap, load_json, prod_sync_pictures, uuid, ext_api):
    # pylint: disable=unused-variable, unused-argument
    with tap.plan(2, 'Проверяем новые ссылки'):
        ext_products = dict()
        ids = []
        products = load_json('data/products.pigeon.json')[0:3]
        for ext_p in products:
            ext_id = uuid()
            ids.append(ext_id)
            ext_p['skuId'] = ext_id
            ext_products[ext_id] = ext_p

        new, upd, rm, not_upd = await prod_sync_pictures.run_pim(
            ext_products,
            []
        )

        tap.eq(
            new[1]['images'][0],
            "https://images.tst.grocery.yandex.net/"
            "1398399/48bf616c-789b-48ff-a532-473c52ca171f/{w}x{h}.png",
            'Тестовая ссылка'
        )

        tap.eq(
            new[2]['images'][0],
            "https://images.grocery.yandex.net/"
            "1397973/6dd3e9bb-b92e-4e88-9828-f622da6fba43/{w}x{h}.png",
            'Тестовая ссылка'
        )
