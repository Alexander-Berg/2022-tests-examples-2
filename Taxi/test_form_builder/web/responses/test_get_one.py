import pytest


@pytest.mark.parametrize(
    'id_, expected_status, expected_data',
    [
        (100500, 404, None),
        (
            5,
            200,
            {
                'created': '2020-04-06T18:00:00+03:00',
                'form_code': 'test_form',
                'id': 5,
                'values': [
                    {
                        'key': 'a',
                        'value': {'stringValue': 'phone_id', 'type': 'string'},
                        'personal_data_type': 'phones',
                        'label': {'translation': 'phone_label'},
                    },
                    {
                        'key': 'b',
                        'value': {'integerValue': 1, 'type': 'integer'},
                    },
                    {
                        'key': 'c',
                        'label': {'translation': 'Какой то заголовок'},
                    },
                ],
            },
        ),
        (
            6,
            200,
            {
                'created': '2020-04-06T19:00:00+03:00',
                'form_code': 'test_form_2',
                'id': 6,
                'values': [],
            },
        ),
    ],
)
@pytest.mark.translations(form_builder={'x.y': {'ru': 'Какой то заголовок'}})
async def test_responses_get(get_one, id_, expected_status, expected_data):
    await get_one(id_, expected_status, expected_data)
