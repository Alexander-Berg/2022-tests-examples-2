import datetime
import uuid

import pytest

from tests_media_storage import consts


def add_hanged_decoding(
        pgsql,
        type_='identity-card',
        etag=uuid.uuid4().hex,
        decoded_id=uuid.uuid4().hex,
        updated=datetime.datetime.utcnow(),
        decoded_type=consts.DecodedType.MEDIA_STORAGE_PUBLIC,
):
    cursor = pgsql['media_storage'].cursor()
    cursor.execute(
        """
        INSERT INTO media_storage.decoded
          (type, etag, decoded_id, updated, decoded_type)
        VALUES
          (%s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        (type_, etag, decoded_id, updated, decoded_type),
    )

    return decoded_id


@pytest.mark.parametrize(
    'lag, limit, expected',
    [(1, 15, 2), (7, 9, 2), (7, 5, 5), (12, 5, 5), (43, 5, 8), (60, 5, 10)],
)
async def test_periodic_task_new_media(
        taxi_media_storage,
        taxi_config,
        pgsql,
        mds_s3,
        avatars,
        lag,
        limit,
        expected,
):
    config = taxi_config.get('MEDIA_STORAGE_CLEAN_SETTINGS')
    config['hanged_decoding_cleaner']['lag'] = lag * 60
    config['hanged_decoding_cleaner']['limit'] = limit
    taxi_config.set_values(dict(MEDIA_STORAGE_CLEAN_SETTINGS=config))

    now = datetime.datetime.utcnow()

    for delta in range(1, 11):
        # first two deltas is less than 10 minutes, so they couldn't be deleted
        add_hanged_decoding(
            pgsql,
            decoded_id=str(delta),
            updated=now - datetime.timedelta(minutes=5 * delta),
        )

    mds_s3.put_object('public', f'3', 'some-value'.encode('utf-8'))
    mds_s3.put_object('public', f'5', 'some-value'.encode('utf-8'))

    await taxi_media_storage.run_periodic_task('hanged-decoding-cleaner')

    cursor = pgsql['media_storage'].cursor()
    cursor.execute('SELECT decoded_id from media_storage.decoded')
    result = set(row[0] for row in cursor)
    assert len(result) == expected

    mds_size = len(result.intersection({'3', '5'}))
    assert mds_s3.get_size('public') == mds_size
