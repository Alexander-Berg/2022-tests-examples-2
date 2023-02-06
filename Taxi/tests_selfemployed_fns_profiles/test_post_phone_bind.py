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


@pytest.mark.pgsql('selfemployed_main', files=['mock_selfemployed_main.sql'])
@pytest.mark.parametrize(
    'passport_uid',
    [
        pytest.param('puid1', id='no prev phone'),
        pytest.param('puid2', id='same prev phone, but unverified'),
        pytest.param('puid3', id='other prev phone, unverified'),
        pytest.param('puid4', id='other prev phone, verified'),
    ],
)
async def test_post_phone_bind(
        taxi_selfemployed_fns_profiles,
        personal_mock,
        passport_internal_mock,
        pgsql,
        prepare_post_rq,
        passport_uid,
):
    response = await taxi_selfemployed_fns_profiles.post(
        json={'phone_number': personal_mock.phone},
        **prepare_post_rq('phone-bind', passport_uid),
    )

    assert response.status == 200
    content = response.json()
    assert content == {
        'next_step': 'phone-confirm',
        'step_count': 9,
        'step_index': 3,
    }

    cursor = pgsql['selfemployed_main'].cursor()

    phone_pd_id, is_phone_verified, track_id = get_form_contractor(
        cursor, passport_uid,
    )

    assert is_phone_verified is False
    assert phone_pd_id == 'PHONE_PD_ID'
    assert track_id == 'TRACK_ID'

    assert personal_mock.v1_phones_store.has_calls
    assert passport_internal_mock.phone_confirm_submit.has_calls


@pytest.mark.config(SE_FNS_PROFILES_ALLOW_FAKE_PHONES=True)
@pytest.mark.pgsql('selfemployed_main', files=['mock_selfemployed_main.sql'])
async def test_post_phone_bind_fake(
        taxi_selfemployed_fns_profiles, personal_mock, pgsql, prepare_post_rq,
):
    personal_mock.phone = FAKE_PHONE
    response = await taxi_selfemployed_fns_profiles.post(
        json={'phone_number': FAKE_PHONE},
        **prepare_post_rq('phone-bind', 'puid1'),
    )

    assert response.status == 200
    content = response.json()
    assert content == {
        'next_step': 'phone-confirm',
        'step_count': 9,
        'step_index': 3,
    }

    cursor = pgsql['selfemployed_main'].cursor()

    phone_pd_id, is_phone_verified, track_id = get_form_contractor(
        cursor, 'puid1',
    )

    assert is_phone_verified is False
    assert phone_pd_id == 'PHONE_PD_ID'
    assert track_id == 'FAKE_TRACK_ID'

    assert personal_mock.v1_phones_store.has_calls


@pytest.mark.pgsql('selfemployed_main', files=['mock_selfemployed_main.sql'])
async def test_post_phone_bind_same_already_verified(
        taxi_selfemployed_fns_profiles, personal_mock, pgsql, prepare_post_rq,
):
    response = await taxi_selfemployed_fns_profiles.post(
        json={'phone_number': personal_mock.phone},
        **prepare_post_rq('phone-bind', 'puid5'),
    )

    assert response.status == 200
    content = response.json()
    assert content == {
        'next_step': 'nalog-app',
        'step_count': 9,
        'step_index': 4,
    }

    cursor = pgsql['selfemployed_main'].cursor()

    phone_pd_id, is_phone_verified, track_id = get_form_contractor(
        cursor, 'puid5',
    )

    assert is_phone_verified is True
    assert phone_pd_id == 'PHONE_PD_ID'
    assert track_id is None

    assert personal_mock.v1_phones_store.has_calls


async def test_post_phone_bind_not_found(
        taxi_selfemployed_fns_profiles, personal_mock, prepare_post_rq,
):
    response = await taxi_selfemployed_fns_profiles.post(
        json={'phone_number': personal_mock.phone},
        **prepare_post_rq('phone-bind', 'passport_uid'),
    )
    assert response.status == 401
    assert personal_mock.v1_phones_store.has_calls


@pytest.mark.pgsql('selfemployed_main', files=['mock_selfemployed_main.sql'])
@pytest.mark.parametrize(
    'phone_number, expect_status, passport_called',
    [
        pytest.param('+70001234567', 500, False, id='fake phone forbidden'),
        pytest.param('+79991234567', 500, True, id='passport-internal failed'),
    ],
)
async def test_post_phone_bind_errors(
        taxi_selfemployed_fns_profiles,
        mockserver,
        personal_mock,
        prepare_post_rq,
        phone_number,
        expect_status,
        passport_called,
):
    personal_mock.phone = phone_number

    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/submit/',
    )
    async def _phone_confirm_submit(request):
        return mockserver.make_response(status=500)

    response = await taxi_selfemployed_fns_profiles.post(
        json={'phone_number': phone_number},
        **prepare_post_rq('phone-bind', 'puid1'),
    )
    assert response.status == expect_status

    assert _phone_confirm_submit.has_calls == passport_called
