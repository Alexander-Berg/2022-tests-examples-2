import pytest

DEFAULT_UID = '4003514353'


POPUP_RULE_REQUIREMENT_CURRENT = {
    'redirection_rule': {
        'type': 'requirement_current',
        'requirement_pattern': 'childchair',
    },
    'action_localization_keys': {
        'title': 'personalstate.popup.choose_childchair_option',
        'content': 'personalstate.popup.about_childchair_option',
        'edit_comment_label': 'personalstate.popup.edit_comment_action',
        'main_option_label': 'personalstate.popup.open_options_action',
    },
}
POPUP_RULE_CLASS = {
    'redirection_rule': {
        'type': 'class',
        'class': 'child_tariff',
        'requirement_pattern': 'childchair',
    },
    'action_localization_keys': {
        'title': 'personalstate.popup.childtariff_has_childchair',
        'content': 'personalstate.popup.about_childchair_in_tariff',
        'edit_comment_label': 'personalstate.popup.edit_comment_action',
        'main_option_label': 'personalstate.popup.choose_tariff_action',
    },
}
POPUP_RULE_REQUIREMENT_OTHER = {
    'redirection_rule': {
        'type': 'requirement_other',
        'requirement_pattern': 'childchair',
    },
    'action_localization_keys': {
        'title': 'personalstate.popup.tariff_has_childchair',
        'content': 'personalstate.popup.about_childchair_in_tariff',
        'edit_comment_label': 'personalstate.popup.edit_comment_action',
        'main_option_label': 'personalstate.popup.choose_tariff_action',
    },
}
POPUP_RULE_REQUIREMENT_EXPRESS = {
    'redirection_rule': {'type': 'class', 'class': 'express'},
    'action_localization_keys': {
        'title': 'personalstate.popup.express.redirect_comment',
        'content': 'personalstate.popup.express.back_to_comment',
        'edit_comment_label': (
            'personalstate.popup.express.go_to_redirected_tariff'
        ),
        'main_option_label': 'personalstate.popup.express.redirect_content',
    },
}
POPUP_RULE_IMPOSSIBLE = {
    'redirection_rule': {'type': 'impossible'},
    'action_localization_keys': {
        'title': 'personalstate.popup.driver_not_see_comment',
        'content': 'personalstate.popup.about_driver_not_see',
        'edit_comment_label': 'personalstate.popup.edit_comment_action',
    },
}
BANNED_WORDS_CONFIG = [
    {
        'words': ['childchair', 'child'],
        'type': 'child',
        'excluded_classes': ['child_tariff'],
        'excluded_selected_requirements': ['childchair_for_child_tariff'],
        'popup_rules': [
            POPUP_RULE_REQUIREMENT_CURRENT,
            POPUP_RULE_CLASS,
            POPUP_RULE_REQUIREMENT_OTHER,
            POPUP_RULE_IMPOSSIBLE,
        ],
    },
    {
        'words': ['торт'],
        'type': 'unknown',
        'excluded_classes': [],
        'excluded_selected_requirements': [],
        'popup_rules': [POPUP_RULE_REQUIREMENT_CURRENT],
    },
    {
        'words': ['торт'],
        'type': 'express',
        'excluded_classes': [],
        'excluded_selected_requirements': [],
        'popup_rules': [POPUP_RULE_REQUIREMENT_EXPRESS],
    },
]


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.config(
    TVM_ENABLED=False,
    PERSONAL_STATE_BANNED_COMMENTS_LIST_USERSTATE=BANNED_WORDS_CONFIG,
)
async def test_redirect_to_requirement(taxi_user_state, load_json):
    json = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'route': [[37.900188446044922, 55.416580200195312]],
        'revision_id': 24,
        'selected_class': 'vip',
        'requirements': {'conditioner': True},
        'comment': 'child',
    }

    response = await taxi_user_state.post(
        'personalstate', json=json, headers={'X-Yandex-UID': DEFAULT_UID},
    )
    assert response.status_code == 200

    expected = load_json('response/redirect_req.json')
    response_json = response.json()
    assert response_json['action'] == expected['action']


@pytest.mark.config(PERSONAL_STATE_BRANDS_STORED_AS_NULL_USERSTATE=[''])
@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.config(
    TVM_ENABLED=False,
    PERSONAL_STATE_BANNED_COMMENTS_LIST_USERSTATE=BANNED_WORDS_CONFIG,
)
@pytest.mark.tariff_settings(
    filename='tariff_settings_redirect_to_other_tariff_req.json',
)
async def test_redirect_to_other_tariff_requirement(
        taxi_user_state, load_json,
):
    json = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'route': [[37.900188446044922, 55.416580200195312]],
        'revision_id': 24,
        'selected_class': 'econom',
        'requirements': {'conditioner': True},
        'comment': 'child',
    }

    response = await taxi_user_state.post(
        'personalstate', json=json, headers={'X-Yandex-UID': DEFAULT_UID},
    )

    assert response.status_code == 200

    expected = load_json('response/redirect_to_other_tariff_req.json')
    response_json = response.json()

    assert response_json['action'] == expected['action']


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.config(
    TARIFF_CATEGORIES_ENABLED_BY_VERSION={},
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': [
            'econom',
            'comfortplus',
            'vip',
            'minivan',
            'pool',
            'child_tariff',
        ],
    },
    TVM_ENABLED=False,
    PERSONAL_STATE_BANNED_COMMENTS_LIST_USERSTATE=BANNED_WORDS_CONFIG,
)
@pytest.mark.tariff_settings(
    filename='tariff_settings_redirect_to_tariff.json',
)
@pytest.mark.parametrize(
    ('selected_class', 'requirements'),
    [
        ('econom', {}),
        ('vip', {'childchair_for_child_tariff': [7, 7]}),
        ('child_tariff', {}),
    ],
)
async def test_redirect_to_tariff(
        taxi_user_state, selected_class, requirements, load_json,
):
    json = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'route': [[37.900188446044922, 55.416580200195312]],
        'revision_id': 24,
        'selected_class': selected_class,
        'requirements': requirements,
        'comment': 'child',
    }

    response = await taxi_user_state.post(
        'personalstate', json=json, headers={'X-Yandex-UID': DEFAULT_UID},
    )
    assert response.status_code == 200

    response_json = response.json()

    expected = load_json('response/redirect_tariff.json')
    if (
            selected_class == 'child_tariff'
            or 'childchair_for_child_tariff' in requirements
    ):
        assert 'action' not in response_json
    else:
        assert response_json['action'] == expected['action']
    assert response_json['comment'] == expected['comment']


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.config(
    TARIFF_CATEGORIES_ENABLED_BY_VERSION={},
    TVM_ENABLED=False,
    PERSONAL_STATE_BANNED_COMMENTS_LIST_USERSTATE=BANNED_WORDS_CONFIG,
)
@pytest.mark.tariff_settings(
    filename='tariff_settings_impossible_to_redirect.json',
)
async def test_impossible_to_redirect(taxi_user_state, load_json):
    json = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'route': [[37.900188446044922, 55.416580200195312]],
        'revision_id': 24,
        'selected_class': 'econom',
        'requirements': {'conditioner': True},
        'comment': 'child',
    }
    response = await taxi_user_state.post(
        'personalstate', json=json, headers={'X-Yandex-UID': DEFAULT_UID},
    )
    assert response.status_code == 200

    expected = load_json('response/impossible_to_redirect.json')
    response_json = response.json()

    assert response_json['action'] == expected['action']


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.config(
    TARIFF_CATEGORIES_ENABLED_BY_VERSION={},
    TVM_ENABLED=False,
    PERSONAL_STATE_BANNED_COMMENTS_LIST_USERSTATE=BANNED_WORDS_CONFIG,
)
@pytest.mark.tariff_settings(
    filename='tariff_settings_redirect_to_tariff.json',
)
async def test_redirect_check_all_matching(taxi_user_state, load_json):
    json = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'route': [[37.900188446044922, 55.416580200195312]],
        'revision_id': 24,
        'selected_class': 'express',
        'requirements': {},
        'comment': 'торт',
    }

    response = await taxi_user_state.post(
        'personalstate', json=json, headers={'X-Yandex-UID': DEFAULT_UID},
    )
    assert response.status_code == 200
    response_json = response.json()
    expected = load_json('response/redirect_all_matching.json')

    assert response_json['action'] == expected['action']
