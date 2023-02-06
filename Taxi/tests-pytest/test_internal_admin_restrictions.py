# -*- coding: utf-8 -*-
import pytest

from taxi.core import async
from taxi.internal import admin_restrictions

import helpers


class Request(object):
    login = None

    def __init__(self, login=None, groups=None, superuser=False):
        self.login = login
        if groups is None:
            self.groups = []
        else:
            self.groups = groups
        self.superuser = superuser


CATEGORY_PRESET_CONFIG = {
  "logistics": {
    "__default__": [
      "express",
    ]
  },
  "passenger_basic": {
    "__default__": [
      "start",
    ],
    "mirny": [
      "start",
      "uberstart",
    ]
  },
  "passenger_functional": {
    "__default__": [
      "minivan",
    ]
  },
  "passenger_luxury": {
    "__default__": []
  }
}
DEFAULT_CONFIG = {
    admin_restrictions.COUNTRY_ACCESS_CONFIG_NAME: {
        '__all__': {
            'logins': [
                'superuser_login',
            ],
            'groups': [
                'superuser_group',
            ],
        },
        'rus': {
            'logins': [
                'khlyzov',
                'armen',
            ],
            'groups': [
                'russian_manager',
            ],
        },
        'geo': {
            'logins': [
                'armen',
            ],
            'groups': [
                'caucasian_manager',
            ],
        },
        'rou': {
            'logins': [
                'khlyzov',
            ],
        },

        'blr': {
            'logins': [
                'khlyzov',
                'armen',
            ],
        },
        'arm': {
            'groups': [
                'armenian_manager',
                'caucasian_manager',
            ],
        },
        'kaz': {
            'logins': [],
            'groups': [],
        },
    },
    admin_restrictions.CATEGORY_ACCESS_CONFIG_NAME: {
        "__all__": {
            'logins': [
                'superuser_login'
            ],
            'groups': [
                'superuser_group'
            ],
        },
        "logistics": {
            'logins': [],
            'groups': [],
        },
        "passenger_basic": {
            'logins': [
                'khlyzov',
                'armen',
            ],
            'groups': [
                'russian_manager',
            ],
        },
        "passenger_functional": {
            'logins': [
                'armen',
            ],
            'groups': [
                'caucasian_manager',
            ],
        },
        "passenger_luxury": {
            'logins': [
                'khlyzov',
            ],
        },
        "technical": {
            'logins': [
                'armen',
            ],
        }
    }
}
DEFAULT_CONSUMER = 'backend/user_info'
MANY_HANDLES_CONFIG = {
    admin_restrictions.COUNTRY_ACCESS_CONFIG_NAME: DEFAULT_CONFIG[
        admin_restrictions.COUNTRY_ACCESS_CONFIG_NAME
    ],
    admin_restrictions.CATEGORY_ACCESS_CONFIG_NAME: DEFAULT_CONFIG[
        admin_restrictions.CATEGORY_ACCESS_CONFIG_NAME
    ]
}


def _patch_internals(patch, config):

    @patch('taxi.external.experiments3.get_config_values')
    @async.inline_callbacks
    def _get_experiments(consumer, config_name, *args, **kwargs):
        yield
        if config_name in config:
            resp = [
                admin_restrictions.experiments3.ExperimentsValue(
                    config_name, config[config_name],
                ),
            ]
        else:
            resp = []
        async.return_value(resp)


case = helpers.case_getter(
    'request_obj country error config',
    config=DEFAULT_CONFIG,
    error=None,
)


@pytest.mark.parametrize(
    case.params,
    [
        # user in config has access
        case(
            request_obj=Request(login='khlyzov'),
            country='rus',
        ),
        case(
            request_obj=Request(login='armen', groups=[]),
            country='blr',
        ),
        # groups in config have access
        case(
            request_obj=Request(groups=['russian_manager']),
            country='rus',
        ),
        case(
            request_obj=Request(groups=['armenian_manager'], login='other'),
            country='arm',
        ),
        # anyone has access anywhere if no config
        case(
            request_obj=Request(groups=[], login='nologin'),
            country='any',
            config={},
        ),
        # superuser from __all__ countries
        case(
            request_obj=Request(groups=[], login='superuser_login'),
            country='any',
        ),
        # supergroup from __all__ countries
        case(
            request_obj=Request(groups=['superuser_group'], login='other'),
            country='any',
        ),
        # user not in config has no access
        case(
            request_obj=Request(login='not_khlyzov'),
            country='rus',
            error=(
                admin_restrictions.RestrictionError,
                'User not_khlyzov has no access to {} in country rus'.format(
                    DEFAULT_CONSUMER
                )
            )
        ),
        case(
            request_obj=Request(login='not_khlyzov'),
            country='blr',
            error=(
                admin_restrictions.RestrictionError,
                'User not_khlyzov has no access to {} in country blr'.format(
                    DEFAULT_CONSUMER
                )
            )
        ),
        # groups not in config have no access
        case(
            request_obj=Request(groups=['not_russian_manager']),
            country='rus',
            error=(
                admin_restrictions.RestrictionError,
                'User None has no access to {} in country rus'.format(
                    DEFAULT_CONSUMER
                )
            )
        ),
        case(
            request_obj=Request(groups=['not_russian_manager'], login='other'),
            country='arm',
            error=(
                admin_restrictions.RestrictionError,
                'User other has no access to {} in country arm'.format(
                    DEFAULT_CONSUMER
                )
            )
        ),
        # country without any accessors
        case(
            request_obj=Request(login='khlyzov'),
            country='kaz',
            error=(
                admin_restrictions.RestrictionError,
                'User khlyzov has no access to {} in country kaz'.format(
                    DEFAULT_CONSUMER
                )
            )
        ),
    ]
)
@pytest.inline_callbacks
def test_check_country_restrictions(patch, request_obj, country, error,
                                    config):
    _patch_internals(patch, config)

    if error is None:
        yield admin_restrictions.check_country_restrictions(
            request_obj, 'backend/user_info', country
        )
    else:
        error_type, error_message = error
        with pytest.raises(error_type) as exc_info:
            yield admin_restrictions.check_country_restrictions(
                request_obj, 'backend/user_info', country
            )
        assert exc_info.value.message == error_message


case = helpers.case_getter(
    'request_obj categories zone error config',
    config=DEFAULT_CONFIG,
    error=None,
    zone='default_zone'
)


@pytest.mark.config(
    OPERATION_CALCULATIONS_GEOSUBVENTIONS_TARIFF_PRESETS=CATEGORY_PRESET_CONFIG
)
@pytest.mark.parametrize(
    case.params,
    [
        # user in config has access
        case(
            request_obj=Request(login='khlyzov'),
            categories={'start'},
        ),
        case(
            request_obj=Request(login='armen', groups=[]),
            categories={'start', 'minivan'},
        ),
        case(
            request_obj=Request(login='armen', groups=[]),
            categories={'start', 'minivan', 'uberstart'},
            zone='mirny'
        ),
        # groups in config have access
        case(
            request_obj=Request(groups=['russian_manager']),
            categories={'start'},
        ),
        # anyone has access anywhere if no config
        case(
            request_obj=Request(groups=[], login='nologin'),
            categories={'any'},
            config={},
        ),
        # superuser from __all__ countries
        case(
            request_obj=Request(groups=[], login='superuser_login'),
            categories={'any'},
        ),
        # supergroup from __all__ countries
        case(
            request_obj=Request(groups=['superuser_group'], login='other'),
            categories={'any'},
        ),
        # user not in config has no access
        case(
            request_obj=Request(login='not_khlyzov'),
            categories={'econom'},
            error=(
                admin_restrictions.RestrictionError,
                'User not_khlyzov has no access to presets {\'econom\': None}'
            ),
        ),
        case(
            request_obj=Request(login='not_khlyzov'),
            categories={'drive', 'business'},
            error=(
                admin_restrictions.RestrictionError,
                'User not_khlyzov has no access to presets {\'drive\': None, \'business\': None}'

            ),
        ),
        # groups not in config have no access
        case(
            request_obj=Request(groups=['not_russian_manager']),
            categories={'econom'},
            error=(
                admin_restrictions.RestrictionError,
                'User None has no access to presets {\'econom\': None}'
            ),
        ),
        case(
            request_obj=Request(groups=['not_russian_manager'], login='other'),
            categories={'econom'},
            error=(
                admin_restrictions.RestrictionError,
                'User other has no access to presets {\'econom\': None}'
            ),
        ),
        # another category among allowed categories
        case(
            request_obj=Request(login='khlyzov'),
            categories={'random_category', 'start'},
            error=(
                admin_restrictions.RestrictionError,
                'User khlyzov has no access to presets {\'random_category\': None}'
            ),
        ),
    ]
)
@pytest.inline_callbacks
def test_check_category_restrictions(patch, request_obj, categories, error,
                                    config, zone):
    _patch_internals(patch, config)

    if error is None:
        yield admin_restrictions.check_category_restrictions(
            request_obj, 'backend/user_info', categories, zone
        )
    else:
        error_type, error_message = error
        with pytest.raises(error_type) as exc_info:
            yield admin_restrictions.check_category_restrictions(
                request_obj, 'backend/user_info', categories, zone
            )
        assert exc_info.value.message == error_message


case = helpers.case_getter(
    'request_obj expected_result config',
    config=DEFAULT_CONFIG,
)


@pytest.mark.parametrize(
    case.params,
    [
        # user in config has access
        case(
            request_obj=Request(login='khlyzov'),
            expected_result={'rus', 'rou', 'blr'},
        ),
        case(
            request_obj=Request(login='armen', groups=[]),
            expected_result={'rus', 'geo', 'blr'},
        ),
        # groups in config have access
        case(
            request_obj=Request(groups=['russian_manager']),
            expected_result={'rus'},
        ),
        case(
            request_obj=Request(groups=['armenian_manager'], login='other'),
            expected_result={'arm'},
        ),
        case(
            request_obj=Request(groups=['caucasian_manager'], login='armen'),
            expected_result={'arm', 'geo', 'rus', 'blr'},
        ),
        # anyone has access if no config
        case(
            request_obj=Request(groups=[], login='nologin'),
            config={},
            expected_result=None,
        ),
        # superuser from __all__ countries
        case(
            request_obj=Request(groups=[], login='superuser_login'),
            expected_result=None,
        ),
        # supergroup from __all__ countries
        case(
            request_obj=Request(groups=['superuser_group'], login='other'),
            expected_result=None,
        ),
        # user not in config has no access to anywhere
        case(
            request_obj=Request(login='not_khlyzov'),
            expected_result=set(),
        ),
        # groups not in config have no access to anywhere
        case(
            request_obj=Request(groups=['not_russian_manager']),
            expected_result=set(),
        ),
    ]
)
@pytest.inline_callbacks
def test_get_allowed_countries(patch, request_obj, expected_result, config):
    _patch_internals(patch, config)

    result = yield admin_restrictions.get_allowed_countries(
            request_obj.login, request_obj.groups, 'backend/user_info',
        )
    assert result == expected_result


@pytest.mark.parametrize(
    case.params,
    [
        # user in config has access
        case(
            request_obj=Request(login='khlyzov'),
            expected_result={'passenger_basic', 'passenger_luxury'},
        ),
        case(
            request_obj=Request(login='armen'),
            expected_result={'passenger_basic', 'passenger_functional', 'technical'},
        ),
        # groups in config have access
        case(
            request_obj=Request(groups=['russian_manager']),
            expected_result={'passenger_basic'},
        ),
        case(
            request_obj=Request(groups=['caucasian_manager']),
            expected_result={'passenger_functional'},
        ),
        case(
            request_obj=Request(groups=['caucasian_manager'], login='armen'),
            expected_result={'passenger_basic', 'passenger_functional', 'technical'},
        ),
        # anyone has access if no config
        case(
            request_obj=Request(groups=[], login='nologin'),
            config={},
            expected_result=None,
        ),
        # superuser from __all__ countries
        case(
            request_obj=Request(groups=[], login='superuser_login'),
            expected_result=None,
        ),
        # supergroup from __all__ countries
        case(
            request_obj=Request(groups=['superuser_group'], login='other'),
            expected_result=None,
        ),
        # user not in config has no access to anywhere
        case(
            request_obj=Request(login='not_khlyzov'),
            expected_result=set(),
        ),
        # groups not in config have no access to anywhere
        case(
            request_obj=Request(groups=['not_russian_manager']),
            expected_result=set(),
        ),
    ]
)
@pytest.inline_callbacks
def test_get_allowed_category_presets(patch, request_obj, expected_result, config):
    _patch_internals(patch, config)

    result = yield admin_restrictions.get_allowed_category_presets(
            request_obj.login, request_obj.groups, 'backend/user_info',
        )
    assert result == expected_result


case = helpers.case_getter('zone categories expected_result')


@pytest.mark.asyncenv('blocking')
@pytest.mark.config(
    OPERATION_CALCULATIONS_GEOSUBVENTIONS_TARIFF_PRESETS=CATEGORY_PRESET_CONFIG
)
@pytest.mark.parametrize(
    case.params,
    [
        case(
            zone='unknown',
            categories={'express', 'start', 'minivan', 'uberstart'},
            expected_result={
                'express': 'logistics',
                'start': 'passenger_basic',
                'minivan': 'passenger_functional',
                'uberstart': None
            }
        ),
        case(
            zone='mirny',
            categories={'express', 'start', 'minivan', 'uberstart'},
            expected_result={
                'express': 'logistics',
                'start': 'passenger_basic',
                'minivan': 'passenger_functional',
                'uberstart': 'passenger_basic'
            }
        )
    ]
)
@pytest.inline_callbacks
def test_get_map_categories_to_presets(zone, categories, expected_result):
    result = yield admin_restrictions._map_categories_to_presets(
        categories, zone
    )
    assert result == expected_result
