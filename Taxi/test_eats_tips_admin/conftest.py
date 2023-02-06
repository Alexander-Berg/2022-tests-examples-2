# pylint: disable=redefined-outer-name
import eats_tips_admin.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['eats_tips_admin.generated.service.pytest_plugins']

# jwt.encode(
#     {'user_id': '1', 'user_code': '000010', 'user_group': '1'},
#     key='awesome_jwt_signature_key',
# )
JWT_USER_1 = (
    'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiM'
    'SIsInVzZXJfY29kZSI6IjAwMDAxMCIsInVzZXJfZ3JvdXAiOiIxIn0'
    '.iyPeG0GUHJc1KptvQ1mgg5x4cb6yIk-NEZHddZ92umU'
)

INCORRECT_JWT = 'INCORRECT_JWT_TOKEN'

USER_ID_1 = '19cf3fc9-98e5-4e3d-8459-179a602bd7a8'
USER_ID_2 = '2590d5f8-bbc7-416b-ad11-99d1f2ace132'
USER_ID_3 = '2590d5f8-bbc7-416b-ad11-99d1f2ace133'

PLACE_1_ID = 'd5e6929e-c92a-4282-9d2e-3a8b233bb50e'
PLACE_2_ID = 'd5e6929e-c92a-4282-9d2e-3a8b233bb50f'
PLACE_3_ID = 'd5e6929e-c92a-4282-9d2e-3a8b233bb510'

PLACE_1 = {'id': PLACE_1_ID, 'title': 'заведение', 'alias': '0000090'}
PLACE_2 = {'id': PLACE_2_ID, 'title': 'кафе'}
USER_1 = (JWT_USER_1, {'id': USER_ID_1, 'alias': '8'})

PLACE_1_USER_1_RECIPIENT = {
    'places': [
        {
            'info': PLACE_1,
            'partners': [
                {
                    'partner_id': USER_ID_1,
                    'roles': ['recipient'],
                    'show_in_menu': False,
                    'confirmed': True,
                },
            ],
        },
    ],
}
PLACE_1_USER_1_BOTH = {
    'places': [
        {
            'info': PLACE_1,
            'partners': [
                {
                    'partner_id': USER_ID_1,
                    'roles': ['admin', 'recipient'],
                    'show_in_menu': False,
                    'confirmed': True,
                },
            ],
        },
    ],
}
PLACE_1_USER_1_UNCONFIRMED = {
    'places': [
        {
            'info': PLACE_1,
            'partners': [
                {
                    'partner_id': USER_ID_1,
                    'roles': ['admin', 'recipient'],
                    'show_in_menu': False,
                    'confirmed': False,
                },
            ],
        },
    ],
}

PLACE_2_USER_1_BOTH = {
    'places': [
        {
            'info': PLACE_2,
            'partners': [
                {
                    'partner_id': USER_ID_1,
                    'roles': ['admin', 'recipient'],
                    'show_in_menu': False,
                    'confirmed': True,
                },
            ],
        },
    ],
}

MONEY_BOX_1 = {
    'id': 'ae9c5024-1c40-4aea-a9b3-d15c4ae44d10',
    'alias': '42',
    'display_name': 'копилка',
    'place_id': 'd5e6929e-c92a-4282-9d2e-3a8b233bb50e',
    'fallback_partner_id': '19cf3fc9-98e5-4e3d-8459-179a602bd7a8',
    'balance': '666',
    'registration_date': '2022-01-18T00:00:00+00:00',
}

MONEY_BOX_1_RESPONSE: dict = {
    **MONEY_BOX_1,
    'place': {'id': MONEY_BOX_1['place_id'], 'name': PLACE_1['title']},
}
MONEY_BOX_1_RESPONSE.pop('place_id')
MONEY_BOX_1_RESPONSE.pop('registration_date')


class _Sentinel:
    pass


SENTINEL = _Sentinel()


def value_or_default(value, default):
    return default if value is SENTINEL else value
