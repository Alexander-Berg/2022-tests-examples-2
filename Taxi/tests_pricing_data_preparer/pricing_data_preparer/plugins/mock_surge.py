# pylint: disable=redefined-outer-name, import-error
import copy

from pricing_extended import mocking_base
import pytest


def _fill_class(value, surcharge=None, alpha=0.0, beta=0.0, name=None):
    surge = {
        'name': name if name else 'undefined',
        'surge': {'value': value},
        'value_raw': value,
        'calculation_meta': {
            'smooth': {'point_a': {'value': value, 'is_default': False}},
            'counts': {
                'radius': 3000,
                'free': 6,
                'free_chain': 0,
                'total': 6,
                'pins': 0,
            },
            'reason': 'no',
            'viewport': {'br': [-0.01, -0.01], 'tl': [0.01, 0.01]},
        },
    }
    if surcharge:
        surge['surge']['surcharge'] = {
            'value': surcharge,
            'alpha': alpha,
            'beta': beta,
        }
    return surge


class SurgerContext(mocking_base.BasicMock):
    def __init__(self):
        super().__init__()
        self.one_class = _fill_class(1)
        self.patches = {}
        self.add_explicit_antisurge = False
        self.due = None
        self.user_id = 'some_user_id'
        self.phone_id = 'some_phone_id'
        self.user_app = None
        self.response = None

    def set_surge(self, surge, surcharge=None, alpha=0.0, beta=0.0, name=None):
        """Set default surge if name is None, or patch for class 'name'"""
        if not name:
            self.one_class = _fill_class(surge, surcharge, alpha, beta)
        else:
            self.patches[name] = (
                _fill_class(surge, surcharge, alpha, beta, name),
            )

    def set_explicit_antisurge(self):
        self.one_class.update({'explicit_antisurge': {'value': 0.5}})

    def collect_response(self, classes_list, point, point_b):
        classes = []
        bottom_right = [point[0] - 0.01, point[1] - 0.01]
        top_left = [point[0] + 0.01, point[1] + 0.01]
        for cat in classes_list:
            if cat not in self.patches:
                new_class = copy.deepcopy(self.one_class)
                new_class['name'] = cat
            else:
                new_class = self.patches[cat]
            new_class['calculation_meta']['viewport'] = {
                'br': bottom_right,
                'tl': top_left,
            }
            if point_b:
                new_class['calculation_meta']['smooth']['point_b'] = {
                    'value': 1.0,
                    'is_default': False,
                }
            classes.append(new_class)

        self.response = {
            'is_cached': False,
            'calculation_id': '012345678901234567890123',
            'zone_id': 'msk__basmannaya',
            'classes': classes,
            'experiment_id': 'exp_id',
            'experiment_name': 'exp_name',
            'experiment_layer': 'default',
            'experiments': [],
            'experiment_errors': [],
        }

    def clear(self):
        self.one_class = _fill_class(self.one_class, 1)
        self.patches = {}

    def check_request(self, data):
        assert data.get('use_cache')
        if self.due:
            assert 'due' in data
            assert self.due == data['due']
        else:
            assert 'due' not in data

        if self.user_id:
            assert self.user_id == data.get('user_id')
            assert self.phone_id == data.get('phone_id')

        if self.user_app:
            assert self.user_app == data['application']

    def set_due(self, due):
        self.due = due

    def set_user_id(self, user_id):
        self.user_id = user_id
        self.phone_id = user_id

    def set_phone_id(self, phone_id):
        self.phone_id = phone_id

    def set_user_app(self, user_app):
        self.user_app = {
            k: user_app[k] for k in ('name', 'version', 'platform_version')
        }


@pytest.fixture
def surger():
    return SurgerContext()


@pytest.fixture
def mock_surger(mockserver, surger):
    @mockserver.json_handler('/surge-calculator/v1/calc-surge')
    def calculator_handler(request):
        data = request.json
        surger.check_request(data)
        surger.collect_response(
            data.get('classes', []), data['point_a'], data.get('point_b'),
        )
        look = surger.process(mockserver)
        return look

    return calculator_handler
