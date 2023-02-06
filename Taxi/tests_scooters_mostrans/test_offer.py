import pytest


@pytest.mark.parametrize(
    ['requested_locale', 'expected_content'],
    [
        pytest.param('en', 'Some offer', id='Locale: en'),
        pytest.param('ru', 'Какая-то оферта', id='Locale: ru'),
    ],
)
@pytest.mark.config(
    SCOOTERS_MOSTRANS_OFFER={
        'text': {'en': 'Some offer', 'ru': 'Какая-то оферта'},
        'version': 1,
    },
)
async def test_offer_get(
        taxi_scooters_mostrans, requested_locale, expected_content,
):
    response = await taxi_scooters_mostrans.get(
        '/offer', headers={'Locale': requested_locale},
    )
    assert response.status_code == 200
    assert response.json() == {'version': 1, 'content': expected_content}


@pytest.mark.config(
    SCOOTERS_MOSTRANS_OFFER={
        'text': {'en': 'Some offer', 'ru': 'Какая-то оферта'},
        'acceptance_tag': 'mt_offer_v1',
        'version': 1,
    },
)
async def test_offer_post(taxi_scooters_mostrans, mockserver):
    @mockserver.json_handler('/scooter-backend/api/taxi/user/tag_add')
    def mock_add_tag(request):
        assert request.query == {'unique_policy': 'skip_if_exists'}
        assert request.json == {
            'object_ids': ['user_id'],
            'tag_name': 'mt_offer_v1',
        }
        return {
            'tagged_objects': [{'tag_id': ['tag_1'], 'object_id': 'user_id'}],
        }

    response = await taxi_scooters_mostrans.post(
        '/offer',
        {'version': 1},
        headers={
            'Locale': 'ru',
            'X-YaTaxi-UserId': 'user_id',
            'X-Yandex-UID': 'uid',
        },
    )
    assert response.status_code == 200
    assert mock_add_tag.times_called == 1
