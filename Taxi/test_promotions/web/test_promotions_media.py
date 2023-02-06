import pytest

from promotions.generated.service.swagger.models import api
from promotions.logic import const
from promotions.logic import media_service
from promotions.models import media_models


DEFAULT_HEADERS = {
    'X-Yandex-UID': '1234567890',
    'X-YaTaxi-UserId': 'test_user_id',
    'X-YaTaxi-PhoneId': 'test_phone_id',
    'User-Agent': (
        'yandex-taxi/3.107.0.dev_sergu_b18dbfd* Android/6.0.1 (LGE; Nexus 5)'
    ),
    'X-Request-Application': (
        'app_name=android,app_brand=yataxi,app_ver1=1,app_ver2=2,app_ver3=3'
    ),
}
MEDIA_TAG = media_models.MediaTag(
    id='f6123ee6-5f98-449d-b47e-f48595f188b6_media_tag1',
    type='image',
    resize_mode='width_fit',
    sizes=[
        api.Size(
            field='original',
            value=0,
            mds_id='original_mds_id',
            url='http://mds.net/original_mds_id',
        ),
        api.Size(
            field='screen_width',
            value=320,
            mds_id='width_320_mds_id',
            url='http://mds.net/width_320_mds_id',
        ),
        api.Size(
            field='screen_width',
            value=750,
            mds_id='width_750_mds_id',
            url='http://mds.net/width_750_mds_id',
        ),
        api.Size(
            field='screen_width',
            value=1080,
            mds_id='width_1080_mds_id',
            url='http://mds.net/width_1080_mds_id',
        ),
    ],
)


def compare_promotions(promo1: dict, promo2: dict):
    """
        Function for comparing fullscreens taken from json, response, etc.
        To make comparison more flexible, we ignore:
            id:
            name: to test editing in same DB, to compare with view response
            start_date:
            end_date:
            created_at:
            updated_at: not to use mock for time
            status: to compare published and unpublished promos

    """
    fields_to_remove = [
        'id',
        'start_date',
        'end_date',
        'name',
        'created_at',
        'updated_at',
        'status',
    ]
    for field in fields_to_remove:
        if field in promo1:
            promo1.pop(field)
        if field in promo2:
            promo2.pop(field)
    assert promo1 == promo2


@pytest.mark.pgsql(
    'promotions',
    files=[
        'pg_promotions_with_media_admin.sql',
        'pg_promotions_media_tags.sql',
    ],
)
async def test_admin_view_with_media(web_app_client, load_json):
    promotion_id = 'story_view_id'
    response = await web_app_client.get(
        f'/admin/promotions/?promotion_id={promotion_id}',
    )
    assert response.status == 200
    data = await response.json()
    assert data['id'] == promotion_id
    assert data == load_json('admin_view_response.json')


@pytest.mark.pgsql('promotions', files=['pg_promotions_media_tags.sql'])
@pytest.mark.parametrize('media_with_text', [True])
async def test_admin_create_with_media(
        web_app_client, load_json, media_with_text,
):
    request_body = load_json('admin_create_request.json')
    if media_with_text:
        request_body['pages'][0]['backgrounds'][0][
            'id'
        ] = 'media_with_text_tag_id'

    response = await web_app_client.post(
        '/admin/promotions/create/', json=request_body,
    )
    response_json = await response.json()
    assert response.status == 201
    promotion_id = response_json['id']

    response = await web_app_client.get(
        f'/admin/promotions/?promotion_id={promotion_id}',
    )
    assert response.status == 200
    promotion = await response.json()
    expected_promotion = load_json('admin_view_response.json')
    expected_promotion['extra_fields']['preview']['title'] = {
        'content': const.PREVIEW_DEFAULT_TITLE_CONTENT,
        'color': const.PREVIEW_DEFAULT_TITLE_COLOR,
    }
    if media_with_text:
        expected_promotion['pages'][0]['backgrounds'][0] = {
            'id': 'media_with_text_tag_id',
            'resize_mode': 'height_fit',
            'sizes': [
                {
                    'field': 'original',
                    'value': 0,
                    'mds_id': 'original_mds_id',
                    'url': 'http://mds.net/original_mds_id',
                    'media_text': 'picture_text',
                },
            ],
            'type': 'image',
        }
    compare_promotions(promotion, expected_promotion)


@pytest.mark.pgsql(
    'promotions',
    files=['pg_promotions_with_media.sql', 'pg_promotions_media_tags.sql'],
)
async def test_admin_edit_with_media(web_app_client, load_json):
    promo_id = 'story_for_edit'

    response = await web_app_client.put(
        f'admin/promotions/{promo_id}/',
        json=load_json('admin_edit_request.json'),
    )
    resp_data = await response.json()
    assert response.status == 200
    assert resp_data == {}

    response = await web_app_client.get(
        f'admin/promotions/?promotion_id={promo_id}',
    )
    assert response.status == 200
    promotion = await response.json()
    compare_promotions(promotion, load_json('admin_view_response.json'))


@pytest.mark.config(PROMOTIONS_ENABLED=True)
@pytest.mark.config(
    ADMIN_IMAGE_SIZE_HINT_TO_SCREEN_INFO={
        128: {'scale': 2, 'screen_height': 1334, 'screen_width': 750},
        160: {'scale': 1, 'screen_height': 480, 'screen_width': 320},
        192: {'scale': 3, 'screen_height': 1920, 'screen_width': 1080},
    },
)
@pytest.mark.parametrize(
    ['size_hint', 'screen_size'],
    [
        (100, {'scale': 2, 'screen_height': 1334, 'screen_width': 750}),
        (128, {'scale': 2, 'screen_height': 1334, 'screen_width': 750}),
        (129, {'scale': 1, 'screen_height': 480, 'screen_width': 320}),
        (160, {'scale': 1, 'screen_height': 480, 'screen_width': 320}),
        (161, {'scale': 3, 'screen_height': 1920, 'screen_width': 1080}),
        (192, {'scale': 3, 'screen_height': 1920, 'screen_width': 1080}),
        (193, {'scale': 3, 'screen_height': 1920, 'screen_width': 1080}),
        (10_000, {'scale': 3, 'screen_height': 1920, 'screen_width': 1080}),
    ],
)
async def test_size_hint_to_media_size_info(
        web_context, size_hint, screen_size,
):
    service = media_service.MediaConfigsService(config=web_context.config)
    assert (
        service.size_hint_to_screen_size(size_hint).serialize() == screen_size
    )


@pytest.mark.config(PROMOTIONS_ENABLED=True)
@pytest.mark.parametrize(
    ['screen_size', 'url'],
    [
        (
            {'scale': 0.75, 'screen_height': 400, 'screen_width': 300},
            'http://mds.net/width_320_mds_id',
        ),
        (
            {'scale': 1, 'screen_height': 480, 'screen_width': 320},
            'http://mds.net/width_320_mds_id',
        ),
        (
            {'scale': 1, 'screen_height': 480, 'screen_width': 321},
            'http://mds.net/width_750_mds_id',
        ),
        (
            {'scale': 2, 'screen_height': 1334, 'screen_width': 750},
            'http://mds.net/width_750_mds_id',
        ),
        (
            {'scale': 2, 'screen_height': 1334, 'screen_width': 751},
            'http://mds.net/width_1080_mds_id',
        ),
        (
            {'scale': 3, 'screen_height': 1920, 'screen_width': 1080},
            'http://mds.net/width_1080_mds_id',
        ),
        (
            {'scale': 3, 'screen_height': 1920, 'screen_width': 1081},
            'http://mds.net/original_mds_id',
        ),
        (
            {'scale': 3, 'screen_height': 50_000, 'screen_width': 10_000},
            'http://mds.net/original_mds_id',
        ),
    ],
)
async def test_media_tag_url_selector(web_context, screen_size, url):
    media_size_info = api.MediaSizeInfo(
        scale=screen_size['scale'],
        screen_height=screen_size['screen_height'],
        screen_width=screen_size['screen_width'],
    )
    assert (
        MEDIA_TAG.get_size_for_screen(media_size_info=media_size_info).url
        == url
    )


@pytest.mark.pgsql(
    'promotions',
    files=['pg_promotions_with_media.sql', 'pg_promotions_media_tags.sql'],
)
async def test_internal_with_media(web_app_client, load_json):
    response = await web_app_client.get('/internal/promotions/list/')
    content = await response.json()
    assert response.status == 200
    # tanker keys should not be translated, response with preview
    assert content == load_json('internal_list.json')
