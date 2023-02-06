from . import driver_profiles
from . import fines_1c
from . import fleet_reports_storage
from . import fleet_vehicles
from . import personal
from . import yql

_SERVICES = [
    driver_profiles,
    fines_1c,
    fleet_vehicles,
    fleet_reports_storage,
    personal,
    yql,
]


def setup(context, mockserver):
    return {s.NAME: s.setup(context, mockserver) for s in _SERVICES}
