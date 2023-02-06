import pytest


@pytest.mark.pgsql('eats_place_rating', files=('pg_new_feedbacks_views.sql',))
async def test_update_feedbacks_view_time_for_all_partner_places_if_place_ids_is_empty(
        taxi_eats_place_rating, pgsql,
):
    cursor = pgsql['eats_place_rating'].cursor()
    cursor.execute(
        'SELECT place_id, last_view_time::DATE '
        'FROM eats_place_rating.new_feedbacks_views '
        'ORDER BY place_id;',
    )
    previous_result = dict()
    for item in cursor.fetchall():
        previous_result[item[0]] = item[1]
    old_places = [4, 6]
    old_date = previous_result[4]

    response = await taxi_eats_place_rating.post(
        '/4.0/restapp-front/eats-place-rating/v1/new-feedbacks/update-view-time',
        json={},
        headers={'X-YaEda-PartnerId': '1', 'X-YaEda-Partner-Places': '1,3,5'},
    )
    assert response.status_code == 204

    cursor.execute(
        'SELECT place_id, last_view_time::DATE '
        'FROM eats_place_rating.new_feedbacks_views '
        'ORDER BY place_id;',
    )
    result = cursor.fetchall()
    for item in result:
        if item[0] in old_places:
            assert item[1] == old_date
        else:
            assert item[1] > old_date


@pytest.mark.pgsql('eats_place_rating', files=('pg_new_feedbacks_views.sql',))
async def test_update_feedbacks_view_time_only_for_place_ids_from_request_body(
        taxi_eats_place_rating, pgsql,
):
    cursor = pgsql['eats_place_rating'].cursor()
    cursor.execute(
        'SELECT place_id, last_view_time::DATE '
        'FROM eats_place_rating.new_feedbacks_views '
        'ORDER BY place_id;',
    )
    previous_result = dict()
    for item in cursor.fetchall():
        previous_result[item[0]] = item[1]
    all_places = [1, 3, 4, 5, 6]
    old_places = [4, 6]
    old_date = previous_result[4]

    response = await taxi_eats_place_rating.post(
        '/4.0/restapp-front/eats-place-rating/v1/new-feedbacks/update-view-time',
        json={'place_ids': [1, 3, 5]},
        headers={
            'X-YaEda-PartnerId': '1',
            'X-YaEda-Partner-Places': '1,3,5,6',
        },
    )
    assert response.status_code == 204

    cursor = pgsql['eats_place_rating'].cursor()
    cursor.execute(
        'SELECT place_id, last_view_time::DATE '
        'FROM eats_place_rating.new_feedbacks_views '
        'ORDER BY place_id;',
    )
    result = cursor.fetchall()
    for item in result:
        if item[0] in old_places:
            assert item[1] == old_date
        else:
            assert item[1] > old_date


async def test_response_500_if_partner_places_is_empty(taxi_eats_place_rating):
    response = await taxi_eats_place_rating.post(
        '/4.0/restapp-front/eats-place-rating/v1/new-feedbacks/update-view-time',
        json={'place_ids': [1, 3, 5]},
        headers={'X-YaEda-PartnerId': '1'},
    )
    assert response.status_code == 500
    assert response.json() == {
        'code': '500',
        'message': 'Internal Server Error',
    }


async def test_response_403_is_some_places_are_unavailable(
        taxi_eats_place_rating,
):
    response = await taxi_eats_place_rating.post(
        '/4.0/restapp-front/eats-place-rating/v1/new-feedbacks/update-view-time',
        json={'place_ids': [2, 3, 5]},
        headers={'X-YaEda-PartnerId': '1', 'X-YaEda-Partner-Places': '1,3,5'},
    )
    assert response.status_code == 403
