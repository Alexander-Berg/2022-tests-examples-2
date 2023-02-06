import pytest


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id, profession)
        VALUES ('passport', 'passport_uid', 'market-courier');
        """,
    ],
)
async def test_post_intro_initial_no_common(
        taxi_selfemployed_fns_profiles, mockserver, prepare_post_rq,
):
    @mockserver.json_handler(
        '/pro-profiles/platform/v1/profiles/drafts/find-by-passport-uid/v1',
    )
    def _find_by_passport(request):
        assert request.json == {'passport_uid': 'passport_uid'}
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

    response = await taxi_selfemployed_fns_profiles.post(
        **prepare_post_rq('intro', 'passport_uid'),
    )

    assert response.status == 200
    content = response.json()
    assert content == {
        'next_step': 'phone-bind',
        'step_count': 9,
        'step_index': 2,
    }


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id, phone_pd_id, profession)
        VALUES ('passport', 'passport_uid', 'PHONE_PD_ID', 'market-courier');
        INSERT INTO se.ownpark_profile_forms_common
            (phone_pd_id, state, external_id)
         VALUES ('PHONE_PD_ID', 'INITIAL', 'external_id');
        """,
    ],
)
async def test_post_intro_initial(
        taxi_selfemployed_fns_profiles, mockserver, prepare_post_rq,
):
    @mockserver.json_handler(
        '/pro-profiles/platform/v1/profiles/drafts/find-by-passport-uid/v1',
    )
    def _find_by_passport(request):
        assert request.json == {'passport_uid': 'passport_uid'}
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

    response = await taxi_selfemployed_fns_profiles.post(
        **prepare_post_rq('intro', 'passport_uid'),
    )

    assert response.status == 200
    content = response.json()
    assert content == {
        'next_step': 'phone-bind',
        'step_count': 9,
        'step_index': 2,
    }


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id, phone_pd_id, profession)
        VALUES ('passport', 'passport_uid', 'PHONE_PD_ID', 'market-courier');
        INSERT INTO se.ownpark_profile_forms_common
            (phone_pd_id, state, external_id)
         VALUES ('PHONE_PD_ID', 'FILLING', 'external_id');
        """,
    ],
)
async def test_post_intro_filling(
        taxi_selfemployed_fns_profiles, mockserver, prepare_post_rq,
):
    @mockserver.json_handler(
        '/pro-profiles/platform/v1/profiles/drafts/find-by-passport-uid/v1',
    )
    def _find_by_passport(request):
        assert request.json == {'passport_uid': 'passport_uid'}
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

    response = await taxi_selfemployed_fns_profiles.post(
        **prepare_post_rq('intro', 'passport_uid'),
    )

    assert response.status == 200
    content = response.json()
    assert content == {
        'next_step': 'agreement',
        'step_count': 9,
        'step_index': 5,
    }


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id, phone_pd_id, profession)
        VALUES ('passport', 'passport_uid', 'PHONE_PD_ID', 'market-courier');
        INSERT INTO se.ownpark_profile_forms_common
            (phone_pd_id, state, external_id)
         VALUES ('PHONE_PD_ID', 'FILLED', 'external_id');
        """,
    ],
)
async def test_post_intro_filled(
        taxi_selfemployed_fns_profiles, mockserver, prepare_post_rq,
):
    @mockserver.json_handler(
        '/pro-profiles/platform/v1/profiles/drafts/find-by-passport-uid/v1',
    )
    def _find_by_passport(request):
        assert request.json == {'passport_uid': 'passport_uid'}
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

    response = await taxi_selfemployed_fns_profiles.post(
        **prepare_post_rq('intro', 'passport_uid'),
    )

    assert response.status == 200
    content = response.json()
    assert content == {
        'next_step': 'await-park-created',
        'step_count': 9,
        'step_index': 7,
    }


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id, phone_pd_id, profession)
        VALUES ('passport', 'passport_uid', 'PHONE_PD_ID', 'market-courier');
        INSERT INTO se.ownpark_profile_forms_common
            (phone_pd_id, state, external_id)
         VALUES ('PHONE_PD_ID', 'FINISHED', 'external_id');
        """,
    ],
)
async def test_post_intro_finished(
        taxi_selfemployed_fns_profiles, mockserver, prepare_post_rq,
):
    @mockserver.json_handler(
        '/pro-profiles/platform/v1/profiles/drafts/find-by-passport-uid/v1',
    )
    def _find_by_passport(request):
        assert request.json == {'passport_uid': 'passport_uid'}
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

    response = await taxi_selfemployed_fns_profiles.post(
        **prepare_post_rq('intro', 'passport_uid'),
    )

    assert response.status == 200
    content = response.json()
    assert content == {
        'next_step': 'requisites',
        'step_count': 9,
        'step_index': 8,
    }
