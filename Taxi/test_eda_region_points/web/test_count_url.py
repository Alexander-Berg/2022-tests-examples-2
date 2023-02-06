async def test_count_url(taxi_eda_region_points_web):
    response = await taxi_eda_region_points_web.get(
        f'eats/v1/eda-region-points/v1/count/eyJiYW5uZXJfaWQiOiAxMjM0LCAidHlwZSI6ICJjb3VudCJ9',  # noqa: E501
    )
    assert response.status == 200


async def test_count_view_url(taxi_eda_region_points_web):
    response = await taxi_eda_region_points_web.get(
        f'/eats/v1/eda-region-points/v1/count/eyJiYW5uZXJfaWQiOiAxMjM0LCAidHlwZSI6ICJ2aWV3In0=',  # noqa: E501
    )
    assert response.status == 200


async def test_count_bad_url(taxi_eda_region_points_web):
    response = await taxi_eda_region_points_web.get(
        f'eats/v1/eda-region-points/v1/count/abdcefjs',  # noqa: E501
    )
    assert response.status == 400
