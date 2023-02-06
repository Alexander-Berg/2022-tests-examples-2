import pytest


@pytest.mark.config(
    FEEDS_MEDIA_SETTINGS={
        's3': {'base_url': 'https://{}.s3.mdst.yandex.net/{}/{}'},
    },
)
@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_list.sql'])
@pytest.mark.parametrize(
    'filters, order_by, media_ids',
    [
        pytest.param(
            {}, None, ['image', 'image2', 'video'], id='default filter',
        ),
        pytest.param(
            {}, 'created', ['video', 'image2', 'image'], id='order by created',
        ),
        pytest.param(
            {'tag': 'another_tag', 'service_group': 'test_group'},
            None,
            ['image2', 'video'],
            id='tag filter with specified service_group',
        ),
        pytest.param(
            {'tag': 'another_tag', 'media_type': 'image'},
            None,
            ['image2'],
            id='tag and type intersection filter',
        ),
    ],
)
async def test_list(web_app_client, filters, order_by, media_ids):
    response = await web_app_client.post(
        '/v1/media/list', json={'filters': filters, 'order_by': order_by},
    )
    assert response.status == 200

    content = await response.json()
    assert content['total'] == len(media_ids)
    assert [item['media_id'] for item in content['items']] == media_ids
