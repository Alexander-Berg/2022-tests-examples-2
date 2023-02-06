import pytest


def response_equals(resp1, resp2):
    """
    For equating lists of promotions, which order depends
    on test order completion. That's why we sort them by id.
    """
    sort_recursive(resp1)
    sort_recursive(resp2)
    assert resp1 == resp2


def sort_recursive(resp):
    if isinstance(resp, dict):
        for value in resp.values():
            sort_recursive(value)
    if (
            isinstance(resp, list)
            and all([isinstance(item, dict) and 'id' in item for item in resp])
            and len(resp) > 1
    ):
        resp.sort(key=lambda k: k['id'])


@pytest.mark.pgsql(
    'promotions',
    files=[
        'pg_promotions_internal.sql',
        'pg_promotions_promo_on_map.sql',
        'pg_promotions_eda_banners_internal.sql',
        'pg_promotions_grocery_informers_internal.sql',
        'pg_promotions_collections.sql',
        'pg_promotions_showcases.sql',
        'pg_promotions_media_tags.sql',
        'pg_campaigns.sql',
    ],
)
async def test_ok(web_app_client, load_json):
    response = await web_app_client.get('/internal/promotions/list/')
    content = await response.json()
    assert response.status == 200
    # tanker keys should not be translated, response with preview

    # we cannot mock postgres' insert time
    content['showcases'][0]['created_at'] = '2020-09-29T17:00:00.000000+03:00'
    content['showcases'][0]['updated_at'] = '2020-09-29T17:00:00.000000+03:00'
    response_equals(content, load_json('internal_list_ok_result.json'))


@pytest.mark.parametrize(
    ['created_at_from', 'result_id'],
    [
        ('2019-07-22T16:51:09+0000', 'equal'),
        ('2019-07-22T17:51:09+0000', 'greater'),
        ('2019-07-22T15:51:09+0000', 'lesser'),
        ('2019-07-22T19:51:09+0300', 'tzequal'),
        ('2019-07-22T20:51:09+0300', 'tzgreater'),
        ('2019-07-22T18:51:09+0300', 'tzlesser'),
    ],
)
@pytest.mark.pgsql(
    'promotions',
    files=[
        'pg_promotions_internal.sql',
        'pg_promotions_promo_on_map.sql',
        'pg_promotions_media_tags.sql',
        'pg_campaigns.sql',
    ],
)
@pytest.mark.config(PROMOTIONS_EXPIRED_PROMOS_RETURNING_TIME=60)
async def test_created_at_from_ok(
        web_app_client, load_json, created_at_from, result_id,
):
    response = await web_app_client.get(
        '/internal/promotions/list/',
        params={'created_at_from': created_at_from},
    )
    content = await response.json()
    assert response.status == 200
    filename = 'internal_list_with_param_ok_result.json'
    response_equals(content, load_json(filename)[result_id])


@pytest.mark.parametrize(
    ['created_at_from', 'result_id'],
    [
        ('2019-07-22T16:51:09+0000', 'equal'),
        ('2019-07-22T17:51:09+0000', 'greater'),
        ('2019-07-22T15:51:09+0000', 'lesser'),
        ('2019-07-22T19:51:09+0300', 'tzequal'),
        ('2019-07-22T20:51:09+0300', 'tzgreater'),
        ('2019-07-22T18:51:09+0300', 'tzlesser'),
    ],
)
@pytest.mark.pgsql('promotions', files=['pg_promotions_internal_rev.sql'])
async def test_created_at_from_revision_history_ok(
        web_app_client, load_json, created_at_from, result_id,
):
    response = await web_app_client.get(
        '/internal/promotions/list/',
        params={'created_at_from': created_at_from},
    )
    content = await response.json()
    assert response.status == 200
    filename = 'internal_list_with_param_rev_ok_result.json'
    response_equals(content, load_json(filename)[result_id])


@pytest.mark.pgsql('promotions', files=['pg_promotions_internal.sql'])
async def test_consumer(web_app_client, load_json):
    response = await web_app_client.get(
        '/internal/promotions/list/', params={'consumer': 'my_consumer'},
    )
    content = await response.json()
    assert response.status == 200
    # tanker keys should not be translated, response with preview
    response_equals(
        content, load_json('internal_list_consumer_ok_result.json'),
    )


@pytest.mark.pgsql(
    'promotions',
    files=[
        'pg_promotions_internal.sql',
        'pg_promotions_promo_on_map.sql',
        'pg_promotions_eda_banners_internal.sql',
        'pg_promotions_grocery_informers_internal.sql',
        'pg_promotions_collections.sql',
        'pg_promotions_showcases.sql',
        'pg_promotions_invalid.sql',
        'pg_promotions_media_tags.sql',
        'pg_promotions_out_of_date.sql',
        'pg_campaigns.sql',
    ],
)
async def test_invalid_promotions_filtering(web_app_client, load_json):
    response = await web_app_client.get('/internal/promotions/list/')
    content = await response.json()

    content['showcases'][0]['created_at'] = '2020-09-29T17:00:00.000000+03:00'
    content['showcases'][0]['updated_at'] = '2020-09-29T17:00:00.000000+03:00'

    assert response.status == 200
    assert len(content['totw_banners']) == 1
    response_equals(content, load_json('internal_list_ok_result.json'))


@pytest.mark.pgsql(
    'promotions',
    files=[
        'pg_promotions_internal.sql',
        'pg_promotions_promo_on_map.sql',
        'pg_promotions_eda_banners_internal.sql',
        'pg_promotions_grocery_informers_internal.sql',
        'pg_promotions_collections.sql',
        'pg_promotions_showcases.sql',
        'pg_promotions_media_tags.sql',
        'pg_test_campaigns.sql',
    ],
)
async def test_is_test_promotion_field(web_app_client, load_json):
    response = await web_app_client.get('/internal/promotions/list/')
    content = await response.json()
    assert response.status == 200
    # tanker keys should not be translated, response with preview

    # we cannot mock postgres' insert time
    content['showcases'][0]['created_at'] = '2020-09-29T17:00:00.000000+03:00'
    content['showcases'][0]['updated_at'] = '2020-09-29T17:00:00.000000+03:00'

    result = load_json('internal_list_ok_result.json')
    result['fullscreens'][2]['campaigns'][0]['is_test_publication'] = True
    result['fullscreens'][2]['campaigns'][1]['is_test_publication'] = True

    result['cards'][1]['campaigns'][0]['is_test_publication'] = True
    result['cards'][1]['campaigns'][1]['is_test_publication'] = True

    result['promos_on_map'][1]['campaigns'][0]['is_test_publication'] = True
    result['promos_on_map'][1]['campaigns'][1]['is_test_publication'] = True
    result['promos_on_map'][2]['campaigns'][0]['is_test_publication'] = True

    response_equals(content, result)
