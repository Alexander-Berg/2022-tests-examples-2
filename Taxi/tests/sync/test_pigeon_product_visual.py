import pytest
from ymlcfg.jpath import JPath


@pytest.mark.parametrize(
    'test_input,expected',
    [
        (
            {}, False
        ),
        (
            {'data': False}, False,
        ),
        (
            {'data': True}, True,
        ),
    ]
)
async def test_sync_visual_control(
        tap, load_json, uuid, test_input, expected, prod_sync):
    with tap:
        a_product = load_json('data/product.pigeon.json')
        a_product['skuId'] = uuid()

        if test_input:
            a_product['attributes']['visual_control'] = test_input['data']

        product = await prod_sync.prepare_obj(JPath(a_product))
        tap.eq_ok(
            product.vars('imported.visual_control'),
            expected,
            'visual_control',
        )


@pytest.mark.parametrize(
    'test_input,expected',
    [
        (
            {
                'visual_control': [{'data': True}],
                'visual_control_reference_image_1': [
                    {'data': 'bad_banana.jpg'},
                ],
                'visual_control_reference_image_2': [
                    {'data': 'bad_banana2.jpg'},
                ],
                'visual_control_reference_image_3': [
                    {'data': 'bad_banana3.jpg'},
                ],
                'visual_control_reference_image_4': [
                    {'data': 'bad_banana4.jpg'},
                ],
                'visual_control_reference_image_5': [
                    {'data': 'bad_banana5.jpg'},
                ],
            },
            [
                {
                    'image': 'bad_banana.jpg',
                    'thumbnail': None,
                },
                {
                    'image': 'bad_banana2.jpg',
                    'thumbnail': None,
                },
                {
                    'image': 'bad_banana3.jpg',
                    'thumbnail': None,
                },
                {
                    'image': 'bad_banana4.jpg',
                    'thumbnail': None,
                },
                {
                    'image': 'bad_banana5.jpg',
                    'thumbnail': None,
                },
            ]
        ),
        (
            {
                'visual_control': [{'data': False}],
                'visual_control_reference_image_1': [
                    {'data': 'bad_banana.jpg'},
                ],
            },
            []
        ),
        (
            {}, [],
        ),
    ]
)
async def test_sync_visual_control_images(
        tap, load_json, uuid, test_input, expected, prod_sync
):
    with tap:
        a_product = load_json('data/product.pigeon.json')
        a_product['skuId'] = uuid()

        if test_input:
            for k, v in test_input.items():
                a_product['attributes'][k] = v[0]['data']

        product = await prod_sync.prepare_obj(JPath(a_product))
        tap.eq_ok(
            product.vars('imported.visual_control_images'),
            expected,
            'visual_control_images',
        )


@pytest.mark.parametrize(
    'test_input,expected',
    [
        (
            {
                'visual_control': [
                    {'data': True},
                ],
                'visual_control_reference_image_1': [
                    {'data': 'bad_product.png'},
                ],
                'defect1': [
                    {
                        'locale': 'ru_RU',
                        'scope': None,
                        'data': '????????????',
                    }
                ],
                'defectdesc1': [
                    {
                        'locale': 'ru_RU',
                        'scope': None,
                        'data': '?????????????? ????????',
                    }
                ],
            },
            {
                'visual_control_images': [
                    {
                        'image': 'bad_product.png',
                        'thumbnail': None,
                    },
                    {
                        'image': 'bad_apple2.jpg',
                        'thumbnail': None,
                    },
                    {
                        'image': 'bad_apple3.jpg',
                        'thumbnail': None,
                    },
                    {
                        'image': 'bad_apple4.jpg',
                        'thumbnail': None,
                    },
                    {
                        'image': 'bad_apple5.jpg',
                        'thumbnail': None,
                    },
                ],
                'visual_control_titles': [
                    {'defect_title': '????????????'},
                    {'defect_title': '??????????'},
                    {'defect_title': '??????????'},
                    {'defect_title': None},
                    {'defect_title': None},
                ],
                'visual_control_descriptions': [
                    {'defect_desc': '?????????????? ????????'},
                    {'defect_desc': '???????????????? ??????????'},
                    {'defect_desc': '?????????????? ??????????'},
                    {'defect_desc': None},
                    {'defect_desc': None},
                ],
            },
        ),
        (
            {
                'visual_control': [{'data': True}],
                'visual_control_reference_image_1': [{}],
                'visual_control_reference_image_2': [{}],
                'visual_control_reference_image_3': [{}],
                'visual_control_reference_image_4': [{}],
                'visual_control_reference_image_5': [{}],
                'defect1': [
                    {
                        'locale': 'ru_RU',
                        'scope': None,
                        'data': '????????????',
                    }
                ],
            },
            {
                'visual_control_images': [],
                'visual_control_titles': [],
                'visual_control_descriptions': [],
            },
        ),
        (
            {
                'visual_control': [{'data': True}],
                'visual_control_reference_image_1': [
                    {'data': 'bad_product1.png'}
                ],
                'visual_control_reference_image_2': [
                    {'data': 'bad_product2.png'}
                ],
                'visual_control_reference_image_3': [
                    {'data': 'bad_product3.png'}
                ],
                'visual_control_reference_image_4': [{}],
                'visual_control_reference_image_5': [{}],
                'defect1': [
                    {
                        'locale': 'ru_RU',
                        'scope': None,
                        'data': '????????????',
                    }
                ],
                'defect2': [{}],
                'defect3': [
                    {
                        'locale': 'ru_RU',
                        'scope': None,
                        'data': '????????',
                    }
                ],
                'defectdesc1': [{}],
                'defectdesc2': [{}],
                'defectdesc3': [
                    {
                        'locale': 'ru_RU',
                        'scope': None,
                        'data': '?????????????????????????? ????????',
                    }
                ],
            },
            {
                'visual_control_images': [
                    {
                        'image': 'bad_product1.png',
                        'thumbnail': None,
                    },
                    {
                        'image': 'bad_product2.png',
                        'thumbnail': None,
                    },
                    {
                        'image': 'bad_product3.png',
                        'thumbnail': None,
                    },
                ],
                'visual_control_titles': [
                    {'defect_title': '????????????'},
                    {'defect_title': None},
                    {'defect_title': '????????'},
                ],
                'visual_control_descriptions': [
                    {'defect_desc': None},
                    {'defect_desc': None},
                    {'defect_desc': '?????????????????????????? ????????'},
                ],
            }
        ),
        (
            {
                'visual_control': [{'data': True}],
                'visual_control_reference_image_1': [
                    {'data': 'bad_product1.png'}
                ],
                'visual_control_reference_image_2': [{}],
                'visual_control_reference_image_3': [{}],
                'visual_control_reference_image_4': [{}],
                'visual_control_reference_image_5': [{}],
                'defect1': [
                    {
                        'locale': 'en_US',
                        'scope': None,
                        'data': 'Death',
                    }
                ],
                'defect2': [{}],
                'defect3': [{}],
                'defectdesc1': [
                    {
                        'locale': 'en_US',
                        'scope': None,
                        'data': 'mf is dead',
                    }
                ],
                'defectdesc2': [{}],
                'defectdesc3': [{}],
            },
            {
                'visual_control_images': [
                    {
                        'image': 'bad_product1.png',
                        'thumbnail': None,
                    },
                ],
                'visual_control_titles': [{'defect_title': 'Death'}],
                'visual_control_descriptions': [{'defect_desc': 'mf is dead'}],
            },
        ),
    ]
)
async def test_sync_visual_defects(
        tap, load_json, uuid, prod_sync, test_input, expected,
):
    with tap.plan(3, '?????????????????? ?????? ???????????? defect1-3 ?? ????????????????'):
        a_product = load_json('data/product.pigeon.json')
        a_product['skuId'] = uuid()

        if test_input:
            for k, v in test_input.items():
                if not v[0]:
                    a_product['attributes'].pop(k, None)
                    continue
                if 'locale' not in v[0].keys():
                    a_product['attributes'][k] = v[0]['data']
                    continue
                a_product['attributes'][k] = {v[0]['locale']: v[0]['data']}

        product = await prod_sync.prepare_obj(JPath(a_product))
        tap.eq_ok(
            product.vars('imported.visual_control_images'),
            expected['visual_control_images'],
            'visual_control_images',
        )
        tap.eq_ok(
            product.vars('imported.visual_control_titles'),
            expected['visual_control_titles'],
            'visual_control_titles',
        )
        tap.eq_ok(
            product.vars('imported.visual_control_descriptions'),
            expected['visual_control_descriptions'],
            'visual_control_descriptions',
        )
