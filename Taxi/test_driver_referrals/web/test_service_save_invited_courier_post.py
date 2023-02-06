import pytest

from test_driver_referrals import conftest


@pytest.mark.parametrize(
    ('courier_id', 'promocode', 'response_status'),
    [(101, 'ПРОМОКОД1', 200), (101, 'not_found', 400)],
)
async def test_service_save_invited_courier_post(
        web_app_client, web_context, courier_id, promocode, response_status,
):
    async with conftest.TablesDiffCounts(
            web_context, {'couriers': int(response_status == 200)},
    ):
        response = await web_app_client.post(
            '/service/save-invited-courier',
            json={'courier_id': courier_id, 'promocode': promocode},
        )
        assert response.status == response_status


async def test_service_save_invited_courier_duple_post(
        web_context, web_app_client,
):
    async with conftest.TablesDiffCounts(web_context, {'couriers': 1}):
        response = await web_app_client.post(
            '/service/save-invited-courier',
            json={'courier_id': 101, 'promocode': 'ПРОМОКОД1'},
        )
        assert response.status == 200

    async with conftest.TablesDiffCounts(web_context):
        response = await web_app_client.post(
            '/service/save-invited-courier',
            json={'courier_id': 101, 'promocode': 'ПРОМОКОД1'},
        )
        assert response.status == 400
