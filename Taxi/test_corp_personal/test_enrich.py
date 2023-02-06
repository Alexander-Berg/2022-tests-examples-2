import pytest

from test_corp_personal import utils

PD_KEYS = ['phone', 'email', 'contact_emails']


@pytest.mark.parametrize(
    'data, expected, remove_values',
    [
        pytest.param(
            {
                'name': 'user',
                'phone': utils.PERSONAL_DATA['phones'][0]['value'],
                'email': utils.PERSONAL_DATA['emails'][0]['value'],
            },
            {
                'name': 'user',
                'phone_id': utils.PERSONAL_DATA['phones'][0]['id'],
                'email_id': utils.PERSONAL_DATA['emails'][0]['id'],
            },
            True,
            id='one object remove values',
        ),
        pytest.param(
            {
                'name': 'user',
                'phone': utils.PERSONAL_DATA['phones'][0]['value'],
                'email': utils.PERSONAL_DATA['emails'][0]['value'],
            },
            {
                'name': 'user',
                'phone': utils.PERSONAL_DATA['phones'][0]['value'],
                'email': utils.PERSONAL_DATA['emails'][0]['value'],
                'phone_id': utils.PERSONAL_DATA['phones'][0]['id'],
                'email_id': utils.PERSONAL_DATA['emails'][0]['id'],
            },
            False,
            id='one object dont remove values',
        ),
        pytest.param(
            {
                'name': 'user',
                'contact_emails': [
                    utils.PERSONAL_DATA['emails'][0]['value'],
                    utils.PERSONAL_DATA['emails'][1]['value'],
                ],
            },
            {
                'name': 'user',
                'contact_emails_ids': [
                    utils.PERSONAL_DATA['emails'][0]['id'],
                    utils.PERSONAL_DATA['emails'][1]['id'],
                ],
            },
            True,
            id='one object with list value remove values',
        ),
        pytest.param(
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
            True,
            id='many objects',
        ),
        pytest.param(
            {'name': 'user', 'phone': ''},
            {'name': 'user', 'phone_id': None},
            True,
            id='empty value',
        ),
        pytest.param(
            {'name': 'user', 'contact_emails': []},
            {'name': 'user', 'contact_emails_ids': []},
            True,
            id='empty list value',
        ),
        pytest.param(
            {'name': 'user', 'phone': None},
            {'name': 'user', 'phone_id': None},
            True,
            id='null value',
        ),
    ],
)
async def test_enrich(library_context, data, expected, remove_values):

    pd_fields = library_context.corp_personal.make_pd_fields(PD_KEYS)
    await library_context.corp_personal.enrich_with_pd_ids(
        pd_fields, data, remove_values=remove_values,
    )
    assert data == expected
