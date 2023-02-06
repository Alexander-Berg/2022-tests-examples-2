import pytest


@pytest.mark.experiments3(
    name='pro_selfemployed_fns_profiles_screen_requisites',
    consumers=['selfemployed_fns_profiles/state_filled'],
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    default_value={
        'title': 'step_requisites.title',
        'enabled': True,
        'items': [
            {
                'horizontal_divider_type': 'bottom_icon',
                'subtitle': 'step_requisites.header.subtitle',
                'type': 'header',
            },
            {
                'hint': '',
                'id': 'account',
                'input_action': 'next',
                'input_pattern_error': (
                    'step_requisites.edit_text.input_pattern_error'
                ),
                'input_type': 'text',
                'text': '',
                'title': 'step_requisites.edit_text.account.title',
                'type': 'edit_text',
            },
            {
                'hint': '',
                'id': 'bik',
                'input_action': 'next',
                'input_pattern_error': (
                    'step_requisites.edit_text.input_pattern_error'
                ),
                'input_type': 'text',
                'text': '',
                'title': 'step_requisites.edit_text.bik.title',
                'type': 'edit_text',
            },
        ],
        'bottom_items': [
            {
                'accent': True,
                'horizontal_divider_type': 'none',
                'payload': {'type': 'navigate_url'},
                'title': 'default_button.title',
                'type': 'button',
            },
        ],
    },
)
@pytest.mark.pgsql('selfemployed_main', files=['ownpark_metadata.sql'])
async def test_get_requisites(
        taxi_selfemployed_fns_profiles, mockserver, prepare_get_rq,
):
    @mockserver.json_handler(
        '/pro-profiles/platform/v1/profiles/drafts/find-by-passport-uid/v1',
    )
    def _find_by_passport(request):
        assert request.json == {'passport_uid': 'puid1'}
        return {
            'profiles': [
                {
                    'park_id': 'newparkid',
                    'driver_id': 'newcontractorid',
                    'profession': 'Driver',
                    'status': 'ready',
                    'city': 'Москва',
                },
            ],
        }

    @mockserver.json_handler(
        '/pro-profiles/platform/v1/profiles/drafts'
        '/salesforce-selfemployed-requisites/v1',
    )
    async def _get_requisites(request):
        return {
            'status': 'success',
            'requisites': {'type': 'bank', 'account': 'account', 'bik': 'bik'},
        }

    request = prepare_get_rq(step='requisites', passport_uid='puid1')
    response = await taxi_selfemployed_fns_profiles.get(**request)
    assert response.status == 200
    assert response.json() == {
        'prev_step': 'intro',
        'title': 'Реквизиты',
        'items': [
            {
                'horizontal_divider_type': 'bottom_icon',
                'subtitle': 'Подзаголовок очередной кнопки для requisites',
                'type': 'header',
            },
            {
                'id': 'account',
                'text': 'account',
                'title': 'Реквизиты банковского счёта',
                'hint': '',
                'input_type': 'text',
                'input_pattern_error': 'Неправильный формат ввода',
                'input_action': 'next',
                'type': 'edit_text',
            },
            {
                'id': 'bik',
                'text': 'bik',
                'title': 'БИК',
                'hint': '',
                'input_type': 'text',
                'input_pattern_error': 'Неправильный формат ввода',
                'input_action': 'next',
                'type': 'edit_text',
            },
        ],
        'bottom_items': [
            {
                'accent': True,
                'horizontal_divider_type': 'none',
                'payload': {'type': 'navigate_url'},
                'title': 'Далее',
                'type': 'button',
            },
        ],
    }


@pytest.mark.experiments3(
    name='pro_selfemployed_fns_profiles_screen_requisites',
    consumers=['selfemployed_fns_profiles/state_filled'],
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    default_value={
        'title': 'step_requisites.title',
        'enabled': True,
        'items': [
            {
                'horizontal_divider_type': 'bottom_icon',
                'subtitle': 'step_requisites.header.subtitle',
                'type': 'header',
            },
            {
                'hint': '',
                'id': 'account',
                'input_action': 'next',
                'input_pattern_error': (
                    'step_requisites.edit_text.input_pattern_error'
                ),
                'input_type': 'text',
                'text': '',
                'title': 'step_requisites.edit_text.account.title',
                'type': 'edit_text',
            },
            {
                'hint': '',
                'id': 'bik',
                'input_action': 'next',
                'input_pattern_error': (
                    'step_requisites.edit_text.input_pattern_error'
                ),
                'input_type': 'text',
                'text': '',
                'title': 'step_requisites.edit_text.bik.title',
                'type': 'edit_text',
            },
        ],
        'bottom_items': [
            {
                'accent': True,
                'horizontal_divider_type': 'none',
                'payload': {'type': 'navigate_url'},
                'title': 'default_button.title',
                'type': 'button',
            },
        ],
    },
)
@pytest.mark.pgsql('selfemployed_main', files=['ownpark_metadata.sql'])
@pytest.mark.parametrize(
    'status',
    [pytest.param('failed'), pytest.param('error'), pytest.param(None)],
)
async def test_get_requisites_failed(
        taxi_selfemployed_fns_profiles, prepare_get_rq, mockserver, status,
):
    @mockserver.json_handler(
        '/pro-profiles/platform/v1/profiles/drafts/find-by-passport-uid/v1',
    )
    def _find_by_passport(request):
        assert request.json == {'passport_uid': 'puid1'}
        return {
            'profiles': [
                {
                    'park_id': 'newparkid',
                    'driver_id': 'newcontractorid',
                    'profession': 'Driver',
                    'status': 'ready',
                    'city': 'Москва',
                },
            ],
        }

    @mockserver.json_handler(
        '/pro-profiles/platform/v1/profiles/drafts'
        '/salesforce-selfemployed-requisites/v1',
    )
    async def _get_requisites(request):
        if status:
            return {
                'status': status,
                'requisites': {
                    'type': 'bank',
                    'account': 'account',
                    'bik': 'bik',
                },
            }
        return mockserver.make_response(status=500)

    request = prepare_get_rq(step='requisites', passport_uid='puid1')
    response = await taxi_selfemployed_fns_profiles.get(**request)
    assert response.status == 200
    assert response.json()['items'][1]['text'] == ''
    assert response.json()['items'][2]['text'] == ''


@pytest.mark.pgsql('selfemployed_main', files=['ownpark_metadata.sql'])
@pytest.mark.config(
    SELFEMPLOYED_NONRESIDENT_SETTINGS={
        'account_prefix': '40820',
        'disabled_tag_name': 'nonresident_temporary_blocked',
        'eligible_banks': [{'bik': '040000000'}],
        'is_enabled': True,
        'use_stq': False,
    },
    SELFEMPLOYED_REQUISITES_SETTINGS={
        'bank': {
            'sf_subject': 'Self-Employed Change Payment Details',
            'resident_account_prefixes': ['40817'],
            'bik_prefixes': ['04'],
        },
        'sbp': {  # not used
            'sf_subject': 'Self-Employed FPS Change Payment Details',
            'banks': [{'id': 'test_bank', 'name': 'sbp_bank_name.test_bank'}],
        },
    },
)
@pytest.mark.parametrize(
    'requisites,expected_code,expected_json',
    [
        # Regular bank account
        pytest.param(
            {
                'type': 'bank',
                'account': '40817312312312312312',
                'bik': '043123123',
            },
            200,
            {'next_step': 'finish', 'step_count': 11, 'step_index': 13},
        ),
        # Nonresident bank account
        pytest.param(
            {
                'type': 'bank',
                'account': '40820312312312312312',
                'bik': '040000000',
            },
            200,
            {'next_step': 'finish', 'step_count': 11, 'step_index': 13},
        ),
        # must be len(bik) == 9
        pytest.param(
            {'account': '40817312312312312312', 'bik': '1231'},
            409,
            {'code': 'BIK_VALIDATION_ERROR', 'message': 'Неверный формат БИК'},
        ),
        # invalid bik prefix
        pytest.param(
            {'account': '40817312312312312312', 'bik': '123123123'},
            409,
            {'code': 'BIK_VALIDATION_ERROR', 'message': 'Неверный формат БИК'},
        ),
        # must be len(account) == 20
        pytest.param(
            {'account': '1231', 'bik': '043123123'},
            409,
            {
                'code': 'ACCOUNT_VALIDATION_ERROR',
                'message': 'Неверный формат банковского аккаунта',
            },
        ),
        # not eligible nonresident bank
        pytest.param(
            {'account': '40820312312312312312', 'bik': '043123123'},
            409,
            {
                'code': 'NONRESIDENT_BANK_INELIGIBLE',
                'message': 'Данный банк не разрешен для нерезидентов',
            },
        ),
    ],
)
async def test_post_requisites(
        taxi_selfemployed_fns_profiles,
        mockserver,
        pgsql,
        requisites,
        expected_code,
        expected_json,
        prepare_post_rq,
):
    @mockserver.json_handler(
        '/pro-profiles/platform/v1/profiles/drafts'
        '/salesforce-selfemployed-requisites/v1',
    )
    async def _set_requisites(request):
        return {'sf_requisites_case_id': 'case_id'}

    request = prepare_post_rq(step='requisites', passport_uid='puid1')
    response = await taxi_selfemployed_fns_profiles.post(
        json=requisites, **request,
    )
    assert response.status == expected_code
    assert response.json() == expected_json

    sql = """
        SELECT salesforce_requisites_case_id
        FROM se.finished_ownpark_profile_metadata
        WHERE created_park_id = 'newparkid'
        AND created_contractor_id = 'newcontractorid'
    """

    cursor = pgsql['selfemployed_main'].cursor()
    cursor.execute(sql)
    row = cursor.fetchone()
    if expected_code == 200:
        assert row == ('case_id',)
    else:
        assert row == ('salesforce_requisites_case_id',)  # old case id


@pytest.mark.pgsql('selfemployed_main', files=['ownpark_metadata.sql'])
async def test_requisites_skip(
        taxi_selfemployed_fns_profiles, prepare_post_rq,
):
    request = prepare_post_rq(step='requisites', passport_uid='puid1')
    response = await taxi_selfemployed_fns_profiles.post(json={}, **request)
    assert response.status == 200
    assert response.json() == {
        'next_step': 'finish',
        'step_count': 11,
        'step_index': 13,
    }
