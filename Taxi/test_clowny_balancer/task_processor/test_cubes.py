async def test_get_cubes(get_all_cubes):
    response = await get_all_cubes()
    assert response == {
        'cubes': [
            {
                'name': 'AwacsAddDcToSlowBackends',
                'needed_parameters': ['namespace_ids'],
                'optional_parameters': [
                    'pod_ids_by_region',
                    'vla_pod_ids',
                    'sas_pod_ids',
                    'man_pod_ids',
                    'environment',
                ],
                'output_parameters': [],
            },
            {
                'name': 'AwacsBackendAddLinksToDB',
                'needed_parameters': ['entry_point_id', 'upstream_ids'],
                'optional_parameters': [],
                'output_parameters': [],
            },
            {
                'name': 'AwacsBackendCreate',
                'needed_parameters': [
                    'namespace_id',
                    'endpoint_set_id',
                    'branch_id',
                ],
                'optional_parameters': ['datacenters', 'backend_id'],
                'output_parameters': ['upstream_id'],
            },
            {
                'name': 'AwacsBackendFindSystem',
                'needed_parameters': ['namespace_id'],
                'optional_parameters': [],
                'output_parameters': ['backend_ids'],
            },
            {
                'name': 'AwacsBackendWaitFor',
                'needed_parameters': ['namespace_id'],
                'optional_parameters': [
                    'wait_for',
                    'backend_id',
                    'backend_ids',
                    'for_delete',
                ],
                'output_parameters': [],
            },
            {
                'name': 'AwacsBackendsCreateByDc',
                'needed_parameters': ['entry_point_id'],
                'optional_parameters': [],
                'output_parameters': [
                    'upstream_ids',
                    'backend_ids_by_env',
                    'namespace_id',
                ],
            },
            {
                'name': 'AwacsBackendsDelete',
                'needed_parameters': ['namespace_id', 'backend_ids'],
                'optional_parameters': [],
                'output_parameters': ['backend_ids'],
            },
            {
                'name': 'AwacsBalancerAddHTTPS',
                'needed_parameters': ['namespace_id', 'balancer_id'],
                'optional_parameters': [],
                'output_parameters': [],
            },
            {
                'name': 'AwacsBalancerChangeOwners',
                'needed_parameters': ['namespace_id', 'balancer_id'],
                'optional_parameters': ['logins', 'groups'],
                'output_parameters': [],
            },
            {
                'name': 'AwacsBalancerChangeProject',
                'needed_parameters': ['new_project_id', 'service_id'],
                'optional_parameters': [],
                'output_parameters': [],
            },
            {
                'name': 'AwacsBalancerDelete',
                'needed_parameters': ['namespace_id', 'balancer_id'],
                'optional_parameters': [],
                'output_parameters': [],
            },
            {
                'name': 'AwacsBalancerGetBalancerIds',
                'needed_parameters': ['awacs_namespace_id'],
                'optional_parameters': [],
                'output_parameters': [
                    'balancer_sas',
                    'balancer_vla',
                    'balancer_man',
                ],
            },
            {
                'name': 'AwacsBalancerUpdateYamlForDomain',
                'needed_parameters': ['awacs_namespace_id', 'balancer_id'],
                'optional_parameters': [],
                'output_parameters': [],
            },
            {
                'name': 'AwacsBalancerWaitFor',
                'needed_parameters': ['namespace_id', 'balancer_id'],
                'optional_parameters': ['wait_for', 'for_deleted'],
                'output_parameters': [],
            },
            {
                'name': 'AwacsCertificateMetaInfo',
                'needed_parameters': ['namespace_id', 'cert_id'],
                'optional_parameters': [],
                'output_parameters': ['sectask_ticket'],
            },
            {
                'name': 'AwacsCertificateOrderNew',
                'needed_parameters': [
                    'namespace_id',
                    'cert_id',
                    'type',
                    'fqdn',
                ],
                'optional_parameters': ['additional_fqdns', 'st_ticket'],
                'output_parameters': [],
            },
            {
                'name': 'AwacsCertificateWaitFor',
                'needed_parameters': ['namespace_id', 'cert_id'],
                'optional_parameters': ['wait_for', 'st_ticket'],
                'output_parameters': [],
            },
            {
                'name': 'AwacsCertificatesGetMany',
                'needed_parameters': ['namespace_id', 'domain_ids'],
                'optional_parameters': ['with_dangling'],
                'output_parameters': ['certificate_ids'],
            },
            {
                'name': 'AwacsCertificatesManyDelete',
                'needed_parameters': ['namespace_id', 'certificate_ids'],
                'optional_parameters': [],
                'output_parameters': ['deleting_certificate_ids'],
            },
            {
                'name': 'AwacsCertificatesManyWaitFor',
                'needed_parameters': ['namespace_id', 'certificate_ids'],
                'optional_parameters': ['for_deleted'],
                'output_parameters': [],
            },
            {
                'name': 'AwacsCheckBalancerNotExists',
                'needed_parameters': ['fqdn'],
                'optional_parameters': [],
                'output_parameters': ['fqdn', 'origin_fqdn'],
            },
            {
                'name': 'AwacsCreateAwacsNamespace',
                'needed_parameters': [
                    'namespace_id',
                    'datacenters',
                    'active_backend_datacenters',
                ],
                'optional_parameters': ['size', 'network'],
                'output_parameters': [],
            },
            {
                'name': 'AwacsCreateDcLocalBackends',
                'needed_parameters': [
                    'branch_id',
                    'namespace_id',
                    'endpoint_set_id',
                ],
                'optional_parameters': [],
                'output_parameters': ['upstream_ids'],
            },
            {
                'name': 'AwacsCreateEmptyAwacsNamespace',
                'needed_parameters': ['namespace_id'],
                'optional_parameters': [],
                'output_parameters': [],
            },
            {
                'name': 'AwacsCreateL3',
                'needed_parameters': [
                    'fqdn',
                    'service_id',
                    'l7_balancers_ids',
                ],
                'optional_parameters': ['entry_point_id'],
                'output_parameters': [],
            },
            {
                'name': 'AwacsDomainChange',
                'needed_parameters': ['awacs_namespace_id', 'awacs_domain_id'],
                'optional_parameters': [
                    'new_upstreams',
                    'new_protocol',
                    'order_new_certificate',
                    'set_cert_id',
                    'new_fqdns',
                    'st_ticket',
                ],
                'output_parameters': [],
            },
            {
                'name': 'AwacsDomainChangeProtocol',
                'needed_parameters': [
                    'entry_point_id',
                    'namespace_id',
                    'domain_id',
                    'new_protocol',
                ],
                'optional_parameters': [],
                'output_parameters': ['new_cert_id'],
            },
            {
                'name': 'AwacsDomainCreate',
                'needed_parameters': ['entry_point_id'],
                'optional_parameters': ['domain_id', 'origin_fqdn'],
                'output_parameters': ['domain_id'],
            },
            {
                'name': 'AwacsDomainWaitFor',
                'needed_parameters': ['domain_id'],
                'optional_parameters': [
                    'wait_for',
                    'entry_point_id',
                    'namespace_id',
                    'st_ticket',
                ],
                'output_parameters': [],
            },
            {
                'name': 'AwacsDomainsDelete',
                'needed_parameters': ['namespace_id', 'domain_ids'],
                'optional_parameters': [],
                'output_parameters': ['domain_ids'],
            },
            {
                'name': 'AwacsDomainsGetAll',
                'needed_parameters': ['namespace_id'],
                'optional_parameters': [],
                'output_parameters': ['domain_ids'],
            },
            {
                'name': 'AwacsDomainsWaitFor',
                'needed_parameters': ['namespace_id', 'domain_ids'],
                'optional_parameters': ['for_deleted'],
                'output_parameters': [],
            },
            {
                'name': 'AwacsGetBackends',
                'needed_parameters': ['fqdn'],
                'optional_parameters': [],
                'output_parameters': [
                    'l7_nanny_services',
                    'l3_backends',
                    'system_backends',
                ],
            },
            {
                'name': 'AwacsGetL7NannyServices',
                'needed_parameters': ['fqdn'],
                'optional_parameters': [],
                'output_parameters': [
                    'nanny_sas',
                    'nanny_vla',
                    'nanny_man',
                    'nanny_services',
                    'l7_balancers_ids',
                ],
            },
            {
                'name': 'AwacsL3AddBackend',
                'needed_parameters': [
                    'namespace_id',
                    'balancer_id',
                    'backend_id',
                ],
                'optional_parameters': [],
                'output_parameters': [],
            },
            {
                'name': 'AwacsL3GetBalancer',
                'needed_parameters': ['namespace_id'],
                'optional_parameters': [],
                'output_parameters': ['l3_balancer_id', 'l3mgr_service_id'],
            },
            {
                'name': 'AwacsNamespaceCanBeDeleted',
                'needed_parameters': ['awacs_namespace_id'],
                'optional_parameters': ['check_backends'],
                'output_parameters': ['namespace_can_be_deleted'],
            },
            {
                'name': 'AwacsNamespaceChangeOwners',
                'needed_parameters': ['namespace_id'],
                'optional_parameters': ['logins', 'groups'],
                'output_parameters': [],
            },
            {
                'name': 'AwacsNamespaceDelete',
                'needed_parameters': ['namespace_id'],
                'optional_parameters': [
                    'delete_empty',
                    'checked_and_ready_to_delete',
                ],
                'output_parameters': ['namespace_id'],
            },
            {
                'name': 'AwacsNamespaceUpdate',
                'needed_parameters': ['namespace_id'],
                'optional_parameters': ['service_abc'],
                'output_parameters': [],
            },
            {
                'name': 'AwacsRemoveL3Link',
                'needed_parameters': ['fqdn'],
                'optional_parameters': [],
                'output_parameters': [],
            },
            {
                'name': 'AwacsRemoveNamespace',
                'needed_parameters': ['fqdn'],
                'optional_parameters': [],
                'output_parameters': [],
            },
            {
                'name': 'AwacsSaveNamespace',
                'needed_parameters': ['service_id', 'env', 'fqdn'],
                'optional_parameters': [
                    'awacs_namespace_id',
                    'is_external',
                    'is_shared',
                    'branch_name',
                ],
                'output_parameters': [
                    'namespace_id',
                    'entry_point_id',
                    'skip_domain_usage',
                    'awacs_namespace_id',
                ],
            },
            {
                'name': 'AwacsSetDefaultYaml',
                'needed_parameters': ['fqdn'],
                'optional_parameters': ['origin_fqdn'],
                'output_parameters': ['default_upstream_name'],
            },
            {
                'name': 'AwacsSetSlbpingYaml',
                'needed_parameters': ['fqdn'],
                'optional_parameters': [],
                'output_parameters': [],
            },
            {
                'name': 'AwacsUpdateEntrypointSet',
                'needed_parameters': [
                    'regions',
                    'awacs_namespace_id',
                    'awacs_backend_id',
                ],
                'optional_parameters': [],
                'output_parameters': [],
            },
            {
                'name': 'AwacsUpstreamChangeUpstreams',
                'needed_parameters': [
                    'entry_point_id',
                    'new_upstream_ids',
                    'origin_yaml',
                ],
                'optional_parameters': [],
                'output_parameters': ['updated_yaml'],
            },
            {
                'name': 'AwacsUpstreamCreate',
                'needed_parameters': [
                    'namespace_id',
                    'upstream_id',
                    'fqdn',
                    'entry_point_id',
                ],
                'optional_parameters': ['backend_id', 'backend_ids'],
                'output_parameters': [],
            },
            {
                'name': 'AwacsUpstreamCreateDcLocalYaml',
                'needed_parameters': ['entry_point_id', 'backend_ids_by_env'],
                'optional_parameters': [],
                'output_parameters': ['dc_local_yaml'],
            },
            {
                'name': 'AwacsUpstreamCreateFromYaml',
                'needed_parameters': [
                    'entry_point_id',
                    'namespace_id',
                    'yaml',
                    'upstream_id',
                ],
                'optional_parameters': [],
                'output_parameters': [],
            },
            {
                'name': 'AwacsUpstreamGetYaml',
                'needed_parameters': ['entry_point_id'],
                'optional_parameters': [],
                'output_parameters': ['yaml', 'awacs_upstream_version'],
            },
            {
                'name': 'AwacsUpstreamUpdateYaml',
                'needed_parameters': [
                    'entry_point_id',
                    'awacs_upstream_version',
                    'origin_yaml',
                    'updated_yaml',
                ],
                'optional_parameters': [],
                'output_parameters': [],
            },
            {
                'name': 'AwacsUpstreamWaitFor',
                'needed_parameters': ['namespace_id', 'upstream_id'],
                'optional_parameters': ['wait_for'],
                'output_parameters': [],
            },
            {
                'name': 'AwacsUpstreamsDelete',
                'needed_parameters': ['namespace_id', 'upstream_ids'],
                'optional_parameters': [],
                'output_parameters': ['upstream_ids'],
            },
            {
                'name': 'AwacsUpstreamsWaitFor',
                'needed_parameters': ['awacs_namespace_id'],
                'optional_parameters': [
                    'wait_for',
                    'for_deleted',
                    'deleted_awacs_upstream_ids',
                ],
                'output_parameters': [],
            },
            {
                'name': 'AwacsWaitForL3',
                'needed_parameters': ['fqdn'],
                'optional_parameters': [],
                'output_parameters': ['l3mgrServiceId'],
            },
            {
                'name': 'AwacsWaitForNamespace',
                'needed_parameters': ['fqdn'],
                'optional_parameters': ['new_service_ticket'],
                'output_parameters': [],
            },
            {
                'name': 'AwacsWaitSyncBackends',
                'needed_parameters': ['namespace_ids'],
                'optional_parameters': [
                    'pod_ids_by_region',
                    'vla_pod_ids',
                    'sas_pod_ids',
                    'man_pod_ids',
                ],
                'output_parameters': ['success_after_sleep'],
            },
            {
                'name': 'DNSCreateARecord',
                'needed_parameters': ['fqdn'],
                'optional_parameters': [
                    'additional_fqdns',
                    'st_ticket',
                    'ipv4',
                    'additional_ips',
                ],
                'output_parameters': [],
            },
            {
                'name': 'DNSCreateAlias',
                'needed_parameters': ['alias', 'canonical_name'],
                'optional_parameters': [],
                'output_parameters': [],
            },
            {
                'name': 'DNSCreateCNAMERecord',
                'needed_parameters': [],
                'optional_parameters': [
                    'left_side',
                    'right_side',
                    'left_sides',
                    'right_sides',
                    'st_ticket',
                ],
                'output_parameters': [],
            },
            {
                'name': 'DNSCreateRecord',
                'needed_parameters': ['fqdn'],
                'optional_parameters': [
                    'additional_fqdns',
                    'st_ticket',
                    'ipv6',
                    'additional_ips',
                ],
                'output_parameters': [],
            },
            {
                'name': 'DNSDeleteAlias',
                'needed_parameters': ['alias', 'canonical_name'],
                'optional_parameters': [],
                'output_parameters': [],
            },
            {
                'name': 'DNSDeleteRecord',
                'needed_parameters': ['fqdn', 'ipv6'],
                'optional_parameters': ['st_ticket'],
                'output_parameters': [],
            },
            {
                'name': 'DNSResolveAlias',
                'needed_parameters': ['alias'],
                'optional_parameters': [],
                'output_parameters': ['host'],
            },
            {
                'name': 'Dummy',
                'needed_parameters': ['name'],
                'optional_parameters': [],
                'output_parameters': ['message'],
            },
            {
                'name': 'InternalCollectForEPCreate',
                'needed_parameters': ['branch_id'],
                'optional_parameters': [],
                'output_parameters': ['nanny_endpoint_set_id'],
            },
            {
                'name': 'InternalCreateEPULink',
                'needed_parameters': ['entry_point_id', 'upstream_id'],
                'optional_parameters': [],
                'output_parameters': [],
            },
            {
                'name': 'InternalCreateEntryPoint',
                'needed_parameters': ['fqdn', 'env', 'namespace_id'],
                'optional_parameters': [
                    'domain_id',
                    'protocol',
                    'is_external',
                    'awacs_upstream_id',
                ],
                'output_parameters': ['entry_point_id', 'awacs_namespace_id'],
            },
            {
                'name': 'InternalCubeInitBalancerAlias',
                'needed_parameters': ['service_id', 'env'],
                'optional_parameters': ['branch_name'],
                'output_parameters': ['host'],
            },
            {
                'name': 'InternalDeleteEntryPoints',
                'needed_parameters': ['entry_point_ids'],
                'optional_parameters': [],
                'output_parameters': [],
            },
            {
                'name': 'InternalDeleteNamespace',
                'needed_parameters': ['namespace_id'],
                'optional_parameters': [],
                'output_parameters': [],
            },
            {
                'name': 'InternalDeleteUpstreams',
                'needed_parameters': ['upstream_ids'],
                'optional_parameters': [],
                'output_parameters': [],
            },
            {
                'name': 'InternalFindModelsToRemove',
                'needed_parameters': [],
                'optional_parameters': ['namespace_id', 'entry_point_id'],
                'output_parameters': [
                    'entry_point_ids',
                    'upstream_ids',
                    'awacs_namespace_id',
                ],
            },
            {
                'name': 'InternalFoldActiveDatacenters',
                'needed_parameters': ['active_datacenters'],
                'optional_parameters': ['clown_branch_id'],
                'output_parameters': ['active_datacenters'],
            },
            {
                'name': 'InternalGetAwacsInfoBranch',
                'needed_parameters': ['clown_service_id', 'clown_branch_id'],
                'optional_parameters': [],
                'output_parameters': [
                    'awacs_backend_id',
                    'awacs_namespace_id',
                ],
            },
            {
                'name': 'InternalGetEntrypointInfo',
                'needed_parameters': ['entry_point_id'],
                'optional_parameters': [],
                'output_parameters': [
                    'awacs_namespace_id',
                    'dns_name',
                    'awacs_domain_ids',
                    'awacs_upstream_ids',
                    'awacs_backend_ids',
                    'entry_point_ids',
                    'upstream_ids',
                ],
            },
            {
                'name': 'InternalGetIoInfo',
                'needed_parameters': ['env'],
                'optional_parameters': [],
                'output_parameters': ['io_info'],
            },
            {
                'name': 'InternalGetNamespaces',
                'needed_parameters': ['service_id'],
                'optional_parameters': ['branch_ids'],
                'output_parameters': ['namespace_ids'],
            },
            {
                'name': 'InternalSleepFor',
                'needed_parameters': ['sleep', 'max_retries'],
                'optional_parameters': [],
                'output_parameters': [],
            },
            {
                'name': 'InternalUpdateEntryPoint',
                'needed_parameters': ['entry_point_id'],
                'optional_parameters': ['is_external'],
                'output_parameters': [],
            },
            {
                'name': 'InternalUpdateNamespace',
                'needed_parameters': ['namespace_id'],
                'optional_parameters': ['is_external'],
                'output_parameters': [],
            },
            {
                'name': 'L3MGRAdd443Port',
                'needed_parameters': ['l3mgr_service_id'],
                'optional_parameters': ['v4'],
                'output_parameters': [
                    'l3mgr_config_id',
                    'l3_update_succeeded',
                ],
            },
            {
                'name': 'L3MGRAddExternalIpv4',
                'needed_parameters': [
                    'abc_service_slug',
                    'l3mgr_service_id',
                    'fqdn',
                ],
                'optional_parameters': [
                    'l3_update_succeeded',
                    'created_new_vs_ids',
                ],
                'output_parameters': ['new_vs_ids', 'l3_update_succeeded'],
            },
            {
                'name': 'L3MGRAddExternalIpv6',
                'needed_parameters': [
                    'abc_service_slug',
                    'l3mgr_service_id',
                    'fqdn',
                ],
                'optional_parameters': [
                    'l3_update_succeeded',
                    'created_new_vs_ids',
                ],
                'output_parameters': ['new_vs_ids', 'l3_update_succeeded'],
            },
            {
                'name': 'L3MGRCreateConfigForVsIds',
                'needed_parameters': ['l3mgr_service_id', 'created_vs_ids'],
                'optional_parameters': ['l3_update_succeeded'],
                'output_parameters': [
                    'l3mgr_config_id',
                    'l3_update_succeeded',
                ],
            },
            {
                'name': 'L3MGRDeployConfiguration',
                'needed_parameters': ['l3mgr_service_id', 'l3mgr_config_id'],
                'optional_parameters': ['l3_update_succeeded'],
                'output_parameters': [],
            },
            {
                'name': 'L3MGRDisableBalancer',
                'needed_parameters': ['l3mgrServiceId'],
                'optional_parameters': [],
                'output_parameters': ['l3_empty_config_id'],
            },
            {
                'name': 'L3MGRFetchIps',
                'needed_parameters': ['l3mgr_service_id'],
                'optional_parameters': [],
                'output_parameters': ['ipv4', 'ipv6'],
            },
            {
                'name': 'L3MGRFetchIpv6',
                'needed_parameters': ['l3mgrServiceId'],
                'optional_parameters': [],
                'output_parameters': ['ipv6'],
            },
            {
                'name': 'L3MGRHideService',
                'needed_parameters': ['l3mgrServiceId'],
                'optional_parameters': [],
                'output_parameters': [],
            },
            {
                'name': 'L3MGRWaitConfigActivated',
                'needed_parameters': ['l3mgr_service_id', 'l3mgr_config_id'],
                'optional_parameters': ['l3_update_succeeded'],
                'output_parameters': [],
            },
            {
                'name': 'L3MGRWaitForEmptyServiceActivation',
                'needed_parameters': ['l3mgrServiceId', 'config_id'],
                'optional_parameters': [],
                'output_parameters': [],
            },
            {
                'name': 'L3MGRWaitKnowNewPods',
                'needed_parameters': ['pod_ids', 'l3mgr_service_id'],
                'optional_parameters': ['wait_for'],
                'output_parameters': [],
            },
            {
                'name': 'MetaCubeApplyL7MonitoringSettings',
                'needed_parameters': ['service_id', 'env', 'fqdn'],
                'optional_parameters': [],
                'output_parameters': ['job_id'],
            },
            {
                'name': 'MetaCubeDomainCreate',
                'needed_parameters': ['entry_point_id'],
                'optional_parameters': ['skip_domain_usage', 'origin_fqdn'],
                'output_parameters': ['job_id'],
            },
            {
                'name': 'MetaCubeRemoveNannyService',
                'needed_parameters': ['nanny_sas', 'nanny_vla', 'nanny_man'],
                'optional_parameters': ['service_id'],
                'output_parameters': ['job_ids'],
            },
            {
                'name': 'MetaCubeWaitForJobCommon',
                'needed_parameters': ['job_id'],
                'optional_parameters': ['st_ticket'],
                'output_parameters': [],
            },
            {
                'name': 'MetaCubeWaitForJobsCommon',
                'needed_parameters': ['job_ids'],
                'optional_parameters': [],
                'output_parameters': [],
            },
            {
                'name': 'MetaRunRemoveJob',
                'needed_parameters': [
                    'entry_point_id',
                    'awacs_namespace_id',
                    'namespace_can_be_deleted',
                ],
                'optional_parameters': [],
                'output_parameters': ['job_id', 'started_job_name'],
            },
            {
                'name': 'MetaStartAllocatingExternalL3Addresses',
                'needed_parameters': [
                    'abc_service_slug',
                    'l3mgr_service_id',
                    'fqdn',
                    'author',
                ],
                'optional_parameters': ['st_ticket'],
                'output_parameters': ['job_id'],
            },
            {
                'name': 'MetaStartBalancerEnsureDoublePods',
                'needed_parameters': [
                    'namespace_id',
                    'sas_pods',
                    'vla_pods',
                    'man_pods',
                    'nanny_services',
                ],
                'optional_parameters': ['st_ticket'],
                'output_parameters': ['job_ids'],
            },
            {
                'name': 'MetaStartBalancerEnsureHttpsEnabled',
                'needed_parameters': ['awacs_namespace_id'],
                'optional_parameters': [],
                'output_parameters': ['job_id'],
            },
            {
                'name': 'MetaStartBalancerReallocateAllPods',
                'needed_parameters': ['awacs_namespace_id'],
                'optional_parameters': ['st_ticket'],
                'output_parameters': ['job_id'],
            },
            {
                'name': 'MetaStartChangeL7PodsOneNannyService',
                'needed_parameters': ['nanny_name', 'env', 'fqdn'],
                'optional_parameters': ['st_ticket'],
                'output_parameters': ['job_id'],
            },
            {
                'name': 'MetaStartChangeQuotaAwacsForBalancers',
                'needed_parameters': [
                    'namespace_ids',
                    'user',
                    'new_quota_abc',
                ],
                'optional_parameters': [],
                'output_parameters': ['job_ids'],
            },
            {
                'name': 'MetaStartChangeQuotaAwacsNanny',
                'needed_parameters': [
                    'nanny_services',
                    'user',
                    'new_quota_abc',
                ],
                'optional_parameters': [],
                'output_parameters': ['job_ids'],
            },
            {
                'name': 'MetaStartEntryPointEnableSsl',
                'needed_parameters': [
                    'entry_point_id',
                    'awacs_namespace_id',
                    'awacs_domain_id',
                    'protocol',
                    'author',
                ],
                'optional_parameters': ['st_ticket'],
                'output_parameters': ['job_id'],
            },
            {
                'name': 'NannyReallocatePods',
                'needed_parameters': ['nanny_name'],
                'optional_parameters': [],
                'output_parameters': ['reallocation_id'],
            },
            {
                'name': 'NannyReallocateWaitFor',
                'needed_parameters': ['service_id', 'reallocation_id'],
                'optional_parameters': ['wait_for'],
                'output_parameters': [],
            },
            {
                'name': 'NannySetL7MonitoringSettings',
                'needed_parameters': ['service_id', 'env', 'nanny_service'],
                'optional_parameters': [],
                'output_parameters': [],
            },
            {
                'name': 'StartrekCreateTicket',
                'needed_parameters': [
                    'queue',
                    'title',
                    'description',
                    'components',
                    'followers',
                ],
                'optional_parameters': [],
                'output_parameters': ['new_ticket'],
            },
            {
                'name': 'StartrekCubeLinkServiceTickets',
                'needed_parameters': ['master_ticket', 'ticket_to_link'],
                'optional_parameters': [],
                'output_parameters': [],
            },
            {
                'name': 'StartrekEnsureDutyTicketExists',
                'needed_parameters': ['awacs_namespace_id'],
                'optional_parameters': ['st_ticket', 'author'],
                'output_parameters': ['st_ticket'],
            },
            {
                'name': 'StartrekGenerateCommentAdd443OnL3',
                'needed_parameters': ['l3mgr_service_id', 'st_ticket'],
                'optional_parameters': ['skip'],
                'output_parameters': ['border_comment'],
            },
            {
                'name': 'StartrekGenerateDutyTicketParamsForSsl',
                'needed_parameters': ['author', 'namespace_id', 'cert_id'],
                'optional_parameters': [],
                'output_parameters': [
                    'queue',
                    'title',
                    'description',
                    'components',
                    'followers',
                ],
            },
            {
                'name': 'StartrekGenerateTrafficTicketParamsForExternal',
                'needed_parameters': ['author', 'l3mgr_service_id', 'skip'],
                'optional_parameters': [],
                'output_parameters': [
                    'queue',
                    'title',
                    'description',
                    'components',
                    'followers',
                ],
            },
            {
                'name': 'StartrekWaitBorderComment',
                'needed_parameters': ['st_ticket', 'border_comment'],
                'optional_parameters': ['skip'],
                'output_parameters': [],
            },
            {
                'name': 'StartrekWaitClosed',
                'needed_parameters': ['ticket'],
                'optional_parameters': ['wait_for'],
                'output_parameters': [],
            },
        ],
    }