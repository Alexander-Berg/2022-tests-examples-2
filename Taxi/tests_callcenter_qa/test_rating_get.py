import pytest


@pytest.mark.pgsql('callcenter_qa', files=['support_ratings.sql'])
@pytest.mark.parametrize(
    ['post_request', 'expected_response'],
    (
        pytest.param(
            {'guids': ['existed_guid1']},
            {'existed_guid1': {'is_finished': True, 'rating': '5'}},
            id='call is done[1]',
        ),
        pytest.param(
            {'guids': ['not_existed_guid']},
            {'not_existed_guid': {'is_finished': False}},
            id='call is during',
        ),
        pytest.param(
            {'guids': ['existed_guid2']},
            {'existed_guid2': {'is_finished': True}},
            id='call is done[2]',
        ),
    ),
)
async def test_rating_get(taxi_callcenter_qa, post_request, expected_response):
    response = await taxi_callcenter_qa.post('/v1/rating/get', post_request)
    assert response.json() == expected_response
