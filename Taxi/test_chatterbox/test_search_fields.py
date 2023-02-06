import pytest


@pytest.mark.translations(
    chatterbox={
        'fields.user_phone': {'ru': 'Телефон', 'en': 'User Phone'},
        'fields.line': {'ru': 'Линия', 'en': ''},
    },
)
@pytest.mark.config(
    CHATTERBOX_ALL_FIELDS_FOR_SEARCH=['user_phone', 'user_email', 'line'],
)
@pytest.mark.parametrize(
    ['locale', 'fields'],
    [
        (
            'ru',
            {
                'available_fields': [
                    {'id': 'user_phone', 'text': 'Телефон'},
                    {'id': 'user_email', 'text': 'user_email'},
                    {'id': 'line', 'text': 'Линия'},
                ],
                'fields': [],
            },
        ),
        (
            'en',
            {
                'available_fields': [
                    {'id': 'user_phone', 'text': 'User Phone'},
                    {'id': 'user_email', 'text': 'user_email'},
                    {'id': 'line', 'text': 'line'},
                ],
                'fields': [],
            },
        ),
        pytest.param(
            'ru',
            {
                'available_fields': [
                    {'id': 'user_phone', 'text': 'Телефон'},
                    {'id': 'user_email', 'text': 'user_email'},
                    {'id': 'line', 'text': 'Линия'},
                ],
                'fields': [
                    {
                        'id': 'requester',
                        'label': 'requester',
                        'type': 'string',
                    },
                    {'id': 'status', 'label': 'status', 'type': 'string'},
                    {'id': 'login', 'label': 'login', 'type': 'string'},
                    {'id': 'tags', 'label': 'tags', 'type': 'array'},
                    {'id': 'created', 'label': 'created', 'type': 'datetime'},
                    {'id': 'updated', 'label': 'updated', 'type': 'datetime'},
                    {'id': 'order_id', 'label': 'order_id', 'type': 'string'},
                    {'id': 'user_phone', 'label': 'Телефон', 'type': 'string'},
                ],
            },
            marks=[
                pytest.mark.config(
                    CHATTERBOX_SEARCH_RESULT_DISPLAY_FIELDS=[
                        {'field': 'requester', 'type': 'string'},
                        {'field': 'status', 'type': 'string'},
                        {'field': 'login', 'type': 'string'},
                        {'field': 'tags', 'type': 'array'},
                        {'field': 'created', 'type': 'datetime'},
                        {'field': 'updated', 'type': 'datetime'},
                        {'field': 'order_id', 'type': 'string'},
                        {'field': 'user_phone', 'type': 'string'},
                    ],
                ),
            ],
        ),
        pytest.param(
            'en',
            {
                'available_fields': [
                    {'id': 'user_phone', 'text': 'User Phone'},
                    {'id': 'user_email', 'text': 'user_email'},
                    {'id': 'line', 'text': 'line'},
                ],
                'fields': [
                    {
                        'id': 'requester',
                        'label': 'requester',
                        'type': 'string',
                    },
                    {'id': 'status', 'label': 'status', 'type': 'string'},
                    {'id': 'login', 'label': 'login', 'type': 'string'},
                    {'id': 'tags', 'label': 'tags', 'type': 'array'},
                    {'id': 'created', 'label': 'created', 'type': 'datetime'},
                    {'id': 'updated', 'label': 'updated', 'type': 'datetime'},
                    {'id': 'order_id', 'label': 'order_id', 'type': 'string'},
                    {'id': 'line', 'label': 'line', 'type': 'string'},
                ],
            },
            marks=[
                pytest.mark.config(
                    CHATTERBOX_SEARCH_RESULT_DISPLAY_FIELDS=[
                        {'field': 'requester', 'type': 'string'},
                        {'field': 'status', 'type': 'string'},
                        {'field': 'login', 'type': 'string'},
                        {'field': 'tags', 'type': 'array'},
                        {'field': 'created', 'type': 'datetime'},
                        {'field': 'updated', 'type': 'datetime'},
                        {'field': 'order_id', 'type': 'string'},
                        {'field': 'line', 'type': 'string'},
                    ],
                ),
            ],
        ),
    ],
)
async def test_search_body(cbox, locale, fields):
    await cbox.query(
        '/v1/tasks/search/available_fields/',
        headers={'Accept-Language': locale},
    )
    assert cbox.status == 200
    assert cbox.body_data == fields
