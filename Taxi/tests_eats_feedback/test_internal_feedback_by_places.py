import pytest


@pytest.mark.now('2021-05-15T00:00:00.0000+00:00')
@pytest.mark.parametrize(
    ['body', 'expected_status_code', 'result_json'],
    [
        [
            {
                'place_ids': ['1'],
                'user_locale': 'ru',
                'hide_unmoderated': False,
                'from': '2021-05-01T11:11:11.1111+00:20',
            },
            200,
            'feedbacks_1.json',
        ],
        [
            {
                'place_ids': ['1'],
                'user_locale': 'ru',
                'from': '2021-05-11T11:11:11.1111+00:20',
            },
            200,
            'feedbacks_0.json',
        ],
        [
            {
                'place_ids': ['1'],
                'user_locale': 'ru',
                'to': '2021-05-11T11:11:11.1111+00:20',
                'from': '2021-05-10T11:11:11.1111+00:20',
            },
            200,
            'feedbacks_0.json',
        ],
        [
            {
                'place_ids': ['4'],
                'user_locale': 'ru',
                'from': '2021-05-01T11:11:11.1111+00:20',
            },
            200,
            'feedbacks_4.json',
        ],
        [
            {
                'place_ids': ['4'],
                'user_locale': 'ru',
                'to': '2021-05-10T11:11:11.1111+00:20',
                'from': '2021-05-01T11:11:11.1111+00:20',
            },
            200,
            'feedbacks_4.json',
        ],
        [
            {
                'place_ids': ['4'],
                'user_locale': 'ru',
                'from': '2021-05-08T08:00:00.000+00:00',
                'to': '2021-05-08T20:00:00.000+00:00',
            },
            200,
            'feedbacks_5.json',
        ],
        [
            {
                'place_ids': ['1', '4'],
                'user_locale': 'ru',
                'hide_unmoderated': False,
                'from': '2021-05-01T11:11:11.1111+00:20',
            },
            200,
            'feedbacks_1_4.json',
        ],
        [
            {
                'place_ids': ['1', '4'],
                'user_locale': 'ru',
                'hide_unmoderated': False,
                'from': '2021-01-11T11:11:11.1111+00:20',
            },
            400,
            None,
        ],
        [
            {
                'place_ids': ['1', '4'],
                'user_locale': 'ru',
                'hide_unmoderated': False,
                'from': '2020-05-11T11:11:11.1111+00:20',
                'to': '2021-01-01T00:00:00.0000+00:00',
            },
            400,
            None,
        ],
    ],
)
@pytest.mark.pgsql(
    'eats_feedback',
    files=[
        'predefined_comments.sql',
        'feedbacks.sql',
        'orders.sql',
        'feedbacks_answer.sql',
    ],
)
async def test_get_feedbacks(
        load_json, taxi_eats_feedback, body, expected_status_code, result_json,
):
    response = await taxi_eats_feedback.post(
        '/internal/eats-feedback/v1/feedbacks-by-places', json=body,
    )
    assert response.status_code == expected_status_code
    if expected_status_code == 200:
        assert response.json() == load_json(result_json)
