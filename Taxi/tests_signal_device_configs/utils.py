import copy
import re

SOFTWARE_VERSION_REGEXP = re.compile(
    '([\\d]{1,10})\\.([\\d]{1,10})\\.([\\d]{1,10})\\-([\\d]{1,10})(\\..{0,1000})?',  # noqa E501
)
VERSION_PART_LENGTH = 10


def get_canonized_software_version(
        software_version,
) -> str:  # pylint: disable=invalid-name
    def _add_leading_zeros(match_part: str):
        if VERSION_PART_LENGTH < len(match_part):
            raise RuntimeError('Incorrect software_version')
        return '0' * (VERSION_PART_LENGTH - len(match_part)) + match_part

    if software_version is None:
        return ''

    match = SOFTWARE_VERSION_REGEXP.match(software_version)
    if match is None:
        raise RuntimeError('Incorrect software_version')
    return ''.join(
        [
            _add_leading_zeros(match[1]),
            '.',
            _add_leading_zeros(match[2]),
            '.',
            _add_leading_zeros(match[3]),
            '-',
            _add_leading_zeros(match[4]),
        ],
    )


def deep_merge_dicts(old, new):
    res = {}
    overlapping_keys = old.keys() & new.keys()
    for key in overlapping_keys:
        if not isinstance(old[key], dict) or not isinstance(new[key], dict):
            res[key] = new[key]
        else:
            res[key] = deep_merge_dicts(old=old[key], new=new[key])
    for key in old.keys() - overlapping_keys:
        res[key] = copy.deepcopy(old[key])
    for key in new.keys() - overlapping_keys:
        res[key] = copy.deepcopy(new[key])
    return res
