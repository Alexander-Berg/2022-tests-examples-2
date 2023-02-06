import pytest

from tests_eats_place_rating import utils


@pytest.mark.config(EATS_PLACE_RATING_FEEDBACK_ANSWER=utils.TEMPLATES_CONFIG)
@pytest.mark.parametrize(
    ['partner_id', 'expected'],
    [
        pytest.param(10, utils.make_response([]), id='without templates'),
        pytest.param(
            11,
            utils.make_response(
                [
                    {'id': '1', 'text': 'abacaba'},
                    {'id': '3', 'text': 'qwerty'},
                    {'id': '4', 'text': 'asdf'},
                ],
            ),
            id='with templates',
        ),
    ],
)
async def test_place_answer_templates_list(
        taxi_eats_place_rating, partner_id, expected,
):
    response = await taxi_eats_place_rating.get(
        '/4.0/restapp-front/eats-place-rating/v1/place-answer-templates/list',
        headers={
            'X-YaEda-PartnerId': str(partner_id),
            'X-YaEda-Partner-Permissions': ','.join(
                [
                    'permission.restaurant.management',
                    'permission.feedbacks.manage_templates',
                ],
            ),
        },
    )
    assert response.status_code == 200
    assert response.json() == expected


async def test_place_answer_templates_list_403_with_no_permisson(
        taxi_eats_place_rating,
):
    response = await taxi_eats_place_rating.get(
        '/4.0/restapp-front/eats-place-rating/v1/place-answer-templates/list',
        headers={
            'X-YaEda-PartnerId': '123',
            'X-YaEda-Partner-Permissions': 'some_permission',
        },
    )
    assert response.status_code == 403
