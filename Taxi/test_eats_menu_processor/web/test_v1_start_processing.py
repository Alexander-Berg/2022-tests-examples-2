import pytest


@pytest.mark.parametrize(
    'request_name, status_code, stq_has_calls',
    [
        ('full', 200, True),
        ('without_place_group_id', 400, False),
        ('without_place_id', 400, False),
        ('without_brand_id', 400, False),
        ('without_s3_link', 400, False),
    ],
)
async def test_start_menu_processing(
        request_name,
        status_code,
        stq_has_calls,
        load_json,
        web_app_client,
        stq,
):
    response = await web_app_client.post(
        '/v1/start-processing',
        json=load_json('request.json')[request_name],
        params={'task_uuid': '123'},
    )
    assert response.status == status_code
    assert stq.eats_menu_processor_processing.has_calls == stq_has_calls


async def test_start_menu_processing_with_right_args(
        load_json, web_app_client, patch,
):
    task_uuid = '123'
    data = load_json('request.json')['full']

    @patch('eats_menu_processor.stq.processing.task')
    def _processing_task(*args, **kwargs):
        assert kwargs == {
            'uuid': task_uuid,
            's3_link': data['s3_link'],
            'brand_id': data['brand_id'],
            'place_group_id': data['place_group_id'],
            'place_id': data['place_id'],
        }

    response = await web_app_client.post(
        '/v1/start-processing', json=data, params={'task_uuid': task_uuid},
    )
    assert response.status == 200


async def test_start_menu_processing_409(load_json, web_app_client, stq):
    response = await web_app_client.post(
        '/v1/start-processing',
        json=load_json('request.json')['full'],
        params={'task_uuid': '123'},
    )
    assert response.status == 200

    response = await web_app_client.post(
        '/v1/start-processing',
        json=load_json('request.json')['full'],
        params={'task_uuid': '123'},
    )
    assert response.status == 409
    assert stq.eats_menu_processor_processing.times_called == 1
