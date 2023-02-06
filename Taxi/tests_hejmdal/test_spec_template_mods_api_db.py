async def test_mods_from_db(taxi_hejmdal):
    await taxi_hejmdal.run_task('services_component/invalidate')
    await taxi_hejmdal.invalidate_caches(
        clean_update=True, cache_names=['spec-template-mod-cache'],
    )
    await taxi_hejmdal.run_task('tuner/initialize')

    response = await taxi_hejmdal.post('/v1/mod/list')
    assert response.status_code == 200
    assert response.json() == {
        'mods': [
            {
                'mod_id': 101,
                'login': 'some-login',
                'updated': '1970-01-15T06:58:08.001+00:00',
                'ticket': 'SOMETICKET',
                'spec_template_id': 'spec_template_id1',
                'apply_when': 'always',
                'domain': 'domain1',
                'mod_type': 'spec_disable',
                'usage_count': 0,
                'expired': False,
            },
            {
                'mod_id': 102,
                'login': 'some-login',
                'updated': '1970-01-15T07:58:08.001+00:00',
                'ticket': 'SOMETICKET',
                'spec_template_id': 'spec_template_id2',
                'apply_when': 'always',
                'env_type': 'stable',
                'mod_type': 'schema_override',
                'usage_count': 0,
                'expired': False,
            },
            {
                'mod_id': 103,
                'login': 'some-login',
                'updated': '1970-01-15T08:58:08.001+00:00',
                'ticket': 'SOMETICKET',
                'spec_template_id': 'spec_template_id3',
                'apply_when': 'always',
                'service_id': 1,
                'service_name': 'test_service (nanny, test_project)',
                'mod_type': 'spec_disable',
                'usage_count': 0,
                'expired': False,
            },
            {
                'mod_id': 104,
                'login': 'some-login',
                'updated': '1970-01-15T09:58:08.001+00:00',
                'ticket': 'SOMETICKET',
                'spec_template_id': 'spec_template_id4',
                'apply_when': 'always',
                'service_id': 1,
                'service_name': 'test_service (nanny, test_project)',
                'domain': 'domain1',
                'mod_type': 'spec_disable',
                'usage_count': 0,
                'expired': False,
            },
            {
                'mod_id': 105,
                'login': 'some-login',
                'updated': '1970-01-15T10:58:08.001+00:00',
                'ticket': 'SOMETICKET',
                'spec_template_id': 'spec_template_id5',
                'apply_when': 'always',
                'service_id': 1,
                'service_name': 'test_service (nanny, test_project)',
                'env_type': 'stable',
                'mod_type': 'spec_disable',
                'usage_count': 0,
                'expired': False,
            },
            {
                'mod_id': 106,
                'login': 'some-login',
                'updated': '1970-01-15T11:58:08.001+00:00',
                'ticket': 'SOMETICKET',
                'spec_template_id': 'spec_template_id6',
                'apply_when': 'always',
                'service_id': 1,
                'service_name': 'test_service (nanny, test_project)',
                'host': 'host1',
                'mod_type': 'spec_disable',
                'usage_count': 0,
                'expired': False,
            },
        ],
    }

    response = await taxi_hejmdal.post(
        '/v1/mod/retrieve', params={'mod_id': 106},
    )
    assert response.status_code == 200
    assert response.json() == {
        'mod_id': 106,
        'login': 'some-login',
        'updated': '1970-01-15T11:58:08.001+00:00',
        'ticket': 'SOMETICKET',
        'spec_template_id': 'spec_template_id6',
        'apply_when': 'always',
        'service_id': 1,
        'service_name': 'test_service (nanny, test_project)',
        'host': 'host1',
        'mod_type': 'spec_disable',
        'mod_data': {'disable': True},
        'usage_count': 0,
        'expired': False,
    }
