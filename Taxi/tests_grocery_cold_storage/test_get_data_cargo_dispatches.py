import datetime

import pytest

NOW_DT = datetime.datetime(
    2020, 3, 13, 7, 19, 00, tzinfo=datetime.timezone.utc,
)


@pytest.mark.yt(
    schemas=['yt_cargo_dispatches_raw_schema.yaml'],
    dyn_table_data=['yt_cargo_dispatches_raw.yaml'],
)
async def test_basic(taxi_grocery_cold_storage, yt_apply, load_json):
    request = load_json('get_cargo_dispatches_request.json')
    response = await taxi_grocery_cold_storage.post(
        '/internal/v1/cold-storage/v1/get/cargo_dispatches', json=request,
    )

    assert response.status_code == 200
    assert response.json() == load_json('get_cargo_dispatches_response.json')


@pytest.mark.yt(
    schemas=['yt_cargo_dispatches_raw_schema.yaml'],
    dyn_table_data=['yt_cargo_dispatches_raw.yaml'],
)
async def test_cache_component(
        taxi_grocery_cold_storage, yt_apply, load_json, testpoint, mocked_time,
):
    @testpoint('do_get_by_key_called')
    def update_cache_tp(data):
        pass

    mocked_time.set(NOW_DT)

    request = load_json('get_cargo_dispatches_request.json')
    response = await taxi_grocery_cold_storage.post(
        '/internal/v1/cold-storage/v1/get/cargo_dispatches', json=request,
    )

    assert response.status_code == 200
    assert response.json() == load_json('get_cargo_dispatches_response.json')
    assert update_cache_tp.times_called == 1

    mocked_time.set(NOW_DT + datetime.timedelta(seconds=60))

    response = await taxi_grocery_cold_storage.post(
        '/internal/v1/cold-storage/v1/get/cargo_dispatches', json=request,
    )

    assert response.status_code == 200
    assert response.json() == load_json('get_cargo_dispatches_response.json')
    assert update_cache_tp.times_called == 1

    mocked_time.set(NOW_DT + datetime.timedelta(seconds=60 + 60))

    response = await taxi_grocery_cold_storage.post(
        '/internal/v1/cold-storage/v1/get/cargo_dispatches', json=request,
    )

    assert response.status_code == 200
    assert response.json() == load_json('get_cargo_dispatches_response.json')
    assert update_cache_tp.times_called == 1

    mocked_time.set(NOW_DT + datetime.timedelta(seconds=60 + 60 + 61))

    response = await taxi_grocery_cold_storage.post(
        '/internal/v1/cold-storage/v1/get/cargo_dispatches', json=request,
    )

    assert response.status_code == 200
    assert response.json() == load_json('get_cargo_dispatches_response.json')
    assert update_cache_tp.times_called == 2
