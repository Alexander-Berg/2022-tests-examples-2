import pytest


def _get_config():
    return {
        'taximeter_category_1': ['class_1'],
        'taximeter_category_2': ['class_2', 'class_3'],
        'taximeter_category_3': [],
        'taximeter_category_4': ['class_3', 'class_4'],
        'taximeter_category_5': ['class_5'],
    }


@pytest.mark.parametrize(
    'data,code,output',
    [
        pytest.param(
            {'taximeter_categories': 'bad_data'}, 400, {}, id='Bad data',
        ),
        pytest.param({}, 400, {}, id='No taximeter categories'),
        pytest.param(
            {'taximeter_categories': []},
            200,
            {'classes': []},
            id='0 taximeter categories to 0 classes',
        ),
        pytest.param(
            {'taximeter_categories': ['taximeter_category_1']},
            200,
            {'classes': ['class_1']},
            id='1 taximeter category to 1 class',
        ),
        pytest.param(
            {'taximeter_categories': ['taximeter_category_2']},
            200,
            {'classes': ['class_2', 'class_3']},
            id='1 taximeter category to 2 classes',
        ),
        pytest.param(
            {'taximeter_categories': ['taximeter_category_3']},
            200,
            {'classes': []},
            id='1 taximeter category to 0 classes',
        ),
        pytest.param(
            {
                'taximeter_categories': [
                    'taximeter_category_0',
                    'taximeter_category_1',
                    'taximeter_category_2',
                    'taximeter_category_3',
                    'taximeter_category_4',
                ],
            },
            200,
            {'classes': ['class_1', 'class_2', 'class_3', 'class_4']},
            id='Several taximeter categories',
        ),
    ],
)
@pytest.mark.config(TAXIMETER_CATEGORIES_TO_CLASSES=_get_config())
async def test_taximeter_categories_to_classes(
        taxi_driver_categories_api, data, code, output,
):
    response = await taxi_driver_categories_api.post(
        '/v1/categories/taximeter-to-classes', json=data,
    )
    assert response.status_code == code
    if code != 200:
        return

    gotten_output = response.json()['classes']
    gotten_output.sort()
    assert gotten_output == output['classes']


@pytest.mark.parametrize(
    'data,code,output',
    [
        pytest.param({'classes': 'bad_data'}, 400, {}, id='Bad data'),
        pytest.param(
            {'classes': []},
            200,
            {'taximeter_categories': []},
            id='0 classes to 0 taximeter categories',
        ),
        pytest.param(
            {'classes': ['class_1']},
            200,
            {'taximeter_categories': ['taximeter_category_1']},
            id='1 class to 1 taximeter category',
        ),
        pytest.param(
            {'classes': ['class_3']},
            200,
            {
                'taximeter_categories': [
                    'taximeter_category_2',
                    'taximeter_category_4',
                ],
            },
            id='1 class to 2 taximeter categories',
        ),
        pytest.param(
            {'classes': ['class_0']},
            200,
            {'taximeter_categories': []},
            id='1 class to 0 taximeter categories',
        ),
        pytest.param(
            {
                'classes': [
                    'class_0',
                    'class_1',
                    'class_2',
                    'class_3',
                    'class_4',
                ],
            },
            200,
            {
                'taximeter_categories': [
                    'taximeter_category_1',
                    'taximeter_category_2',
                    'taximeter_category_4',
                ],
            },
            id='Several classes',
        ),
        pytest.param(
            {},
            200,
            {
                'taximeter_categories': [
                    'taximeter_category_1',
                    'taximeter_category_2',
                    'taximeter_category_3',
                    'taximeter_category_4',
                    'taximeter_category_5',
                ],
            },
            id='All taximeter categories',
        ),
    ],
)
@pytest.mark.config(TAXIMETER_CATEGORIES_TO_CLASSES=_get_config())
async def test_classes_to_taximeter_categories(
        taxi_driver_categories_api, data, code, output,
):
    response = await taxi_driver_categories_api.post(
        '/v1/categories/classes-to-taximeter', json=data,
    )
    assert response.status_code == code
    if code != 200:
        return

    gotten_output = response.json()['taximeter_categories']
    gotten_output.sort()
    assert gotten_output == output['taximeter_categories']
