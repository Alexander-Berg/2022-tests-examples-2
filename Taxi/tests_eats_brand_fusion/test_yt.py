import pytest


@pytest.mark.yt(static_table_data=['yt_related_restaurants_data.yaml'])
@pytest.mark.usefixtures('yt_apply')
async def test_get_restaurants_data_from_yt(
        taxi_eats_brand_fusion, testpoint, yt_apply_force, yt_apply, yt_client,
):
    @testpoint('correct_restaurants_data_from_yt')
    def mytp(data):
        assert data['size'] == 2
        assert data['1']['int_photo'] == 0.19

    await taxi_eats_brand_fusion.tests_control(invalidate_caches=True)
    assert mytp.times_called == 1


@pytest.mark.yt()
@pytest.mark.usefixtures('yt_apply')
async def test_get_restaurants_data_from_yt_empty_table(
        taxi_eats_brand_fusion, testpoint, yt_apply_force, yt_apply, yt_client,
):
    @testpoint('correct_restaurants_data_from_yt')
    def mytp(data):
        assert data['size'] == 0

    await taxi_eats_brand_fusion.tests_control(invalidate_caches=True)
    assert mytp.times_called == 1


@pytest.mark.yt(
    static_table_data=['yt_related_restaurants_data_big_table.yaml'],
)
@pytest.mark.usefixtures('yt_apply')
async def test_get_restaurants_data_from_yt_big_table(
        taxi_eats_brand_fusion, testpoint, yt_apply_force, yt_apply, yt_client,
):
    @testpoint('correct_restaurants_data_from_yt')
    def mytp(data):
        assert data['size'] == 14
        assert data['1']['int_photo'] == 19.84

    await taxi_eats_brand_fusion.tests_control(invalidate_caches=True)
    assert mytp.times_called == 1
