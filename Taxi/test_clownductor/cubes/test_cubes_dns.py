from clownductor.internal.tasks import cubes


def task_data(name='name'):
    return {
        'id': 123,
        'job_id': 456,
        'name': name,
        'sleep_until': 0,
        'input_mapping': {},
        'output_mapping': {},
        'payload': {},
        'retries': 0,
        'status': 'in_progress',
        'error_message': None,
        'created_at': 0,
        'updated_at': 0,
    }


async def test_create_record(web_context, dns_mockserver):
    dns_mockserver()

    cube = cubes.CUBES['DNSCreateRecord'](
        web_context,
        task_data(),
        {
            'fqdn': 'clownductor.taxi.yandex.net',
            'ipv6': '2a02:6b8:0:3400:0:71d:0:176',
        },
        [],
        None,
    )

    await cube.update()

    assert cube.success


async def test_wait_for_job(web_context, dns_mockserver):
    dns_mockserver()

    cube = cubes.CUBES['DNSWaitForJob'](
        web_context, task_data(), {'job_id': '1324'}, [], None,
    )

    await cube.update()

    assert cube.success


async def test_create_alias(web_context, dns_mockserver):
    dns_mockserver()

    cube = cubes.CUBES['DNSCreateAlias'](
        web_context,
        task_data(),
        {
            'alias': 'clownductor.taxi.dev.yandex.net',
            'canonical_name': (
                'taxi-infra-clownductor-' 'unstable-1.sas.yp-c.yandex.net'
            ),
        },
        [],
        None,
    )

    await cube.update()

    assert cube.success
