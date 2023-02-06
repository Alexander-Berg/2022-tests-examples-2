import copy
import json

import dateutil as du
import pytest


NOMENCLATURE_VALIDATION_METRICS_NAME = 'nomenclature-validation'
MOCK_NOW = '2021-03-03T09:00:00+00:00'


@pytest.mark.config(
    EATS_NOMENCLATURE_COLLECTOR_BRAND_TASK_RESULT_SENDER_SETTINGS={
        'enabled': True,
        'period_in_sec': 5,
        'limit': 1000,
        'stq_delay_step_in_sec': 5,
    },
)
@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql(
    'eats_nomenclature_collector', files=['fill_for_stq_task_reschedule.sql'],
)
async def test_stq_task_reschedule(
        taxi_eats_nomenclature_collector,
        taxi_config,
        testpoint,
        stq,
        mds_s3_storage,
        get_integrations_data,
        mockserver,
):
    @mockserver.json_handler(
        '/eats-core-retail/v1/place/client-categories/retrieve',
    )
    def _eats_core_retail(request):
        return {
            'has_client_categories': False,
            'has_client_categories_synchronization': False,
            'client_categories': [],
        }

    config = taxi_config.get(
        'EATS_NOMENCLATURE_COLLECTOR_BRAND_TASK_RESULT_SENDER_SETTINGS',
    )
    stq_delay_step_in_sec = config['stq_delay_step_in_sec']

    brand_id_1 = '1'
    place_ids = ['1', '2', '3']

    base_data = get_integrations_data(['integrations_data.json'])

    # changing of name changes the hash
    data_with_another_name = copy.deepcopy(base_data)
    data_with_another_name['menu_items'][0]['name'] = 'Рагу свиное'

    data2_with_another_name = copy.deepcopy(base_data)
    data2_with_another_name['menu_items'][0]['name'] = 'Рагу свиное 2'

    mds_s3_storage.put_object(
        'some_path/test1.json', json.dumps(base_data).encode('utf-8'),
    )
    mds_s3_storage.put_object(
        'some_path/test2.json',
        json.dumps(data_with_another_name).encode('utf-8'),
    )
    mds_s3_storage.put_object(
        'some_path/test3.json',
        json.dumps(data2_with_another_name).encode('utf-8'),
    )

    # pylint: disable=unused-variable
    @testpoint('eats_nomenclature_collector::brand-task-result-sender')
    def handle_finished(arg):
        pass

    await taxi_eats_nomenclature_collector.run_periodic_task(
        'eats-nomenclature-collector_brand-task-result-sender',
    )
    handle_finished.next_call()

    assert stq.eats_nomenclature_brand_processing.times_called == len(
        place_ids,
    )

    result_place_ids = []
    prev_task_time = du.parser.parse(MOCK_NOW).replace(tzinfo=None)
    for i in range(len(place_ids)):
        task_info = stq.eats_nomenclature_brand_processing.next_call()
        assert task_info['kwargs']['brand_id'] == brand_id_1
        result_json = json.loads(
            mds_s3_storage.storage[task_info['kwargs']['s3_path']].data,
        )
        result_place_ids += result_json['place_ids']
        assert result_json['place_ids'] == task_info['kwargs']['place_ids']
        if i > 0:
            eta = task_info['eta'].replace(tzinfo=None)
            assert (
                eta - prev_task_time
            ).total_seconds() == stq_delay_step_in_sec
            file_datetime = du.parser.parse(
                task_info['kwargs']['file_datetime'],
            ).replace(tzinfo=None)
            assert (
                file_datetime - prev_task_time
            ).total_seconds() == stq_delay_step_in_sec
            prev_task_time = eta
    assert set(result_place_ids) == set(place_ids)
