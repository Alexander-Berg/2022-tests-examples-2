import pytest


@pytest.mark.parametrize(
    'yandex_uid, service_id, binding_id',
    [
        ('1', 'mango', 'c30c0444-fc23-465e-a5d2-5e8173ddfbce'),
        ('2', 'mango', None),
        ('1', 'yango', 'd30c0444-fc23-465e-a5d2-5e8173ddfbce'),
    ],
)
@pytest.mark.pgsql(
    'cashback_int_api', files=['cashback_int_api_user_bindings.sql'],
)
async def test_get_or_create_binding(
        web_cashback_int_api, yandex_uid, service_id, binding_id,
):
    result = await web_cashback_int_api.binding_create.request(
        yandex_uid=yandex_uid, service=service_id,
    ).perform()

    assert result.status_code == 200
    result_body = result.json()
    assert result_body['service'] == service_id
    assert len(result_body['binding_id']) == 36
    if binding_id is not None:
        assert result_body['binding_id'] == binding_id
