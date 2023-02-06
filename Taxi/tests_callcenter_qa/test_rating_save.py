import pytest

RATING_SAVE_URL = '/v1/rating/save'


@pytest.mark.pgsql('callcenter_qa', files=['support_ratings.sql'])
@pytest.mark.parametrize(
    [
        'body',
        'expected_code',
        'expected_len',
        'expected_rating',
        'expected_call_guid',
    ],
    (
        pytest.param(
            {
                'rating': '5',
                'call_guid': '0000000001-0000000002-0000000003-0000000004',
            },
            200,
            2,
            '5',
            '0000000001-0000000002-0000000003-0000000004',
            id='good request',
        ),
        pytest.param(
            {'bad_request': 'bad'},
            400,
            1,
            '5',
            'existed_guid',
            id='bad request',
        ),
        pytest.param(
            {'rating': '3', 'call_guid': 'existed_guid'},
            200,
            1,
            '5',
            'existed_guid',
            id='existed call_guid',
        ),
    ),
)
async def test_rating_save(
        taxi_callcenter_qa,
        body,
        expected_code,
        expected_len,
        expected_rating,
        expected_call_guid,
        pgsql,
):
    response = await taxi_callcenter_qa.post(RATING_SAVE_URL, body)
    assert response.status_code == expected_code

    if response.status_code != 200:
        return

    cursor = pgsql['callcenter_qa'].cursor()

    cursor.execute('SELECT * FROM callcenter_qa.support_ratings')

    res = cursor.fetchall()

    assert len(res) == expected_len
    if expected_len > 0:
        assert res[-1][1] == expected_rating
        assert res[-1][2] == expected_call_guid
