import pytest


@pytest.mark.pgsql('biometry_etalons', files=['test_data.sql'])
@pytest.mark.parametrize(
    'profile_id, deleted_amount, expected_code',
    [('p1_d1', 1, 200), ('p1_d2', 2, 200), ('p2_d1', 0, 404)],
)
async def test_internal_v1_profile_delete(
        taxi_biometry_etalons,
        pgsql,
        profile_id,
        deleted_amount,
        expected_code,
        mockserver,
):
    def _count_deleted_media():
        return (
            'SELECT COUNT(*) '
            'FROM biometry_etalons.face_features '
            'WHERE deleted '
            '  AND media_id IS NOT NULL'
        )

    response = await taxi_biometry_etalons.delete(
        '/internal/biometry-etalons/v1/profile',
        json={'profile_id': profile_id, 'provider': 'signalq'},
    )

    assert response.status_code == expected_code, response.text

    if response.status_code != 200:
        return

    cursor = pgsql['biometry_etalons'].cursor()

    cursor.execute(_count_deleted_media())
    assert deleted_amount == cursor.fetchone()[0]
