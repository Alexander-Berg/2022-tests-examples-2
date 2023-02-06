async def test_recipe(load_yaml, mockserver, task_processor, run_job_common):
    @mockserver.json_handler('/client-awacs/api/ListL3Balancers/')
    def _list_l3(_):
        return {
            'l3Balancers': [
                {
                    'meta': {'id': 'l3-balancer'},
                    'spec': {'l3mgrServiceId': '123'},
                },
            ],
        }

    @mockserver.json_handler('/client-awacs/api/RemoveL3Balancer/')
    def _remove_l7(request):
        assert request.json['id'] == 'l3-balancer'

    @mockserver.json_handler('/client-awacs/api/ListBalancers/')
    def _list_l7(_):
        return {
            'balancers': [
                {
                    'meta': {
                        'id': 'awacs_ns_1_sas',
                        'location': {
                            'type': 'YP_CLUSTER',
                            'yp_cluster': 'SAS',
                        },
                    },
                },
            ],
        }

    get_balancer_called = False

    @mockserver.json_handler('/client-awacs/api/GetBalancer/')
    def _get_balancer(_):
        nonlocal get_balancer_called
        if get_balancer_called:
            return mockserver.make_response(status=404)
        get_balancer_called = True
        return {}

    @mockserver.json_handler('/client-awacs/api/RemoveBalancer/')
    def _delete_balancer(_):
        return {}

    @mockserver.json_handler('/client-awacs/api/ListBackends/')
    def _list_backends(_):
        return {'backends': []}

    @mockserver.json_handler('/client-awacs/api/RemoveNamespace/')
    def _delete_namespace(_):
        return {}

    @mockserver.json_handler('/client-awacs/api/GetNamespace/')
    def _get_namespace(_):
        return {'namespace': {'meta': {'id': 'awacs-ns-1', 'version': 'some'}}}

    list_domains_once = False

    @mockserver.json_handler('/client-awacs/api/ListDomains/')
    def _list_domains(_):
        nonlocal list_domains_once
        if not list_domains_once:
            list_domains_once = True
            return {
                'domains': [
                    {'meta': {'id': 'domain-1'}},
                    {'meta': {'id': 'domain-2'}},
                ],
            }
        return {'domains': []}

    get_domain_once = False

    @mockserver.json_handler('/client-awacs/api/GetDomain/')
    def _get_domain(_):
        nonlocal get_domain_once
        if not get_domain_once:
            get_domain_once = True
            return {'meta': {'id': 'domina-1'}}
        return mockserver.make_response(status=404)

    @mockserver.json_handler('/client-awacs/api/RemoveDomain/')
    def _remove_domain(_):
        return {}

    remove_certs_called = False

    @mockserver.json_handler('/client-awacs/api/ListCertificates/')
    def _list_certs(_):
        nonlocal remove_certs_called
        if not remove_certs_called:
            return {'certificates': [{'meta': {'id': 'cert-1'}}]}
        return {'certificates': []}

    @mockserver.json_handler('/client-awacs/api/RemoveCertificate/')
    def _remove_cert(_):
        nonlocal remove_certs_called
        remove_certs_called = True
        return {}

    recipe = task_processor.load_recipe(
        load_yaml('RemoveAwacsBalancer.yaml')['data'],
    )
    job = await recipe.start_job(
        job_vars={'namespace_id': 1}, initiator='clowny-balancer',
    )
    await run_job_common(job)
    assert job.job_vars == {
        'awacs_domain_ids': ['domain-1', 'domain-2'],
        'deleting_awacs_domain_ids': ['domain-1'],
        'awacs_certificate_ids': ['cert-1'],
        'deleting_certificate_ids': ['cert-1'],
        'awacs_namespace_id': 'awacs-ns-1',
        'balancer_man': '',
        'balancer_sas': 'awacs_ns_1_sas',
        'balancer_vla': '',
        'entry_point_ids': [1],
        'namespace_id': 1,
        'upstream_ids': [1, 2],
    }
