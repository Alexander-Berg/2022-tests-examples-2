import pytest

CATALOG_STORAGE_URL = (
    '/eats-catalog-storage/internal/eats-catalog-storage/v1/search/places/list'
)

CATALOG_STORAGE_RESPONSE = {
    'places': [
        {
            'place_id': 50,
            'created_at': '2021-01-01T09:00:00+06:00',
            'updated_at': '2021-01-01T09:00:00+06:00',
            'place': {
                'slug': 'some_slug',
                'enabled': True,
                'name': 'some_name',
                'revision': 1,
                'type': 'native',
                'business': 'restaurant',
                'launched_at': '2021-01-01T09:00:00+06:00',
                'payment_methods': ['cash', 'payture', 'taxi'],
                'gallery': [{'type': 'image', 'url': 'some_url', 'weight': 1}],
                'brand': {
                    'id': 100,
                    'slug': 'some_slug',
                    'name': 'some_brand',
                    'picture_scale_type': 'aspect_fit',
                },
                'address': {'city': 'Moscow', 'short': 'some_address'},
                'country': {
                    'id': 1,
                    'name': 'Russia',
                    'code': 'RU',
                    'currency': {'sign': 'RUB', 'code': 'RUB'},
                },
                'categories': [{'id': 1, 'name': 'some_name'}],
                'quick_filters': {
                    'general': [{'id': 1, 'slug': 'some_slug'}],
                    'wizard': [{'id': 1, 'slug': 'some_slug'}],
                },
                'region': {'id': 1, 'geobase_ids': [1], 'time_zone': 'UTC'},
                'location': {'geo_point': [52.569089, 39.60258]},
                'rating': {'users': 5.0, 'admin': 5.0, 'count': 1},
                'price_category': {'id': 1, 'name': 'some_name', 'value': 5.0},
                'extra_info': {},
                'features': {
                    'ignore_surge': False,
                    'supports_preordering': False,
                    'fast_food': False,
                },
                'timing': {
                    'preparation': 60.0,
                    'extra_preparation': 60.0,
                    'average_preparation': 60.0,
                },
                'sorting': {'weight': 5, 'popular': 5},
                'assembly_cost': 1,
            },
        },
    ],
    'not_found_places': ['40'],
}

DETECTORS_CONFIG = {
    'lateness_accepted': {
        'events_settings': [
            {'enabled': True, 'delay_sec': 0, 'order_event': 'finished'},
        ],
    },
}
LA_ACTION = {
    'push_action_default': {
        'type': 'eater_notification',
        'payload': {
            'notification_code': 'lateness_accepted.promocode',
            'channels': ['push', 'taxi_push'],
        },
    },
}

CONFIG_LATENESS_ACCEPTED_ON = pytest.mark.experiments3(
    name='eats_proactive_support_lateness_accepted_detector',
    consumers=['eats_proactive_support/lateness_accepted_detector'],
    default_value={'enabled': True},
    is_config=True,
)

CONFIG_LATENESS_ACCEPTED_OFF = pytest.mark.experiments3(
    name='eats_proactive_support_lateness_accepted_detector',
    consumers=['eats_proactive_support/lateness_accepted_detector'],
    default_value={'enabled': False},
    is_config=True,
)

LATENESS_ACCEPTED_DETECTOR_EXPERIMENT = pytest.mark.experiments3(
    name='eats_proactive_support_lateness_accepted_detector_actions',
    consumers=['eats_proactive_support/lateness_accepted_detector'],
    default_value={'enabled': False},
    clauses=[
        {
            'enabled': True,
            'extension_method': 'replace',
            'value': {'payload': {'rate': '10', 'max_value': '100'}},
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'arg_name': 'lateness_value_sec',
                                'arg_type': 'int',
                                'value': 300,
                            },
                            'type': 'gt',
                        },
                    ],
                },
            },
        },
    ],
)


def assert_db_problems(psql, expected_db_problems_count):
    cursor = psql.cursor()
    cursor.execute(
        'SELECT * FROM eats_proactive_support.problems'
        ' WHERE type=\'lateness_accepted\';',
    )
    db_problems = cursor.fetchall()
    assert len(db_problems) == expected_db_problems_count


def assert_db_actions(psql, expected_db_actions_count):
    cursor = psql.cursor()
    cursor.execute('SELECT * FROM eats_proactive_support.actions;')
    db_actions = cursor.fetchall()
    assert len(db_actions) == expected_db_actions_count


@pytest.fixture(name='mock_eats_catalog_storage')
def _mock_eats_catalog_storage(mockserver):
    @mockserver.json_handler(CATALOG_STORAGE_URL)
    def mock(request):
        return mockserver.make_response(
            status=200, json=CATALOG_STORAGE_RESPONSE,
        )

    return mock


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(EATS_PROACTIVE_SUPPORT_PROBLEM_LATENESS_ACCEPTED=LA_ACTION)
@LATENESS_ACCEPTED_DETECTOR_EXPERIMENT
@CONFIG_LATENESS_ACCEPTED_OFF
@pytest.mark.pgsql('eats_proactive_support', files=['fill_database.sql'])
@pytest.mark.now('2020-04-28T12:30:00+03:00')  # reallly lateness is 30 minutes
async def test_lateness_accepted_detector_disabled(stq_runner, pgsql, stq):
    order_nr = '123'
    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': order_nr,
            'event_name': 'finished',
            'detector_name': 'lateness_accepted',
        },
    )

    assert_db_problems(pgsql['eats_proactive_support'], 0)
    assert_db_actions(pgsql['eats_proactive_support'], 0)

    assert stq.eats_proactive_support_actions.times_called == 0


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(EATS_PROACTIVE_SUPPORT_PROBLEM_LATENESS_ACCEPTED=LA_ACTION)
@LATENESS_ACCEPTED_DETECTOR_EXPERIMENT
@CONFIG_LATENESS_ACCEPTED_ON
@pytest.mark.now('2020-04-28T12:30:00+03:00')  # reallly lateness is 30 minutes
@pytest.mark.pgsql('eats_proactive_support', files=['fill_database.sql'])
@pytest.mark.parametrize(
    """order_nr,expected_eats_catalog_storage_count""",
    [('123', 0), ('100', 0)],  # no_lateness_problem_in_db  # not_exist_order
    ids=['no_lateness_problem_in_db', 'not_exist_order'],
)
async def test_lateness_accepted_detector_not_detected_problem(
        stq_runner, pgsql, stq, order_nr, expected_eats_catalog_storage_count,
):
    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': order_nr,
            'event_name': 'finished',
            'detector_name': 'lateness_accepted',
        },
    )

    assert_db_problems(pgsql['eats_proactive_support'], 0)
    assert_db_actions(pgsql['eats_proactive_support'], 0)

    assert stq.eats_proactive_support_actions.times_called == 0
    assert stq.eats_proactive_support_detections.times_called == 0


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(EATS_PROACTIVE_SUPPORT_PROBLEM_LATENESS_ACCEPTED=LA_ACTION)
@LATENESS_ACCEPTED_DETECTOR_EXPERIMENT
@CONFIG_LATENESS_ACCEPTED_ON
@pytest.mark.pgsql('eats_proactive_support', files=['fill_database.sql'])
@pytest.mark.parametrize(
    """catalog_body,catalog_code""",
    [
        ({'places': [], 'not_found_places': ['40']}, 200),
        ({'code': '500', 'message': 'mess_500'}, 500),
    ],
    ids=['not_found_places', 'error_500'],
)
async def test_lateness_accepted_detector_catalog_problems(
        stq_runner, pgsql, stq, catalog_body, catalog_code, mockserver,
):
    order_nr = '124'

    @mockserver.json_handler(
        f'eats-core-orders/internal-api/v1/order/{order_nr}/metainfo',
    )
    def _mock_core_metainfo(request):
        return mockserver.make_response(
            status=200,
            json={
                'order_nr': order_nr,
                'location_latitude': 1.0,
                'location_longitude': 2.0,
                'is_asap': True,
                'place_id': '50',
                'region_id': '1',
                'order_status_history': {  # reallly lateness is 30 minutes
                    'arrived_to_customer_at': '2020-04-28T12:30:00+03:00',
                },
            },
        )

    @mockserver.json_handler(CATALOG_STORAGE_URL)
    def _mock_catalog_storage(request):
        return mockserver.make_response(status=catalog_code, json=catalog_body)

    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': order_nr,  # place_id = 40 from database
            'event_name': 'finished',
            'detector_name': 'lateness_accepted',
        },
    )

    assert_db_problems(pgsql['eats_proactive_support'], 0)
    assert_db_actions(pgsql['eats_proactive_support'], 0)

    assert _mock_core_metainfo.times_called == 1
    assert _mock_catalog_storage.times_called == 1
    assert stq.eats_proactive_support_actions.times_called == 0


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(EATS_PROACTIVE_SUPPORT_PROBLEM_LATENESS_ACCEPTED=LA_ACTION)
@LATENESS_ACCEPTED_DETECTOR_EXPERIMENT
@CONFIG_LATENESS_ACCEPTED_ON
@pytest.mark.pgsql('eats_proactive_support', files=['fill_database.sql'])
@pytest.mark.parametrize(
    """metainfo_body, metainfo_code""",
    [
        (
            {
                'order_nr': '123',
                'location_latitude': 1.0,
                'location_longitude': 1.0,
                'is_asap': True,
                'place_id': '50',
                'region_id': '1',
            },
            200,
        ),
        (
            {
                'order_nr': '123',
                'location_latitude': 1.0,
                'location_longitude': 1.0,
                'is_asap': True,
                'place_id': '50',
                'region_id': '1',
                'order_status_history': {
                    'created_at': (
                        '2020-04-28T12:30:00+03:00'  # not arrived_at
                    ),
                },
            },
            200,
        ),
        ({'code': '404', 'message': 'mess_404'}, 404),
        ({'code': '500', 'message': 'mess_500'}, 500),
    ],
    ids=[
        'no_order_status_history',
        'no_arrived_to_customer_at',
        'error_404',
        'error_500',
    ],
)
async def test_lateness_accepted_detector_metainfo_problems(
        stq_runner, pgsql, stq, metainfo_body, metainfo_code, mockserver,
):
    order_nr = '125'

    @mockserver.json_handler(
        f'eats-core-orders/internal-api/v1/order/{order_nr}/metainfo',
    )
    def _mock_core_metainfo(request):
        return mockserver.make_response(
            status=metainfo_code, json=metainfo_body,
        )

    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': order_nr,
            'event_name': 'finished',
            'detector_name': 'lateness_accepted',
        },
    )

    assert_db_problems(pgsql['eats_proactive_support'], 0)
    assert_db_actions(pgsql['eats_proactive_support'], 0)

    assert _mock_core_metainfo.times_called == 1
    assert stq.eats_proactive_support_actions.times_called == 0


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(EATS_PROACTIVE_SUPPORT_PROBLEM_LATENESS_ACCEPTED=LA_ACTION)
@LATENESS_ACCEPTED_DETECTOR_EXPERIMENT
@CONFIG_LATENESS_ACCEPTED_ON
@pytest.mark.pgsql('eats_proactive_support', files=['fill_database.sql'])
@pytest.mark.parametrize(
    """order_nr, exp_metainfo_called""",
    [
        ('125', 1),
        ('126', 0),
    ],  # have place_id with founded info from CATALOG_STORAGE_RESPONSE
    ids=['native', 'marketplace'],
)
@pytest.mark.now(
    '2020-04-28T12:30:00+03:00',
)  # reallly lateness is 30 minutes for marketplace
async def test_lateness_accepted_detector_greenflow(
        stq_runner, order_nr, exp_metainfo_called, pgsql, stq, mockserver,
):
    @mockserver.json_handler(CATALOG_STORAGE_URL)
    def _mock_catalog_storage(request):
        return mockserver.make_response(
            status=200, json=CATALOG_STORAGE_RESPONSE,
        )

    @mockserver.json_handler(
        f'eats-core-orders/internal-api/v1/order/{order_nr}/metainfo',
    )
    def _mock_core_metainfo(request):
        return mockserver.make_response(
            status=200,
            json={
                'order_nr': order_nr,
                'location_latitude': 1.0,
                'location_longitude': 1.0,
                'is_asap': True,
                'place_id': '50',
                'region_id': '1',
                'order_status_history': {
                    # reallly lateness is 30 minutes for native
                    'arrived_to_customer_at': '2020-04-28T12:30:00+03:00',
                },
            },
        )

    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': order_nr,
            'event_name': 'finished',
            'detector_name': 'lateness_accepted',
        },
    )

    assert_db_problems(pgsql['eats_proactive_support'], 1)
    assert_db_actions(pgsql['eats_proactive_support'], 2)

    assert _mock_catalog_storage.times_called == 1
    assert _mock_core_metainfo.times_called == exp_metainfo_called
    assert stq.eats_proactive_support_actions.times_called == 2
