import pytest


EATS_NOTIFICATIONS_TRANSLATIONS = {
    'eats_eats-notifications': {'title_key': {'ru': 'title %(param)s'}},
    'notify': {'title_key': {'ru': 'title %(param)s'}},
}


@pytest.mark.translations(**EATS_NOTIFICATIONS_TRANSLATIONS)
@pytest.mark.parametrize(
    'request_json',
    [
        pytest.param(
            {'tanker_keyset': 'notify', 'tanker_key': 'title_key'},
            id='notify without tanker_project_key',
        ),
        pytest.param(
            {
                'tanker_project_key': 'eats',
                'tanker_keyset': 'eats-notifications',
                'tanker_key': 'title_key',
            },
            id='empty keyset',
        ),
    ],
)
async def test_translation_200(
        taxi_eats_notifications, mockserver, request_json,
):
    response = await taxi_eats_notifications.get(
        '/v1/admin/translation', params=request_json,
    )
    assert response.status_code == 200
    assert response.json() == {'text': 'title {param}'}


@pytest.mark.parametrize(
    'keyset, key',
    [
        pytest.param('notify', '', id='empty key'),
        pytest.param('', '', id='empty keyset'),
        pytest.param('notify', 'title_key', id='key not found'),
        pytest.param('unknown', '', id='keyset not found'),
    ],
)
async def test_translation_404(taxi_eats_notifications, keyset, key):
    response = await taxi_eats_notifications.get(
        '/v1/admin/translation',
        params={'tanker_keyset': keyset, 'tanker_key': key},
    )
    assert response.status_code == 404
