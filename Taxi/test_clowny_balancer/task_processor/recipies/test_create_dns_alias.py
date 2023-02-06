async def test_create_dns_alias(
        dns_mockserver,
        mock_clownductor,
        load_yaml,
        task_processor,
        run_job_common,
):
    dns_mockserver()

    @mock_clownductor('/v1/branches/')
    def _branches(_):
        return [
            {
                'id': 1,
                'env': 'unstable',
                'direct_link': 'taxi_service_unstable',
                'name': '',
                'service_id': 0,
            },
        ]

    @mock_clownductor('/v1/hosts/')
    def _hosts(request):
        host = 'host.yp.net'
        branch_id = int(request.query['branch_id'])
        if branch_id == 2:
            host = 'host.ucustom.yp.net'
        return [{'branch_id': branch_id, 'name': host}]

    recipe = task_processor.load_recipe(
        load_yaml('CreateBalancerAlias.yaml')['data'],
    )
    job = await recipe.start_job(
        job_vars={
            'service_id': 123,
            'env': 'unstable',
            'fqdn': 'test-fqdn.net',
        },
        initiator='clowny-balancer',
    )
    await run_job_common(job)

    assert job.job_vars == {
        'env': 'unstable',
        'fqdn': 'test-fqdn.net',
        'host': 'host.yp.net',
        'origin_fqdn': '',
        'service_id': 123,
    }
