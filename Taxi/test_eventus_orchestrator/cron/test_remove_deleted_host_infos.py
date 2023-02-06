import pytest

from eventus_orchestrator.generated.cron import run_cron


async def run_host_info_clean():
    await run_cron.main(
        [
            'eventus_orchestrator.crontasks.remove_deleted_host_infos',
            '-t',
            '0',
        ],
    )


def get_nanny_resp_for_host(hostname: str):
    return {
        'engine': '',
        'network_settings': 'MTN_ENABLED',
        'container_hostname': hostname,
        'hostname': 'man0-3730.search.yandex.net',
        'port': 80,
        'itags': [
            'a_geo_man',
            'a_dc_man',
            'a_itype_order-events-producer',
            'a_ctype_testing',
            'a_prj_taxi_order-events-producer_testing',
            'a_metaprj_taxi',
            'a_tier_none',
            'use_hq_spec',
            'enable_hq_report',
            'enable_hq_poll',
        ],
    }


_NANNY_RESPONSE = {
    'result': [
        get_nanny_resp_for_host('gmqnrk4fmwjqie6o.man.yp-c.yandex.net'),
        get_nanny_resp_for_host('hvh6pxgqmmhsqubw.sas.yp-c.yandex.net'),
    ],
}


def get_mock_handler_name(nanny_service_id):
    return (
        '/client-nanny/v2/services/'
        f'{nanny_service_id}/current_state/instances/'
    )


def check_instances_and_schemas(mongodb, expected_instances, expected_schemas):
    current_instances = list(mongodb.eventus_instances.find({}, {'_id': 0}))
    current_schemas = list(
        mongodb.eventus_pipeline_schemas.find({}, {'_id': 0}),
    )
    assert expected_instances == current_instances
    assert expected_schemas == current_schemas


@pytest.mark.filldb(eventus_instances='no_nanny_id_1')
async def test_absent_nanni_id_1(
        taxi_eventus_orchestrator_web,
        taxi_config,
        mockserver,
        load_json,
        mongodb,
):
    @mockserver.json_handler(
        get_mock_handler_name('taxi_order-events-producer_testing'),
    )
    def handler(request):
        assert request.method in ['GET']
        return _NANNY_RESPONSE

    _ = handler

    await run_host_info_clean()

    check_instances_and_schemas(
        mongodb,
        load_json('db_eventus_instances_no_nanny_id_1.json'),
        load_json('db_eventus_pipeline_schemas.json'),
    )


@pytest.mark.filldb(eventus_instances='no_nanny_id_2')
async def test_absent_nanni_id_2(
        taxi_eventus_orchestrator_web,
        taxi_config,
        mockserver,
        load_json,
        mongodb,
):
    @mockserver.json_handler(
        get_mock_handler_name('taxi_order-events-producer_testing'),
    )
    def handler(request):
        assert request.method in ['GET']
        return _NANNY_RESPONSE

    _ = handler

    await run_host_info_clean()

    check_instances_and_schemas(
        mongodb,
        load_json('db_eventus_instances_no_nanny_id_2.json'),
        load_json('db_eventus_pipeline_schemas.json'),
    )


@pytest.mark.filldb(eventus_instances='empty')
async def test_empty_instances(
        taxi_eventus_orchestrator_web,
        taxi_config,
        mockserver,
        load_json,
        mongodb,
):
    @mockserver.json_handler(
        get_mock_handler_name('taxi_order-events-producer_testing'),
    )
    def handler(request):
        assert request.method in ['GET']
        return _NANNY_RESPONSE

    _ = handler

    await run_host_info_clean()

    check_instances_and_schemas(
        mongodb,
        load_json('db_eventus_instances_empty.json'),
        load_json('db_eventus_pipeline_schemas.json'),
    )


def get_expected_collection(
        json_val,
        host_field,
        prestable_hosts,
        stable_hosts,
        another_instance_hosts,
):
    result = list(
        filter(
            lambda val: val[host_field] in prestable_hosts
            or val[host_field] in stable_hosts
            or val[host_field] in another_instance_hosts,
            json_val,
        ),
    )
    return result


@pytest.mark.parametrize(
    'prestable_hosts, stable_hosts, another_instance_hosts',
    [
        (['karachaevo-cherkesiya.taxi.tst.yandex.net'], [], []),
        ([], ['ulyalya.taxi.yandex.net'], []),
        ([], [], ['ulyalya2.taxi.yandex.net', 'ulyalya3.taxi.yandex.net']),
        ([], [], ['ulyalya3.taxi.yandex.net']),
        (
            ['karachaevo-cherkesiya.taxi.tst.yandex.net'],
            ['ulyalya.taxi.yandex.net'],
            ['ulyalya2.taxi.yandex.net', 'ulyalya3.taxi.yandex.net'],
        ),
        (
            [
                'extra_host1.yandex.net',
                'karachaevo-cherkesiya.taxi.tst.yandex.net',
            ],
            ['extra_host2.yandex.net', 'ulyalya.taxi.yandex.net'],
            [
                'extra_host3.yandex.net',
                'ulyalya2.taxi.yandex.net',
                'ulyalya3.taxi.yandex.net',
            ],
        ),
    ],
)
@pytest.mark.filldb(
    eventus_instances='normal', eventus_pipeline_schemas='normal',
)
async def test_delete(
        taxi_eventus_orchestrator_web,
        taxi_config,
        mockserver,
        load_json,
        mongodb,
        prestable_hosts,
        stable_hosts,
        another_instance_hosts,
):
    @mockserver.json_handler(
        get_mock_handler_name('taxi_order-events-producer_pre_stable'),
    )
    def handler_prestable(request):
        assert request.method in ['GET']
        return {
            'result': [
                get_nanny_resp_for_host(host) for host in prestable_hosts
            ],
        }

    _ = handler_prestable

    @mockserver.json_handler(
        get_mock_handler_name('taxi_order-events-producer_stable'),
    )
    def handler_stable(request):
        assert request.method in ['GET']
        return {
            'result': [get_nanny_resp_for_host(host) for host in stable_hosts],
        }

    _ = handler_stable

    @mockserver.json_handler(
        get_mock_handler_name('taxi_another-instance_stable'),
    )
    def handler_another(request):
        assert request.method in ['GET']
        return {
            'result': [
                get_nanny_resp_for_host(host)
                for host in another_instance_hosts
            ],
        }

    _ = handler_another

    await run_host_info_clean()

    check_instances_and_schemas(
        mongodb,
        get_expected_collection(
            load_json('db_eventus_instances_normal.json'),
            'host',
            prestable_hosts,
            stable_hosts,
            another_instance_hosts,
        ),
        get_expected_collection(
            load_json('db_eventus_pipeline_schemas_normal.json'),
            'hostname',
            prestable_hosts,
            stable_hosts,
            another_instance_hosts,
        ),
    )
