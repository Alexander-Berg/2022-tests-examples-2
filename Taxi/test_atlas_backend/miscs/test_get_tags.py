async def test_get_tags(web_app_client):
    response = await web_app_client.get('/api/v1/tags')
    assert response.status == 200

    content = await response.json()
    assert content == [
        'BusyCommTest',
        'comfort_night_weekend',
        'crm_lavka_target_audience',
        'drivers_workshifts_msk_exp1',
        'drivers_workshifts_msk_exp2',
        'kt_ekb_disgmv30',
        'selfemployed',
    ]
