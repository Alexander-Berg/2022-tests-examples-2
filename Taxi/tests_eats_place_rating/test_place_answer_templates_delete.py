import pytest

from tests_eats_place_rating import utils


async def test_place_answer_templates_delete_403_with_no_permisson(
        taxi_eats_place_rating,
):
    response = await taxi_eats_place_rating.post(
        '/4.0/restapp-front/eats-place-rating/'
        'v1/place-answer-templates/delete',
        headers={
            'X-YaEda-PartnerId': '11',
            'X-YaEda-Partner-Permissions': 'some_permission',
        },
        params={'template_id': '1'},
        json={'text': 'testtest'},
    )
    assert response.status_code == 403


@pytest.mark.config(EATS_PLACE_RATING_FEEDBACK_ANSWER=utils.TEMPLATES_CONFIG)
async def test_place_answer_templates_delete_skip_invalid_id(
        taxi_eats_place_rating, pgsql,
):
    response = await taxi_eats_place_rating.post(
        '/4.0/restapp-front/eats-place-rating/'
        'v1/place-answer-templates/delete',
        headers={
            'X-YaEda-PartnerId': '11',
            'X-YaEda-Partner-Permissions': ','.join(
                [
                    'permission.restaurant.management',
                    'permission.feedbacks.manage_templates',
                ],
            ),
        },
        params={'template_id': 'abc'},
    )
    assert response.status_code == 200
    expected = utils.make_response(
        [{'id': '3', 'text': 'qwerty'}, {'id': '6', 'text': 'zxcvbnm'}],
    )
    assert response.json() == expected
    assert utils.get_db_templates(pgsql, 11) == expected['templates']


@pytest.mark.config(EATS_PLACE_RATING_FEEDBACK_ANSWER=utils.TEMPLATES_CONFIG)
async def test_place_answer_templates_delete_skip_unknown_id(
        taxi_eats_place_rating, pgsql,
):
    response = await taxi_eats_place_rating.post(
        '/4.0/restapp-front/eats-place-rating/'
        'v1/place-answer-templates/delete',
        headers={
            'X-YaEda-PartnerId': '11',
            'X-YaEda-Partner-Permissions': ','.join(
                [
                    'permission.restaurant.management',
                    'permission.feedbacks.manage_templates',
                ],
            ),
        },
        params={'template_id': '1'},
    )
    assert response.status_code == 200
    expected = utils.make_response(
        [{'id': '3', 'text': 'qwerty'}, {'id': '6', 'text': 'zxcvbnm'}],
    )
    assert response.json() == expected
    assert utils.get_db_templates(pgsql, 11) == expected['templates']


@pytest.mark.config(EATS_PLACE_RATING_FEEDBACK_ANSWER=utils.TEMPLATES_CONFIG)
async def test_place_answer_templates_update_skip_different_user(
        taxi_eats_place_rating, pgsql,
):
    response = await taxi_eats_place_rating.post(
        '/4.0/restapp-front/eats-place-rating/'
        'v1/place-answer-templates/delete',
        headers={
            'X-YaEda-PartnerId': '12',
            'X-YaEda-Partner-Permissions': ','.join(
                [
                    'permission.restaurant.management',
                    'permission.feedbacks.manage_templates',
                ],
            ),
        },
        params={'template_id': '6'},
    )
    assert response.status_code == 200
    expected = utils.make_response([{'id': '2', 'text': 'abacaba'}])
    assert response.json() == expected
    assert utils.get_db_templates(pgsql, 12) == expected['templates']
    assert utils.get_db_templates(pgsql, 11) == [
        {'id': '3', 'text': 'qwerty'},
        {'id': '6', 'text': 'zxcvbnm'},
    ]


@pytest.mark.config(EATS_PLACE_RATING_FEEDBACK_ANSWER=utils.TEMPLATES_CONFIG)
async def test_place_answer_templates_delete(taxi_eats_place_rating, pgsql):
    response = await taxi_eats_place_rating.post(
        '/4.0/restapp-front/eats-place-rating/'
        'v1/place-answer-templates/delete',
        headers={
            'X-YaEda-PartnerId': '11',
            'X-YaEda-Partner-Permissions': ','.join(
                [
                    'permission.restaurant.management',
                    'permission.feedbacks.manage_templates',
                ],
            ),
        },
        params={'template_id': '6'},
    )
    assert response.status_code == 200
    expected = utils.make_response([{'id': '3', 'text': 'qwerty'}])
    assert response.json() == expected
    assert utils.get_db_templates(pgsql, 11) == expected['templates']
    assert utils.get_db_templates(pgsql, 12) == [
        {'id': '2', 'text': 'abacaba'},
    ]
