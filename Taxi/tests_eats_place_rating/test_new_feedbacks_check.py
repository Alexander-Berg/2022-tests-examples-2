import pytest


@pytest.mark.pgsql('eats_place_rating', files=('pg_new_feedbacks_views.sql',))
async def test_get_new_feedbacks_false(taxi_eats_place_rating):
    response = await taxi_eats_place_rating.get(
        '/4.0/restapp-front/eats-place-rating/v1/new-feedbacks/check',
        headers={'X-YaEda-PartnerId': '1', 'X-YaEda-Partner-Places': '1,3,5'},
    )
    assert response.status_code == 200
    assert response.json() == {'new_feedbacks_flag': False}


@pytest.mark.pgsql('eats_place_rating', files=('pg_new_feedbacks_views.sql',))
async def test_get_new_feedbacks_true(taxi_eats_place_rating):
    response = await taxi_eats_place_rating.get(
        '/4.0/restapp-front/eats-place-rating/v1/new-feedbacks/check',
        headers={'X-YaEda-PartnerId': '1', 'X-YaEda-Partner-Places': '2,5'},
    )
    assert response.status_code == 200
    assert response.json() == {'new_feedbacks_flag': True}


@pytest.mark.pgsql('eats_place_rating', files=('pg_new_feedbacks_views.sql',))
async def test_get_new_feedbacks_places_not_in_db(taxi_eats_place_rating):
    response = await taxi_eats_place_rating.get(
        '/4.0/restapp-front/eats-place-rating/v1/new-feedbacks/check',
        headers={'X-YaEda-PartnerId': '1', 'X-YaEda-Partner-Places': '10,11'},
    )
    assert response.status_code == 200
    assert response.json() == {'new_feedbacks_flag': False}
