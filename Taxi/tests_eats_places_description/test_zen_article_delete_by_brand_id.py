async def test_basic(taxi_eats_places_description, now):
    published = now
    await taxi_eats_places_description.post(
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

    response = await taxi_eats_places_description.delete(
        '/v1/brand/articles/zen?brand_id=777',
    )
    assert response.status == 204

    response = await taxi_eats_places_description.delete(
        '/v1/brand/articles/zen?brand_id=777',
    )
    assert response.status == 404
