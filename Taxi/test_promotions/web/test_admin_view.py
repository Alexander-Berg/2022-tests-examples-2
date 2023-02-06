import pytest


@pytest.mark.config(
    PROMOTIONS_IMAGES_URL_TEMPLATE='https://some-cool-url.ya/{}',
)
@pytest.mark.pgsql('promotions', files=['pg_promotions_admin.sql'])
@pytest.mark.parametrize(
    ['promotion_id', 'expected_code', 'expected_json'],
    [
        ('5a8aaed572ab3656114313ed', 404, None),
        ('id1', 200, 'promotion_view_ok.json'),
        ('6b2ee5529f5b4ffc8fea7008e6913ca6', 200, None),
        ('eda_unpublished', 200, 'promotion_view_eda_banner_ok.json'),
        ('promo_on_summary1', 200, 'promotion_view_promo_on_summary_ok.json'),
        ('story_id1', 200, 'promotion_view_story_ok.json'),
        ('totw_banner_1', 200, 'promotion_view_totw_banner_ok.json'),
        ('id5', 200, 'promotion_view_fs_by_campaign_label_ok.json'),
        ('object_over_map_1', 200, 'promotion_view_object_over_map_ok.json'),
        ('card_2', 200, 'promotion_view_card_by_campaign_label_ok.json'),
        (
            'notification_3',
            200,
            'promotion_view_notification_by_campaign_label_ok.json',
        ),
        ('grocery_published', 200, 'promotion_view_grocery_informer_ok.json'),
    ],
)
async def test_view(
        web_app_client, promotion_id, expected_code, expected_json, load_json,
):
    response = await web_app_client.get(
        f'/admin/promotions/?promotion_id={promotion_id}',
    )
    assert response.status == expected_code
    if expected_code == 200:
        data = await response.json()
        assert data['id'] == promotion_id
        if not expected_json:
            return

        expected_data = load_json(expected_json)
        assert data == expected_data
