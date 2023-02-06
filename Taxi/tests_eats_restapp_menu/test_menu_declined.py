# pylint: disable=redefined-outer-name,unused-variable
import pytest
PARTNER_ID = 777
PLACE_ID = 109151


@pytest.mark.parametrize(
    (
        'file_new_moderation',
        'file_old_moderation',
        'file_core_items',
        'file_result',
    ),
    [
        pytest.param(
            'eats_moderation.json',
            'eats_core_tasks.json',
            'eats_core_items.json',
            'result.json',
            id='happy path',
        ),
        pytest.param(
            'eats_moderation.json',
            'eats_core_tasks_empty.json',
            'eats_core_items_empty.json',
            'result_core_empty.json',
            id='core empty',
        ),
        pytest.param(
            'eats_moderation_empty.json',
            'eats_core_tasks_empty.json',
            'eats_core_items_empty.json',
            'result_empty.json',
            id='empty',
        ),
    ],
)
async def test_menu_declined(
        mockserver,
        mock_place_access_200,
        taxi_eats_restapp_menu,
        load_json,
        file_new_moderation,
        file_old_moderation,
        file_core_items,
        file_result,
):
    @mockserver.json_handler('eats-moderation/moderation/v1/tasks/list')
    def mock_moderation(request):
        return mockserver.make_response(
            status=200, json=load_json(file_new_moderation),
        )

    @mockserver.json_handler('/eats-core-restapp/v1/moderation-tasks')
    def mock_moderation_core(request):
        return mockserver.make_response(
            status=200, json=load_json(file_old_moderation),
        )

    @mockserver.json_handler(
        '/eats-core-restapp/v1/eats-restapp-menu/place-menu-selection',
    )
    def mock_core_(request):
        return mockserver.make_response(
            status=200, json=load_json(file_core_items),
        )

    response = await taxi_eats_restapp_menu.get(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/declined?place_id='
        f'{PLACE_ID}',
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )

    assert response.status_code == 200
    assert response.json() == load_json(file_result)
