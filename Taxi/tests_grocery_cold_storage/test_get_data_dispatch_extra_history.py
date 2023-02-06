import datetime

import pytest

NOW_DT = datetime.datetime(
    2020, 3, 13, 7, 19, 00, tzinfo=datetime.timezone.utc,
)


@pytest.mark.yt(
    schemas=['yt_dispatches_extra_history_raw_schema.yaml'],
    dyn_table_data=['yt_dispatches_extra_history_raw.yaml'],
)
async def test_basic(taxi_grocery_cold_storage, yt_apply, load_json):
    request = load_json('get_dispatch_extra_history_request.json')
    response = await taxi_grocery_cold_storage.post(
        '/internal/v1/cold-storage/v1/get/dispatch_eta_history', json=request,
    )

    assert response.status_code == 200
    assert response.json() == load_json(
        'get_dispatch_extra_history_response.json',
    )


@pytest.mark.yt(
    schemas=[
        'yt_dispatches_extra_history_raw_schema.yaml',
        'yt_dispatches_history_index_table_raw_schema.yaml',
    ],
    dyn_table_data=[
        'yt_dispatches_extra_history_raw.yaml',
        'yt_dispatches_history_index_table_raw.yaml',
    ],
)
async def test_request_by_order_id(
        taxi_grocery_cold_storage, yt_apply, load_json,
):
    request = load_json('get_dispatch_extra_history_by_order_id_request.json')
    response = await taxi_grocery_cold_storage.post(
        '/internal/v1/cold-storage/v1/get/dispatch_eta_history', json=request,
    )

    assert response.status_code == 200
    assert response.json() == load_json(
        'get_dispatch_extra_history_responce_by_order_id.json',
    )
