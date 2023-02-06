import pytest


@pytest.mark.pgsql('biometry_etalons', files=['test_data.sql'])
@pytest.mark.parametrize(
    'merge_from_profile, merge_to_profile, expected_code',
    [
        (
            {'in_media_id': 'y', 'id': 'www_yyy'},
            {'in_media_id': 'x', 'id': 'xxx_yyy'},
            200,
        ),
        (
            {'in_media_id': 'x', 'id': 'xxx_yyy'},
            {'in_media_id': 'z', 'id': 'sss_yyy'},
            200,
        ),
        (
            {'in_media_id': 'a', 'id': 'aaa_yyy'},
            {'in_media_id': 'z', 'id': 'sss_yyy'},
            200,
        ),
    ],
)
async def test_internal_v1_profile_force_merge_photo_transition(
        taxi_biometry_etalons,
        pgsql,
        merge_from_profile,
        merge_to_profile,
        expected_code,
):
    def _count_media_and_features(profile_id):
        return (
            'SELECT COUNT(*) '
            'FROM biometry_etalons.media m '
            'INNER JOIN biometry_etalons.face_features f ON '
            'f.media_id = m.id '
            f'WHERE profile_id = \'{profile_id}\''
        )

    cursor = pgsql['biometry_etalons'].cursor()

    cursor.execute(
        _count_media_and_features(merge_from_profile['in_media_id']),
    )
    from_amount_media = cursor.fetchone()[0]

    cursor.execute(_count_media_and_features(merge_to_profile['in_media_id']))
    to_amount_media = cursor.fetchone()[0]

    response = await taxi_biometry_etalons.post(
        '/internal/biometry-etalons/v1/profile/force-merge',
        json={
            'merge_to_profile_id': merge_to_profile['id'],
            'merge_from_profile_id': merge_from_profile['id'],
            'provider': 'signalq',
        },
    )

    assert response.status_code == expected_code, response.text

    if expected_code != 200:
        return

    cursor.execute(_count_media_and_features(merge_to_profile['in_media_id']))
    assert cursor.fetchone()[0] == to_amount_media + from_amount_media


@pytest.mark.pgsql('biometry_etalons', files=['test_data.sql'])
@pytest.mark.parametrize(
    'merge_from_profile, merge_to_profile, expected_code,'
    'from_expected_mean, from_expected_total,'
    'to_expected_mean, to_expected_total',
    [
        (
            {'id': 'www_yyy', 'etalon_id': 'e2'},
            {'id': 'xxx_yyy', 'etalon_id': 'e2'},
            200,
            [2.0, 2.0, 4.0, 3.0],
            2,
            [[2.0, 2.0, 4.0, 3.0]],
            [2],
        ),
        (
            {'id': 'xxx_yyy', 'etalon_id': 'e2'},
            {'id': 'sss_yyy', 'etalon_id': 'e1'},
            200,
            [3.0, 2.0, 4.0, 2.0],
            1,
            [[1.75, 2.0, 3.25, 2.5]],
            [4],
        ),
        (
            {'id': 'sss_yyy', 'etalon_id': 'e1'},
            {'id': 'xxx_yyy', 'etalon_id': 'e2'},
            200,
            None,
            None,
            [[2.0, 2.0, 3.4, 2.4]],
            [5],
        ),
        pytest.param(
            {'id': 'aaa_yyy', 'etalon_id': 'e3'},
            {'id': 'sss_yyy', 'etalon_id': 'e1'},
            200,
            None,
            None,
            [[2.0, 2.0, 3.0, 2.0], [2.0, 3.0, 4.0, 1.0]],
            [3, 1],
            id='profile with one feature handler etalon with another',
        ),
    ],
)
async def test_internal_v1_profile_force_merge_mean_features(
        taxi_biometry_etalons,
        pgsql,
        merge_from_profile,
        merge_to_profile,
        expected_code,
        from_expected_mean,
        from_expected_total,
        to_expected_mean,
        to_expected_total,
):
    def _get_mean_features_and_total(etalon_id):
        return (
            'SELECT f.features, '
            'e.total_face_features_by_biometrics_features_v1, '
            'e.total_face_features_by_cbir '
            'FROM biometry_etalons.face_features f '
            'INNER JOIN biometry_etalons.etalons e ON '
            'e.id = f.etalon_id '
            'WHERE f.media_id IS NULL '
            'AND f.deleted IS FALSE '
            f'AND f.etalon_id = \'{etalon_id}\' '
            'ORDER BY f.features_handler != \'cbir\' DESC'
        )

    response = await taxi_biometry_etalons.post(
        '/internal/biometry-etalons/v1/profile/force-merge',
        json={
            'merge_to_profile_id': merge_to_profile['id'],
            'merge_from_profile_id': merge_from_profile['id'],
            'provider': 'signalq',
        },
    )

    assert response.status_code == expected_code, response.text

    if expected_code != 200:
        return

    cursor = pgsql['biometry_etalons'].cursor()

    cursor.execute(
        _get_mean_features_and_total(merge_from_profile['etalon_id']),
    )
    if from_expected_mean:
        assert cursor.fetchone()[0:2] == (
            from_expected_mean,
            from_expected_total,
        )
    else:
        assert cursor.fetchone() is None

    cursor.execute(_get_mean_features_and_total(merge_to_profile['etalon_id']))
    to_mean, to_total_biometrics, _ = cursor.fetchone()
    assert to_total_biometrics == to_expected_total[0]
    assert [round(val, 2) for val in to_mean] == to_expected_mean[0]

    if len(to_expected_mean) > 1:
        to_mean, _, to_total_cbir = cursor.fetchone()
        assert to_total_cbir == to_expected_total[1]
        assert [round(val, 2) for val in to_mean] == to_expected_mean[1]


@pytest.mark.pgsql('biometry_etalons', files=['test_data.sql'])
@pytest.mark.parametrize(
    'merge_from_profile, merge_to_profile, expected_code,'
    'expected_deleted_features_amount,'
    'expected_profiles_amount',
    [
        ({'id': 'xxx_yyy'}, {'id': 'sss_yyy'}, 200, 0, 3),
        ({'id': 'sss_yyy'}, {'id': 'xxx_yyy'}, 200, 1, 3),
    ],
)
async def test_internal_v1_profile_force_merge_deleted_features_and_profiles(
        taxi_biometry_etalons,
        pgsql,
        merge_from_profile,
        merge_to_profile,
        expected_code,
        expected_deleted_features_amount,
        expected_profiles_amount,
):
    def _get_deleted_features_amount():
        return (
            'SELECT COUNT(*) '
            'FROM biometry_etalons.face_features f '
            'WHERE f.media_id IS NULL '
            'AND f.deleted IS TRUE '
        )

    def _get_profiles_amount():
        return 'SELECT COUNT(*) ' 'FROM biometry_etalons.profiles'

    response = await taxi_biometry_etalons.post(
        '/internal/biometry-etalons/v1/profile/force-merge',
        json={
            'merge_to_profile_id': merge_to_profile['id'],
            'merge_from_profile_id': merge_from_profile['id'],
            'provider': 'signalq',
        },
    )

    assert response.status_code == expected_code, response.text

    if expected_code != 200:
        return

    cursor = pgsql['biometry_etalons'].cursor()

    cursor.execute(_get_deleted_features_amount())
    assert cursor.fetchone()[0] == expected_deleted_features_amount

    cursor.execute(_get_profiles_amount())
    assert cursor.fetchone()[0] == expected_profiles_amount


@pytest.mark.pgsql('biometry_etalons', files=['test_data.sql'])
@pytest.mark.parametrize(
    'merge_from_profile, merge_to_profile, expected_code',
    [({'id': 'x', 'profile_id': 'xxx_yyy'}, {'profile_id': '1'}, 404)],
)
async def test_internal_v1_profile_force_merge_fail(
        taxi_biometry_etalons,
        pgsql,
        merge_from_profile,
        merge_to_profile,
        expected_code,
):
    response = await taxi_biometry_etalons.post(
        '/internal/biometry-etalons/v1/profile/force-merge',
        json={
            'merge_to_profile_id': merge_to_profile['profile_id'],
            'merge_from_profile_id': merge_from_profile['profile_id'],
            'provider': 'signalq',
        },
    )

    assert response.status_code == expected_code, response.text
