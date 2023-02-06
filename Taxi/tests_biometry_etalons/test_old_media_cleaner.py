import pytest


@pytest.mark.pgsql('biometry_etalons', files=['media.sql'])
@pytest.mark.config(
    BIOMETRY_ETALONS_MEDIA_CLEANER_SETTINGS={
        'enabled': True,
        'period_s': 10,
        'limit': 1,
        'lag': 1,
    },
)
async def test_calculation_features(taxi_biometry_etalons, pgsql, mockserver):
    def _count_features():
        cursor = pgsql['biometry_etalons'].cursor()
        cursor.execute(
            'SELECT COUNT(*) ' 'FROM biometry_etalons.face_features ',
        )
        result = list(row for row in cursor)
        cursor.close()

        return int(result[0][0])

    def _count_meta():
        cursor = pgsql['biometry_etalons'].cursor()
        cursor.execute('SELECT COUNT(*)' 'FROM biometry_etalons.media_meta ')
        result = list(row for row in cursor)
        cursor.close()

        return int(result[0][0])

    def _count_media():
        cursor = pgsql['biometry_etalons'].cursor()
        cursor.execute('SELECT COUNT(*)' 'FROM biometry_etalons.media ')
        result = list(row for row in cursor)
        cursor.close()

        return int(result[0][0])

    assert _count_meta() == 3
    assert _count_features() == 3
    assert _count_media() == 5

    await taxi_biometry_etalons.run_periodic_task('old-media-cleaner')

    assert _count_media() == 4
    assert _count_features() == 2

    await taxi_biometry_etalons.run_periodic_task('old-media-cleaner')

    assert _count_meta() == 1
    assert _count_features() == 1
    assert _count_media() == 3
