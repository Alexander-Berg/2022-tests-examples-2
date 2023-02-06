# for DEPTRANS_DRIVER_STATUS_LICENSE_PREFIXES
def license_prefixes():
    return {'prefix_to_country': {'LR': 'ЛНР', 'DR': 'ДНР'}}


def remove_dprlpr_in_license(license_id, license_country):
    if license_country == 'oth':
        prefix_to_country = license_prefixes()
        for prefix in prefix_to_country['prefix_to_country']:
            if license_id.startswith(prefix):
                return license_id[len(prefix) :]
    return license_id


def is_dprlpr_license(license_id, license_country):
    return (
        license_country == 'oth'
        and remove_dprlpr_in_license(license_id, license_country) != license_id
    )


def is_license_oth_without_prefix(license_id, license_country):
    return (
        license_country == 'oth'
        and remove_dprlpr_in_license(license_id, license_country) == license_id
    )
