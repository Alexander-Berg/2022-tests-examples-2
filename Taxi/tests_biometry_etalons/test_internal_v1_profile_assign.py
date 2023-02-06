import pytest


@pytest.mark.pgsql('biometry_etalons', files=['etalons_face_features.sql'])
@pytest.mark.parametrize(
    'old_profile, new_profile, expected_code',
    [
        (
            {'id': 'xxx_yyy', 'type': 'park_driver_profile_id'},
            {'id': 'zzz_zzz', 'type': 'lol_i_kek'},
            200,
        ),
        (
            {'id': 'xxKEK_yyy', 'type': 'park_driver_profile_id'},
            {'id': 'zzz_zzz', 'type': 'lol_i_kek'},
            400,
        ),
        (
            {'id': 'xxx_yyy', 'type': 'park_driver_profile_id'},
            {'id': 'www_yyy', 'type': 'lol_i_kek'},
            400,
        ),
    ],
)
async def test_internal_v1_profiles_identify(
        taxi_biometry_etalons,
        pgsql,
        mockserver,
        old_profile,
        new_profile,
        expected_code,
):
    def _build_profile_request(profile_id, profile_type):
        return (
            'SELECT 1 '
            'FROM biometry_etalons.profiles '
            f'WHERE profile_id = \'{profile_id}\' AND '
            f'profile_type = \'{profile_type}\' AND '
            f'provider = \'signalq\''
        )

    response = await taxi_biometry_etalons.post(
        '/internal/biometry-etalons/v1/profile/assign',
        json={
            'old_profile': old_profile,
            'new_profile': new_profile,
            'provider': 'signalq',
        },
    )

    assert response.status_code == expected_code

    if expected_code != 200:
        return

    cursor = pgsql['biometry_etalons'].cursor()

    # new profile exists, old does not exist
    cursor.execute(
        _build_profile_request(new_profile['id'], new_profile['type']),
    )
    result = list(row for row in cursor)
    assert len(result) == 1

    cursor.execute(
        _build_profile_request(old_profile['id'], old_profile['type']),
    )
    result = list(row for row in cursor)
    assert result == []

    # successful retry
    response = await taxi_biometry_etalons.post(
        '/internal/biometry-etalons/v1/profile/assign',
        json={
            'old_profile': old_profile,
            'new_profile': new_profile,
            'provider': 'signalq',
        },
    )

    assert response.status_code == expected_code
