import datetime
from urllib import parse
import uuid

import dateutil
import pytest
import pytz

# Feel free to provide your custom implementation to override generated tests.

# pylint: disable=import-error,wildcard-import
from media_storage_plugins.generated_tests import *  # noqa


def parse_presigned_url(url):
    parsed = parse.urlparse(url)
    parts = parsed.path.split('/')
    bucket = parts[2]
    path = '/'.join(parts[3:])

    args = {
        x.split('=', 1)[0]: x.split('=', 1)[1] for x in parsed.query.split('&')
    }

    return (
        bucket,
        path,
        datetime.datetime.fromtimestamp(int(args['Expires']), tz=pytz.utc),
    )


@pytest.mark.now('2021-01-01T12:00:00')
@pytest.mark.servicetest
async def test_main_flow(
        taxi_media_storage, load_binary, pgsql, mds_s3, mocked_time, avatars,
):
    def delete_decoded_meta(etag):
        cursor = pgsql['media_storage'].cursor()
        cursor.execute(
            f'DELETE FROM media_storage.decoded WHERE etag = \'{etag}\'',
        )
        cursor.close()

    headers = {
        'X-Idempotency-Token': uuid.uuid4().hex,
        'Content-Type': 'image/jpeg',
    }
    image = load_binary('test_image.jpg')

    # Store new image
    response = await taxi_media_storage.post(
        'service/identity-card/v1/store',
        headers=headers,
        params=dict(source='test'),
        data=image,
    )

    store_data = response.json()
    assert response.status_code == 200

    # Send request again using the same idempotency token
    # Check if response contains the same media id
    response = await taxi_media_storage.post(
        'service/identity-card/v1/store',
        headers=headers,
        params=dict(source='test'),
        data=image,
    )

    assert response.status_code == 200
    assert response.json() == store_data

    # Store mp3 in order to check in service/identity-card/v1/avatars
    # that content type is image
    audio_headers = {
        'X-Idempotency-Token': uuid.uuid4().hex,
        'Content-Type': 'audio/aac',
    }
    audio_file = load_binary('test_audio.mp3')

    response = await taxi_media_storage.post(
        'service/identity-card/v1/store',
        headers=audio_headers,
        params=dict(source='test'),
        data=audio_file,
    )

    assert response.status_code == 200
    audio_store_data = response.json()

    headers['Content-Type'] = 'application/json'

    expired_at = mocked_time.now() + datetime.timedelta(minutes=20, seconds=-1)
    expired_at = pytz.utc.localize(expired_at)

    # Retrieve data without descryption.
    # Raw data stored to public mds by /store handler
    response = await taxi_media_storage.post(
        'service/identity-card/v1/retrieve',
        params=dict(source='test', id=store_data['id'], ttl=20),
        headers=headers,
    )

    assert response.status_code == 200

    retrieve_data = response.json()
    bucket, path, expires = parse_presigned_url(retrieve_data['url'])
    assert mds_s3.get_object(bucket, path) == image

    retrieve_expired_at = dateutil.parser.parse(retrieve_data['expired_at'])
    assert retrieve_expired_at <= expires
    assert expired_at < retrieve_expired_at

    assert retrieve_data['version'] == store_data['version']

    # Put image to avatars
    response = await taxi_media_storage.post(
        'service/identity-card/v1/avatars',
        params=dict(source='test', id=store_data['id'], ttl=20),
        headers=headers,
    )

    assert response.status_code == 200

    retrieve_data = response.json()

    retrieve_expired_at = dateutil.parser.parse(retrieve_data['expired_at'])
    assert retrieve_expired_at <= expires
    assert expired_at < retrieve_expired_at

    assert retrieve_data['version'] == store_data['version']

    response = await taxi_media_storage.post(
        'service/identity-card/v1/avatars',
        params=dict(source='test', id=audio_store_data['id'], ttl=20),
        headers=headers,
    )

    assert response.status_code == 400

    # Remove information about decryption from postgres
    delete_decoded_meta(retrieve_data['version'])

    # Retrieve data again with decryption
    response = await taxi_media_storage.post(
        'service/identity-card/v1/retrieve',
        params=dict(source='test', id=store_data['id'], ttl=20),
        headers=headers,
    )

    retrieve_data = response.json()
    bucket, new_path, expires = parse_presigned_url(retrieve_data['url'])
    assert new_path != path
    assert mds_s3.get_object(bucket, new_path) == image

    retrieve_expired_at = dateutil.parser.parse(retrieve_data['expired_at'])
    assert retrieve_expired_at <= expires
    assert expired_at < retrieve_expired_at

    assert retrieve_data['version'] == store_data['version']


@pytest.mark.servicetest
async def test_audio_flow_with_deletion(
        taxi_media_storage, load_binary, mockserver, pgsql, mds_s3, avatars,
):
    audio = load_binary('test_audio.mp3')
    headers = {
        'X-Idempotency-Token': uuid.uuid4().hex,
        'Content-Type': 'audio/aac',
    }

    # Store new audio
    response = await taxi_media_storage.post(
        'service/sos-audio/v1/store',
        headers=headers,
        params=dict(source='test'),
        data=audio,
    )

    store_data = response.json()
    assert response.status_code == 200

    # Delete new audio
    response = await taxi_media_storage.delete(
        'service/sos-audio/v1/delete',
        headers=headers,
        params=dict(source='test', id=store_data['id']),
    )
    assert response.status_code == 200
    delete_data = response.json()
    assert delete_data['deleted'] == 1

    # Delete not existent audio
    response = await taxi_media_storage.delete(
        'service/sos-audio/v1/delete',
        headers=headers,
        params=dict(source='test', id=store_data['id']),
    )

    assert response.status_code == 404

    # Store different versions
    response = await taxi_media_storage.post(
        'service/sos-audio/v1/store',
        headers=headers,
        params=dict(source='test', version='1234'),
        data=audio,
    )
    store_data1 = response.json()
    assert response.status_code == 200
    response = await taxi_media_storage.post(
        'service/sos-audio/v1/store',
        headers=headers,
        params=dict(
            source='test',
            id=store_data1['id'],
            version=(store_data1['version'] + 'postfix'),
        ),
        data=audio,
    )
    store_data2 = response.json()
    assert response.status_code == 200
    assert store_data1['id'] == store_data2['id']
    assert store_data1['version'] != store_data2['version']

    # Delete all audios
    response = await taxi_media_storage.delete(
        'service/sos-audio/v1/delete',
        headers=headers,
        params=dict(source='test', id=store_data1['id']),
    )
    assert response.status_code == 200
    delete_data = response.json()
    assert delete_data['deleted'] == 2

    # Store new audio
    response = await taxi_media_storage.post(
        'service/sos-audio/v1/store',
        headers=headers,
        params=dict(source='test'),
        data=audio,
    )
    store_data = response.json()
    assert response.status_code == 200

    # Remove from mds
    assert mds_s3.delete_object(
        'secret',
        'sos-audio/{}/{}'.format(store_data['id'], store_data['version']),
    )

    # Delete not existent in mds
    response = await taxi_media_storage.delete(
        'service/sos-audio/v1/delete',
        headers=headers,
        params=dict(source='test', id=store_data['id']),
    )

    assert response.status_code == 200
