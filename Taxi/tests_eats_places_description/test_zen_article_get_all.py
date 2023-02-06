async def test_basic(taxi_eats_places_description, now):
    published = now

    first_response = await taxi_eats_places_description.post(
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

    second_response = await taxi_eats_places_description.post(
        '/v1/brand/articles/zen?brand_id=999',
        json={
            'title': 'Заголовок',
            'description': 'Описание',
            'authorAvatarUrl': 'http://ссылка_на_аватар',
            'url': 'http://ссылка_на_текст',
            'priority': 20,
            'published': f'{published.isoformat()}+00:00',
        },
    )

    assert first_response.json()['id'] != second_response.json()['id']

    await taxi_eats_places_description.invalidate_caches(clean_update=False)

    response = await taxi_eats_places_description.post(
        '/v1/articles/zen/list', json={'limit': 1},
    )
    first_articles = response.json()['articles']
    assert len(first_articles) == 1

    cursor = response.json()['cursor']
    response = await taxi_eats_places_description.post(
        '/v1/articles/zen/list', json={'limit': 1, 'cursor': cursor},
    )

    second_articles = response.json()['articles']
    assert len(second_articles) == 1

    cursor = response.json()['cursor']
    response = await taxi_eats_places_description.post(
        '/v1/articles/zen/list', json={'limit': 1, 'cursor': cursor},
    )

    assert response.json() == {}
