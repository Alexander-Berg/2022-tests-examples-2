import json

from generated.clients import grocery_depots as grocery_depots_client
from generated.models import grocery_depots as grocery_depots_models

from atlas_backend.generated.cron import run_cron


async def test_update_groceries_list(web_app_client, patch, db, open_file):
    with open_file('actual_grocery_depots_result.json') as json_file:
        actual_result = json.load(json_file)

    @patch(
        'generated.clients.grocery_depots.GroceryDepotsClient.'
        'internal_v1_depots_v1_depots_post',
    )
    async def _internal_v1_depots_v1_depots_post(*args, **kwargs):
        return grocery_depots_client.InternalV1DepotsV1DepotsPost200(
            grocery_depots_models.InternalDepotsResponse.deserialize(
                actual_result,
            ),
        )

    await run_cron.main(
        [
            'atlas_backend.crontasks.update_groceries_list',  # noqa: E501
            '-t',
            '0',
        ],
    )

    response = await web_app_client.get('/api/v1/groceries/list')
    assert response.status == 200
    content = await response.json()

    with open_file('expected_groceries_list_result.json') as json_file:
        expected_result = json.load(json_file)

    assert content == expected_result
