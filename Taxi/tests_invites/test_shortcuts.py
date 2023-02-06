import pytest

URL = '/invites/v1/shortcuts'


def get_headers(phone_id):
    return {'X-YaTaxi-PhoneId': phone_id, 'X-Request-Language': 'ru'}


async def test_no_shortcuts(taxi_invites):
    response = await taxi_invites.post(
        URL, headers=get_headers('phone_id_another'),
    )
    assert response.status_code == 200
    assert response.json() == {'scenario_tops': []}


@pytest.mark.parametrize(
    'phone_id, expected_data_file',
    [
        pytest.param(
            'phone_id_ivan',
            'shortcuts_ivan.json',
            id='shortcut_with_inactivated_invites',
        ),
        pytest.param(
            'phone_id_anna',
            'shortcuts_anna.json',
            id='shortcut_with_all_activated_invites',
        ),
    ],
)
async def test_shortcuts(
        taxi_invites, load_json, phone_id, expected_data_file,
):
    response = await taxi_invites.post(
        URL, headers=get_headers(phone_id=phone_id),
    )
    assert response.status_code == 200

    data = response.json()
    assert len(data['scenario_tops']) == 1
    assert data == load_json(expected_data_file)


async def test_no_translations(taxi_config, taxi_invites):
    # replace tanker key by invalid
    shortcuts_params = taxi_config.get('INVITES_SHORTCUTS_PARAMS')
    shortcuts_params['yandex_go']['shortcut']['title'] = 'invailid_key'
    taxi_config.set(INVITES_SHORTCUTS_PARAMS=shortcuts_params)

    response = await taxi_invites.post(
        URL, headers=get_headers(phone_id='phone_id_ivan'),
    )
    assert response.status_code == 200
    assert response.json() == {'scenario_tops': []}
