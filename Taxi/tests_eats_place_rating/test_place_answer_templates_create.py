import pytest

from tests_eats_place_rating import utils


async def test_place_answer_templates_create_403_with_no_permisson(
        taxi_eats_place_rating,
):
    response = await taxi_eats_place_rating.post(
        '/4.0/restapp-front/eats-place-rating/'
        'v1/place-answer-templates/create',
        headers={
            'X-YaEda-PartnerId': '123',
            'X-YaEda-Partner-Permissions': 'some_permission',
        },
        json={'text': 'testtest'},
    )
    assert response.status_code == 403


@pytest.mark.config(EATS_PLACE_RATING_FEEDBACK_ANSWER=utils.TEMPLATES_CONFIG)
async def test_place_answer_templates_create_400_on_long_text(
        taxi_eats_place_rating,
):
    response = await taxi_eats_place_rating.post(
        '/4.0/restapp-front/eats-place-rating/'
        'v1/place-answer-templates/create',
        headers={
            'X-YaEda-PartnerId': '10',
            'X-YaEda-Partner-Permissions': ','.join(
                [
                    'permission.restaurant.management',
                    'permission.feedbacks.manage_templates',
                ],
            ),
        },
        json={'text': 'a' * (utils.TEMPLATES_CONFIG['max_answer_size'] + 1)},
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Template is too long',
    }


@pytest.mark.config(EATS_PLACE_RATING_FEEDBACK_ANSWER=utils.TEMPLATES_CONFIG)
async def test_place_answer_templates_create_400_on_limit(
        taxi_eats_place_rating,
):
    response = await taxi_eats_place_rating.post(
        '/4.0/restapp-front/eats-place-rating/'
        'v1/place-answer-templates/create',
        headers={
            'X-YaEda-PartnerId': '11',
            'X-YaEda-Partner-Permissions': ','.join(
                [
                    'permission.restaurant.management',
                    'permission.feedbacks.manage_templates',
                ],
            ),
        },
        json={'text': 'testtest'},
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Max template number exceeded',
    }


@pytest.mark.config(EATS_PLACE_RATING_FEEDBACK_ANSWER=utils.TEMPLATES_CONFIG)
async def test_place_answer_templates_create_first_template(
        taxi_eats_place_rating, pgsql,
):
    response = await taxi_eats_place_rating.post(
        '/4.0/restapp-front/eats-place-rating/'
        'v1/place-answer-templates/create',
        headers={
            'X-YaEda-PartnerId': '10',
            'X-YaEda-Partner-Permissions': ','.join(
                [
                    'permission.restaurant.management',
                    'permission.feedbacks.manage_templates',
                ],
            ),
        },
        json={'text': 'testtest'},
    )
    assert response.status_code == 200
    expected = utils.make_response([{'id': '11', 'text': 'testtest'}])
    assert response.json() == expected
    assert utils.get_db_templates(pgsql, 10) == expected['templates']


@pytest.mark.config(EATS_PLACE_RATING_FEEDBACK_ANSWER=utils.TEMPLATES_CONFIG)
async def test_place_answer_templates_create_second_template(
        taxi_eats_place_rating, pgsql,
):
    response = await taxi_eats_place_rating.post(
        '/4.0/restapp-front/eats-place-rating/'
        'v1/place-answer-templates/create',
        headers={
            'X-YaEda-PartnerId': '12',
            'X-YaEda-Partner-Permissions': ','.join(
                [
                    'permission.restaurant.management',
                    'permission.feedbacks.manage_templates',
                ],
            ),
        },
        json={'text': 'testtest'},
    )
    assert response.status_code == 200
    expected = utils.make_response(
        [{'id': '2', 'text': 'qwerty'}, {'id': '11', 'text': 'testtest'}],
    )
    assert response.json() == expected
    assert utils.get_db_templates(pgsql, 12) == expected['templates']
