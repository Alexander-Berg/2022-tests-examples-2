# pylint: disable=unused-argument,redefined-outer-name,too-many-arguments
import pytest

from ymlcfg.jpath import JPath
from stall.sync.base import sync_images, grocery_pics_client, \
    sort_tree
from stall.model.product import Product


@pytest.fixture
def its_a_hard_life(monkeypatch, fake_grocery_pics_client):
    """UGLY: не делай так!"""

    monkeypatch.setattr(
        grocery_pics_client,
        grocery_pics_client.upload.__name__,
        fake_grocery_pics_client.upload,
    )


@pytest.mark.parametrize('cls_type, expected_images', [
    (
        'product',
        ['https://s3/image.png', 'https://s3/image2.png'],
    ),
    (
        'product_group',
        ['https://s3/image.png'],
    )
])
async def test_sync_images(
        tap,
        dataset,
        load_json,
        uuid,
        cls_type,
        expected_images,
        its_a_hard_life,
        prod_sync,
        prod_sync_group,
):
    # pylint: disable=too-many-arguments
    with tap:
        cls = getattr(dataset, cls_type)

        obj = await cls(
            vars={
                'imported': {
                    'images': [{'image': uuid(), 'thumbnail': uuid()}],
                    'image': uuid(),
                    'thumbnail': uuid(),
                },
                'not_imported': 'spam',
            }
        )

        tap.ok(obj, 'объект с превьюшкой')

        if isinstance(obj, Product):
            obj_data = load_json('data/product.pigeon.json')
            obj_data['skuId'] = obj.external_id
            prepare_obj = prod_sync.prepare_obj

        else:
            obj_data = load_json('data/category.pigeon.json')
            obj_data['code'] = obj.external_id
            prepare_obj = prod_sync_group.prepare_obj

        obj = await prepare_obj(JPath(obj_data))

        tap.eq_ok(obj.vars('imported.images.0.image'), 'image.jpg', 'New image')
        tap.eq_ok(obj.vars('imported.images.0.thumbnail'), None, 'нет превью')

        if isinstance(obj, Product):
            tap.eq_ok(
                obj.vars('imported.images.1'),
                {'image': 'image2.jpg', 'thumbnail': None},
                'New extra image'
            )

        await sync_images(obj, 'https://some_base_url')

        tap.eq_ok(
            obj.images,
            expected_images,
            'появились картинки'
        )

        if isinstance(obj, Product):
            tap.eq_ok(
                obj.vars('imported.images.1'),
                {'image': 'image2.jpg', 'thumbnail': 'https://s3/image2.png'},
                'превьюшка появилась'
            )

        await obj.save()

        obj = await prepare_obj(JPath(obj_data))

        tap.eq_ok(
            obj.images,
            expected_images,
            'старые картинки'
        )

        if isinstance(obj, Product):
            tap.eq_ok(
                obj.vars('imported.images.1'),
                {'image': 'image2.jpg', 'thumbnail': 'https://s3/image2.png'},
                'допкартинка не изменилась'
            )


async def test_sync_images_drop(
        tap, dataset, its_a_hard_life, fake_grocery_pics_client
):
    with tap.plan(3, 'сначала поставили картинку, потом снесли'):
        p = await dataset.product(
            images=['https://xxx.com/bad.png', 'https://extra.com/wow.png'],
            vars={
                'imported': {
                    'image': None,
                    'thumb': 'https://xxx.com/bad.png',
                    'extra_images': [],
                }
            }
        )

        await sync_images(p, 'https://some_base_url')

        tap.eq(p.images, [], 'снесли картинки')
        tap.eq(p.rehashed('-check'), {'images'}, 'поле рехешнуто')
        tap.eq(fake_grocery_pics_client.call_count, 0, 'Не было запросов')


@pytest.mark.parametrize('obj_args, expected_images, expected_count', [
    # сменилась одна дополнительная картинка
    (
        {
            'images': ['https://s3/good.png', 'https://s3/wowthumb.png'],
            'vars': {
                'imported': {
                    'images': [
                        {
                            'image': 'good.jpg',
                            'thumbnail': 'https://s3/good.png'
                        },
                        {'image': 'foo.jpeg', 'thumbnail': None}
                    ],
                }
            }
        },
        ['https://s3/good.png', 'https://s3/foo.png'],
        1
    ),

    # сменилась главная картинка, добавилась дополнительная
    (
        {
            'images': ['https://s3/old.png', 'https://s3/wowthumb.png'],
            'vars': {
                'imported': {
                    'images': [
                        {'image': 'new.jpg', 'thumbnail': None},
                        {
                            'image': 'wow.png',
                            'thumbnail': 'https://s3/wowthumb.png'
                        },
                        {'image': 'extra_new.png', 'thumbnail': None}
                    ],
                }
            }
        },
        [
            'https://s3/new.png',
            'https://s3/wowthumb.png',
            'https://s3/extra_new.png',
        ],
        2
    ),

    # основная картинка удалилась, дополнительная новая вклинилась
    (
        {
            'images': ['https://s3/old.png', 'https://s3/wowthumb.png'],
            'vars': {
                'imported': {
                    'images': [
                        {'image': None, 'thumbnail': None},
                        {'image': 'new_extra.png', 'thumbnail': None},
                        {
                            'image': 'wow.png',
                            'thumbnail': 'https://s3/wowthumb.png'
                        },
                    ],
                }
            }
        },
        ['https://s3/new_extra.png', 'https://s3/wowthumb.png'],
        1
    ),

    # основная картинка удалилась, дополнительная новая вклинилась
    (
        {
            'images': ['https://s3/old.png', 'https://s3/wowthumb.png'],
            'vars': {
                'imported': {
                    'images': [
                        {'image': 'new.png', 'thumbnail': None},
                        {
                            'image': 'wow.png',
                            'thumbnail': 'https://s3/wowthumb.png'
                        },
                    ],
                }
            }
        },
        ['https://s3/new.png', 'https://s3/wowthumb.png'],
        1
    ),
])
async def test_sync_extra_images(
        tap,
        dataset,
        obj_args,
        expected_images,
        expected_count,
        its_a_hard_life,
        fake_grocery_pics_client,
):
    with tap.plan(3, 'несколько картинок изменились'):
        p = await dataset.product(**obj_args)

        await sync_images(p, 'https://some_base_url')

        tap.eq(
            p.images,
            expected_images,
            'дополнительная картинка сменилась'
        )
        tap.eq(p.rehashed('-check'), {'vars', 'images'}, 'поля рехешнуты')
        tap.eq(
            fake_grocery_pics_client.call_count,
            expected_count,
            'Запросы в сервис'
        )


@pytest.mark.parametrize(
    'test_input,expected',
    [
        (
            [
                {'image': 'src1.png', 'thumbnail': None},
                {'image': 'src2.png', 'thumbnail': None},
            ],
            [
                {'image': 'src1.png', 'thumbnail': 'https://s3/src1.png'},
                {'image': 'src2.png', 'thumbnail': 'https://s3/src2.png'},
            ]
        ),
        (
            [
                {'image': 'src1.png', 'thumbnail': 't1.png'},
                {'image': 'src2.png', 'thumbnail': None},
            ],
            [
                {'image': 'src1.png', 'thumbnail': 't1.png'},
                {'image': 'src2.png', 'thumbnail': 'https://s3/src2.png'},
            ]
        ),
    ]
)
async def test_sync_visual_control_images(
        tap, dataset, test_input, expected, its_a_hard_life,
):
    with tap:
        p = await dataset.product(
            vars={'imported': {'visual_control_images': test_input}},
        )

        await sync_images(p, 'https://some_base_url')

        tap.eq(
            p.vars('imported.visual_control_images'),
            expected,
            'превью фров',
        )

        tap.eq(p.rehashed('-check'), {'images', 'vars'}, 'поля рехешнуты')


def test_sort_tree(tap):
    with tap.plan(3):
        children_by_parent = {None: [1, 2, 3]}
        tap.eq_ok(
            list(sort_tree(children_by_parent)),
            [1, 2, 3],
            'Wide tree sorted',
        )

        children_by_parent = {
            None: [1],
            1: [2],
            2: [3],
        }
        tap.eq_ok(
            list(sort_tree(children_by_parent)),
            [1, 2, 3],
            'Deep tree sorted',
        )

        children_by_parent = {
            None: [1000, 2000, 3000],
            1000: [1100, 1200],
            1100: [1110],
            2000: [2100],
            2100: [2110],
            2110: [2111],
        }
        tap.eq_ok(
            list(sort_tree(children_by_parent)),
            [1000, 1100, 1110, 1200, 2000, 2100, 2110, 2111, 3000],
            'Tree sorted',
        )
