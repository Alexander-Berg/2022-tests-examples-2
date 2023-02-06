import math
import uuid


def find_place_by_slug(response, slug):
    for place in response['places']:
        if place['place']['meta']['place_slug'] == slug:
            return place['place'], place['map_pin']
    return None, None


def _find_meta_by_type(list_, meta_type):
    for meta in list_:
        if meta['type'] == meta_type:
            return meta
    return None


def find_meta_in_place(place, meta_type):
    return _find_meta_by_type(place['payload']['data']['meta'], meta_type)


def find_meta_in_map_pin(map_pin, meta_type):
    return _find_meta_by_type(map_pin['meta'], meta_type)


def _is_valid_uuid(value):
    if not isinstance(value, str):
        return False
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


def purge_object_of_uuids(obj):
    if isinstance(obj, dict):
        return {
            key: purge_object_of_uuids(value)
            for key, value in obj.items()
            if not value
            or not _is_valid_uuid(value)
            and (not isinstance(value, list) or not _is_valid_uuid(value[0]))
        }
    if isinstance(obj, list):
        return [purge_object_of_uuids(entry) for entry in obj]
    return obj


def objects_approx_equal(lhs, rhs, abs_tol=1e-2):
    for key, value in lhs.items():
        rhs_value = rhs.get(key, None)
        if not rhs_value or not math.isclose(value, rhs_value, abs_tol=1e-2):
            return False
    return True
