import pytest


async def test_configs(web_context):
    assert web_context.config.EXAMPLE_SERVICE_TO_EXPERIMENTS3_TIMEOUT == 1000
    with pytest.raises(AttributeError):
        web_context.config.SOMETHING  # pylint: disable=pointless-statement


@pytest.mark.config(LOCALES_SUPPORTED=['ru', 'en', 'ar'])
async def test_check_config_locales(web_app_client):
    response = await web_app_client.get('/config/check_config_locales')
    assert response.status == 200
    content = await response.text()
    assert content == 'ru_en_ar'


@pytest.mark.config(ENABLE_DRIVER_CHANGE_COST=True)
async def test_config_true(web_app_client):
    response = await web_app_client.get('/change_cost')
    assert response.status == 200


@pytest.mark.config(ENABLE_DRIVER_CHANGE_COST=False)
async def test_config_false(web_app_client):
    response = await web_app_client.get('/change_cost')
    assert response.status == 404


@pytest.mark.config(ENABLE_EDA_FEEDS_CRONTASK=True)
async def test_undefined_config(web_app_client):
    response = await web_app_client.get('/undefined_config')
    assert response.status == 500
    response_json = await response.json()
    assert (
        response_json['details']['reason']
        == '\'Config\' object has no attribute \'ENABLE_EDA_FEEDS_CRONTASK\''
    )
