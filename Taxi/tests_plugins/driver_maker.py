import datetime

import bson
import flatbuffers
import pytest

from fbs.tracker import ChainBusyDriver
from fbs.tracker import ChainBusyDriverList
from fbs.tracker import GeoPoint
from taxi_tests import utils


TARIFFS_MAP = {
    'business': 'comfort',
    'vip': 'business',
    'comfortplus': 'comfort_plus',
    'universal': 'wagon',
    'business2': 'comfort_plus',
}


class DriverMaker:
    """Help create drivers with specifi cpositions and properties.
    Usage example:
    def test_super_puper_test(tracker, driver_maker):
        # clean all mongo db (optional, may be skipped if you shure
        # that drivers
        # you add not conflict with existing db data)

        driver_maker.init()

        # create driver ready to get order with folowing properties
        #   uuid = uuid_1 (clid='clid', dbid='dbid')
        #   position = [37.460842, 55.722467],
        #   classes is optional (default value = ['econom'])
        #   busy_info is optional (default value = None)

        driver_maker.add_driver('uuid_1', [37.460842, 55.722467],
                                classes=['econom'], busy_info={
                                    'destination': [37.458645, 55.719260],
                                    'left_time': left_time,
                                    'left_dist': 200,
                                    'order_id': 'some_order_id'
                                })
        driver_maker.add_driver('uuid_2', [37, 55])

        driver_maker.update_redis()   # write redis data based on previous
                                      # add_driver calls
        tracker.invalidate_caches()
    """

    class TrackSource:
        ADJUSTED = 'A'
        GPS = 'G'
        NAVIGATOR = 'N'

    class DriverId:
        """Represents driver id, clid may be None
        """

        def __init__(self, uuid, dbid='dbid', clid='clid'):
            self.uuid = uuid
            self.dbid = dbid
            self.clid = clid

        def clid_uuid(self):
            if not self.clid:
                raise ValueError('clid may not be None')
            return '_'.join([self.clid, self.uuid])

        def dbid_uuid(self):
            return '_'.join([self.dbid, self.uuid])

    class TrackPoint:
        """Initialize track point for tracker
        @param time_diff sets diff from current time (now fixture)
                         It should be negative to move in the past
        """

        def __init__(
                self,
                position=[37, 55],
                direction=-1.0,
                speed=10.0,
                time_diff=0,
                accuracy=None,
                source=None,
        ):
            self.position = position
            self.direction = direction
            self.speed = speed
            self.time_diff = time_diff
            self.accuracy = accuracy
            self.source = source

    class Track:
        def __init__(self, driver_id, track_points=[]):
            self.driver_id = driver_id
            self.track = track_points

    def __init__(self, db, redis_store, now):
        self.db = db
        self.redis_store = redis_store
        self.car_counter = 0
        self.bson_counter = 0
        self.order_id_counter = 0
        self.mongo_increment = 0
        self.drivers = []
        self.now = now

    def init(self):
        self.db.dbparks.drop()
        self.db.parks.drop()
        self.db.cars.drop()
        self.db.drivers.drop()
        self.db.tracks_driver_statuses.drop()
        self.db.unique_drivers.drop()
        self.update_redis()

    def update_redis(self):
        """Update data in redis:
            - chain_busy_drivers
            Use DriverMaker.add_driver(...) info passed before
        """
        self._prepare_chain_drivers_redis()

    def add_driver(
            self,
            driver_id,
            position,
            classes=['econom'],
            busy_info=None,
            direction=-1.0,
            speed=10.0,
    ):
        """Fill databases with driver specified

        :param driver_id: drivers uuid. Will be prepended with clid and dbid
                          where needed. You may create your own DriverId object
                          instead of defaults.
        :param position: array [lon, lat]
        :param direction: degrees CW from the North direction
        :param speed: m/s
        :param classes: array of classes as strings
        :param busy_info: dict with following fields (all fields optional):
            {'order_id': string,
             'destination': [lon, lat],
             'left_time': 42,     # seconds
             'left_dist': 100500  # meters
            }
        """
        assert isinstance(classes, list)
        assert isinstance(classes[0], str)

        if isinstance(driver_id, str):
            driver_id = DriverMaker.DriverId(driver_id)

        if busy_info and 'order_id' not in busy_info:
            busy_info['order_id'] = self._make_order_id()

        car_number = self._make_car_number()
        license = self._make_driver_license()
        self.drivers.append(
            _DriverDesc(driver_id, position, classes, busy_info),
        )

        self._make_car(car_number)
        self._make_permit(car_number)
        self._make_driver(driver_id, car_number, license, classes, busy_info)
        self._make_driver_status(driver_id, classes, busy_info)
        self._make_unique_drivers(driver_id, license)
        self._make_park(driver_id)
        self._make_dbdriver(driver_id, license, license)
        categories = {}
        for tariff in classes:
            categories[TARIFFS_MAP.get(tariff, tariff)] = True
        self._make_dbcar(driver_id, license, car_number, categories)

    def _make_car_number(self):
        ret = 'К' + str(self.car_counter).zfill(3) + 'РТ150'
        self.car_counter += 1
        return ret

    def _make_driver_license(self):
        ret = 'DRIVER_LICENSE_' + str(self.car_counter).zfill(3)
        return ret

    def _make_bson_id(self):
        ret = str(self.bson_counter).zfill(24)
        self.bson_counter += 1
        return bson.ObjectId(ret)

    def _make_order_id(self):
        ret = str(self.order_id_counter).zfill(24)
        self.order_id_counter += 1
        return ret

    def _make_updated_ts(self):
        self.mongo_increment += 1
        return bson.timestamp.Timestamp(
            int(self.now.timestamp()), self.mongo_increment,
        )

    def _make_unique_drivers(self, driver_id, license):
        if not driver_id.clid:
            return
        data = {
            '_id': self._make_bson_id(),
            'updated': self.now,
            'licenses': [{'license': license}],
            'score': {'total': 0.7, 'complete_daily': [], 'complete_today': 0},
            'new_score': {'Москва': {'total': 0.8}},
            'comment': 'It is a complete unique driver profile',
            'profiles': [{'driver_id': driver_id.clid_uuid()}],
        }
        self.db.unique_drivers.insert(data)

    def _make_driver_status(self, driver_id, classes, busy_info):
        if not driver_id.clid:
            return
        data = {
            'ac': classes,
            'txi': _make_taximiter_status(busy_info),
            'rs': 0,
            's': _make_driver_status(busy_info),
            'u': self.now,
            '_id': driver_id.clid_uuid(),
            'os': self.now,
            'op': -1,
        }
        self.db.tracks_driver_statuses.insert(data)

    def _make_permit(self, license):
        data = {
            'city': 'Москва',
            'area': 'moscow',
            'age': 2012,
            '_state': 'active',
            'number': license,
            'issuer_id': 3,
            'permit': '014240',
        }
        self.db.permits.insert(data)

    def _make_park(self, driver_id):
        if not driver_id.clid:
            return

        query = {'_id': driver_id.dbid}
        data = {
            'login': 'uniq_26_park',
            'provider_config': {'yandex': {'clid': driver_id.clid}},
            'updated_ts': self._make_updated_ts(),
        }
        self.db.dbparks.update(query, {'$set': data}, upsert=True)

        query = {'_id': driver_id.clid}
        data = {
            'apikey': 'apikey',
            'city': 'Москва',
            'name': 'Я.Taxi',
            'host': 'host',
            'takes_urgent': True,
            'requirements': {'creditcard': True},
        }
        self.db.parks.update(query, {'$set': data}, upsert=True)

    def _make_car(self, car_number):
        car = {
            '_id': car_number,
            'age': 2012,
            'color': 'серебристый',
            'model': 'Tayota Carola',
            'number': car_number,
            'raw_model': 'Tayota Carola',
            'requirements': {
                'animaltransport': True,
                'check': True,
                'childbooster_amount': 1,
                'childchair_max': 12,
                'childchair_min': 6,
                'childseat_amount': 0,
                'conditioner': True,
                'infantseat_amount': 0,
                'nosmoking': True,
                'universal': True,
            },
            'updated': self.now,
        }
        self.db.cars.insert(car)

    def _make_driver(self, driver_id, car_number, license, classes, busy_info):
        if not driver_id.clid:
            return
        data = {
            '_id': driver_id.clid_uuid(),
            'updated': self.now,
            'updated_ts': self._make_updated_ts(),
            'clid': driver_id.clid,
            'uuid': driver_id.uuid,
            'db_id': driver_id.dbid,
            'status': 'free',
            '_state': 'active',
            'taximeter_version': '9.9',
            'driver_license': license,
            'class': classes + ['child_tariff'],
            'car': {
                'age': 2012,
                'allowed_classes': classes,
                'color': 'серебристый',
                'model': 'Toyota Corolla',
                'model_boost': {},
                'model_hunger_boost': {},
                'number': car_number,
                'raw_model': 'Tayota Carola',
            },
            'grades': [{'class': 'econom', 'value': 9, 'airport_value': 9}],
            'requirements': {
                'childseats': [[1, 3, 7], [7]],
                'nosmoking': True,
            },
            'online': {
                'e': self.now - datetime.timedelta(seconds=1000),
                's': self.now,
            },
            'op': -1,
            'rs': 0,
            'txs': _make_taximiter_status(busy_info),
            'disabled': False,
        }
        self.db.drivers.insert(data)

    def _make_dbdriver(self, driver_id, car_id, license):
        data = {
            'driver_id': driver_id.uuid,
            'modified_date': self.now,
            'license_series': '',
            'license_number': license,
            'taximeter_version': '9.9',
            'work_status': 'working',
            'updated_ts': self._make_updated_ts(),
            'park_id': driver_id.dbid,
            'car_id': car_id,
        }
        self.db.dbdrivers.insert(data)

    def _make_dbcar(self, driver_id, car_id, car_number, categories):
        data = {
            'category': categories,
            'modified_date': self.now,
            'service': {
                'pos': False,
                'rug': False,
                'delivery': False,
                'conditioner': False,
                'smoking': False,
                'booster': False,
                'animals': False,
                'child_seat': False,
            },
            'color': 'серебристый',
            'brand': 'Tayota',
            'year': 2012,
            'number': car_number,
            'updated_ts': self._make_updated_ts(),
            'park_id': driver_id.dbid,
            'model': 'Carola',
            'car_id': car_id,
            'booster_count': 1,
            'chairs': [
                {'brand': 'Geoby', 'categories': [1, 2, 3], 'isofix': False},
            ],
            'confirmed_boosters': 1,
            'confirmed_chairs': [
                {
                    'brand': 'Geoby',
                    'categories': [1, 2, 3],
                    'isofix': False,
                    'is_enabled': True,
                    'confirmed_categories': [1, 2, 3],
                },
            ],
        }
        self.db.dbcars.insert(data)

    def _prepare_chain_drivers_redis(self):
        # driver_id must have clid for chains
        drivers = self.drivers
        redis_store = self.redis_store
        busy_drivers = [
            {
                'driver_id': driver.driver_id.clid_uuid(),
                'order_id': driver.busy_info['order_id'],
                'pos': driver.position,
                'destination': driver.busy_info['destination'],
                'left_time': driver.busy_info.get('left_time', 420),
                'left_dist': driver.busy_info.get('left_dist', 1400),
                # Set approximate == false -> MAX_ROUTE_DISTANCE will be used
                'approximate': False,
                'flags': '10',
            }
            for driver in drivers
            if driver.busy_info
        ]
        redis_store.set(
            'chain_busy_drivers:data',
            _gen_chain_busy_drivers_data(self.now, busy_drivers),
        )
        redis_store.set(
            'chain_busy_drivers:meta',
            _gen_chain_busy_drivers_meta(self.now, busy_drivers),
        )


class _DriverDesc:
    def __init__(
            self, driver_id, position, classes=['econom'], busy_info=None,
    ):
        self.driver_id = driver_id
        self.position = position
        self.classes = classes
        self.busy_info = busy_info


def _make_taximiter_status(busy_info):
    TAXIMITER_STATUS_FREE = 2
    TAXIMITER_STATUS_ORDER_FREE = 3
    if busy_info is None:
        return TAXIMITER_STATUS_FREE
    else:
        return TAXIMITER_STATUS_ORDER_FREE


def _make_driver_status(busy_info):
    DRIVER_STATUS_FREE = 0
    DRIVER_STATUS_BUSY = 3
    if busy_info is None:
        return DRIVER_STATUS_FREE
    else:
        return DRIVER_STATUS_BUSY


def _gen_chain_busy_drivers_data(now, drivers):
    drivers_sz = len(drivers)
    builder = flatbuffers.Builder(0)

    driver_objs = []
    for driver in drivers:
        driver_id = builder.CreateString(driver['driver_id'])
        order_id = builder.CreateString(driver['order_id'])
        flags = builder.CreateString(driver['flags'])

        ChainBusyDriver.ChainBusyDriverStart(builder)
        ChainBusyDriver.ChainBusyDriverAddDriverId(builder, driver_id)
        ChainBusyDriver.ChainBusyDriverAddOrderId(builder, order_id)
        ChainBusyDriver.ChainBusyDriverAddDestination(
            builder, GeoPoint.CreateGeoPoint(builder, *driver['destination']),
        )
        ChainBusyDriver.ChainBusyDriverAddLeftTime(
            builder, driver['left_time'],
        )
        ChainBusyDriver.ChainBusyDriverAddLeftDist(
            builder, driver['left_dist'],
        )
        ChainBusyDriver.ChainBusyDriverAddApproximate(
            builder, driver['approximate'],
        )
        ChainBusyDriver.ChainBusyDriverAddFlags(builder, flags)
        driver_objs.append(ChainBusyDriver.ChainBusyDriverEnd(builder))

    ChainBusyDriverList.ChainBusyDriverListStartListVector(builder, drivers_sz)
    for obj in driver_objs:
        builder.PrependUOffsetTRelative(obj)
    vec = builder.EndVector(drivers_sz)

    ChainBusyDriverList.ChainBusyDriverListStart(builder)
    ChainBusyDriverList.ChainBusyDriverListAddTimestamp(
        builder, int(utils.timestamp(now)),
    )
    ChainBusyDriverList.ChainBusyDriverListAddList(builder, vec)
    obj = ChainBusyDriverList.ChainBusyDriverListEnd(builder)

    builder.Finish(obj)
    return bytes(builder.Output())


def _gen_chain_busy_drivers_meta(now, drivers):
    return '{}'


@pytest.fixture
def driver_maker(db, redis_store, now):
    return DriverMaker(db, redis_store, now)
