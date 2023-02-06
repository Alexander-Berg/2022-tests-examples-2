import copy

import pytest


_K_DEFAULT = '__default__'
_KNOWN_FEATURES = {
    'idm_add_nodes_for_new_service',
    'idm_request_roles_for_new_service',
    'internal_add_nodes_for_service',
    'sync_old_system_to_new',
}


def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'roles_features_on: enables given roles features',
    )
    config.addinivalue_line(
        'markers', 'roles_features_off: disables given roles features',
    )


@pytest.fixture(autouse=True)
def _roles_features(request, taxi_config):
    updates = {}
    old_values = copy.deepcopy(
        taxi_config.get('CLOWNDUCTOR_NEW_IDM_SYSTEM_USAGE'),
    )

    for marker_name, value in [
            ('roles_features_on', True),
            ('roles_features_off', False),
    ]:
        for marker in request.node.iter_markers(marker_name):
            diff = set(marker.args) - _KNOWN_FEATURES
            assert not diff, 'passed unknown features: {}'.format(
                ', '.join(diff),
            )
            updates.update((x, value) for x in marker.args)

    if not updates:
        yield taxi_config
        return

    values = copy.deepcopy(old_values)
    old = values[_K_DEFAULT][_K_DEFAULT][_K_DEFAULT]
    values[_K_DEFAULT][_K_DEFAULT][_K_DEFAULT] = {**old, **updates}
    taxi_config.set(CLOWNDUCTOR_NEW_IDM_SYSTEM_USAGE=values)

    yield taxi_config

    taxi_config.set(CLOWNDUCTOR_NEW_IDM_SYSTEM_USAGE=old_values)
