# pylint: disable=dangerous-default-value


def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    return obj


def get_unique_driver(
        driver_license,
        license_type,
        mongodb,
        fields={
            'licenses',
            'license_ids',
            'profiles',
            'exam_score',
            'decoupled_from',
        },
):
    unique_driver = mongodb.unique_drivers.find_one(
        {license_type: {'$in': [driver_license]}}, fields,
    )
    return unique_driver


def get_union_unique_driver(driver_license, license_type, mongodb):
    union_unique_driver = mongodb.union_unique_drivers.find_one(
        {license_type: {'$in': [driver_license]}},
        {'license_ids', 'licenses', 'unique_drivers'},
    )
    if not union_unique_driver:
        return None

    union_unique_driver.pop('_id')
    return union_unique_driver
