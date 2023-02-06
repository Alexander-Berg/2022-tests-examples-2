import pytest


@pytest.mark.pgsql('eats_user_reactions', files=['test_articles.sql'])
async def test_basic(taxi_eats_places_description):

    await taxi_eats_places_description.invalidate_caches(clean_update=False)

    response = await taxi_eats_places_description.post(
        '/v1/articles/zen/list', json={'limit': 10},
    )

    articles = response.json()['articles']['zenArticles']
    assert len(articles) == 4

    assert articles[0]['title'] == 'title_2'
    assert articles[1]['title'] == 'title_4'
    assert articles[2]['title'] == 'title_6'
    assert articles[3]['title'] == 'title_8'
