import pytest


class TaxiExperiments:
    def __init__(self, mongodb, experiments_class):
        self.mongodb = mongodb
        self.experiments_class = experiments_class

    def set_value(self, values):
        values = {name: {} for name in values}
        _update_experiments_in_db(self.experiments_class, self.mongodb, values)


@pytest.fixture
def order_experiments(mongodb, _experiments10_support):
    return TaxiExperiments(mongodb, 'experiments')


@pytest.fixture
def user_experiments(mongodb, _experiments10_support):
    return TaxiExperiments(mongodb, 'user_experiments')


@pytest.fixture(autouse=True)
def _experiments10_support(request, mongodb):
    _update_experiments(
        'user_experiments', 'user_experiments', request, mongodb,
    )
    _update_experiments(
        'order_experiments', 'experiments', request, mongodb,
    )
    _update_experiments(
        'driver_experiments', 'driver_experiments', request, mongodb,
        tmpl={'active': True, 'version': '>=1'},
    )


def _merge_dicts(dict_0, *args):
    z = dict_0.copy()
    for dict_i in args:
        z.update(dict_i)
    return z


def _update_experiments(marker_name, static_id, request, mongodb, tmpl=None):
    if tmpl is None:
        tmpl = {}
    marker = request.node.get_marker(marker_name)
    if not marker or not marker.args:
        return
    experiments = {name: {} for name in marker.args}
    experiments.update(marker.kwargs)
    _update_experiments_in_db(static_id, mongodb, experiments, tmpl)


def _update_experiments_in_db(static_id, mongodb, experiments, tmpl=None):
    if tmpl is None:
        tmpl = {}
    mongodb.static.update(
        {'_id': static_id},
        {
            '$push': {
                'rules': {
                    '$each': [
                        _merge_dicts(tmpl, {
                            'name': name,
                        }, extra) for name, extra in experiments.items()
                    ],
                },
            },
        }, upsert=True,
    )
