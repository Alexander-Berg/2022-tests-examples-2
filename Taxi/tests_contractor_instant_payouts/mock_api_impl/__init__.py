from . import billing_replication
from . import contractor_instant_payouts_modulbank
from . import contractor_instant_payouts_mozen
from . import contractor_instant_payouts_qiwi
from . import driver_orders
from . import driver_profiles
from . import fleet_antifraud
from . import fleet_offers
from . import fleet_parks
from . import fleet_transactions_api
from . import interpay
from . import parks
from . import parks_replica
from . import personal


_SERVICES = [
    billing_replication,
    contractor_instant_payouts_modulbank,
    contractor_instant_payouts_mozen,
    contractor_instant_payouts_qiwi,
    driver_profiles,
    fleet_parks,
    interpay,
    parks_replica,
    parks,
    fleet_offers,
    fleet_transactions_api,
    driver_orders,
    fleet_antifraud,
    personal,
]


def setup(load_yaml, mockserver):
    context = load_yaml('mock_api.yaml')
    return {s.NAME: s.setup(context, mockserver) for s in _SERVICES}
