import datetime
import uuid

import pytest

from tests_media_storage import consts


def add_decoded_media(
        pgsql,
        mds_s3,
        avatars,
        type_='identity-card',
        etag=uuid.uuid4().hex,
        decoded_id=uuid.uuid4().hex,
        expired_at=datetime.datetime.utcnow(),
        decoded_type=consts.DecodedType.MEDIA_STORAGE_PUBLIC,
        avatar_id=None,
):
    cursor = pgsql['media_storage'].cursor()
    cursor.execute(
        """
        INSERT INTO media_storage.decoded
          (type, etag, decoded_id, expired_at, decoded_type, avatar_id)
        VALUES
          (%s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        (type_, etag, decoded_id, expired_at, decoded_type, avatar_id),
    )

    if decoded_type == consts.DecodedType.MEDIA_STORAGE_PUBLIC:
        mds_s3.put_object(
            'public', f'{decoded_id}', 'some-value'.encode('utf-8'),
        )
    else:
        avatars.add_media(decoded_id)


@pytest.mark.parametrize(
    'lag, limit, expected',
    [(1, 15, 0), (7, 9, 1), (7, 5, 5), (12, 5, 5), (43, 5, 8), (60, 5, 10)],
)
@pytest.mark.parametrize(
    'decoded_type',
    [
        consts.DecodedType.MEDIA_STORAGE_PUBLIC,
        consts.DecodedType.MEDIA_STORAGE_AVATARS,
    ],
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
        decoded_type,
):
    config = taxi_config.get('MEDIA_STORAGE_CLEAN_SETTINGS')
    config['expired_media_cleaner']['lag'] = lag * 60
    config['expired_media_cleaner']['limit'] = limit
    taxi_config.set_values(dict(MEDIA_STORAGE_CLEAN_SETTINGS=config))

    now = datetime.datetime.utcnow()

    avatar_id = None
    if decoded_type == consts.DecodedType.MEDIA_STORAGE_AVATARS:
        avatar_id = avatars.group_id

    for delta in range(1, 11):
        add_decoded_media(
            pgsql,
            mds_s3,
            avatars,
            decoded_id=str(delta),
            expired_at=now - datetime.timedelta(minutes=5 * delta),
            decoded_type=decoded_type,
            avatar_id=avatar_id,
        )

    if decoded_type == consts.DecodedType.MEDIA_STORAGE_PUBLIC:
        assert mds_s3.delete_object('public', '3')
        assert mds_s3.delete_object('public', '5')

    await taxi_media_storage.run_periodic_task('expired-media-cleaner')

    cursor = pgsql['media_storage'].cursor()
    cursor.execute('SELECT count(*) from media_storage.decoded')
    result = list(row for row in cursor)[0][0]
    assert result == expected

    if decoded_type == consts.DecodedType.MEDIA_STORAGE_PUBLIC:
        if expected >= 5:
            expected -= 2  # deleted: 3, 5
        elif expected >= 3:
            expected -= 1  # deleted: 3

        assert mds_s3.get_size('public') == expected
