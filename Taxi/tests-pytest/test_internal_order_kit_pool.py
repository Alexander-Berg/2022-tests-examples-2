# coding=utf-8
import collections
import datetime

import humbledb
import pytest

from taxi.core import async
from taxi.internal import dbh
from taxi.internal import driver_manager
from taxi.internal.order_kit import const
from taxi.internal.order_kit import pool
from taxi.taxi_protocol.protocol_1x import producers

OrderProcChecker = collections.namedtuple('OrderProcChecker', ['func', 'msg'])


@pytest.mark.filldb(_throw_on_db_access=True)
@pytest.inline_callbacks
def test_collect_pool_info(patch):
    umbrella_order = dbh.orders.Doc()
    umbrella_order.user_locale = 'en_GB'
    umbrella_order.experiments = ['umbrella_experiment']

    umbrella_order_proc = dbh.order_proc.Doc()
    umbrella_order_proc._id = 'umb1'
    umbrella_order_proc.embedded_orders = ['emb1', 'emb2']
    umbrella_order_proc.candidates = []
    umbrella_order_proc.order = umbrella_order
    candidate = umbrella_order_proc.candidates.new()
    candidate.driver_id = 'clid_uuid'

    embedded_order_1 = dbh.orders.Doc()
    embedded_order_1._id = 'emb1'
    embedded_order_1.phone_id = '5d1e0f3b404ef804b57704fe'
    embedded_order_1.cost_umbrella = 123
    embedded_order_1.status = dbh.orders.STATUS_ASSIGNED
    embedded_order_1.taxi_status = dbh.orders.TAXI_STATUS_DRIVING
    embedded_order_1.request.due = datetime.datetime(2017, 1, 1)
    embedded_order_1.request.source = [.1, 1]
    embedded_order_1.request.destinations = [[.2, 2], [.4, 4]]
    embedded_order_1.request.payment.type = const.CARD
    embedded_order_1.fixed_price.price = 788
    embedded_order_1.fixed_price.max_distance_from_b = 1024
    embedded_order_1.fixed_price.show_price_in_taximeter = True
    embedded_order_1.request.passengers_count = 1
    embedded_order_1.request.luggage_count = 1
    embedded_order_1.request.requirements = {}
    embedded_order_1.payment_tech.type = 'creditcard'
    embedded_order_1.experiments = ['experiment1', 'experiment2', 'experiment3']

    embedded_order_proc_1 = dbh.order_proc.Doc(order=embedded_order_1)
    embedded_order_proc_1._id = 'emb1'
    embedded_order_proc_1.order.cost_umbrella = embedded_order_1.cost_umbrella
    embedded_order_proc_1.candidates = []
    embedded_order_proc_1.order_info.statistics.status_updates = []
    new_candidate = embedded_order_proc_1.candidates.new()
    new_candidate.alias_id = 'emb1alias'
    new_candidate.pool.enabled = True
    new_candidate.pool.umbrella_order_id = 'umb1'
    new_candidate.pool.suggested_route = None
    embedded_order_proc_1.performer.candidate_index = 0
    embedded_order_proc_1.aliases = []
    alias = embedded_order_proc_1.aliases.new()
    alias.id = 'emb1alias'
    alias.due = datetime.datetime(2017, 1, 1)
    embedded_order_proc_1.order.pricing_data.user.price = {'total': 788}
    embedded_order_proc_1.order.pricing_data.taximeter_metadata = {
        'max_distance_from_point_b': 1024,
        'show_price_in_taximeter': True,
    }

    embedded_order_2 = dbh.orders.Doc()
    embedded_order_2._id = 'emb2'
    embedded_order_2.phone_id = '5d1e0f3b404ef804b57704ff'
    embedded_order_2.cost_umbrella = 145
    embedded_order_2.status = dbh.orders.STATUS_PENDING
    embedded_order_2.taxi_status = None
    embedded_order_2.request.due = datetime.datetime(2017, 1, 2)
    embedded_order_2.request.source = [.3, 3]
    embedded_order_2.request.destinations = [[.5, 5]]
    embedded_order_2.request.payment.type = const.CASH
    embedded_order_2.request.passengers_count = 1
    embedded_order_2.request.luggage_count = 1
    embedded_order_2.request.requirements = {}
    embedded_order_2.payment_tech.type = 'cash'
    embedded_order_2.experiments = ['experiment2', 'experiment3',
                                    'auto_accept_embedded']

    embedded_order_proc_2 = dbh.order_proc.Doc(order=embedded_order_2)
    embedded_order_proc_2._id = 'emb2'
    embedded_order_proc_2.order.cost_umbrella = embedded_order_2.cost_umbrella
    embedded_order_proc_2.candidates = []
    new_candidate = embedded_order_proc_2.candidates.new()
    new_candidate.driver_id = 'clid_uuid'
    new_candidate.alias_id = 'emb2alias'
    new_candidate.pool.enabled = True
    new_candidate.pool.umbrella_order_id = 'umb1'
    new_candidate.pool.suggested_route = []
    embedded_order_proc_2.performer.candidate_index = 0
    # 5 points: emb2_IN, emb1_IN, emb1_Intermediate, emb1_OUT, emb2_OUT.
    checkpoint1 = new_candidate.pool.suggested_route.new()
    checkpoint1.type = driver_manager.POINT_TYPE_SOURCE
    checkpoint1.point = [0.1, 1]
    checkpoint1.embedded_order_id = 'emb2'
    checkpoint2 = new_candidate.pool.suggested_route.new()
    checkpoint2.type = driver_manager.POINT_TYPE_SOURCE
    checkpoint2.point = [0.2, 2]
    checkpoint2.embedded_order_id = 'emb1'
    checkpoint3 = new_candidate.pool.suggested_route.new()
    checkpoint3.type = driver_manager.POINT_TYPE_DESTINATION
    checkpoint3.point = [0.3, 3]
    checkpoint3.embedded_order_id = 'emb1'
    checkpoint4 = new_candidate.pool.suggested_route.new()
    checkpoint4.type = driver_manager.POINT_TYPE_DESTINATION
    checkpoint4.point = [0.4, 4]
    checkpoint4.embedded_order_id = 'emb1'
    checkpoint5 = new_candidate.pool.suggested_route.new()
    checkpoint5.type = driver_manager.POINT_TYPE_DESTINATION
    checkpoint5.point = [0.5, 5]
    checkpoint5.embedded_order_id = 'emb2'
    embedded_order_proc_2.performer.candidate_index = 0
    embedded_order_proc_2.aliases = []
    alias = embedded_order_proc_2.aliases.new()
    alias.id = 'emb2alias'
    alias.due = datetime.datetime(2017, 1, 2)

    @patch('taxi.internal.dbh.orders.Doc.find_many')
    @async.inline_callbacks
    def get_order_by_id(query):
        yield
        assert query == {'_id': {'$in': ['emb1', 'emb2']}}
        async.return_value([embedded_order_2, embedded_order_1])

    @patch('taxi.internal.dbh.order_proc.Doc.find_many')
    @async.inline_callbacks
    def get_order_procs_by_id(query):
        yield
        assert query == {'_id': {'$in': ['emb1', 'emb2']}}
        async.return_value([embedded_order_proc_2, embedded_order_proc_1])

    @patch('taxi.internal.dbh.user_phones.Doc.find_one_by_id')
    @async.inline_callbacks
    def find_phone_by_id(*args, **kwargs):
        yield
        assert str(args[0]) in [
            '5d1e0f3b404ef804b57704fe',
            '5d1e0f3b404ef804b57704ff',
        ]
        number = str(args[0]) + '_number'
        doc = {
            '_id': args[0],
            'phone': number,
        }
        async.return_value(dbh.user_phones.Doc(doc))

    @patch('taxi.taxi_protocol.protocol_1x.producers.'
           'localize_addresses')
    @async.inline_callbacks
    def localize_addresses(order_id, driver_id, user_locale,
                           driver_position=None, source=None, destinations=None,
                           log_extra=None):
        yield
        assert source is None
        assert driver_position == {}
        assert driver_id == 'clid_uuid'
        assert user_locale == 'Unique User Locale To Force Computations'
        assert ([d.get('point') or d.get('geopoint') for d in destinations] ==
                [[.1, 1], [.2, 2], [.3, 3], [.4, 4], [.5, 5]])
        async.return_value((None, None, [
            dict(fullname='Leo Tolstoy, 16', short_text='Leo Tolstoy, 16',
                 title='Yandex', country='Russia', geopoint=[.1, 1],
                 porchnumber='1a'),
            dict(fullname='Kremlin', country='Russia', geopoint=[.2, 2],
                 title='', short_text='Kremlin', locality='gates'),
            dict(fullname='SVO', country='Russia', geopoint=[.3, 3],
                 title='', terminal='F', flight='SU-232', short_text='SVO'),
            dict(fullname='Sokol', country='Russia', geopoint=[.4, 4],
                 title='', premisenumber='7', short_text='Sokol'),
            dict(fullname='VDNH', short_text='VDNH', country='Russia',
                 title='', geopoint=[.5, 5]),
        ]))

    pool_info = yield pool.collect_pool_info(
        umbrella_order_proc, umbrella_order)

    expected_pool_info = pool.PoolInfo(
        orders=[
            pool.EmbeddedOrderInfo(
                embedded_order_id='emb1',
                alias_id='emb1alias',
                due=datetime.datetime(2017, 1, 1),
                status=dbh.orders.STATUS_ASSIGNED,
                requirements={},
                requested_payment_type='card',
                current_payment_type='creditcard',
                fixed_price_info=producers.FixedPriceInfo(
                    price=788,
                    driver_price=None,
                    paid_supply_price=None,
                    max_distance=1024,
                    show_price=True,
                ),
                passengers_count=1,
                luggage_count=1,
                cost_umbrella=123,
                phone='5d1e0f3b404ef804b57704fe_number',
                comments=None,
                total_distance=0,
                complete_time=None,
                cancel_dt=None,
                start_transporting_time=None,
                experiments=['experiment1', 'experiment2', 'experiment3'],
                is_auto_accept=False,
                changed_pickups_order_show_ms=10000,
                taxi_status=dbh.orders.TAXI_STATUS_DRIVING
            ),
            pool.EmbeddedOrderInfo(
                embedded_order_id='emb2',
                alias_id='emb2alias',
                due=datetime.datetime(2017, 1, 2),
                status=dbh.orders.STATUS_PENDING,
                requirements={},
                requested_payment_type='cash',
                current_payment_type='cash',
                fixed_price_info=None,
                passengers_count=1,
                luggage_count=1,
                cost_umbrella=145,
                phone='5d1e0f3b404ef804b57704ff_number',
                comments=None,
                total_distance=0,
                complete_time=None,
                cancel_dt=None,
                start_transporting_time=None,
                experiments=['experiment2', 'experiment3',
                             'auto_accept_embedded'],
                is_auto_accept=True,
                changed_pickups_order_show_ms=10000,
                taxi_status=None
            ),
        ],
        route=[
            pool.LocalizedPoint(
                embedded_order_id='emb2', alias_id='emb2alias',
                type=pool.PointType_IN,
                geopoint=[.1, 1], country='Russia', fullname='Leo Tolstoy, 16',
                title='Yandex', short_text='Leo Tolstoy, 16',
                locality='', flight='', terminal='', thoroughfare='',
                premisenumber='', porchnumber='1a', object_type='',
            ),
            pool.LocalizedPoint(
                embedded_order_id='emb1', alias_id='emb1alias',
                type=pool.PointType_IN,
                geopoint=[.2, 2], country='Russia', fullname='Kremlin',
                title='', short_text='Kremlin',
                locality='gates', flight='', terminal='', thoroughfare='',
                premisenumber='', porchnumber='', object_type='',
            ),
            pool.LocalizedPoint(
                embedded_order_id='emb1', alias_id='emb1alias',
                type=pool.PointType_OUT,
                geopoint=[.3, 3], country='Russia', fullname='SVO',
                title='', short_text='SVO',
                locality='', flight='SU-232', terminal='F', thoroughfare='',
                premisenumber='', porchnumber='', object_type='',
            ),
            pool.LocalizedPoint(
                embedded_order_id='emb1', alias_id='emb1alias',
                type=pool.PointType_OUT,
                geopoint=[.4, 4], country='Russia', fullname='Sokol',
                title='', short_text='Sokol',
                locality='', flight='', terminal='', thoroughfare='',
                premisenumber='7', porchnumber='', object_type='',
            ),
            pool.LocalizedPoint(
                embedded_order_id='emb2', alias_id='emb2alias',
                type=pool.PointType_OUT,
                geopoint=[.5, 5], country='Russia', fullname='VDNH',
                title='', short_text='VDNH',
                locality='', flight='', terminal='', thoroughfare='',
                premisenumber='', porchnumber='', object_type='',
            ),
        ],
        driver_address=None,
        close_point_order_ids=[],
        previous_close_point_order_ids=[],
        experiments=['umbrella_experiment', 'experiment2', 'experiment3'],
        changed_pickups_order_id='emb2'
    )

    assert pool_info == expected_pool_info


@pytest.mark.filldb(_throw_on_db_access=True)
@pytest.inlineCallbacks
def test_multiple_pending_embedded_orders(patch):
    # It should be possible to have two pending embedded orders

    umbrella_order_proc = dbh.order_proc.Doc()
    umbrella_order_proc._id = 'umb1'
    umbrella_order_proc.embedded_orders = ['emb1', 'emb2']
    umbrella_order_proc.candidates = []
    candidate = umbrella_order_proc.candidates.new()
    candidate.driver_id = 'clid_uuid'

    umbrella_order = dbh.orders.Doc()
    umbrella_order._id = umbrella_order_proc._id
    umbrella_order.payment_tech.type = 'cash'

    embedded_order_1 = dbh.orders.Doc()
    embedded_order_1._id = 'emb1'
    embedded_order_1.request.requirements = {}
    embedded_order_1.payment_tech.type = 'cash'
    embedded_order_proc_1 = dbh.order_proc.Doc()
    embedded_order_proc_1._id = embedded_order_1._id
    embedded_order_proc_1.status = dbh.order_proc.STATUS_PENDING
    embedded_order_proc_1.order.request.source = {'use_geopoint': True, 'geopoint': [1, 2]}
    embedded_order_proc_1.order.request.destinations = [
        {'use_geopoint': True, 'geopoint': [1.1, 2.2]}
    ]
    embedded_order_proc_1.order.phone_id = '5d1e0f3b404ef804b57704fe'
    embedded_order_proc_1.candidates = []
    new_candidate = embedded_order_proc_1.candidates.new()
    new_candidate.alias_id = 'emb1alias'
    new_candidate.pool.enabled = True
    new_candidate.pool.umbrella_order_id = 'umb1'
    new_candidate.pool.suggested_route = None
    embedded_order_proc_1.performer.candidate_index = 0
    embedded_order_proc_1.aliases = []
    alias = embedded_order_proc_1.aliases.new()
    alias.id = 'emb1alias'
    alias.due = datetime.datetime(2017, 1, 1)

    embedded_order_2 = dbh.orders.Doc()
    embedded_order_2._id = 'emb2'
    embedded_order_2.request.requirements = {}
    embedded_order_2.payment_tech.type = 'cash'
    embedded_order_proc_2 = dbh.order_proc.Doc()
    embedded_order_proc_2._id = embedded_order_2._id
    embedded_order_proc_2.order.request.source = {
        'use_geopoint': True, 'geopoint': [1.1, 2.2]}
    embedded_order_proc_2.order.request.destinations = [
        {'use_geopoint': True, 'geopoint': [1, 2]}]
    embedded_order_proc_2.order.phone_id = '5d1e0f3b404ef804b57704ff'
    embedded_order_proc_2.status = dbh.order_proc.STATUS_PENDING
    embedded_order_proc_2.candidates = []
    new_candidate = embedded_order_proc_2.candidates.new()
    new_candidate.alias_id = 'emb2alias'
    new_candidate.pool.enabled = True
    new_candidate.pool.umbrella_order_id = 'umb1'
    new_candidate.pool.suggested_route = None
    embedded_order_proc_2.performer.candidate_index = 0
    embedded_order_proc_2.aliases = []
    alias = embedded_order_proc_2.aliases.new()
    alias.id = 'emb2alias'
    alias.due = datetime.datetime(2017, 1, 1)

    @patch('taxi.internal.dbh.user_phones.Doc.find_one_by_id')
    @async.inline_callbacks
    def find_phone_by_id(*args, **kwargs):
        yield
        assert str(args[0]) in [
            '5d1e0f3b404ef804b57704fe',
            '5d1e0f3b404ef804b57704ff',
        ]
        number = str(args[0]) + '_number'
        doc = {
            '_id': args[0],
            'phone': number,
        }
        async.return_value(dbh.user_phones.Doc(doc))

    @patch('taxi.internal.dbh.orders.Doc.find_many')
    @async.inline_callbacks
    def get_order_by_id(query):
        yield
        assert query == {'_id': {'$in': ['emb1', 'emb2']}}
        async.return_value([embedded_order_1, embedded_order_2])

    @patch('taxi.internal.dbh.order_proc.Doc.find_many')
    @async.inline_callbacks
    def get_order_procs_by_id(query):
        yield
        assert query == {'_id': {'$in': ['emb1', 'emb2']}}
        async.return_value([embedded_order_proc_1, embedded_order_proc_2])

    @patch('taxi.taxi_protocol.protocol_1x.producers.'
           'localize_addresses')
    @async.inline_callbacks
    def localize_addresses(order_id, driver_id, user_locale,
                           driver_position=None, source=None, destinations=None,
                           log_extra=None):
        yield
        async.return_value((None, source, destinations))

    yield pool.collect_pool_info(umbrella_order_proc, umbrella_order)


@pytest.mark.filldb(_throw_on_db_access=True)
@pytest.inlineCallbacks
def test_no_embedds_silent_exit(patch):
    embedded_order_1 = dbh.orders.Doc()
    embedded_order_1._id = 'emb1'
    embedded_order_1.request.source.point = [.1, 1]
    embedded_order_1.request.destinations = []
    destination_point_1 = embedded_order_1.request.destinations.new()
    destination_point_1.point = [.2, 2]
    destination_point_2 = embedded_order_1.request.destinations.new()
    destination_point_2.point = [.3, 3]
    embedded_order_1.request.requirements = {}
    embedded_order_1.payment_tech.type = 'cash'

    embedded_order_proc_2 = dbh.order_proc.Doc()
    embedded_order_proc_2._id = 'emb2'
    embedded_order_proc_2.status = dbh.order_proc.STATUS_PENDING
    new_candidate = embedded_order_proc_2.candidates.new()
    new_candidate.alias_id = 'emb2alias'
    new_candidate.pool.enabled = True
    new_candidate.pool.umbrella_order_id = 'umb2'
    new_candidate.pool.suggested_route = None
    new_candidate.driver_id = 'clid_uuid'
    embedded_order_proc_2.performer.candidate_index = 0
    embedded_order_proc_2.aliases = []
    alias = embedded_order_proc_2.aliases.new()
    alias.id = 'emb2alias'
    alias.due = datetime.datetime(2017, 1, 1)
    embedded_order_proc_2.order.request.source.point = [.4, 4]
    embedded_order_proc_2.order.request.destinations = []
    destination_point_1 = embedded_order_proc_2.order.request.destinations.new()
    destination_point_1.point = [.5, 5]
    embedded_order_proc_2.order.request.requirements = {}

    embedded_order_2 = dbh.orders.Doc()
    embedded_order_2._id = 'emb2'
    embedded_order_2.request = embedded_order_proc_2.order.request
    embedded_order_2.payment_tech.type = 'cash'

    umbrella_order = dbh.orders.Doc()
    umbrella_order_proc = dbh.order_proc.Doc()
    umbrella_order_proc._id = 'umb1'
    umbrella_order_proc.embedded_orders = ['emb1', 'emb2']

    @patch('taxi.internal.dbh.orders.Doc.find_many')
    @async.inline_callbacks
    def dbh_orders_find_many(query):
        yield
        assert query == {'_id': {'$in': ['emb1', 'emb2']}}
        async.return_value([embedded_order_1, embedded_order_2])

    @patch('taxi.internal.dbh.order_proc.Doc.find_many')
    @async.inline_callbacks
    def dbh_order_proc_find_many(query):
        yield
        assert query == {'_id': {'$in': ['emb1', 'emb2']}}
        result = [embedded_order_proc_2]
        async.return_value(result)

    pool_info = yield pool.collect_pool_info(umbrella_order_proc,
                                             umbrella_order)

    assert 0 == len(pool_info.orders)
    assert 0 == len(pool_info.route)


@pytest.mark.filldb(_throw_on_db_access=True)
@pytest.inlineCallbacks
def test_order_with_updated_performer_is_excluded(patch):
    embedded_order_proc_1 = dbh.order_proc.Doc()
    embedded_order_proc_1._id = 'emb1'
    embedded_order_proc_1.status = dbh.order_proc.STATUS_PENDING
    embedded_order_proc_1.order.status = dbh.orders.STATUS_PENDING
    new_candidate = embedded_order_proc_1.candidates.new()
    new_candidate.alias_id = 'emb1alias'
    new_candidate.pool.enabled = True
    new_candidate.pool.umbrella_order_id = 'umb2'
    new_candidate.pool.suggested_route = None
    new_candidate.driver_id = 'clid_uuid'
    embedded_order_proc_1.performer.candidate_index = 0
    embedded_order_proc_1.aliases = []
    alias = embedded_order_proc_1.aliases.new()
    alias.id = 'emb1alias'
    alias.due = datetime.datetime(2017, 1, 1)
    embedded_order_proc_1.order.request.source.point = [.1, 1]
    embedded_order_proc_1.order.request.destinations = []
    dest_point_1 = embedded_order_proc_1.order.request.destinations.new()
    dest_point_1.point = [.2, 2]
    dest_point_2 = embedded_order_proc_1.order.request.destinations.new()
    dest_point_2.point = [.3, 3]
    embedded_order_proc_1.order.phone_id = 'phone_id_1'

    embedded_order_1 = dbh.orders.Doc()
    embedded_order_1._id = 'emb1'
    embedded_order_1.request.passengers_count = 1
    embedded_order_1.request.luggage_count = 1
    embedded_order_1.request.requirements = {}
    embedded_order_1.payment_tech.type = 'cash'

    embedded_order_proc_2 = dbh.order_proc.Doc()
    embedded_order_proc_2._id = 'emb2'
    embedded_order_proc_2.status = dbh.order_proc.STATUS_PENDING
    embedded_order_proc_2.order.status = dbh.orders.STATUS_PENDING
    new_candidate = embedded_order_proc_2.candidates.new()
    new_candidate.alias_id = 'emb2alias'
    new_candidate.pool.enabled = True
    new_candidate.pool.umbrella_order_id = 'umb1'
    new_candidate.pool.suggested_route = None
    new_candidate.driver_id = 'clid_uuid'
    embedded_order_proc_2.performer.candidate_index = 0
    embedded_order_proc_2.aliases = []
    alias = embedded_order_proc_2.aliases.new()
    alias.id = 'emb2alias'
    alias.due = datetime.datetime(2017, 1, 1)
    embedded_order_proc_2.order.request.source.point = [.01, 10]
    embedded_order_proc_2.order.request.destinations = []
    dest_point_1 = embedded_order_proc_2.order.request.destinations.new()
    dest_point_1.point = [.02, 20]
    dest_point_2 = embedded_order_proc_2.order.request.destinations.new()
    dest_point_2.point = [.03, 30]
    embedded_order_proc_2.order.phone_id = '5d1e0f3b404ef804b57704fe'

    embedded_order_2 = dbh.orders.Doc()
    embedded_order_2._id = 'emb2'
    embedded_order_2.request.passengers_count = 1
    embedded_order_2.request.luggage_count = 1
    embedded_order_2.request.requirements = {}
    embedded_order_2.payment_tech.type = 'cash'

    umbrella_order = dbh.orders.Doc()
    umbrella_order_proc = dbh.order_proc.Doc()
    umbrella_order_proc._id = 'umb1'
    umbrella_order_proc.embedded_orders = ['emb1', 'emb2']

    @patch('taxi.internal.dbh.orders.Doc.find_many')
    @async.inline_callbacks
    def dbh_orders_find_many(query):
        yield
        assert query == {'_id': {'$in': ['emb1', 'emb2']}}
        async.return_value([embedded_order_1, embedded_order_2])

    @patch('taxi.internal.dbh.order_proc.Doc.find_many')
    @async.inline_callbacks
    def dbh_order_proc_find_many(query):
        yield
        assert query == {'_id': {'$in': ['emb1', 'emb2']}}
        result = [embedded_order_proc_1, embedded_order_proc_2]
        async.return_value(result)

    @patch('taxi.internal.dbh.user_phones.Doc.find_one_by_id')
    @async.inline_callbacks
    def find_phone_by_id(phone_id, *args, **kwargs):
        yield
        assert str(phone_id) == '5d1e0f3b404ef804b57704fe'
        doc = {
            '_id': phone_id,
            'phone': 'phone',
        }
        async.return_value(dbh.user_phones.Doc(doc))

    @patch('taxi.taxi_protocol.protocol_1x.producers.'
           'localize_addresses')
    @async.inline_callbacks
    def localize_addresses(order_id, driver_id, user_locale,
                           driver_position=None, source=None, destinations=None,
                           log_extra=None):
        yield
        assert source is None
        assert driver_position == {}
        assert driver_id == 'clid_uuid'
        assert user_locale == 'Unique User Locale To Force Computations'
        assert ([d.get('point') or d.get('geopoint') for d in destinations] ==
                [[.01, 10], [.02, 20], [.03, 30]])
        async.return_value((None, None, [
            dict(fullname='Leo Tolstoy, 16', country='Russia',
                 geopoint=[.01, 10], porchnumber='1a'),
            dict(fullname='Kremlin', country='Russia', geopoint=[.02, 20],
                 locality='gates'),
            dict(fullname='SVO', country='Russia', geopoint=[.03, 30],
                 terminal='F', flight='SU-232'),
        ]))

    pool_info = yield pool.collect_pool_info(umbrella_order_proc,
                                             umbrella_order)

    assert 1 == len(pool_info.orders)
    assert pool_info.orders[0].embedded_order_id == 'emb2'


def _generate_embedded_pool_order():
    order = dbh.orders.Doc()
    order._id = 'embedid'
    order.city_id = u'Тула'
    return order


def _generate_embedded_pool_proc(is_new_pool):
    order_proc_doc = dbh.order_proc.Doc()
    order_proc_doc._id = 'embedid'
    order_proc_doc.status = dbh.order_proc.STATUS_PENDING
    order_proc_doc.processing.version = 1
    order_proc_doc.order.version = 1

    new_candidate = order_proc_doc.candidates.new()
    new_candidate.driver_id = 'd_id'
    new_candidate.alias_id = 'a_id'
    new_candidate.db_id = 'db_id'
    new_candidate.pool.enabled = True
    performer = order_proc_doc.performer
    performer.candidate_index = 0
    performer.driver_id = new_candidate.driver_id
    performer.alias_id = new_candidate.alias_id
    alias = order_proc_doc.aliases.new()
    alias.id = new_candidate.alias_id
    alias.due = datetime.datetime.now()
    if not is_new_pool:
        new_candidate.pool.umbrella_order_id = 'my_umbrella'

    order_proc_doc.order.request.source = {
        'use_geopoint': True, 'geopoint': [1.1, 2.2]}
    order_proc_doc.order.request.destinations = [
        {'use_geopoint': True, 'geopoint': [1, 2]}
    ]
    order_proc_doc.order.request.classes = ['pool']
    return order_proc_doc


def _generate_umbrella_proc():
    order_proc_doc = dbh.order_proc.Doc()
    order_proc_doc._id = 'my_umbrella'
    order_proc_doc.candidates = []
    order_proc_doc.order.experiments = ['experiment']
    new_candidate = order_proc_doc.candidates.new()
    new_candidate.driver_id = 'd_id'
    new_candidate.alias_id = 'a_id'
    new_candidate.pool.enabled = True
    new_candidate.tariff_class = 'test_tariff'
    order_proc_doc.embedded_orders = ['embedid']
    return order_proc_doc


def _generate_umbrella_proc_without_embedded_orders():
    order_proc_doc = _generate_umbrella_proc()
    order_proc_doc.embedded_orders = {}
    return order_proc_doc


def _generate_umbrella_with_two_candidates():
    order_proc_doc = _generate_umbrella_proc()
    order_proc_doc.candidates.new()
    return order_proc_doc


@pytest.mark.parametrize('taxi_statuses,source_expected,dest_expected', [
    (['assigned', 'driving'], False, False),
    (['assigned', 'driving', 'waiting'], True, False),
    (['assigned', 'driving', 'waiting', 'transporting'], True, False),
    (['transporting', 'complete'], True, True),
    (['expired'], False, False),
    (['transporting', 'complete', 'expired'], True, True),
    (['transporting', 'expired'], True, False),
    (['assigned', 'driving', 'waiting', 'cancelled',
      'assigned', 'driving'], False, False),
    (['assigned', 'driving', 'waiting', 'failed',
      'assigned', 'driving'], False, False),
    (['assigned', 'driving', 'waiting', 'cancelled',
      'assigned', 'driving', 'waiting'], True, False),
    (['assigned', 'driving', 'waiting', 'failed', 'assigned',
      'driving', 'waiting', 'transporting', 'complete'], True, True)
])
def test_is_route_point_reached(taxi_statuses, source_expected, dest_expected):
    status_updates = []

    for taxi_status in taxi_statuses:
        status_update = humbledb.Embed('status_updates')
        status_update.embedded_order_id = 'emb1'
        status_update.taxi_status = taxi_status
        status_updates.append(status_update)

    source_reached = pool.is_route_point_reached('source', status_updates)
    assert source_reached == source_expected

    dest_reached = pool.is_route_point_reached('destination', status_updates)
    assert dest_reached == dest_expected


def _generate_route(embedded_orders_vec):
    orders = set()
    route = []
    for embedded_id in embedded_orders_vec:
        point = humbledb.Embed('suggested_route')
        point.embedded_order_id = embedded_id
        if embedded_id in orders:
            point.type = 'destination'
        else:
            point.type = 'source'
            orders.add(embedded_id)
        route.append(point)
    return route


@pytest.mark.parametrize('new_route,prev_route,expected_index', [
    (['emb1', 'emb2', 'emb1', 'emb2'], ['emb1', 'emb1'], 1),
    (['emb1', 'emb1'], ['emb1', 'emb1'], None),
    (['emb2', 'emb1', 'emb1', 'emb2'], ['emb1', 'emb1'], 0),
    (['emb1', 'emb3', 'emb2', 'emb2', 'emb3', 'emb1'],
     ['emb1', 'emb2', 'emb1', 'emb2'], 1),
    (['emb1', 'emb2', 'emb3', 'emb2', 'emb3', 'emb1'],
     ['emb1', 'emb2', 'emb1', 'emb2'], 2),
    ([], [], None),
    (['emb1', 'emb1'], [], None),
    ([], ['emb1', 'emb1'], None)
])
def test_find_mismatch_index(new_route, prev_route, expected_index):
    new_route = _generate_route(new_route)
    prev_route = _generate_route(prev_route)

    assert pool.find_mismatch_index(
        new_route=new_route, prev_route=prev_route) == expected_index


EmbeddedData = collections.namedtuple('EmbeddedData', [
    'id', 'status', 'type', 'route'
])


def _prepare_embedded_order_proc(embedded_data):
    """
    Creates order_proc instance from test data
    :param embedded_data: instance of EmbeddedData
    :return: dbh.order_proc.Doc
    """
    order_proc = dbh.order_proc.Doc()
    order_proc._id = embedded_data.id
    order_proc.status = embedded_data.status

    order = dbh.orders.Doc()
    order._id = embedded_data.id
    order.status = embedded_data.status

    # This experiment enables auto accept possibility
    order.experiments = (['auto_accept_embedded']
                         if embedded_data.type == 'auto' else [])
    order_proc.order = order

    # Prepare suggested route and candidate
    candidate = humbledb.Embed('candidates')
    candidate.pool = humbledb.Embed('pl')
    candidate.pool.suggested_route = _generate_route(embedded_data.route)
    order_proc._indexed_candidates = {0: candidate}
    order_proc.performer = humbledb.Embed('performer')
    order_proc.performer.candidate_index = 0

    # For deciding if route point was reached
    status_update = humbledb.Embed('status_updates')
    status_update.embedded_order_id = embedded_data.id
    status_update.taxi_status = embedded_data.status
    order_proc.order_info.statistics.status_updates = [status_update]

    return order_proc


@pytest.mark.parametrize('embeddeds_data,expected_id', [
    ([
         EmbeddedData(id='emb0', status='assigned', type='manual', route=[])
     ], None),
    ([
         EmbeddedData(id='emb0', status='transporting', type='manual',
                      route=[]),
         EmbeddedData(id='emb1', status='pending', type='manual',
                      route=['emb0', 'emb1', 'emb0', 'emb1'])
     ], None),
    ([
         EmbeddedData(id='emb0', status='transporting', type='manual',
                      route=[]),
         EmbeddedData(id='emb1', status='pending', type='auto',
                      route=['emb0', 'emb1', 'emb0', 'emb1'])
     ], 'emb1'),
    ([
         EmbeddedData(id='emb0', status='transporting', type='manual',
                      route=[]),
         EmbeddedData(id='emb1', status='driving', type='auto',
                      route=['emb0', 'emb1', 'emb0', 'emb1'])
     ], 'emb1'),
    ([
         EmbeddedData(id='emb0', status='driving', type='manual',
                      route=[]),
         EmbeddedData(id='emb1', status='driving', type='manual',
                      route=['emb1', 'emb0', 'emb0', 'emb1'])
     ], None),
    ([
         EmbeddedData(id='emb0', status='driving', type='manual',
                      route=[]),
         EmbeddedData(id='emb1', status='driving', type='auto',
                      route=['emb1', 'emb0', 'emb0', 'emb1'])
     ], 'emb1'),
    ([
         EmbeddedData(id='emb0', status='driving', type='manual',
                      route=[]),
         EmbeddedData(id='emb1', status='driving', type='auto',
                      route=['emb1', 'emb0', 'emb0', 'emb1']),
         EmbeddedData(id='emb2', status='driving', type='auto',
                      route=['emb2', 'emb1', 'emb0', 'emb0', 'emb2', 'emb1'])
     ], 'emb2'),
    ([
         EmbeddedData(id='emb0', status='driving', type='manual',
                      route=[]),
         EmbeddedData(id='emb1', status='driving', type='auto',
                      route=['emb1', 'emb0', 'emb0', 'emb1']),
         EmbeddedData(id='emb2', status='driving', type='auto',
                      route=['emb0', 'emb2', 'emb1', 'emb0', 'emb2', 'emb1'])
     ], 'emb0'),
    ([
         EmbeddedData(id='emb0', status='driving', type='manual',
                      route=[]),
         EmbeddedData(id='emb1', status='driving', type='auto',
                      route=['emb1', 'emb0', 'emb0', 'emb1']),
         EmbeddedData(id='emb2', status='driving', type='auto',
                      route=['emb0', 'emb2', 'emb1', 'emb0', 'emb2', 'emb1']),
         EmbeddedData(id='emb3', status='pending', type='auto',
                      route=['emb3', 'emb0', 'emb2', 'emb1',
                             'emb0', 'emb2', 'emb1', 'emb3'])
     ], 'emb3'),
    ([  # Отменён последний заказ emb1
        EmbeddedData(id='emb0', status='driving', type='manual',
                     route=[]),
        EmbeddedData(id='emb1', status='cancelled', type='auto',
                     route=['emb1', 'emb0', 'emb0', 'emb1'])
     ], None),
    ([  # Отменён заказ emb1, точка emb2 становится ближайшей
         EmbeddedData(id='emb0', status='driving', type='manual',
                      route=[]),
         EmbeddedData(id='emb1', status='cancelled', type='auto',
                      route=['emb1', 'emb0', 'emb0', 'emb1']),
         EmbeddedData(id='emb2', status='driving', type='auto',
                      route=['emb2', 'emb0', 'emb0', 'emb2'])
     ], 'emb2'),
    ([  # Отменён заказ emb1, точка emb0 снова становится ближайшей
         EmbeddedData(id='emb0', status='driving', type='manual',
                      route=[]),
         EmbeddedData(id='emb1', status='cancelled', type='auto',
                      route=['emb1', 'emb0', 'emb0', 'emb1']),
         EmbeddedData(id='emb2', status='driving', type='auto',
                      route=['emb0', 'emb2', 'emb0', 'emb2'])
     ], 'emb0'),
])
def test_get_changed_pickups_order_id(embeddeds_data, expected_id):
    embeddeds = [_prepare_embedded_order_proc(emb) for emb in embeddeds_data]
    assert pool.get_changed_pickups_order_id(embeddeds) == expected_id
