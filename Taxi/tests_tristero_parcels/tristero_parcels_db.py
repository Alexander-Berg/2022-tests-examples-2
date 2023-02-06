from tests_tristero_parcels import sql_queries


DEFAULT_USER_ID = 'default-user-id'
ORDER_ID_TEMPLATE = '01234567-89ab-cdef-000a-{:012d}'
PARCEL_ID_TEMPLATE = '01234567-89ab-cdef-000f-{:06d}{:06d}'
DEPOT_ID_TEMPLATE = '0123456789abcdef{:028d}'
VENDOR_TEMPLATE = 'vendor-{:06d}'
PARCEL_VENDOR_TEMPLATE = 'vendor-{:06d}-{:06d}'
REF_ORDER_TEMPLATE = 'ref-order-{:06d}'
BARCODE_TEMPLATE = '1{}_{}'
PARCEL_WMS_ID_TEMPLATE = '98765432-10ab-cdef-0000-{:06d}{:06d}'
DESCRIPTION_TEMPLATE = 'Parcel {} description'


def _execute_sql_query(sql_query, pgsql):
    db = pgsql['tristero_parcels']
    cursor = db.cursor()
    cursor.execute(sql_query)


def _fetch_from_sql(sql_query, pgsql):
    db = pgsql['tristero_parcels']
    cursor = db.cursor()
    cursor.execute(sql_query)
    return cursor.fetchall()


class TristeroParcelsDbAgent:
    def __init__(self, pgsql):
        self._pgsql = pgsql
        self._in_transaction = False
        self._sql_query = ''
        self._orders = {}

    def begin_transaction(self):
        assert not self._in_transaction
        self._in_transaction = True

    def commit_transaction(self):
        assert self._in_transaction

        sql_query = sql_queries.transaction(self._sql_query)
        _execute_sql_query(sql_query, pgsql=self._pgsql)

        self._sql_query = ''
        self._in_transaction = False

    def __enter__(self):
        self.begin_transaction()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if exception_type is None:
            self.commit_transaction()

    def apply_sql_query(self, sql_query, as_transaction=False):
        if self._in_transaction:
            self._sql_query += f'\n{sql_query}'
        else:
            if as_transaction:
                sql_query = sql_queries.transaction(sql_query)
            _execute_sql_query(sql_query, pgsql=self._pgsql)

    def fetch_from_sql(self, sql_query):
        return _fetch_from_sql(sql_query, pgsql=self._pgsql)

    def add_order(
            self,
            test_order_id,
            ref_order=None,
            user_id=None,
            depot_id=None,
            vendor=1,
            status='reserved',
            token='some-token',
            timeslot_start=None,
            timeslot_end=None,
            personal_phone_id=None,
            customer_address=None,
            customer_location=None,
            customer_meta=None,
            price=None,
            request_kind=None,
    ):
        if vendor is None:
            vendor = 1
        assert (
            isinstance(test_order_id, int)
            and test_order_id > 0
            and test_order_id not in self._orders
        )
        if ref_order:
            for order in [
                    o
                    for o in self._orders.values()
                    if o.ref_order == ref_order
            ]:
                assert order.vendor != vendor

        order = Order(
            test_order_id=test_order_id,
            tristero_parcels_db_agent=self,
            ref_order=ref_order,
            user_id=user_id,
            depot_id=depot_id,
            vendor_id=vendor,
            status=status,
            token=token,
            timeslot_start=timeslot_start,
            timeslot_end=timeslot_end,
            personal_phone_id=personal_phone_id,
            customer_address=customer_address,
            customer_location=customer_location,
            customer_meta=customer_meta,
            price=price,
            request_kind=request_kind,
        )

        self._orders[test_order_id] = order

        return order

    def make_depot_id(self, test_depot_id):
        assert isinstance(test_depot_id, int) and test_depot_id > 0
        return DEPOT_ID_TEMPLATE.format(test_depot_id)

    def flush_distlocks(self):
        _execute_sql_query(sql_queries.flush_distlocks(), self._pgsql)


class Order:
    def __init__(
            self,
            test_order_id,
            tristero_parcels_db_agent,
            ref_order=None,
            user_id=None,
            depot_id=None,
            vendor_id=1,
            status='reserved',
            token=None,
            timeslot_start=None,
            timeslot_end=None,
            personal_phone_id=None,
            customer_address=None,
            customer_location=None,
            customer_meta=None,
            price=None,
            request_kind=None,
    ):
        if depot_id is None:
            depot_id = tristero_parcels_db_agent.make_depot_id(1)
        if user_id is None:
            user_id = DEFAULT_USER_ID

        self._test_order_id = test_order_id
        self._order_id = ORDER_ID_TEMPLATE.format(test_order_id)
        self._uid = user_id
        self._depot_id = depot_id
        self._vendor = (
            VENDOR_TEMPLATE.format(vendor_id)
            if isinstance(vendor_id, int)
            else vendor_id
        )
        if ref_order is None:
            self._ref_order = REF_ORDER_TEMPLATE.format(test_order_id)
        else:
            self._ref_order = ref_order
        self._status = status
        self._tristero_parcels_db_agent = tristero_parcels_db_agent
        self._parcels = {}
        self._token = token
        self._timeslot_start = timeslot_start
        self._timeslot_end = timeslot_end
        self._personal_phone_id = personal_phone_id
        self._customer_address = customer_address
        self._customer_location = customer_location
        self._customer_meta = {} if customer_meta is None else customer_meta
        self._updated = None
        self._price = price
        self._request_kind = request_kind

        add_order_query = sql_queries.add_order(
            order_id=self._order_id,
            uid=self._uid,
            depot_id=self._depot_id,
            vendor=self._vendor,
            ref_order=self._ref_order,
            status=self._status,
            token=self._token,
            timeslot_start=self._timeslot_start,
            timeslot_end=self._timeslot_end,
            personal_phone_id=self._personal_phone_id,
            customer_address=self._customer_address,
            customer_location=self._customer_location,
            customer_meta=self._customer_meta,
            price=self._price,
            request_kind=self._request_kind,
        )

        tristero_parcels_db_agent.apply_sql_query(
            add_order_query, as_transaction=True,
        )

    def add_parcel(
            self,
            test_parcel_id,
            *,
            status='reserved',
            in_stock_quantity=0,
            partner_id=None,
            status_meta=None,
            updated=None,
    ):
        assert (
            isinstance(test_parcel_id, int)
            and test_parcel_id > 0
            and test_parcel_id not in self._parcels
        )

        parcel = Parcel(
            test_parcel_id=test_parcel_id,
            test_order_id=self._test_order_id,
            tristero_parcels_db_agent=self._tristero_parcels_db_agent,
            order_id=self._order_id,
            status=status,
            vendor_id=self.vendor,
            in_stock_quantity=in_stock_quantity,
            partner_id=partner_id,
            status_meta=status_meta,
        )

        self._parcels[test_parcel_id] = parcel

        if updated is not None:
            parcel.set_updated(updated)

        return parcel

    def set_status(self, new_status):
        set_order_status_query = sql_queries.set_order_status(
            self._order_id, new_status,
        )
        self._tristero_parcels_db_agent.apply_sql_query(set_order_status_query)

    def set_updated(self, timestamp):
        set_updated_query = sql_queries.set_order_updated(
            self._order_id, timestamp,
        )
        self._tristero_parcels_db_agent.apply_sql_query(set_updated_query)

    def update_from_db(self):
        select_order_query = sql_queries.select_order(self._order_id)
        data = self._tristero_parcels_db_agent.fetch_from_sql(
            select_order_query,
        )

        self._order_id = data[0][0]
        self._uid = data[0][1]
        self._depot_id = data[0][2]
        self._vendor = data[0][3]
        self._ref_order = data[0][4]
        self._status = data[0][5]
        self._updated = data[0][6]
        self._timeslot_start = data[0][7]
        self._timeslot_end = data[0][8]
        self._request_kind = data[0][9]

    def insert_dispatch_schedule(
            self,
            dispatch_start,
            dispatch_end,
            dispatched=False,
            dispatch_id=None,
    ):
        insert_dispatch_schedule = sql_queries.insert_order_dispatch_schedule(
            self._order_id,
            dispatch_start,
            dispatch_end,
            dispatched,
            dispatch_id,
        )
        self._tristero_parcels_db_agent.apply_sql_query(
            insert_dispatch_schedule,
        )

    @property
    def order_id(self):
        return self._order_id

    @property
    def uid(self):
        return self._uid

    @property
    def depot_id(self):
        return self._depot_id

    @property
    def vendor(self):
        return self._vendor

    @property
    def ref_order(self):
        return self._ref_order

    @property
    def token(self):
        return self._token

    @property
    def status(self):
        return self._status

    @property
    def parcels(self):
        ret = []
        for k in self._parcels:
            ret.append(self._parcels[k])
        return ret

    @property
    def items(self):
        return self._parcels

    @property
    def updated(self):
        return self._updated

    @property
    def timeslot_start(self):
        return self._timeslot_start

    @property
    def timeslot_end(self):
        return self._timeslot_end

    @property
    def price(self):
        return self._price

    @property
    def request_kind(self):
        return self._request_kind

    def customer_meta(self):
        return self._customer_meta


class Parcel:
    def __init__(
            self,
            test_parcel_id,
            test_order_id,
            tristero_parcels_db_agent,
            order_id,
            status,
            vendor_id=1,
            barcode=None,
            partner_id=None,
            measurements=(1, 1, 1, 1),
            status_meta=None,
            in_stock_quantity=0,
    ):
        self._test_parcel_id = test_parcel_id
        self._item_id = PARCEL_ID_TEMPLATE.format(
            test_order_id, test_parcel_id,
        )
        self._order_id = order_id
        self._vendor = (
            PARCEL_VENDOR_TEMPLATE.format(test_order_id, vendor_id)
            if isinstance(vendor_id, int)
            else vendor_id
        )
        self._barcode = (
            BARCODE_TEMPLATE.format(self._item_id, vendor_id)
            if barcode is None
            else barcode
        )
        self._partner_id = partner_id
        self._wms_id = PARCEL_WMS_ID_TEMPLATE.format(
            test_order_id, test_parcel_id,
        )
        self._measurements = measurements
        self._status = status
        self._status_meta = {} if status_meta is None else status_meta
        self._in_stock_quantity = in_stock_quantity
        self._description = DESCRIPTION_TEMPLATE.format(self._item_id)
        self._tristero_parcels_db_agent = tristero_parcels_db_agent
        self._updated = None

        add_parcel_query = sql_queries.add_parcel(
            item_id=self._item_id,
            order_id=self._order_id,
            vendor=self._vendor,
            barcode=self._barcode,
            partner_id=self._partner_id,
            wms_id=self._wms_id,
            measurements=self._measurements,
            status=self._status,
            description=self._description,
            status_meta=self._status_meta,
            in_stock_quantity=self._in_stock_quantity,
        )

        tristero_parcels_db_agent.apply_sql_query(
            add_parcel_query, as_transaction=True,
        )

    def update_from_db(self):
        select_parcel_query = sql_queries.select_parcel(self._item_id)
        data = self._tristero_parcels_db_agent.fetch_from_sql(
            select_parcel_query,
        )

        self._item_id = data[0][0]
        self._order_id = data[0][1]
        self._vendor = data[0][2]
        self._barcode = data[0][3]
        self._partner_id = data[0][4]
        self._wms_id = data[0][5]
        self._measurements = data[0][6]
        self._status = data[0][7]
        self._status_meta = data[0][8]
        self._in_stock_quantity = data[0][9]
        self._updated = data[0][10]

    def set_status(self, new_status, status_meta=None):
        set_parcel_status_query = sql_queries.set_parcel_status(
            self._item_id,
            new_status,
            {} if status_meta is None else status_meta,
        )
        self._tristero_parcels_db_agent.apply_sql_query(
            set_parcel_status_query,
        )

    def insert_deffered_acceptance(
            self,
            real_acceptance_time='NOW()',
            new_acceptance_time=None,
            accepted=False,
    ):
        insert_deffered_acceptance = sql_queries.insert_deffered_acceptance(
            self._item_id, real_acceptance_time, new_acceptance_time, accepted,
        )
        self._tristero_parcels_db_agent.apply_sql_query(
            insert_deffered_acceptance,
        )

    def set_updated(self, timestamp):
        set_updated_query = sql_queries.set_parcel_updated(
            self._item_id, timestamp,
        )
        self._tristero_parcels_db_agent.apply_sql_query(set_updated_query)

    @property
    def item_id(self):
        return self._item_id

    @property
    def order_id(self):
        return self._order_id

    @property
    def vendor(self):
        return self._vendor

    @property
    def barcode(self):
        return self._barcode

    @property
    def partner_id(self):
        return self._partner_id

    @property
    def wms_id(self):
        return self._wms_id

    @property
    def product_key(self):
        return self._wms_id + ':st-pa'

    @property
    def measurements(self):
        return self._measurements

    @property
    def status(self):
        return self._status

    @property
    def status_meta(self):
        return self._status_meta

    @property
    def description(self):
        return self._description

    @property
    def in_stock_quantity(self):
        return self._in_stock_quantity

    @property
    def updated(self):
        return self._updated

    def get_measurements_as_object(self):
        return {
            'width': self._measurements[0],
            'height': self._measurements[1],
            'length': self._measurements[2],
            'weight': self._measurements[3],
        }
