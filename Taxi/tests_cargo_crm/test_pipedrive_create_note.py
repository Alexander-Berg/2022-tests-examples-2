import pytest


DEFAULT_BODY = {
    'success': True,
    'data': {
        'id': 2,
        'user_id': 5809307,
        'deal_id': 1,
        'person_id': None,
        'org_id': 9,
        'lead_id': None,
        'content': 'this is a note',
        'add_time': '2021-07-29 10:28:50',
        'update_time': '2021-07-29 10:28:50',
        'active_flag': True,
        'pinned_to_deal_flag': False,
        'pinned_to_person_flag': False,
        'pinned_to_organization_flag': False,
        'pinned_to_lead_flag': False,
        'last_update_user_id': None,
        'organization': {'name': 'Альфатранс ООО'},
        'person': None,
        'deal': {'title': 'Альфатранс ООО'},
        'user': {
            'email': 'voytekh@yandex-team.ru',
            'name': 'Алексей Войтех',
            'icon_url': '',
            'is_you': None,
        },
    },
}


@pytest.mark.parametrize(
    'pipedrive_code, expected_code', ((201, 200), (500, 500)),
)
async def test_func_create_fake_org(
        taxi_cargo_crm, mockserver, pipedrive_code, expected_code,
):
    @mockserver.json_handler('pipedrive-api/v1/notes')
    def _handler(request):
        body = None
        if pipedrive_code == 201:
            body = DEFAULT_BODY
        return mockserver.make_response(status=pipedrive_code, json=body)

    response = await taxi_cargo_crm.post(
        '/functions/pipedrive/note/create',
        json={'deal_id': 1, 'content': 'some text'},
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        assert response.json() == {'id': 2, 'deal_id': 1}
