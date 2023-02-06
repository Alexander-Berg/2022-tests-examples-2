import uuid

import pytest

TASK_ID = '5GMix9mn36g1hlQtb40FoJ3DYsCZuYrk4'
PLACE_ID = 'oBk3xjmoTB3pw2fwf7gc17xWv3BIXupGHx7tJ4ztF7g'
BRAND_MAP = {
    'vernyj': '76397',
    'lenta': '123456',
    'miratorg': '573821',
    'coolclever': '1112',
    'vkusvill': '1113',
    'azbuka_vkusa': '1114',
    'erkapharm': '1115',
}
TASK_TYPE_QUEUE_MAP = {
    'price': 'prices',
    'availability': 'availability',
    'stock': 'stocks',
    'nomenclature': 'nomenclature',
}


def _get_stq_name(brand_name, task_type):
    task_type_mapped = TASK_TYPE_QUEUE_MAP[task_type]
    queue_name = f'eats_retail_retail_parser_{task_type_mapped}'
    if brand_name not in BRAND_MAP:
        return queue_name
    return f'{queue_name}_{brand_name}'


@pytest.mark.parametrize(
    'brand',
    [
        'coolclever',
        'vkusvill',
        'azbuka_vkusa',
        'vernyj',
        'lenta',
        'miratorg',
        'erkapharm',
        'some-random-brand',
    ],
)
@pytest.mark.parametrize(
    'task_type', ['price', 'availability', 'stock', 'nomenclature'],
)
@pytest.mark.parametrize(
    'request_data, code',
    [
        (
            {
                'place_group_id': uuid.uuid4().hex,
                'place_id': uuid.uuid4().hex,
                'forwarded_data': {'origin_place_id': uuid.uuid4().hex},
            },
            200,
        ),
        (
            {
                'place_group_id': uuid.uuid4().hex,
                'place_id': uuid.uuid4().hex,
                'forwarded_data': {'origin_place_id': uuid.uuid4().hex},
            },
            200,
        ),
        (
            {
                'place_group_id': uuid.uuid4().hex,
                'place_id': uuid.uuid4().hex,
                'forwarded_data': {'origin_place_id': uuid.uuid4().hex},
            },
            200,
        ),
        (
            {
                'place_group_id': uuid.uuid4().hex,
                'place_id': uuid.uuid4().hex,
                'forwarded_data': {'origin_place_id': uuid.uuid4().hex},
            },
            200,
        ),
        (
            {
                'place_group_id': uuid.uuid4().hex,
                'place_id': uuid.uuid4().hex,
                'forwarded_data': {},
            },
            400,
        ),
        ({}, 400),
    ],
)
@pytest.mark.config(
    EATS_RETAIL_RETAIL_PARSER_MAPPING_BRAND={
        'mapping_brands': {
            'vernyj': ['76397'],
            'lenta': ['123456'],
            'miratorg': ['573821'],
            'coolclever': ['1112'],
            'vkusvill': ['1113'],
            'azbuka_vkusa': ['1114'],
            'erkapharm': ['1115'],
        },
    },
)
async def test_post_task(
        web_app_client, web_context, stq, request_data, code, brand, task_type,
):
    stq_name = _get_stq_name(brand, task_type)
    request_data['brand_id'] = (
        BRAND_MAP[brand] if brand in BRAND_MAP else uuid.uuid4().hex
    )
    request_data['task_type'] = task_type
    response = await web_app_client.post(
        '/v1/start-parsing?task_uuid=taskuuid', json=request_data,
    )
    assert response.status == code
    if response.status == 200:
        stq_handler = getattr(stq, stq_name)
        assert stq_handler.has_calls
