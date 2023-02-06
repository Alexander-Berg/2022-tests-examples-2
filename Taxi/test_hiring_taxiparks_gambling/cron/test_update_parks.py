import logging
import typing


logger = logging.getLogger(__name__)


async def test_happy_path(hiring_oldparks_mockserver, run_update_parks):
    handler = hiring_oldparks_mockserver()
    await run_update_parks()
    assert handler.has_calls  # some calls to external service were made


async def test_rewrite_parks(
        hiring_oldparks_mockserver,
        run_update_parks,
        load_json,
        full_scan_parks,
):
    parks_to_load = load_json('parks_first_response.json')
    hiring_oldparks_mockserver(parks_to_load)
    await run_update_parks()

    loaded_parks = await full_scan_parks()
    check_equality(parks_to_load['taxiparks'], loaded_parks['taxiparks'])

    parks_to_load = load_json('parks_second_response.json')
    hiring_oldparks_mockserver(parks_to_load)
    await run_update_parks()

    loaded_parks = await full_scan_parks()
    check_equality(parks_to_load['taxiparks'], loaded_parks['taxiparks'])


async def test_empty_medium(
        hiring_oldparks_mockserver,
        run_update_parks,
        load_json,
        full_scan_parks,
):
    parks_to_load = load_json('parks_empty_medium.json')
    hiring_oldparks_mockserver(parks_to_load)
    await run_update_parks()

    loaded_parks = await full_scan_parks()
    for park in loaded_parks['taxiparks']:
        assert park.get('mediums') == []


def remap_keys(park: dict) -> dict:
    mapper = {
        '_id': 'mongo_id',
        'db_uuid': 'db_id',
        'city': 'cities',
        'private_owners': 'private_owning',
    }
    result = {}
    for key, value in park.items():
        if key == 'city':
            value = [city.strip() for city in value.split(',')]
        if key in mapper:
            result[mapper[key]] = value
            continue
        if key == 'mediums':
            result['mediums'] = [d['allowed'] for d in park['mediums']]
            continue
        if key == 'acquisition':
            result[key] = [
                {
                    ikey: ivalue
                    for ikey, ivalue in item.items()
                    if not (ikey == 'location' and not ivalue)
                }
                for item in value
            ]
            continue
        result[key] = value
    return result


def check_equality(
        parks_to_load: typing.List[typing.Dict],
        loaded_parks: typing.List[typing.Dict],
):
    for new_park in parks_to_load:
        park_in_database: dict = next(
            (
                item
                for item in loaded_parks
                if item['mongo_id'] == new_park['_id']
            ),
            {},
        )
        assert park_in_database
        new_park = remap_keys(new_park)
        assert park_in_database.items() >= new_park.items()
