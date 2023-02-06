import pytest

FAKE_PHONE = '+70001234567'


def get_form_contractor(cursor, passport_uid):
    cursor.execute(
        """
        SELECT
            phone_pd_id,
            is_phone_verified,
            track_id
        FROM se.ownpark_profile_forms_contractor
        WHERE initial_contractor_id = %(passport_uid)s
        """,
        {'passport_uid': passport_uid},
    )
    return cursor.fetchone()


def get_form_common(cursor, phone_pd_id):
    cursor.execute(
        """
        SELECT state, external_id
        FROM se.ownpark_profile_forms_common
        WHERE phone_pd_id = %(phone_pd_id)s
        """,
        {'phone_pd_id': phone_pd_id},
    )
    return cursor.fetchone()


@pytest.mark.pgsql('selfemployed_main', files=['mock_selfemployed_main.sql'])
@pytest.mark.parametrize(
    'passport_uid, phone_code, code_ok',
    [
        pytest.param('puid1', '0000', True, id='confirm ok'),
        pytest.param('puid1', 'FAIL', False, id='confirm fail'),
    ],
)
async def test_post_phone_confirm(
        taxi_selfemployed_fns_profiles,
        passport_internal_mock,
        personal_mock,
        pgsql,
        prepare_post_rq,
        passport_uid,
        phone_code,
        code_ok,
):
    response = await taxi_selfemployed_fns_profiles.post(
        json={'phone_code': phone_code},
        **prepare_post_rq('phone-confirm', passport_uid),
    )

    if code_ok:
        assert response.status == 200
        content = response.json()
        assert content == {
            'next_step': 'nalog-app',
            'step_count': 9,
            'step_index': 4,
        }

        phone_pd_id, is_phone_verified, track_id = get_form_contractor(
            pgsql['selfemployed_main'].cursor(), passport_uid,
        )
        assert is_phone_verified is True
        assert phone_pd_id == 'PHONE_PD_ID'
        assert track_id is None

        state, external_id = get_form_common(
            pgsql['selfemployed_main'].cursor(), phone_pd_id,
        )
        assert state == 'INITIAL'
        assert external_id is not None
    else:
        assert response.status == 400
        content = response.json()
        assert content == {
            'code': '400',
            'message': 'failed to verify phone code',
        }

        phone_pd_id, is_phone_verified, track_id = get_form_contractor(
            pgsql['selfemployed_main'].cursor(), passport_uid,
        )
        assert is_phone_verified is False
        assert phone_pd_id == 'PHONE_PD_ID'
        assert track_id == 'TRACK_ID'

        form_common = get_form_common(
            pgsql['selfemployed_main'].cursor(), phone_pd_id,
        )
        assert form_common is None

    assert passport_internal_mock.phone_confirm_commit.has_calls


@pytest.mark.config(SE_FNS_PROFILES_ALLOW_FAKE_PHONES=True)
@pytest.mark.pgsql('selfemployed_main', files=['mock_selfemployed_main.sql'])
async def test_post_phone_confirm_fake(
        taxi_selfemployed_fns_profiles, personal_mock, pgsql, prepare_post_rq,
):
    personal_mock.phone = FAKE_PHONE

    response = await taxi_selfemployed_fns_profiles.post(
        json={'phone_code': 'ANYCODE'},
        **prepare_post_rq('phone-confirm', 'puid1'),
    )

    assert response.status == 200
    content = response.json()
    assert content == {
        'next_step': 'nalog-app',
        'step_count': 9,
        'step_index': 4,
    }

    phone_pd_id, is_phone_verified, track_id = get_form_contractor(
        pgsql['selfemployed_main'].cursor(), 'puid1',
    )
    assert is_phone_verified is True
    assert phone_pd_id == 'PHONE_PD_ID'
    assert track_id is None

    state, external_id = get_form_common(
        pgsql['selfemployed_main'].cursor(), phone_pd_id,
    )
    assert state == 'INITIAL'
    assert external_id is not None


@pytest.mark.pgsql('selfemployed_main', files=['mock_selfemployed_main.sql'])
@pytest.mark.parametrize(
    'passport_uid, phone_code, phone_pd_id, expect_status',
    [
        pytest.param('puid2', '0000', None, 500, id='no phone'),
        pytest.param('puid2', None, None, 500, id='resend code: no phone'),
        pytest.param(
            'puid3',
            '0000',
            'PHONE_PD_ID3',
            500,
            id='no track id, prev verified',
        ),
        pytest.param(
            'puid4',
            '0000',
            'PHONE_PD_ID4',
            500,
            id='no track id, prev not verified',
        ),
    ],
)
async def test_post_phone_confirm_errors(
        taxi_selfemployed_fns_profiles,
        personal_mock,
        pgsql,
        prepare_post_rq,
        passport_uid,
        phone_code,
        phone_pd_id,
        expect_status,
):
    personal_mock.phone_pd_id = phone_pd_id

    response = await taxi_selfemployed_fns_profiles.post(
        json={'phone_code': phone_code} if phone_code else {},
        **prepare_post_rq('phone-confirm', passport_uid),
    )

    assert response.status == expect_status

    _, _, track_id = get_form_contractor(
        pgsql['selfemployed_main'].cursor(), passport_uid,
    )
    assert track_id is None


@pytest.mark.pgsql('selfemployed_main', files=['mock_selfemployed_main.sql'])
@pytest.mark.parametrize(
    'passport_uid, prev_phone_pd_id, form_common_exists',
    [
        pytest.param('puid1', 'PHONE_PD_ID', False, id='resend ok'),
        pytest.param(
            'puid3', 'PHONE_PD_ID3', True, id='resend ok, prev verified',
        ),
        pytest.param(
            'puid4', 'PHONE_PD_ID4', False, id='resend ok, prev not verified',
        ),
    ],
)
async def test_post_phone_confirm_resend_code(
        taxi_selfemployed_fns_profiles,
        passport_internal_mock,
        personal_mock,
        pgsql,
        prepare_post_rq,
        passport_uid,
        prev_phone_pd_id,
        form_common_exists,
):
    personal_mock.phone_pd_id = prev_phone_pd_id

    response = await taxi_selfemployed_fns_profiles.post(
        json={}, **prepare_post_rq('phone-confirm', passport_uid),
    )

    assert response.status == 200
    content = response.json()
    assert content == {
        'next_step': 'phone-confirm',
        'step_count': 9,
        'step_index': 3,
    }

    phone_pd_id, is_phone_verified, track_id = get_form_contractor(
        pgsql['selfemployed_main'].cursor(), passport_uid,
    )
    assert is_phone_verified is False
    assert phone_pd_id == prev_phone_pd_id
    assert track_id == 'TRACK_ID'

    form_common = get_form_common(
        pgsql['selfemployed_main'].cursor(), phone_pd_id,
    )
    assert bool(form_common) == form_common_exists

    assert passport_internal_mock.phone_confirm_submit.has_calls
    assert personal_mock.v1_phones_retrieve.has_calls


@pytest.mark.config(SE_FNS_PROFILES_ALLOW_FAKE_PHONES=True)
@pytest.mark.pgsql('selfemployed_main', files=['mock_selfemployed_main.sql'])
async def test_post_phone_confirm_resend_code_fake(
        taxi_selfemployed_fns_profiles, personal_mock, pgsql, prepare_post_rq,
):
    personal_mock.phone = FAKE_PHONE

    response = await taxi_selfemployed_fns_profiles.post(
        json={}, **prepare_post_rq('phone-confirm', 'puid1'),
    )

    assert response.status == 200
    content = response.json()
    assert content == {
        'next_step': 'phone-confirm',
        'step_count': 9,
        'step_index': 3,
    }

    phone_pd_id, is_phone_verified, track_id = get_form_contractor(
        pgsql['selfemployed_main'].cursor(), 'puid1',
    )
    assert is_phone_verified is False
    assert phone_pd_id == 'PHONE_PD_ID'
    assert track_id == 'FAKE_TRACK_ID'

    form_common = get_form_common(
        pgsql['selfemployed_main'].cursor(), phone_pd_id,
    )
    assert form_common is None

    assert personal_mock.v1_phones_retrieve.has_calls


async def test_post_phone_confirm_not_found(
        taxi_selfemployed_fns_profiles, prepare_post_rq,
):
    response = await taxi_selfemployed_fns_profiles.post(
        json={'phone_code': '0000'},
        **prepare_post_rq('phone-confirm', 'puid1'),
    )
    assert response.status == 401
