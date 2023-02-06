import base64

import pytest

from tests_eats_restapp_marketing import sql


def init_table(x: int, pgsql):
    sql.insert_campaign(pgsql, sql.Campaign(id=str(x)))

    return sql.insert_banner(
        pgsql,
        sql.Banner(
            id=x,
            place_id=x,
            inner_campaign_id=str(x),
            image='',
            original_image_id='',
            image_text='',
            status=sql.BannerStatus.REJECTED,
        ),
    )


def get_banners_by_status(status: str, pgsql):
    cursor = pgsql.cursor()
    cursor.execute(
        'SELECT inner_campaign_id,image_text '
        'FROM eats_restapp_marketing.banners '
        'WHERE status = \'%s\' ' % status,
        'ORDER BY inner_campaign_id;',
    )

    result = [(row[0], row[1]) for row in cursor.fetchall()]
    return result


def get_media_id(campaign_id: str, pgsql):
    cursor = pgsql.cursor()
    cursor.execute(
        'SELECT image,original_image_id '
        'FROM eats_restapp_marketing.banners '
        'WHERE inner_campaign_id = \'%s\';' % campaign_id,
    )

    result = [(row[0], row[1]) for row in cursor.fetchall()]
    return result


def corrupt_table(pgsql):
    cursor = pgsql.cursor()
    cursor.execute(
        'ALTER TABLE eats_restapp_marketing.banners DROP COLUMN image;',
    )


def restore_table(pgsql):
    cursor = pgsql.cursor()
    cursor.execute(
        'ALTER TABLE eats_restapp_marketing.banners ADD COLUMN image TEXT;',
    )


TEST_IMG_1 = 'foo_source_image'
TEST_IMG_2 = 'bar_source_image'


@pytest.mark.parametrize(
    'return_code_access, return_code_common,'
    'error_campaign, error_feeds_admin, error_pg, image, source_image',
    [
        pytest.param(
            200,
            204,
            False,
            False,
            False,
            TEST_IMG_1,
            TEST_IMG_1,
            id='Succesful responses',
        ),
        pytest.param(
            200,
            204,
            False,
            False,
            False,
            TEST_IMG_1,
            TEST_IMG_2,
            marks=pytest.mark.xfail,
            id='Different images',
        ),
        pytest.param(
            400,
            400,
            False,
            False,
            False,
            TEST_IMG_1,
            TEST_IMG_1,
            id='Failed access 400',
        ),
        pytest.param(
            403,
            403,
            False,
            False,
            False,
            TEST_IMG_1,
            TEST_IMG_1,
            id='Failed access 403',
        ),
        pytest.param(
            200,
            404,
            True,
            False,
            False,
            TEST_IMG_1,
            TEST_IMG_1,
            id='No campaign found',
        ),
        pytest.param(
            200,
            500,
            False,
            True,
            False,
            TEST_IMG_1,
            TEST_IMG_1,
            id='Error feeds-admin',
        ),
        pytest.param(
            200,
            500,
            False,
            False,
            True,
            TEST_IMG_1,
            TEST_IMG_1,
            id='Error pg',
        ),
        pytest.param(
            200,
            204,
            False,
            False,
            False,
            TEST_IMG_1,
            None,
            id='Backward compatibility',
        ),
    ],
)
async def test_upload_image(
        taxi_eats_restapp_marketing,
        mock_feeds_admin,
        eats_restapp_marketing_db,
        mockserver,
        return_code_access,
        return_code_common,
        error_campaign,
        error_feeds_admin,
        error_pg,
        testpoint,
        image,
        source_image,
):
    """
    Проверка загрузки изображения
    """

    @mockserver.json_handler('/eats-restapp-authorizer/v1/user-access/check')
    async def _handle_check_user_access(request):
        return mockserver.make_response(
            status=return_code_access,
            json={'code': str(return_code_access), 'message': 'foo'},
        )

    @testpoint('before-update-table')
    async def pg_handle(arg):
        if error_pg:
            corrupt_table(eats_restapp_marketing_db)
        return

    campaign_id = 11
    url = '/4.0/restapp-front/marketing/v1/ad/cpm/upload_banner'
    headers = {'X-YaEda-PartnerId': str(123)}

    prefix = 'data:image/jpeg;base64,'

    image_encoded = str(base64.b64encode(bytes(image, 'utf-8')))

    body = {'image': prefix + image_encoded, 'campaign_id': str(campaign_id)}

    title_image = None
    if source_image:
        source_image_encoded = str(
            base64.b64encode(bytes(source_image, 'utf-8')),
        )
        body['source_image'] = prefix + source_image_encoded
        title_image = 'foo_title'
        body['text'] = title_image

    if error_campaign:
        campaign_id = 12

    for x in [campaign_id, 22, 33]:
        init_table(x, eats_restapp_marketing_db)

    mock_feeds_admin.set_expected_upload_image_data(
        str(campaign_id), image_encoded, error_feeds_admin,
    )

    response = await taxi_eats_restapp_marketing.post(
        url, headers=headers, json=body,
    )
    assert response.status_code == return_code_common
    if return_code_common in [400, 403, 404] or error_feeds_admin:
        assert pg_handle.times_called == 0
    else:
        assert pg_handle.times_called == 1
    if error_pg:
        restore_table(eats_restapp_marketing_db)

    if response.status_code == 204:
        assert [(str(campaign_id), title_image)] == get_banners_by_status(
            'uploaded', eats_restapp_marketing_db,
        )
        assert [
            (
                'media_id_%s' % str(campaign_id),
                'media_id_%s' % str(campaign_id) if source_image else None,
            ),
        ] == get_media_id(str(campaign_id), eats_restapp_marketing_db)
