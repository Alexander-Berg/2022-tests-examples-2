async def test_surge_points_calculations_cache(
        taxi_surge_calculator, testpoint,
):
    content = None

    @testpoint('surge-points-calculations')
    def _set_cache_content(data_json):
        nonlocal content
        content = data_json

    await taxi_surge_calculator.invalidate_caches(
        cache_names=['surge-points-calculations-cache'],
    )
    assert sorted(content, key=lambda x: x['id']) == [
        {'id': ''},
        {'id': '6010bde7eb37e20aaa602576'},
    ]
