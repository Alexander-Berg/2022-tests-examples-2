import pytest


@pytest.mark.pgsql('biometry_etalons', files=['test_data.sql'])
@pytest.mark.parametrize(
    'profile, media_ids, expected_code',
    [
        ({'in_media_id': 'x', 'id': 'xxx_yyy'}, ['1'], 200),
        ({'in_media_id': 'y', 'id': 'www_yyy'}, ['3'], 200),
        ({'in_media_id': 'x', 'id': 'xxx_yyy'}, ['1', '2'], 200),
    ],
)
async def test_internal_v1_profile_split_photo_transition(
        taxi_biometry_etalons, pgsql, profile, media_ids, expected_code,
):
    def _count_media_and_features(profile):
        return (
            'WITH inner_id AS ('
            'SELECT id FROM biometry_etalons.profiles p '
            f'WHERE profile_id = \'{profile["id"]}\' '
            'AND provider = \'signalq\' '
            'AND meta->>\'park_id\' = \'p1\') '
            'SELECT COUNT(*) '
            'FROM inner_id, biometry_etalons.media m '
            'INNER JOIN biometry_etalons.face_features f ON '
            'f.media_id = m.id '
            f'WHERE profile_id = inner_id.id'
        )

    cursor = pgsql['biometry_etalons'].cursor()

    cursor.execute(_count_media_and_features(profile))
    media_amount = cursor.fetchone()[0]

    response = await taxi_biometry_etalons.post(
        '/internal/biometry-etalons/v1/profile/split',
        headers={'X-Idempotency-Token': 'someCorrectToken'},
        json={
            'provider': 'signalq',
            'profile_id': profile['id'],
            'media_ids': media_ids,
            'new_profile_meta': {'park_id': 'p1'},
        },
    )

    assert response.status_code == expected_code, response.text

    if response.status_code != 200:
        return

    cursor.execute(_count_media_and_features(profile))
    assert cursor.fetchone()[0] == media_amount - len(media_ids)

    cursor.execute(_count_media_and_features(response.json()['profile']))
    assert cursor.fetchone()[0] == len(media_ids)


@pytest.mark.pgsql('biometry_etalons', files=['test_data.sql'])
@pytest.mark.parametrize(
    'profile, media_ids, expected_code, '
    'profile_expected_mean, profile_expected_total, split_expected_mean',
    [
        pytest.param(
            {'id': 'www_yyy', 'etalon_id': 'e1'},
            ['3'],
            200,
            None,
            None,
            [11.0, 2.0, 4.0, 0.0],
            id='One media in profile transition',
        ),
        pytest.param(
            {'id': 'xxx_yyy', 'etalon_id': 'e2'},
            ['1'],
            200,
            [2.0, 2.0, 3.0, 3.0],
            2,
            [1.0, 2.0, 4.0, 4.0],
            id='One media when many in profile transition',
        ),
        pytest.param(
            {'id': 'xxx_yyy', 'etalon_id': 'e2'},
            ['1', '2'],
            200,
            [1.0, 2.0, 2.0, 4.0],
            1,
            [2.0, 2.0, 4.0, 3.0],
            id='Two media transition',
        ),
    ],
)
async def test_internal_v1_profile_split_mean_features(
        taxi_biometry_etalons,
        pgsql,
        profile,
        media_ids,
        expected_code,
        profile_expected_mean,
        profile_expected_total,
        split_expected_mean,
):
    def _get_mean_features_and_total(etalon_id):
        return (
            'SELECT f.features, '
            'e.total_face_features_by_biometrics_features_v1 '
            'FROM biometry_etalons.face_features f '
            'INNER JOIN biometry_etalons.etalons e ON '
            'e.id = f.etalon_id '
            'WHERE f.media_id IS NULL '
            'AND f.deleted IS FALSE '
            f'AND f.etalon_id = \'{etalon_id}\''
        )

    def _get_etalon_id(profile):
        return (
            'SELECT etalon_id '
            'FROM biometry_etalons.profiles '
            f'WHERE profile_id = \'{profile["id"]}\' '
            'AND provider = \'signalq\' '
        )

    response = await taxi_biometry_etalons.post(
        '/internal/biometry-etalons/v1/profile/split',
        headers={'X-Idempotency-Token': 'someCorrectToken'},
        json={
            'provider': 'signalq',
            'profile_id': profile['id'],
            'media_ids': media_ids,
        },
    )

    assert response.status_code == expected_code, response.text

    if expected_code != 200:
        return

    cursor = pgsql['biometry_etalons'].cursor()

    cursor.execute(_get_mean_features_and_total(profile['etalon_id']))
    if profile_expected_mean:
        assert cursor.fetchone() == (
            profile_expected_mean,
            profile_expected_total,
        )
    else:
        assert cursor.fetchone() is None

    cursor.execute(_get_etalon_id(response.json()['profile']))
    etalon_id = cursor.fetchone()[0]
    cursor.execute(_get_mean_features_and_total(etalon_id))
    assert cursor.fetchone() == (split_expected_mean, len(media_ids))


@pytest.mark.pgsql('biometry_etalons', files=['test_data.sql'])
@pytest.mark.parametrize(
    'profile, media_ids, expected_code',
    [({'id': 'xxx_yyy'}, ['1', '3'], 404), ({'id': 'no_such_id'}, ['1'], 404)],
)
async def test_internal_v1_profiles_split_wrong_photo_or_profile(
        taxi_biometry_etalons, pgsql, profile, media_ids, expected_code,
):
    response = await taxi_biometry_etalons.post(
        '/internal/biometry-etalons/v1/profile/split',
        headers={'X-Idempotency-Token': 'someCorrectToken'},
        json={
            'provider': 'signalq',
            'profile_id': profile['id'],
            'media_ids': media_ids,
        },
    )

    assert response.status_code == expected_code, response.text


@pytest.mark.pgsql('biometry_etalons', files=['test_data.sql'])
@pytest.mark.parametrize(
    'profile, media_ids, expected_code',
    [({'id': 'www_yyy', 'etalon_id': 'e1'}, ['3'], 200)],
)
async def test_internal_v1_profiles_split_existing_idemp_violation(
        taxi_biometry_etalons, pgsql, profile, media_ids, expected_code,
):
    response = await taxi_biometry_etalons.post(
        '/internal/biometry-etalons/v1/profile/split',
        headers={'X-Idempotency-Token': 'unique_token_2'},
        json={
            'provider': 'signalq',
            'profile_id': profile['id'],
            'media_ids': media_ids,
        },
    )

    assert response.status_code == expected_code, response.text
    assert response.json() == {
        'profile': {'id': 'www_yyy', 'type': 'park_driver_profile_id'},
    }
