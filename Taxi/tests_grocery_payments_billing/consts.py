from . import models

ORDER_ID = 'order_id-grocery'
EATS_ORDER_ID = '211010-12345'
DEPOT_REGION_ID = 213
CART_ID = '28fe4a6e-c00d-45c1-a34e-6329c4a4e329'
INVOICE_ID = 'invoice-id-xxx-2004'
EATS_COURIER_ID = 'eats-courier-id-123'
COURIER_VAT = '99'
ISRAEL_COURIER_VAT = '17'
FRANCE_COURIER_VAT = '20'
GREAT_BRITAIN_COURIER_VAT = '20'
TRANSPORT_TYPE = 'car'
YANDEX_UID = 'user-uid'
PERSONAL_PHONE_ID = 'some_phone_id_111'
USER_IP = '1.1.1.1'

NOW = '2021-02-19T12:40:00+00:00'
FINISH_STARTED = '2021-06-12T12:40:00+00:00'
PAYMENT_FINISHED = '2020-06-17T12:40:00+00:00'
OPERATION_ID = 'operation-id-xxx'
TERMINAL_ID = 'terminal_id'
EXTERNAL_PAYMENT_ID = 'external_payment_id'
BALANCE_CLIENT_ID = '28349765'
DEPOT_ID = '71249'
OEBS_DEPOT_ID = 'OEBS_' + DEPOT_ID
DEPOT_TIN = 'depot_tin'

RECEIPT_ID = 'receipt_id-grocery'

COUNTRIES = [
    models.Country.Russia,
    models.Country.Israel,
    models.Country.France,
    models.Country.GreatBritain,
]

COMPANY_TYPE = 'company-type'
CONTRACT_ID = 'contract-id'
FIRM_ID = 'firm-id'
IGNORE_IN_BALANCE = False
SERVICE_ID = 629
AGGLOMERATION = 'agglomeration'

WITHOUT_VAT = '-1'
