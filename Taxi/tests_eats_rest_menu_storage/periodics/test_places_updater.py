import pytest


PLACES_LIMIT = 2


@pytest.mark.config(
    EATS_REST_MENU_STORAGE_PLACES_UPDATER_SETTINGS={
        'enabled': True,
        'period_in_sec': 3600,
        'places_limit': PLACES_LIMIT,
        'full_update_interval': 86400,
    },
)
async def test_catalog_storage_periodic(
        testpoint, taxi_eats_rest_menu_storage, mockserver, pgsql,
):
    @testpoint('eats_rest_menu_storage::places-updater')
    def handle_finished(arg):
        pass

    places = list(gen_place(place_id=i, brand_id=i * 10) for i in range(3))
    places.append(gen_place(place_id=3, brand_id=3, business='zapravki'))
    non_restaurant_place = gen_place(
        place_id=1000, brand_id=10000, business='store',
    )

    sql_put_place(pgsql, place_id=1, slug='old_slug', brand_id=10)

    @mockserver.json_handler(
        (
            '/eats-catalog-storage'
            '/internal/eats-catalog-storage/v1'
            '/places/updates'
        ),
    )
    def _catalog_storage(request):
        request_json = request.json
        assert request_json['limit'] == PLACES_LIMIT
        # first request
        if request_json['last_known_revision'] == 0:
            return {
                'last_known_revision': 1,
                'places': [places[0], non_restaurant_place],
            }
        # second request
        if request_json['last_known_revision'] == 1:
            return {'last_known_revision': 2, 'places': places[1:4]}
        # third request
        if request_json['last_known_revision'] == 2:
            return {'last_known_revision': 2, 'places': []}
        return {'last_known_revision': 2, 'places': []}

    await taxi_eats_rest_menu_storage.run_distlock_task('places-updater')
    assert handle_finished.has_calls

    places_data = sql_get_places(pgsql)
    expected_places_data = [
        {
            'id': place['id'],
            'slug': place['slug'],
            'brand_id': place['brand']['id'],
        }
        for place in places
    ]

    assert places_data == expected_places_data
    assert sql_get_last_revision(pgsql) == 2


def gen_place(place_id, brand_id, business='restaurant'):
    return {
        'id': place_id,
        'slug': 'slug_{}'.format(place_id),
        'brand': {
            'id': brand_id,
            'slug': 'brand_slug_{}'.format(brand_id),
            'name': 'name_{}'.format(brand_id),
            'picture_scale_type': 'aspect_fit',
        },
        'business': business,
        'revision_id': place_id,
        'updated_at': '2020-04-28T12:00:00+03:00',
    }


def sql_put_place(pgsql, place_id, slug, brand_id):
    cursor = pgsql['eats_rest_menu_storage'].cursor()
    cursor.execute(
        f"""
        insert into eats_rest_menu_storage.brands(
            id
        ) values ({brand_id})
        on conflict (id) do nothing
        """,
    )

    cursor.execute(
        f"""
        insert into eats_rest_menu_storage.places(
            id, slug, brand_id
        ) values ({place_id}, '{slug}', {brand_id})
        """,
    )


def sql_get_places(pgsql):
    cursor = pgsql['eats_rest_menu_storage'].cursor()
    cursor.execute(
        """
        select
            id,
            slug,
            brand_id
        from eats_rest_menu_storage.places
        order by id
        """,
    )
    return [
        {'id': row[0], 'slug': row[1], 'brand_id': row[2]} for row in cursor
    ]


def sql_get_last_revision(pgsql):
    cursor = pgsql['eats_rest_menu_storage'].cursor()
    cursor.execute(
        """
        select last_revision
        from eats_rest_menu_storage.place_updater_states
        """,
    )
    return list(cursor)[0][0]
