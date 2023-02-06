import pytest

ALERTS_PAGE_SIZE = 50
TEMPLATES_PAGE_SIZE = 10
CHANNEL_ID = 'channel_id'
TPL_ID = 'tpl_id'
TPL_VERSION = 'tpl_v'
DEBUG_TPL_ID = 'debug_tpl_id'
DEBUG_TPL_VERSION = 'debug_tpl_v'
DEBUG_DATA = {
    'enabled': True,
    'templates': [
        {'template_id': DEBUG_TPL_ID, 'template_version': DEBUG_TPL_VERSION},
        {'template_id': TPL_ID, 'template_version': TPL_VERSION},
    ],
}
CREATED_BY = 'hejmdal_testsuite'
CREATED_BY_DEBUG = CREATED_BY + '_debug'
RE_INIT_PERIOD = 2
HEJMDAL_SOLOMON_COMPONENT_SETTINGS = {
    'enabled': True,
    'get_alerts_page_size': ALERTS_PAGE_SIZE,
    'get_templates_page_size': TEMPLATES_PAGE_SIZE,
    'notification_channel_ids': ['test-channel'],
    'period_min': 5,
    're_initialization_period_iterations': RE_INIT_PERIOD,
    're_notification_period_sec': 90,
    'solomon_requests_settings': {'retries': 3, 'timeout': 1000},
}


def create_alert(alert_id, template_id, template_version, created_by):
    return {
        'id': alert_id,
        'type': {
            'fromTemplate': {
                'templateId': template_id,
                'templateVersionTag': template_version,
            },
        },
        'labels': {'created_by': created_by},
    }


def create_alert_template(tpl_id, tpl_version, object_type):
    return {
        'id': tpl_id,
        'templateVersionTag': tpl_version,
        'serviceProviderId': 'hejmdal',
        'name': 'Test Template',
        'description': 'test description',
        'createdBy': '',
        'createdAt': '2022-04-27T15:49:43.712Z',
        'updatedBy': '',
        'updatedAt': '2022-04-27T15:49:43.712Z',
        'groupByLabels': ['host'],
        'type': {
            'expression': {
                'program': 'warn_if(random01() > {{templateParameter.warn}});',
            },
        },
        'annotations': {
            'juggler_raw_event_service': 'hejmdal-test-alert',
            'juggler_raw_event_host': '{{labels.host}}',
            'alert_description': 'Warning!',
        },
        'labels': {
            'object_type': object_type,
            'cluster_type': 'nanny',
            'env': 'stable',
        },
        'periodMillis': 300000,
        'delaySeconds': 0,
        'resolvedEmptyPolicy': 'RESOLVED_EMPTY_MANUAL',
        'noPointsPolicy': 'NO_POINTS_MANUAL',
        'isDefaultTemplate': False,
        'intParameters': [
            {
                'defaultValue': 0,
                'name': 'service_id',
                'title': 'Service ID',
                'description': '',
                'unitFormat': 'UNIT_FORMAT_UNSPECIFIED',
            },
            {
                'defaultValue': 0,
                'name': 'branch_id',
                'title': 'Branch ID',
                'description': '',
                'unitFormat': 'UNIT_FORMAT_UNSPECIFIED',
            },
        ],
        'textParameters': [
            {
                'defaultValue': '',
                'name': 'service_name',
                'title': 'Service Name',
                'description': '',
            },
            {
                'defaultValue': '',
                'name': 'direct_link',
                'title': 'Branch Direct Link',
                'description': '',
            },
        ],
        'doubleThresholds': [
            {
                'defaultValue': 0.5,
                'name': 'warn',
                'title': 'Warning threshold, [%, 0.0 - 1.0]',
                'description': '',
                'unitFormat': 'UNIT_FORMAT_UNSPECIFIED',
            },
        ],
    }


async def solomon_component_iteration(
        taxi_hejmdal,
        testpoint,
        templates_cnt,
        alerts_created,
        alerts_deleted,
        request_errors,
):
    @testpoint('solomon-distlock::iteration-finished')
    def task_progress(stats):
        assert stats['received-templates-cnt'] == templates_cnt
        assert stats['alerts-created'] == alerts_created
        assert stats['alerts-deleted'] == alerts_deleted
        assert stats['request-errors'] == request_errors

    await taxi_hejmdal.run_task('services_component/invalidate')

    async with taxi_hejmdal.spawn_task('distlock/solomon-distlock'):
        await task_progress.wait_call()


@pytest.mark.config(
    HEJMDAL_SOLOMON_COMPONENT_SETTINGS=HEJMDAL_SOLOMON_COMPONENT_SETTINGS,
)
async def test_main(taxi_hejmdal, testpoint, mockserver, taxi_config):
    alerts_in_solomon = dict()
    iter_cnt = 0

    # Delete alert - register delete handler for created alerts
    def register_mock_delete_alert(alert_id):
        @mockserver.json_handler(f'/api/v2/projects/hejmdal/alerts/{alert_id}')
        def _mock_delete_alert(request):
            assert request.headers['X-Service-Provider'] == 'hejmdal'

            if alert_id not in alerts_in_solomon:
                # alert with such ID already exists
                return mockserver.make_response(status=404)

            del alerts_in_solomon[alert_id]
            return mockserver.make_response(status=204)

    # Create alert - check header, register delete handler and return alert
    @mockserver.json_handler('/api/v2/projects/hejmdal/alerts')
    def _mock_create_alert(request):
        assert request.headers['X-Service-Provider'] == 'hejmdal'

        alert_data = request.json
        alert_id = alert_data['id']
        if alert_id in alerts_in_solomon:
            # alert with such ID already exists
            return mockserver.make_response(status=400)

        register_mock_delete_alert(alert_id)
        alerts_in_solomon[alert_id] = request.json
        return mockserver.make_response(status=200, json=request.json)

    # Mock request to Solomon to receive existed alerts
    # Must be called during (re)initialization
    @mockserver.json_handler('/api/v2/projects/hejmdal/alertsFullModel')
    def _mock_alerts_full_model(request):
        # check that re-init called correctly
        assert iter_cnt % RE_INIT_PERIOD == 0

        assert request.query['pageSize'] == f'{ALERTS_PAGE_SIZE}'
        assert (
            request.query['labelsSelector']
            == f'created_by={CREATED_BY}|{CREATED_BY_DEBUG}'
        )

        return {'items': [alert for _, alert in alerts_in_solomon]}

    # Register mock handlers for published templates
    def reg_get_published_tpl_mock(empty):
        @mockserver.json_handler('/api/v2/alertTemplates')
        def _get_published_template(request):
            assert request.query['serviceProviderId'] == 'hejmdal'
            assert request.query['pageSize'] == f'{TEMPLATES_PAGE_SIZE}'

            if empty:
                response = {'items': []}
            else:
                response = {
                    'items': [
                        create_alert_template(TPL_ID, TPL_VERSION, 'branch'),
                    ],
                }
            return response

    # Register mock handlers for debug templates
    def reg_get_debug_tpl_mock(tpl_id, tpl_version, object_type):
        @mockserver.json_handler(
            f'/api/v2/alertTemplates/{tpl_id}/versions/{tpl_version}',
        )
        def _get_debug_template(request):
            return create_alert_template(tpl_id, tpl_version, object_type)

    # Case 1.
    # - No alerts in Solomon
    # - 1 published template
    # - No debug templates
    #
    # Expect: 1 alert will be created for published template
    reg_get_published_tpl_mock(empty=False)
    await solomon_component_iteration(
        taxi_hejmdal,
        testpoint,
        templates_cnt=1,
        alerts_created=1,
        alerts_deleted=0,
        request_errors=0,
    )
    iter_cnt += 1
    assert len(alerts_in_solomon) == 1

    # Case 2.
    # - 1 alert in Solomon: created for published template
    # - 1 published template
    # - No debug templates
    #
    # Expect: nothing will be created/removed
    await solomon_component_iteration(
        taxi_hejmdal,
        testpoint,
        templates_cnt=1,
        alerts_created=0,
        alerts_deleted=0,
        request_errors=0,
    )
    iter_cnt += 1
    assert len(alerts_in_solomon) == 1

    # Case 3.
    # - 1 alert in Solomon: created for published template
    # - 1 published template
    # - 2 debug templates, 1 with same id as the published one
    #
    # Expect: 2 alerts for debug template will be created
    reg_get_debug_tpl_mock(TPL_ID, TPL_VERSION, 'branch')
    reg_get_debug_tpl_mock(DEBUG_TPL_ID, DEBUG_TPL_VERSION, 'host')
    HEJMDAL_SOLOMON_COMPONENT_SETTINGS['debug'] = DEBUG_DATA
    taxi_config.set_values(
        {
            'HEJMDAL_SOLOMON_COMPONENT_SETTINGS': (
                HEJMDAL_SOLOMON_COMPONENT_SETTINGS
            ),
        },
    )
    await taxi_hejmdal.invalidate_caches()
    await solomon_component_iteration(
        taxi_hejmdal,
        testpoint,
        templates_cnt=2,
        alerts_created=2,
        alerts_deleted=0,
        request_errors=0,
    )
    iter_cnt += 1
    assert len(alerts_in_solomon) == 3

    # Case 4.
    # - 3 alert in Solomon: created for published and debug templates
    # - No published template
    # - 2 debug templates
    #
    # Expect: 1 alert will be removed (because published template was
    # unpublished) and 1 alert will be created (for debug template with the
    # same id as the published one)
    reg_get_published_tpl_mock(empty=True)
    await solomon_component_iteration(
        taxi_hejmdal,
        testpoint,
        templates_cnt=2,
        alerts_created=1,
        alerts_deleted=1,
        request_errors=0,
    )
    iter_cnt += 1
    assert len(alerts_in_solomon) == 3

    # Case 5.
    # - 3 alert in Solomon: created for debug templates
    # - No published template
    # - No debug templates
    #
    # Expect: 3 alerts will be removed for debug templates as debug was
    # disabled
    DEBUG_DATA['enabled'] = False
    HEJMDAL_SOLOMON_COMPONENT_SETTINGS['debug'] = DEBUG_DATA
    taxi_config.set_values(
        {
            'HEJMDAL_SOLOMON_COMPONENT_SETTINGS': (
                HEJMDAL_SOLOMON_COMPONENT_SETTINGS
            ),
        },
    )
    await taxi_hejmdal.invalidate_caches()
    await solomon_component_iteration(
        taxi_hejmdal,
        testpoint,
        templates_cnt=0,
        alerts_created=0,
        alerts_deleted=3,
        request_errors=0,
    )
    iter_cnt += 1
    assert not alerts_in_solomon
