import pytest

from test_corp_personal import utils

PD_KEYS = ['phone', 'email', 'contact_emails']


@pytest.mark.parametrize(
    'data, expected',
    [
        pytest.param(
            {
                'name': 'user',
                'phone_id': utils.PERSONAL_DATA['phones'][0]['id'],
                'email_id': utils.PERSONAL_DATA['emails'][0]['id'],
            },
            {
                'name': 'user',
                'phone': utils.PERSONAL_DATA['phones'][0]['value'],
                'email': utils.PERSONAL_DATA['emails'][0]['value'],
            },
            id='one object',
        ),
        pytest.param(
            {
                'name': 'user',
                'contact_emails_ids': [
                    utils.PERSONAL_DATA['emails'][0]['id'],
                    utils.PERSONAL_DATA['emails'][1]['id'],
                ],
            },
            {
                'name': 'user',
                'contact_emails': [
                    utils.PERSONAL_DATA['emails'][0]['value'],
                    utils.PERSONAL_DATA['emails'][1]['value'],
                ],
            },
            id='one object with list value',
        ),
        pytest.param(
            [
                {
                    'name': 'user_1',
                    'phone_id': utils.PERSONAL_DATA['phones'][0]['id'],
                    'email_id': utils.PERSONAL_DATA['emails'][0]['id'],
                },
                {
                    'name': 'user_2',
                    'phone_id': utils.PERSONAL_DATA['phones'][1]['id'],
                    'email_id': utils.PERSONAL_DATA['emails'][1]['id'],
                },
            ],
            [
                {
                    'name': 'user_1',
                    'phone': utils.PERSONAL_DATA['phones'][0]['value'],
                    'email': utils.PERSONAL_DATA['emails'][0]['value'],
                },
                {
                    'name': 'user_2',
                    'phone': utils.PERSONAL_DATA['phones'][1]['value'],
                    'email': utils.PERSONAL_DATA['emails'][1]['value'],
                },
            ],
            id='many objects',
        ),
        pytest.param(
            {'name': 'user', 'contact_emails_ids': []},
            {'name': 'user', 'contact_emails': []},
            id='empty list value',
        ),
        pytest.param(
            {'name': 'user', 'phone_id': None},
            {'name': 'user', 'phone': None},
            id='null pd_id',
        ),
        pytest.param(
            {'name': 'user', 'phone_id': 'unknown'},
            {'name': 'user', 'phone': None},
            id='unexpected pd_id',
        ),
    ],
)
async def test_replace(library_context, data, expected):

    pd_fields = library_context.corp_personal.make_pd_fields(PD_KEYS)
    await library_context.corp_personal.replace_pd_with_values(pd_fields, data)
    assert data == expected
