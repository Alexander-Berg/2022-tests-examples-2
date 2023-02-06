import pytest


@pytest.mark.parametrize(
    'params, expected_data',
    [
        (
            {},
            {
                'responses': [
                    {
                        'created': '2020-04-06T19:00:00+03:00',
                        'form_code': 'test_form',
                        'id': 7,
                    },
                    {
                        'created': '2020-04-06T19:00:00+03:00',
                        'form_code': 'test_form_2',
                        'id': 6,
                    },
                    {
                        'created': '2020-04-06T18:00:00+03:00',
                        'form_code': 'test_form',
                        'id': 5,
                    },
                ],
                'min_id': 5,
            },
        ),
        (
            {'form_code': 'test_form'},
            {
                'responses': [
                    {
                        'created': '2020-04-06T19:00:00+03:00',
                        'form_code': 'test_form',
                        'id': 7,
                    },
                    {
                        'created': '2020-04-06T18:00:00+03:00',
                        'form_code': 'test_form',
                        'id': 5,
                    },
                ],
                'min_id': 5,
            },
        ),
        ({'form_code': 'non_existing_form'}, {'responses': []}),
        (
            {'less_than_id': 7},
            {
                'responses': [
                    {
                        'created': '2020-04-06T19:00:00+03:00',
                        'form_code': 'test_form_2',
                        'id': 6,
                    },
                    {
                        'created': '2020-04-06T18:00:00+03:00',
                        'form_code': 'test_form',
                        'id': 5,
                    },
                ],
                'min_id': 5,
            },
        ),
    ],
)
async def test_responses_list(get_list, params, expected_data):
    await get_list(params, expected_data)
