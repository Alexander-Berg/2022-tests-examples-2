# pylint: disable=import-only-modules, unsubscriptable-object, invalid-name
# flake8: noqa IS001, I202
from datetime import datetime

from tests_grocery_performer_watcher import events

DEPOT_ID = '12345'
DEPOT_LOCATION = [37.656090259552, 55.73674252164294]
ORDER_ID = '451ae655d0a84c7c98a195f6e295bcb3-grocery'
CLAIM_ID = 'CLAIM_ID_1'
REGION_ID = 123
TIMEZONE = 'Europe/Moscow'
TASK_ID = 'TASK_UNIQUE_ID'

PARK_ID = '05941f975c604bcebc1933864bd18f41'
PROFILE_ID = '4bc5f30599b940368403830a932c2f3d'

# (park_id)_(driver_id) or (dbid_uuid)
PERFORMER_ID = f'{PARK_ID}_{PROFILE_ID}'
WAYBILL_REF = 'logistic-dispatch/7d246299-8b70-484c-ba11-127319ac98b6'
WAYBILL_REF_1 = WAYBILL_REF
WAYBILL_REF_2 = 'logistic-dispatch/7d246299-8b70-484c-ba11-127319ac98b7'

TS = datetime.fromisoformat('2021-08-01T09:00:00+00:00')


MATCHED_EVENT = events.GroceryOrderMatchedEvent(
    performer_id=PERFORMER_ID,
    order_id=ORDER_ID,
    depot_id=DEPOT_ID,
    delivery_type='courier',
    claim_id=CLAIM_ID,
    timestamp=TS.isoformat(),
)
