import json

import pytest


NOMENCLATURE_VALIDATION_METRICS_NAME = 'nomenclature-validation'
MOCK_NOW = '2021-03-03T09:00:00+00:00'


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql(
    'eats_nomenclature_collector', files=['fill_for_no_origin_id.sql'],
)
async def test_products_description(
        taxi_eats_nomenclature_collector,
        testpoint,
        load_json,
        stq,
        mds_s3_storage,
        get_expected_result,
        get_integrations_data_from_json,
        mockserver,
        assert_added_stq_task,
):
    def _get_index_by_origin_id(elements, origin_id):
        for elem in elements:
            if elem['origin_id'] == origin_id:
                return elements.index(elem)
        return -1

    # Generate input data

    data = load_json('integrations_data.json')
    data['place_id'] = 1

    data['menu_items'][0]['description'] = 'description'
    data['menu_items'][0]['retail_info']['general'] = ''
    description_only_id = data['menu_items'][0]['origin_id']

    data['menu_items'][1]['description'] = ''
    data['menu_items'][1]['retail_info']['general'] = 'general'
    general_only_id = data['menu_items'][1]['origin_id']

    data['menu_items'][2]['description'] = 'description'
    data['menu_items'][2]['retail_info']['general'] = 'general'
    general_w_descr_id = data['menu_items'][2]['origin_id']

    integrations_data = get_integrations_data_from_json([data])
    mds_s3_storage.put_object(
        f'some_path/test1.json', json.dumps(integrations_data).encode('utf-8'),
    )

    # Task for 'some_path/test1.json' is added in `fill_for_no_origin_id.sql`

    # Generate expected output data

    expected_result = get_expected_result(['base'], ['base'])

    idx = _get_index_by_origin_id(
        expected_result['items'], description_only_id,
    )
    expected_result['items'][idx]['description']['general'] = 'description'

    idx = _get_index_by_origin_id(expected_result['items'], general_only_id)
    expected_result['items'][idx]['description']['general'] = 'general'

    idx = _get_index_by_origin_id(expected_result['items'], general_w_descr_id)
    expected_result['items'][idx]['description']['general'] = 'general'

    # Verify

    @mockserver.json_handler(
        '/eats-core-retail/v1/place/client-categories/retrieve',
    )
    def _eats_core_retail(request):
        return {
            'has_client_categories': False,
            'has_client_categories_synchronization': False,
            'client_categories': [],
        }

    # pylint: disable=unused-variable
    @testpoint('eats_nomenclature_collector::brand-task-result-sender')
    def handle_finished(arg):
        pass

    await taxi_eats_nomenclature_collector.run_periodic_task(
        'eats-nomenclature-collector_brand-task-result-sender',
    )
    assert handle_finished.times_called == 1
    assert _eats_core_retail.times_called == 2
    assert stq.eats_nomenclature_brand_processing.times_called == 1

    task_info = stq.eats_nomenclature_brand_processing.next_call()
    assert_added_stq_task(
        task_info,
        expected_brand_id='1',
        expected_brand_task_id='uuid-3',
        expected_place_ids=['1'],
        expected_result=expected_result,
    )
