import copy


MULTIOFFER_TIMEOUT = 22
LAG_COMPENSATION_TIMEOUT = 2
OFFER_TIMEOUT = 20
PLAY_TIMEOUT = 15
DISPATCH_TYPE = 'test_multioffer'

DEFAULT_PARAMS = {
    'allowed_classes': ['econom'],
    'order_id': 'order_id',
    'order': {
        'nearest_zone': 'moscow',
        'user_phone_id': 'user_phone_id',
        'request': {'class': ['econom']},
    },
    'point': [50.276871024, 53.233412039],
    'lookup': {
        'generation': 1,
        'start_eta': 1604055148.006,
        'version': 2,
        'next_call_eta': 1604055164.614,
        'wave': 2,
    },
    'callback': {'url': 'some_url', 'timeout_ms': 500, 'attempts': 2},
}


def experiment3(
        tag,
        contractor_limit=10,
        contractor_threshold=2,
        enable_doaa=False,
        locked_dispatch=None,
        tags_limit=None,
        is_auction=False,
        disable_chains=False,
        max_waves=1,
):
    test_multioffer = {
        'tags_to_match': [tag],
        'tags_to_play': [tag],
        'contractor_limit': contractor_limit,
        'contractor_threshold': contractor_threshold,
        'multioffer_timeout': MULTIOFFER_TIMEOUT,
        'lag_compenstation_timeout': LAG_COMPENSATION_TIMEOUT,
        'offer_timeout': OFFER_TIMEOUT,
        'play_timeout': PLAY_TIMEOUT,
        'is_auction': is_auction,
        'max_waves': max_waves,
    }

    if tags_limit:
        test_multioffer['tags_to_play'] = [x[0] for x in tags_limit]
        test_multioffer['tags_to_play_limit'] = {
            x[0]: x[1] for x in tags_limit
        }

    return {
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'name': 'contractor_orders_multioffer_dispatcher_stub_settings',
        'consumers': ['contractor-orders-multioffer/dispatcher'],
        'clauses': [],
        'default_value': {
            'enable_doaa_call': enable_doaa,
            'disable_chains': disable_chains,
            'locked_dispatch': locked_dispatch,
            DISPATCH_TYPE: test_multioffer,
        },
    }


def default_params():
    return copy.deepcopy(DEFAULT_PARAMS)


def create_version_settings(multioffer_version, chain_version='1.00'):
    return {
        'TAXIMETER_VERSION_SETTINGS_BY_BUILD': {
            '__default__': {
                'feature_support': {
                    'multioffer': multioffer_version,
                    'multioffer_chain': chain_version,
                },
            },
        },
    }


def create_freeze_settings(enable_freeze):
    return {
        'CONTRACTOR_ORDERS_MULTIOFFER_FREEZING_SETTINGS': {
            'enable': enable_freeze,
            'freeze_duration': 60,
        },
    }
