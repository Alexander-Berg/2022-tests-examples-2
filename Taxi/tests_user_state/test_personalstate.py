import pytest


DEFAULT_UID = '4003514353'


async def test_unauthorized_user(taxi_user_state):
    json = {
        'id': 'unauthorized_id',
        'route': [[37.900188446044922, 55.416580200195312]],
    }
    response = await taxi_user_state.post('personalstate', json=json)
    assert response.status_code == 401


@pytest.mark.config(PERSONAL_STATE_BRANDS_STORED_AS_NULL_USERSTATE=[''])
@pytest.mark.config(TVM_ENABLED=False)
@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
async def test_personalstate_get_response_no_entry(taxi_user_state):
    json = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'route': [[37.1946401739712, 55.478983901730004]],
    }
    response = await taxi_user_state.post(
        'personalstate', json=json, headers={'X-Yandex-UID': DEFAULT_UID},
    )
    response_json = response.json()
    assert response_json['revision_id'] == 0


@pytest.mark.config(
    PERSONAL_STATE_BRANDS_STORED_AS_NULL_USERSTATE=[''], TVM_ENABLED=False,
)
@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
async def test_personalstate_get_response_bad_route(taxi_user_state):
    json = {'id': 'b300bda7d41b4bae8d58dfa93221ef16', 'route': [[0, 0]]}
    response = await taxi_user_state.post(
        'personalstate', json=json, headers={'X-Yandex-UID': DEFAULT_UID},
    )
    assert response.status_code == 400


@pytest.mark.config(
    TVM_ENABLED=False, PERSONAL_STATE_BRANDS_STORED_AS_NULL_USERSTATE=[''],
)
@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.parametrize(
    'selected_class, selected_class_can_be_default',
    [
        pytest.param('business', True, id='save_default_category'),
        pytest.param('minivan', False, id='skip_no_default_category'),
    ],
)
@pytest.mark.parametrize(
    'has_previous_state',
    [
        pytest.param(False, id='no_previous_state'),
        pytest.param(
            True,
            marks=[pytest.mark.filldb(personal_state='one')],
            id='has_previous_state',
        ),
    ],
)
async def test_personalstate_write_response(
        taxi_user_state,
        mongodb,
        selected_class,
        selected_class_can_be_default,
        has_previous_state,
):
    json = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'route': [[37.900188446044922, 55.416580200195312]],
        'revision_id': 778,
        'selected_class': selected_class,
        'tariffs': [
            {
                'class': 'econom',
                'requirements': {'nosmoking': True, 'yellowcarnumber': True},
            },
            {'class': 'business', 'requirements': {'yellowcarnumber': True}},
        ],
    }
    response = await taxi_user_state.post(
        'personalstate', json=json, headers={'X-Yandex-UID': DEFAULT_UID},
    )
    response_data = response.json()
    assert response.status_code == 200

    # check that only persistent requirements saved
    state = mongodb.personal_state.find_one()
    econom = list(filter(lambda x: x['class'] == 'econom', state['tariffs']))[
        0
    ]
    assert econom['requirements'] == {'nosmoking': True}

    if selected_class_can_be_default:
        assert response_data['selected_class'] == selected_class
        assert state['selected_class'] == selected_class
    else:
        if has_previous_state:
            assert state['selected_class'] == 'econom'
            assert response_data['selected_class'] == 'econom'
        else:
            assert econom['requirements'] == {'nosmoking': True}
            assert 'selected_class' not in response_data
            assert 'selected_class' not in state


@pytest.mark.config(
    TVM_ENABLED=False, PERSONAL_STATE_BRANDS_STORED_AS_NULL_USERSTATE=[''],
)
@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
async def test_personalstate_write_bad_requirements(taxi_user_state):
    json = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'route': [[37.900188446044922, 55.416580200195312]],
        'revision_id': 778,
        'selected_class': 'econom',
        'tariffs': [{'class': 'econom', 'requirements': {'nosmoking': None}}],
    }
    response = await taxi_user_state.post(
        'personalstate', json=json, headers={'X-Yandex-UID': DEFAULT_UID},
    )
    assert response.status_code == 400


@pytest.mark.config(
    PERSONAL_STATE_BRANDS_STORED_AS_NULL_USERSTATE=[''], TVM_ENABLED=False,
)
@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
async def test_personalstate_write_response_only_requirements(taxi_user_state):
    json = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'route': [[37.900188446044922, 55.416580200195312]],
        'revision_id': 24,
        'selected_class': 'business',
        'requirements': {'conditioner': True},
        'comment': 'child chair please',
    }
    response = await taxi_user_state.post(
        'personalstate', json=json, headers={'X-Yandex-UID': DEFAULT_UID},
    )
    assert response.status_code == 200


@pytest.mark.config(PERSONAL_STATE_BRANDS_STORED_AS_NULL_USERSTATE=[''])
@pytest.mark.config(TVM_ENABLED=False)
@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.filldb(personal_state='one')
async def test_personalstate_write_response_bad_revision(taxi_user_state):
    json = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'route': [[37.900188446044922, 55.416580200195312]],
        'revision_id': 24,
        'selected_class': 'econom',
        'tariffs': [
            {
                'class': 'econom',
                'requirements': {'nosmoking': True, 'yellowcarnubmer': 7},
            },
        ],
        'comment': 'child chair please',
    }

    response = await taxi_user_state.post(
        'personalstate', json=json, headers={'X-Yandex-UID': DEFAULT_UID},
    )
    assert response.status_code == 409


@pytest.mark.config(PERSONAL_STATE_BRANDS_STORED_AS_NULL_USERSTATE=[''])
@pytest.mark.config(TVM_ENABLED=False)
@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.parametrize(
    'input_json,expected_json',
    [
        ('request/two_verticals.json', 'response/two_verticals.json'),
        ('request/big.json', 'response/big.json'),
    ],
)
async def test_personalstate_check_response_succeeded(
        taxi_user_state, load_json, input_json, expected_json,
):
    json = load_json(input_json)

    response = await taxi_user_state.post(
        'personalstate', json=json, headers={'X-Yandex-UID': DEFAULT_UID},
    )

    assert response.status_code == 200
    response_json = response.json()
    assert response_json == load_json(expected_json)


@pytest.mark.config(PERSONAL_STATE_BRANDS_STORED_AS_NULL_USERSTATE=[''])
@pytest.mark.config(TVM_ENABLED=False)
@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.filldb(personal_state='one')
async def test_personalstate_get_response(taxi_user_state):
    json = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'route': [[37.900188446044922, 55.416580200195312]],
    }
    response = await taxi_user_state.post(
        'personalstate', json=json, headers={'X-Yandex-UID': DEFAULT_UID},
    )

    response_json = response.json()

    assert response.status_code == 200
    assert response_json['revision_id'] == 777
    assert response_json['selected_class'] == 'econom'
    assert len(response_json['requirements']) == 2
    assert response_json['requirements']['yellowcarnumber'] is True
    assert len(response_json['tariffs']) == 2


@pytest.mark.config(PERSONAL_STATE_BRANDS_STORED_AS_NULL_USERSTATE=[''])
@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.config(TVM_ENABLED=False)
@pytest.mark.filldb(personal_state='multiclass')
async def test_personalstate_multiclass_get(taxi_user_state):
    json = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'route': [[37.900188446044922, 55.416580200195312]],
    }
    response = await taxi_user_state.post(
        'personalstate', json=json, headers={'X-Yandex-UID': DEFAULT_UID},
    )

    response_json = response.json()
    assert response.status_code == 200
    assert response_json == {
        'multiclass_options': {
            'class': ['econom', 'comfortplus'],
            'selected': False,
        },
        'requirements': {'nosmoking': True, 'yellowcarnumber': True},
        'revision_id': 777,
        'selected_class': 'econom',
        'tariffs': [
            {
                'class': 'business',
                'payments_methods_extra': [],
                'requirements': {'childchair': 1},
            },
            {
                'class': 'econom',
                'payments_methods_extra': [],
                'requirements': {'nosmoking': True, 'yellowcarnumber': True},
            },
        ],
    }


@pytest.mark.config(PERSONAL_STATE_BRANDS_STORED_AS_NULL_USERSTATE=[''])
@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.config(TVM_ENABLED=False)
@pytest.mark.filldb(personal_state='multiclass')
async def test_personalstate_multiclass_post(taxi_user_state, mongodb):
    json = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'route': [[37.900188446044922, 55.416580200195312]],
        'revision_id': 778,
        'multiclass_options': {
            'class': ['comfortplus'],
            'selected': True,
            'selected_vertical_id': 'ultima',
        },
    }
    response = await taxi_user_state.post(
        'personalstate', json=json, headers={'X-Yandex-UID': DEFAULT_UID},
    )
    assert response.status_code == 200

    # check that only persistent requirements saved
    state = mongodb.personal_state.find_one()
    state.pop('_id')
    state.pop('updated')

    assert state == {
        'brand': None,
        'multiclass_options': {
            'class': ['comfortplus'],
            'selected': True,
            'selected_vertical_id': 'ultima',
        },
        'nearest_zone': 'moscow',
        'revision_id': 778,
        'selected_class': 'econom',
        'selected_vertical': None,
        'tariffs': [],
        'yandex_uid': DEFAULT_UID,
    }

    json = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'route': [[37.900188446044922, 55.416580200195312]],
    }
    response = await taxi_user_state.post(
        'personalstate', json=json, headers={'X-Yandex-UID': DEFAULT_UID},
    )

    response_json = response.json()
    assert response.status_code == 200
    assert response_json == {
        'multiclass_options': {
            'class': ['comfortplus'],
            'selected': True,
            'selected_vertical_id': 'ultima',
        },
        'revision_id': 778,
        'requirements': {},
        'selected_class': 'econom',
        'tariffs': [],
    }


@pytest.mark.config(PERSONAL_STATE_BRANDS_STORED_AS_NULL_USERSTATE=[''])
@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.config(TVM_ENABLED=False)
@pytest.mark.filldb(personal_state='multiclass')
@pytest.mark.parametrize(
    'exp_enabled',
    [
        pytest.param(
            True,
            marks=pytest.mark.experiments3(
                filename='exp3/android_fix_exp.json',
            ),
        ),
        pytest.param(False, marks=()),
    ],
)
async def test_personalstate_multiclass_android_fix(
        taxi_user_state, exp_enabled,
):
    json = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'route': [[37.900188446044922, 55.416580200195312]],
        'revision_id': 1,
        'multiclass_options': {'class': ['comfortplus'], 'selected': True},
    }
    response = await taxi_user_state.post(
        'personalstate', json=json, headers={'X-Yandex-UID': 'any_uid'},
    )
    assert response.status_code == 200
    response_json = response.json()
    if exp_enabled:
        assert response_json == {
            'multiclass_options': {'class': ['comfortplus'], 'selected': True},
            'revision_id': 1,
            'requirements': {},
            'selected_class': 'demostand',
        }
    else:
        assert response_json == {
            'multiclass_options': {'class': ['comfortplus'], 'selected': True},
            'revision_id': 1,
        }


def assert_state(
        cur_state,
        exp_selected_class,
        exp_selected_vertical,
        exp_selected_options_in_verticals,
):
    assert cur_state['selected_class'] == exp_selected_class
    assert cur_state.get('selected_vertical') == exp_selected_vertical
    if exp_selected_options_in_verticals:
        assert (
            cur_state['selected_options_in_verticals']
            == exp_selected_options_in_verticals
        )


@pytest.mark.config(PERSONAL_STATE_BRANDS_STORED_AS_NULL_USERSTATE=[''])
@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.config(TVM_ENABLED=False)
@pytest.mark.parametrize(
    'selected_class,selected_vertical,selected_options_in_verticals',
    [
        ('business', 'black', None),
        ('econom', 'some_vert', {'black': {'selected_class': 'business'}}),
        ('econom', 'some_vert', {'black': {'selected_class': 'business'}}),
        (
            'econom',
            None,
            {
                '': {
                    'selected_class': 'business',
                    'multiclass_options': {'selected': False, 'class': []},
                },
            },
        ),
    ],
)
@pytest.mark.filldb(personal_state='multiclass')
async def test_personalstate_update_verticals(
        taxi_user_state,
        mongodb,
        selected_class,
        selected_vertical,
        selected_options_in_verticals,
):
    json = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'route': [[37.900188446044922, 55.416580200195312]],
        'revision_id': 778,
        'selected_class': selected_class,
    }
    if selected_vertical:
        json['selected_vertical'] = selected_vertical
    if selected_options_in_verticals:
        json['selected_options_in_verticals'] = selected_options_in_verticals
    response = await taxi_user_state.post(
        'personalstate', json=json, headers={'X-Yandex-UID': DEFAULT_UID},
    )
    assert response.status_code == 200

    # check that only persistent requirements saved
    state = mongodb.personal_state.find_one()

    db_options = (
        selected_options_in_verticals.copy()
        if selected_options_in_verticals
        else None
    )
    if selected_vertical is None and db_options:
        db_options['null_vertical'] = db_options.pop('')
        db_options['null_vertical']['multiclass_options'] = None

    assert_state(state, selected_class, selected_vertical, db_options)

    json = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'route': [[37.900188446044922, 55.416580200195312]],
    }
    response = await taxi_user_state.post(
        'personalstate', json=json, headers={'X-Yandex-UID': DEFAULT_UID},
    )
    assert response.status_code == 200
    if selected_vertical is None:
        del selected_options_in_verticals['']['multiclass_options']
    assert_state(
        response.json(),
        selected_class,
        selected_vertical,
        selected_options_in_verticals,
    )


@pytest.mark.config(TVM_ENABLED=False)
@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
async def test_personalstate_categories_changed_by_visibility_helper(
        taxi_user_state, mongodb,
):
    not_visible_category = 'uberblack'
    json = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'route': [[37.900188446044922, 55.416580200195312]],
        'revision_id': 24,
        'selected_class': 'business',
        'tariffs': [
            {
                'class': not_visible_category,
                'requirements': {'nosmoking': True, 'yellowcarnumber': True},
            },
            {'class': 'business', 'requirements': {'yellowcarnumber': True}},
        ],
    }
    response = await taxi_user_state.post(
        'personalstate', json=json, headers={'X-Yandex-UID': DEFAULT_UID},
    )
    assert response.status_code == 200

    state = mongodb.personal_state.find_one()
    found = False
    for x in state['tariffs']:
        if x['class'] == not_visible_category:
            found = True
            break

    assert found is False


# https://st.yandex-team.ru/TAXIBACKEND-32774
@pytest.mark.config(PERSONAL_STATE_BRANDS_STORED_AS_NULL_USERSTATE=[''])
@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.config(TVM_ENABLED=False)
@pytest.mark.filldb(personal_state='multiclass')
async def test_personalstate_update_verticals_remove_selected(
        taxi_user_state, mongodb,
):
    json = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'route': [[37.900188446044922, 55.416580200195312]],
        'revision_id': 779,
        'selected_class': 'business',
        'selected_vertical': 'ultima',
    }
    response = await taxi_user_state.post(
        'personalstate', json=json, headers={'X-Yandex-UID': DEFAULT_UID},
    )
    assert response.status_code == 200

    state = mongodb.personal_state.find_one()
    assert state['selected_class'] == 'business'
    assert state['selected_vertical'] == 'ultima'

    json = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'route': [[37.900188446044922, 55.416580200195312]],
        'revision_id': 780,
        'selected_class': 'econom',
    }
    response = await taxi_user_state.post(
        'personalstate', json=json, headers={'X-Yandex-UID': DEFAULT_UID},
    )
    assert response.status_code == 200

    state = mongodb.personal_state.find_one()
    assert state['selected_class'] == 'econom'
    assert state['selected_vertical'] is None

    json = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'route': [[37.900188446044922, 55.416580200195312]],
    }
    response = await taxi_user_state.post(
        'personalstate', json=json, headers={'X-Yandex-UID': DEFAULT_UID},
    )
    assert response.status_code == 200
    response_json = response.json()

    assert response_json['selected_class'] == 'econom'
    assert 'selected_vertical' not in response_json


@pytest.mark.config(PERSONAL_STATE_BRANDS_STORED_AS_NULL_USERSTATE=[''])
@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.config(TVM_ENABLED=False)
@pytest.mark.filldb(personal_state='multiclass')
async def test_personalstate_for_not_can_be_default_tariff(
        taxi_user_state, mongodb,
):
    json = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'route': [[37.900188446044922, 55.416580200195312]],
        'revision_id': 779,
        'selected_class': 'business',
        'selected_vertical': 'ultima',
    }
    response = await taxi_user_state.post(
        'personalstate', json=json, headers={'X-Yandex-UID': DEFAULT_UID},
    )
    assert response.status_code == 200

    response_json = response.json()
    state = mongodb.personal_state.find_one()
    assert state['selected_class'] == 'business'
    assert state['selected_vertical'] == 'ultima'
    assert response_json['selected_class'] == 'business'
    assert response_json['selected_vertical'] == 'ultima'

    json = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'route': [[37.900188446044922, 55.416580200195312]],
        'revision_id': 780,
        'selected_class': 'minivan',
        'selected_vertical': 'taxi',
    }
    response = await taxi_user_state.post(
        'personalstate', json=json, headers={'X-Yandex-UID': DEFAULT_UID},
    )
    assert response.status_code == 200

    response_json = response.json()
    state = mongodb.personal_state.find_one()
    assert state['selected_class'] == 'business'
    assert state['selected_vertical'] == 'ultima'
    assert response_json['selected_class'] == 'business'
    assert response_json['selected_vertical'] == 'ultima'

    json = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'route': [[37.900188446044922, 55.416580200195312]],
        'revision_id': 781,
        'selected_class': 'econom',
    }
    response = await taxi_user_state.post(
        'personalstate', json=json, headers={'X-Yandex-UID': DEFAULT_UID},
    )
    assert response.status_code == 200

    response_json = response.json()
    state = mongodb.personal_state.find_one()
    assert state['selected_class'] == 'econom'
    assert state['selected_vertical'] is None
    assert response_json['selected_class'] == 'econom'
    assert 'selected_vertical' not in response_json
