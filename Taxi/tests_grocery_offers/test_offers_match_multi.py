import pytest

from tests_grocery_offers import tests_headers


@pytest.mark.pgsql('grocery_offers', files=['offers_match_multi.sql'])
@pytest.mark.now('2020-04-20 15:15:00.000000+03')
@pytest.mark.parametrize(
    'offers_request, result',
    [
        (
            [
                {
                    'id': 'offer_id_one',
                    'tag': 'offer_tag_one',
                    'params': {'invalid': True},
                },
                {
                    'id': 'offer_id_one',
                    'tag': 'offer_tag_one',
                    'params': {'place_id': 'place_id_one'},
                },
                {'id': '404_id', 'tag': 'offer_tag_one', 'params': {}},
            ],
            [
                {
                    'matched': False,
                    'not_matched_reason': 'PARAMS_NOT_MATCHING',
                },
                {'matched': True},
                {'matched': False, 'not_matched_reason': 'OFFER_NOT_FOUND'},
            ],
        ),
        (
            [
                {
                    'id': 'offer_id_one',
                    'tag': 'offer_tag_one',
                    'params': {'place_id': 'place_id_one'},
                },
                {
                    'id': 'offer_id_expired',
                    'tag': 'offer_tag_expired',
                    'params': {'place_id': 'place_id_expired'},
                },
            ],
            [
                {'matched': True},
                {'matched': False, 'not_matched_reason': 'OFFER_EXPIRED'},
            ],
        ),
    ],
)
async def test_match_by_ids(taxi_grocery_offers, offers_request, result):
    await _perform_test(taxi_grocery_offers, offers_request, result)


@pytest.mark.pgsql('grocery_offers', files=['offers_match_multi.sql'])
@pytest.mark.now('2020-04-20 15:15:00.000000+03')
@pytest.mark.parametrize(
    'offers_request, result',
    [
        (
            [
                {'tag': 'offer_tag_one', 'params': {'invalid': True}},
                {
                    'tag': 'offer_tag_one',
                    'params': {'place_id': 'place_id_one'},
                },
                {
                    'tag': 'offer_tag_expired',
                    'params': {'place_id': 'place_id_expired'},
                },
            ],
            [
                {'matched': False, 'not_matched_reason': 'OFFER_NOT_FOUND'},
                {'matched': True},
                {'matched': False, 'not_matched_reason': 'OFFER_EXPIRED'},
            ],
        ),
        (
            [
                {
                    'tag': 'offer_tag_one',
                    'params': {'place_id': 'place_id_one'},
                },
                {'tag': 'offer_tag_one', 'params': {'place_id': '2'}},
            ],
            [
                {'matched': True},
                {'matched': False, 'not_matched_reason': 'OFFER_NOT_FOUND'},
            ],
        ),
    ],
)
async def test_match_by_params(taxi_grocery_offers, offers_request, result):
    await _perform_test(taxi_grocery_offers, offers_request, result)


@pytest.mark.pgsql('grocery_offers', files=['offers_match_multi.sql'])
@pytest.mark.now('2020-04-20 15:15:00.000000+03')
@pytest.mark.parametrize(
    'offers_request, result',
    [
        (
            [
                {'tag': 'offer_tag_one', 'params': {'invalid': True}},
                {
                    'id': 'offer_id_one',
                    'tag': 'offer_tag_one',
                    'params': {'place_id': 'place_id_one'},
                },
                {
                    'id': 'offer_id_expired',
                    'tag': 'offer_tag_expired',
                    'params': {'place_id': 'place_id_expired'},
                },
            ],
            [
                {'matched': False, 'not_matched_reason': 'OFFER_NOT_FOUND'},
                {'matched': True},
                {'matched': False, 'not_matched_reason': 'OFFER_EXPIRED'},
            ],
        ),
        (
            [
                {
                    'tag': 'offer_tag_one',
                    'params': {'place_id': 'place_id_one'},
                },
                {
                    'id': 'offer_id_one',
                    'tag': 'offer_tag_one',
                    'params': {'place_id': '2'},
                },
            ],
            [
                {'matched': True},
                {
                    'matched': False,
                    'not_matched_reason': 'PARAMS_NOT_MATCHING',
                },
            ],
        ),
    ],
)
async def test_match_combined(taxi_grocery_offers, offers_request, result):
    await _perform_test(taxi_grocery_offers, offers_request, result)


@pytest.mark.pgsql('grocery_offers', files=['offers_match_multi.sql'])
@pytest.mark.now('2020-04-20 15:15:00.000000+03')
async def test_grouping_sorting(taxi_grocery_offers):
    response = await taxi_grocery_offers.post(
        '/v1/match/multi',
        headers=tests_headers.HEADERS,
        json={
            'offers': [
                {
                    'tag': 'offer_tag_one',
                    'params': {'place_id': 'place_id_one'},
                },
                {
                    'tag': 'offer_tag_three',
                    'params': {'place_id': 'place_id_three'},
                },
            ],
        },
    )
    assert response.status_code == 200

    offers_response = response.json()['offers']
    assert len(offers_response) == 2

    assert offers_response[0] == {
        'matched': True,
        'offer_params': {'place_id': 'place_id_one'},
        'payload': {'payload': 'i am a payload!'},
    }
    assert offers_response[1] == {
        'matched': True,
        'offer_params': {'place_id': 'place_id_three'},
        'payload': {'payload': 'i am a payload three!'},
    }


async def _perform_test(taxi_grocery_offers, offers_request, result):
    response = await taxi_grocery_offers.post(
        '/v1/match/multi',
        headers=tests_headers.HEADERS,
        json={'offers': offers_request},
    )
    assert response.status_code == 200

    offers_response = response.json()['offers']
    assert len(offers_response) == len(offers_request)

    for expected, actual in zip(result, offers_response):
        _assert_offer_response(expected, actual)


def _assert_offer_response(expected, actual):
    assert expected['matched'] == actual['matched']

    if not actual['matched']:
        assert expected['not_matched_reason'] == actual['not_matched_reason']
