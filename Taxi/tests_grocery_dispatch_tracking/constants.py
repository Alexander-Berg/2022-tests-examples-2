import enum

# Constant samples
ORDER_ID = '06e24e27fd584ee1a5ebec051d308e10-grocery'
ORDER_ID_2 = '06e24e27fd584ee1a5ebec051d308e11-grocery'
PERFORMER_ID = (
    '05941f975c604bcebc1933864bd18f41_4bc5f30599b940368403830a932c2f3d'
)
PERFORMER_ID_2 = (
    '05941f975c604bcebc1933864bd18f41_4bc5f30599b940368403830a932c2f3e'
)
DEPOT_ID_LEGACY = '12345'
DEPOT_ID_LEGACY_2 = '12346'

SHIFT_ID = 'shift_1'
NOW = '2021-08-01T09:00:00+00:00'

DELIVERY_ID = '05941f975c604bcebc1933864bd18f41_1'
DELIVERY_ID_1 = DELIVERY_ID
DELIVERY_ID_2 = DELIVERY_ID[:-1] + '2'

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'


class ShiftStatus(str, enum.Enum):
    open = 'open'
    close = 'close'
    pause = 'pause'
    unpause = 'unpause'
