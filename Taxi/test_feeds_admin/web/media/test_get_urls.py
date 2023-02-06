import pytest

IMAGE_LINK = '$mockserver/mds_avatars/get-feeds-media/1396527/image/orig'
VIDEO_LINK = 'https://feeds-admin-bucket.s3.mdst.yandex.net/example/video'


@pytest.mark.config(
    FEEDS_MEDIA_SETTINGS={
        's3': {'base_url': 'https://{}.s3.mdst.yandex.net/{}/{}'},
    },
)
@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_urls.sql'])
async def test_urls(web_app_client):
    response = await web_app_client.post(
        '/v1/media/get-urls', json={'media_ids': ['image', 'video']},
    )
    assert response.status == 200

    content = (await response.json())['urls']
    urls = {item['media_url'] for item in content}
    assert urls == {IMAGE_LINK, VIDEO_LINK}


@pytest.mark.config(
    FEEDS_MEDIA_SETTINGS={
        's3': {'base_url': 'https://{}.s3.mdst.yandex.net/{}/{}'},
    },
)
@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_urls.sql'])
async def test_skip_not_existing(web_app_client):
    response = await web_app_client.post(
        '/v1/media/get-urls', json={'media_ids': ['image', 'not_existed']},
    )
    assert response.status == 200

    content = await response.json()
    assert content == {
        'urls': [
            {
                'media_id': 'image',
                'media_type': 'image',
                'media_url': IMAGE_LINK,
                'tags': ['some_tag'],
            },
        ],
    }
