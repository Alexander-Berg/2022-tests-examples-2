from . import dac
from . import feeds
from . import fleet_parks
from . import fleet_payouts
from . import parks

_SERVICES = [parks, feeds, dac, fleet_payouts, fleet_parks]


def setup(load_yaml, mockserver):
    context = load_yaml('mock_api.yaml')
    return {s.NAME: s.setup(context, mockserver) for s in _SERVICES}
