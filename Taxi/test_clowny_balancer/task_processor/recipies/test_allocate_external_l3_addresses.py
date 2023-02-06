import pytest


@pytest.mark.usefixtures('allocate_l3_addresses_mocks')
async def test_recipe(load_yaml, task_processor, run_job_common):

    recipe = task_processor.load_recipe(
        load_yaml('AllocateExternalL3Addresses.yaml')['data'],
    )
    job = await recipe.start_job(
        job_vars={
            'abc_service_slug': 'taxi_abc_service',
            'l3mgr_service_id': '123',
            'fqdn': 'service-fqdn.net',
            'author': 'd1mbas',
        },
        initiator='clowny-balancer',
    )
    await run_job_common(job)

    assert job.job_vars == {
        'abc_service_slug': 'taxi_abc_service',
        'author': 'd1mbas',
        'components': [28072],
        'description': (
            'Привет, нужны ip-адреса для внешнего балансера '
            'service-fqdn.net.'
        ),
        'followers': ['d1mbas'],
        'fqdn': 'service-fqdn.net',
        'l3_update_succeeded': True,
        'l3mgr_config_id': '1',
        'l3mgr_service_id': '123',
        'new_vs_ids': ['1', '2', '3', '4', '5'],
        'queue': '',
        'title': 'IP для внешнего балансера service-fqdn.net',
        'traffic_ticket': '',
    }
