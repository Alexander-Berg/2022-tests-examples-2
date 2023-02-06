import pytest


DEFAULT_UI_BUTTON = {
    'accent': True,
    'horizontal_divider_type': 'none',
    'payload': {'type': 'navigate_url'},
    'title': 'Далее',
    'type': 'button',
}

CONTENT = {
    'intro': {
        'title': 'Добро пожаловать!',
        'items': [
            {
                'horizontal_divider_type': 'bottom_icon',
                'subtitle': 'Станьте гуру самозанятости',
                'type': 'header',
            },
            {
                'type': 'tip_detail',
                'title': 'Нет комиссии парка',
                'accent': True,
                'left_tip': {
                    'form': 'round',
                    'text': '2',
                    'background_color': '#FCB000',
                },
                'subtitle': 'Подключение к сервису напрямую',
                'right_icon': 'star',
                'horizontal_divider_type': 'bottom_icon',
            },
        ],
        'bottom_items': [DEFAULT_UI_BUTTON],
    },
    'phone-bind': {
        'title': 'Введите телефон',
        'items': [
            {
                'horizontal_divider_type': 'bottom_icon',
                'subtitle': 'Мы отправим вам код',
                'type': 'header',
            },
            {
                'id': 'phone_number',
                'title': 'Телефон',
                'input_pattern_error': 'Неверный формат номера',
                'hint': '',
                'text': '+70001234567',
                'input_type': 'text',
                'input_action': 'next',
                'type': 'edit_text',
            },
        ],
        'bottom_items': [DEFAULT_UI_BUTTON],
    },
    'phone-confirm': {
        'title': 'Введите код',
        'items': [
            {
                'horizontal_divider_type': 'bottom_icon',
                'subtitle': 'Мы проверим ваш код',
                'type': 'header',
            },
            {
                'id': 'phone_code',
                'title': 'Код',
                'hint': '',
                'text': '',
                'input_type': 'text',
                'input_action': 'next',
                'type': 'edit_text',
            },
        ],
        'bottom_items': [DEFAULT_UI_BUTTON],
    },
    'nalog-app': {
        'title': 'Стать самозанятым',
        'items': [
            {
                'type': 'header',
                'subtitle': 'Регистрация займет 7 минут',
                'right_icon': 'star',
                'horizontal_divider_type': 'bottom_icon',
            },
        ],
        'enabled': True,
        'bottom_items': [
            {
                'accent': False,
                'horizontal_divider_type': 'none',
                'payload': {'type': 'navigate_url'},
                'title': 'Открыть Мой налог',
                'type': 'button',
            },
            DEFAULT_UI_BUTTON,
        ],
    },
    'permission': {
        'bottom_items': [
            {
                'accent': True,
                'horizontal_divider_type': 'none',
                'payload': {'type': 'navigate_url'},
                'title': 'Далее',
                'type': 'button',
            },
        ],
        'enabled': True,
        'items': [
            {
                'horizontal_divider_type': 'bottom_icon',
                'right_icon': 'star',
                'subtitle': 'Дайте разрешение',
                'type': 'header',
            },
        ],
        'title': 'Разрешения',
    },
}


@pytest.mark.pgsql('selfemployed_main', files=['mock_selfemployed_main.sql'])
@pytest.mark.experiments3(filename='exp3_get_ui_handles.json')
@pytest.mark.parametrize(
    'step, expect_prev_step, expect_content',
    [
        ('intro', None, CONTENT['intro']),
        ('phone-bind', 'intro', CONTENT['phone-bind']),
        ('phone-confirm', 'phone-bind', CONTENT['phone-confirm']),
        ('nalog-app', 'intro', CONTENT['nalog-app']),
        ('permission', 'intro', CONTENT['permission']),
    ],
)
async def test_get_step(
        taxi_selfemployed_fns_profiles,
        personal_mock,
        mockserver,
        prepare_get_rq,
        step,
        expect_prev_step,
        expect_content,
):
    @mockserver.json_handler(
        '/pro-profiles/platform/v1/profiles/drafts/find-by-passport-uid/v1',
    )
    def _find_by_passport(request):
        assert request.json == {'passport_uid': 'puid1'}
        return {
            'profiles': [
                {
                    'park_id': 'created_park_id',
                    'driver_id': 'created_contractor_id',
                    'profession': 'Driver',
                    'status': 'ready',
                    'city': 'Москва',
                },
            ],
        }

    personal_mock.phone = '+70001234567'

    request = prepare_get_rq(step=step, passport_uid='puid1')
    response = await taxi_selfemployed_fns_profiles.get(**request)
    assert response.status_code == 200
    resp_body = response.json()
    assert resp_body.get('prev_step') == expect_prev_step
    assert resp_body['title'] == expect_content['title']
    assert resp_body['items'] == expect_content['items']
    assert resp_body['bottom_items'] == expect_content['bottom_items']
