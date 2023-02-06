import freezegun
import pytest

from taxi.robowarehouse.lib.concepts import package_places
from taxi.robowarehouse.lib.misc import datetime_utils
from taxi.robowarehouse.lib.misc.helpers import generate_id
from taxi.robowarehouse.lib.test_utils.helpers import convert_to_frontend_response


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_update(client):
    now = datetime_utils.get_now()
    place = await package_places.factories.create()

    response = await client.patch(
        f'/admin/v1/package-places/{place.package_place_id}/',
        json={'state': 'FILLED'},
    )

    new_place = await package_places.get_all()
    new_place_history = await package_places.get_all_history()
    expected_place = {**place.to_dict(), 'state': 'FILLED', 'updated_at': now}

    assert response.status_code == 200
    assert len(new_place) == 1
    assert len(new_place_history) == 1
    assert new_place[0].to_dict() == expected_place
    assert response.json() == convert_to_frontend_response(expected_place)


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_update_not_found_error(client):
    place_id = generate_id()

    response = await client.patch(
        f'/admin/v1/package-places/{place_id}/',
        json={'state': 'FILLED'},
    )

    expected = {
        'code': 'PACKAGE_PLACE_NOT_FOUND_ERROR',
        'details': {'occurred_at': '2020-01-02T00:04:05+00:00', 'package_place_id': place_id},
        'message': 'Package place not found for package'
    }
    assert response.status_code == 404
    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_update_nothing_update_error(client):
    place = await package_places.factories.create()

    response = await client.patch(
        f'/admin/v1/package-places/{place.package_place_id}/',
        json={},
    )

    expected = {
        'code': 'PACKAGE_PLACE_NOTHING_UPDATE',
        'details': {'occurred_at': '2020-01-02T00:04:05+00:00'},
        'message': 'Package place nothing to update'
    }
    assert response.status_code == 400
    assert response.json() == expected
