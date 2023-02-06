import copy

import pytest


class _Grants:
    def __init__(self):
        self.grants = []

    @property
    def _last_id(self):
        if not self.grants:
            return 0
        return max(x['grand']['id'] for x in self.grants)

    def add_dev_approver(self, login, scope):
        self.grants.append(
            {
                'grand': {'id': self._next_id(), 'login': login, 'role_id': 1},
                'role': self._make_role('deploy_approve_programmer', scope),
                'related_slugs': [],
            },
        )
        return self

    def add_dev_sandbox_approver(self, login, scope):
        self.grants.append(
            {
                'grand': {'id': self._next_id(), 'login': login, 'role_id': 1},
                'role': self._make_role(
                    'deploy_approve_sandbox_programmer', scope,
                ),
                'related_slugs': [],
            },
        )

    def add_manager_approver(self, login, scope):
        self.grants.append(
            {
                'grand': {'id': self._next_id(), 'login': login, 'role_id': 1},
                'role': self._make_role('deploy_approve_manager', scope),
                'related_slugs': [],
            },
        )
        return self

    def _next_id(self) -> int:
        return self._last_id + 1

    @staticmethod
    def _make_role(slug, scope):
        assert scope['type'] in ['namespace', 'project', 'service']
        return {
            'id': 1,
            'slug': slug,
            'name': {'en': slug, 'ru': slug},
            'reference': {
                'external_slug': str(scope['id']),
                'type': scope['type'],
            },
        }


@pytest.fixture
def clowny_roles_grants(mock_clowny_roles):
    _mock = _Grants()

    @mock_clowny_roles('/grands/v1/retrieve/')
    def _handler(request):
        _grants = _mock.grants[:]
        filters = request.json['filters']
        if filters.get('login'):
            _login = request.json['filters']['login']
            _grants = [x for x in _grants if x['grand']['login'] == _login]
        if filters.get('related_role'):
            _role = filters['related_role']
            _grants = [x for x in _grants if x['role']['slug'] == _role]
        if filters.get('references'):
            _references = {
                (x['external_slug'], x['type']) for x in filters['references']
            }

            def _one_of(grant) -> bool:
                _ref = grant['role']['reference']
                return (_ref['external_slug'], _ref['type']) in _references

            _grants = [x for x in _grants if _one_of(x)]
        return {'grands': sorted(_grants, key=lambda x: x['grand']['id'])}

    return _mock


_K_DEFAULT = '__default__'
_KNOWN_FEATURES = {'approve_check', 'full_info'}


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
