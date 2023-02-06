import contextlib
import datetime

import pytest

from taxi.core import async
from taxi.internal import dbh
from taxi.internal.yt_replication.rules import rule_names
from taxi.util import dates
from taxi_maintenance.stuff import repair_failed_subventions


_NEW_BILLING_MIGRATION = {
    'subventions': {
        'enabled': {
            'moscow': [
                {
                    'first_date': '2019-03-09',
                }
            ]
        }
    }
}


@pytest.inline_callbacks
def check_repaired_sg_possibly_skipped(order_id, should_skip, repaired_geoareas):
    if should_skip:
        async.return_value((
            yield fetch_order_subvention_geoareas(order_id)
        ) is None)
    else:
        async.return_value((
            yield fetch_order_subvention_geoareas(order_id)
        ) == repaired_geoareas)


@pytest.inline_callbacks
def fetch_order_subvention_geoareas(order_id):
    doc = yield dbh.orders.Doc.find_one_by_id(order_id)
    async.return_value(doc['performer'].get('subvention_geoareas'))


@pytest.inline_callbacks
def fetch_order_tags(order_id):
    doc = yield dbh.orders.Doc.find_one_by_id(order_id)
    async.return_value(doc['performer'].get('tags'))


@pytest.inline_callbacks
def _fetch_order_proc_last_candidate(order_id):
    doc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    candidate_idx = len(doc['candidates']) - 1
    async.return_value(doc['candidates'][candidate_idx])


@pytest.inline_callbacks
def fetch_order_proc_subvention_geoareas(order_id):
    candidate = yield _fetch_order_proc_last_candidate(order_id)
    async.return_value(candidate['subvention_geoareas'])


@pytest.inline_callbacks
def fetch_order_proc_tags(order_id):
    candidate = yield _fetch_order_proc_last_candidate(order_id)
    async.return_value(candidate['tags'])


@pytest.inline_callbacks
def fetch_order_proc_updated_time(order_id):
    doc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    async.return_value(doc['updated'])


@pytest.inline_callbacks
def fetch_subvention_calc_rules(order_id):
    doc = yield dbh.subvention_reasons.Doc.find_one_by_order_id(
        order_id
    )
    calc_rules = doc['subvention_calc_rules']
    async.return_value(calc_rules)


def default_calc_rules(rule_id):
    from taxi.internal.subvention_kit import rule_processors
    return [
        rule_processors.CalcRule.from_dict({
            "sub_commission": True,
            "sum": 150,
            "is_fake": False,
            "type": "guarantee",
            "id": rule_id,
            "display_in_taximeter": True,
            "geoareas": []
        })
    ]


@pytest.mark.config(
    ENABLE_REPAIR_FAILED_SUBVENTION_FIELDS=True,
    ENABLE_APPLYING_FAILED_SUBVENTION_FIELDS=True,
    ENABLE_GEOAREAS_SUBVENTIONS_FETCHING=True,
    ENABLE_DRIVER_TAGS_FETCHING=True,
    ENABLE_DRIVER_TAGS_SYNC_TO_ORDER=True,
    NEW_BILLING_MIGRATION=_NEW_BILLING_MIGRATION,
    ALLOW_FIXING_ABSENT_SUBVENTION_FIELDS=True
)
@pytest.mark.parametrize(
    'should_skip_sg',
    [
        False, True,
    ],
)
@pytest.inline_callbacks
def test_skip_repair_failed_geoareas_and_tags_subventions(patch, should_skip_sg):

    @patch('taxi.external.geoareas.find_active_geoareas_in_point')
    @async.inline_callbacks
    def find_active_geoareas_in_point(*args, **kwargs):
        yield async.return_value(['sadovoe'])

    @patch('taxi.external.driver_tags_service.drivers_tags_by_profile_match')
    def driver_tags_drivers_tags_by_profile_match(*args, **kwargs):
        async.return_value(['driver_tag'])

    @patch('taxi.internal.order_kit.plg.setcar_sender.'
           'get_subvention_calc_rules_from_params')
    @async.inline_callbacks
    def get_subvention_calc_rules_from_params(
            order, driver_license, tariff_class, due,
            acceptance_rate, completed_rate, driver_points,
            subvention_geoareas, tags, payment_type):
        yield
        if subvention_geoareas is not None:
            async.return_value(default_calc_rules('test_subvention_id_new'))
        else:
            async.return_value([])

    @patch('taxi.config.RFS_SHOULD_SKIP_SG_REPAIR.get')
    @async.inline_callbacks
    def get():
        yield
        async.return_value(should_skip_sg)

    yield repair_failed_subventions.do_stuff()

    # no changes
    assert (
        yield fetch_order_subvention_geoareas('order_id_ok')
    ) == ['ttk']
    # no changes because empty is valid value of geoareas
    assert (
        yield fetch_order_subvention_geoareas('order_id_ok_empty_subvention_geoareas')
    ) == []
    # repaired geoareas from None or absent to ['sadovoe']
    assert (
        yield check_repaired_sg_possibly_skipped('order_id_missing_subvention_geoareas',
                                                 should_skip_sg, ['sadovoe'])
    )
    assert (
        yield check_repaired_sg_possibly_skipped('order_id_no_subvention_geoarea',
                                                 should_skip_sg, ['sadovoe'])
    )
    # no changes because of overtiming
    assert (
        yield fetch_order_subvention_geoareas('order_id_missing_subvention_geoareas_but_overtimed')
    ) is None

    # repaired tags from None or absent to ['driver_tag']
    assert (
        yield fetch_order_tags('order_id_missing_tags')
    ) == ['driver_tag']
    assert (
        yield fetch_order_tags('order_id_no_tags')
    ) == ['driver_tag']

    # repaired geoareas and tags
    assert (
        yield check_repaired_sg_possibly_skipped('order_id_missing_subvention_geoareas_and_tags',
                                                 should_skip_sg, ['sadovoe'])
    )
    assert (
        yield fetch_order_tags('order_id_missing_subvention_geoareas_and_tags')
    ) == ['driver_tag']

    # repaired geoareas and tags new billing
    assert (
               yield check_repaired_sg_possibly_skipped(
                   'new_billing_order_id_missing_subvention_geoareas_and_tags',
                   should_skip_sg, ['sadovoe']
               )
           )
    assert (
               yield fetch_order_tags(
                   'new_billing_order_id_missing_subvention_geoareas_and_tags'
               )
           ) == ['driver_tag']

    # checking that already fetched subvention is remained
    assert (
        yield fetch_subvention_calc_rules('order_id_missing_subvention_geoareas')
    )[0]['id'] == 'test_subvention_id_already_fetched_geoareas'
    assert (
        yield fetch_subvention_calc_rules('order_id_missing_tags')
    )[0]['id'] == 'test_subvention_id_already_fetched_tags'
    assert (
        yield fetch_subvention_calc_rules('order_id_missing_subvention_geoareas_and_tags')
    )[0]['id'] == 'test_subvention_id_already_fetched_geoareas_and_tags'
    #  checking repaired subventions rules
    if not should_skip_sg:
        assert (
            yield fetch_subvention_calc_rules('order_id_missing_subvention_geoareas')
        )[1]['id'] == 'test_subvention_id_new'
        assert (
            yield fetch_subvention_calc_rules('order_id_missing_subvention_geoareas_and_tags')
        )[1]['id'] == 'test_subvention_id_new'
    assert (
        yield fetch_subvention_calc_rules('order_id_missing_tags')
    )[1]['id'] == 'test_subvention_id_new'
    # we don't change subvention_reasons in new billing orders
    assert len(
        (yield fetch_subvention_calc_rules(
                'new_billing_order_id_missing_subvention_geoareas_and_tags'
            )
         )
    ) == 1


@pytest.mark.config(
    ENABLE_REPAIR_FAILED_SUBVENTION_FIELDS=True,
    ENABLE_APPLYING_FAILED_SUBVENTION_FIELDS=True,
    ENABLE_GEOAREAS_SUBVENTIONS_FETCHING=True,
    ENABLE_DRIVER_TAGS_FETCHING=True,
    ENABLE_DRIVER_TAGS_SYNC_TO_ORDER=True
)
@pytest.inline_callbacks
def test_repair_failed_geoareas_and_tags_subventions_failed(patch):

    @patch('taxi.external.geoareas.find_active_geoareas_in_point')
    @async.inline_callbacks
    def find_active_geoareas_in_point(*args, **kwargs):
        yield async.return_value(None)

    @patch('taxi.external.driver_tags_service.drivers_tags_by_profile_match')
    def driver_tags_drivers_tags_by_profile_match(*args, **kwargs):
        async.return_value(None)

    @patch('taxi.internal.order_kit.plg.setcar_sender.'
           'get_subvention_calc_rules_from_params')
    @async.inline_callbacks
    def get_subvention_calc_rules_from_params(
            order, driver_license, tariff_class, due,
            acceptance_rate, completed_rate, driver_points,
            subvention_geoareas, tags, payment_type):
        yield
        if subvention_geoareas is not None:
            async.return_value(default_calc_rules('test_subvention_id_new'))
        else:
            async.return_value([])

    yield repair_failed_subventions.do_stuff()

    # repaired tags from None to ['driver_tag']
    assert (
        yield fetch_order_tags('order_id_missing_tags')
    ) is None

    # repaired geoareas and tags
    assert (
        yield fetch_order_subvention_geoareas('order_id_missing_subvention_geoareas_and_tags')
    ) is None
    assert (
        yield fetch_order_tags('order_id_missing_subvention_geoareas_and_tags')
    ) is None


@pytest.mark.config(
    ENABLE_REPAIR_FAILED_SUBVENTION_FIELDS=True,
    ENABLE_APPLYING_FAILED_SUBVENTION_FIELDS=True,
    ENABLE_GEOAREAS_SUBVENTIONS_FETCHING=True,
    ENABLE_PRE_REPAIR_FAILED_SUBVENTION_FIELDS_FROM_YT=True,
    FORCED_USING_YT_FOR_REPAIR_FAILED_SUBVENTION_FIELDS=True,
    ENABLE_DRIVER_TAGS_FETCHING=True,
    ENABLE_DRIVER_TAGS_SYNC_TO_ORDER=True,
    YT_CLUSTER_NAMES_FOR_FETCHING_ORDERS_WITH_FAILED_SUBVENTION_FIELDS=[
        'hahn', 'arnold']
)
@pytest.inline_callbacks
def test_repair_failed_geoareas_and_tags_subventions_from_yt(
        patch, monkeypatch, replication_yt_target_info):

    @patch('taxi.external.geoareas.find_active_geoareas_in_point')
    @async.inline_callbacks
    def find_active_geoareas_in_point(*args, **kwargs):
        yield async.return_value(['sadovoe'])

    @patch('taxi.external.driver_tags_service.drivers_tags_by_profile_match')
    def driver_tags_drivers_tags_by_profile_match(*args, **kwargs):
        async.return_value(['driver_tag'])

    @patch('taxi.internal.order_kit.plg.setcar_sender.'
           'get_subvention_calc_rules_from_params')
    @async.inline_callbacks
    def get_subvention_calc_rules_from_params(
            order, driver_license, tariff_class, due,
            acceptance_rate, completed_rate, driver_points,
            subvention_geoareas, tags, payment_type):
        yield
        if subvention_geoareas is not None:
            async.return_value(default_calc_rules('test_subvention_id_new'))
        else:
            async.return_value([])

    class DummyTable():
        gets_count = 0

        def __init__(self):
            self._rows = None

        def fetch_full_data(self):
            if (DummyTable.gets_count == 0):
                self._rows = [['order_id_missing_subvention_geoareas', '1'],
                              ['order_id_missing_tags', '1']]
            else:
                self._rows = [
                    ['order_id_missing_subvention_geoareas_and_tags', '2']]
            return True

        @property
        def rows(self):
            DummyTable.gets_count += 1
            return self._rows

    class DummyYqlRequest(object):
        operation_id = 1111

        def __init__(self, query):
            self._query = query
            self._table = DummyTable()

        @property
        def table(self):
            return self._table

        @property
        def is_success(self):
            return True

        def run(self):
            pass

    @contextlib.contextmanager
    def dummy_yql_client(*args, **kwargs):
        class Dummy(object):
            def query(self, query, **kwargs):
                return DummyYqlRequest(query)

        yield Dummy()

    monkeypatch.setattr('yql.api.v1.client.YqlClient', dummy_yql_client)
    replication_yt_target_info({rule_names.orders_monthly_orders: {
        'table_path': 'replica/mongo/struct/orders_monthly',
        'clients_delays': [{
            'client_name': 'hahn',
            'current_timestamp': dates.timestring(
                datetime.datetime.utcnow() -
                datetime.timedelta(seconds=10), tz='UTC',
            ),
            'current_delay': 0,
        }]
    }})
    yield repair_failed_subventions.do_stuff()

    # check that needed branch is handled
    assert DummyTable.gets_count == 2

    # repaired geoareas from None to ['sadovoe']
    assert (
        yield fetch_order_subvention_geoareas('order_id_missing_subvention_geoareas')
    ) == ['sadovoe']
    assert (
        yield fetch_order_proc_subvention_geoareas('order_id_missing_subvention_geoareas')
    ) == ['sadovoe']

    # repaired tags from None to ['driver_tag']
    assert (
        yield fetch_order_tags('order_id_missing_tags')
    ) == ['driver_tag']
    assert (
        yield fetch_order_proc_tags('order_id_missing_tags')
    ) == ['driver_tag']

    # repaired geoareas and tags
    assert (
        yield fetch_order_subvention_geoareas('order_id_missing_subvention_geoareas_and_tags')
    ) == ['sadovoe']
    assert (
        yield fetch_order_proc_subvention_geoareas('order_id_missing_subvention_geoareas_and_tags')
    ) == ['sadovoe']
    assert (
        yield fetch_order_tags('order_id_missing_subvention_geoareas_and_tags')
    ) == ['driver_tag']
    assert (
        yield fetch_order_proc_tags('order_id_missing_subvention_geoareas_and_tags')
    ) == ['driver_tag']
