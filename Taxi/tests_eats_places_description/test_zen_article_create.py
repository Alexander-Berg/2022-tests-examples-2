async def test_basic(taxi_eats_places_description, now, pgsql):
    published = now
    response = await taxi_eats_places_description.post(
        '/v1/brand/articles/zen?brand_id=777',
        json={
            'title': 'Заголовок',
            'description': 'Описание',
            'authorAvatarUrl': 'http://ссылка_на_аватар',
            'url': 'http://ссылка_на_текст',
            'priority': 20,
            'published': f'{published.isoformat()}+00:00',
        },
    )
    zen_article_id = response.json()['id']
    cursor = pgsql['eats_user_reactions'].cursor()
    cursor.execute(
        """SELECT id
        FROM eats_places_description.zen_articles""",
    )
    zen_articles = list(cursor)
    assert len(zen_articles) == 1, zen_articles
    zen_article = zen_articles[0]
    assert zen_article[0] == zen_article_id
