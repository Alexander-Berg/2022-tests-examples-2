async def test_region_settings_cache(
        taxi_eda_delivery_price, testpoint, set_region_max_price,
):
    """
    Проверяет что ответ ручки
    /v1/export/settings/retions/settings
    перекладывается в кэш
    """
    region_id = 1
    native_max_delivery_fee = 1000
    taxi_max_delivery_fee = 2000
    set_region_max_price(
        region_id, native_max_delivery_fee, taxi_max_delivery_fee,
    )

    @testpoint('region-settings-cache-finish')
    def region_settings_cache_finished(data):
        key = str(region_id)
        assert data == {
            key: {
                'native_max_delivery_fee': native_max_delivery_fee,
                'taxi_max_delivery_fee': taxi_max_delivery_fee,
            },
        }

    await taxi_eda_delivery_price.get('/ping')

    assert region_settings_cache_finished.times_called == 1
