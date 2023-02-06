import pytest


JOB_NAME = 'cargo-claims-carrier-info-enricher'


@pytest.mark.parametrize(
    ('stq_times_called', 'status'),
    [
        pytest.param(
            1,
            'processing',
            id='all_zones_allowed',
            marks=(
                pytest.mark.config(
                    CARGO_CLAIMS_CARRIER_INFO_ENRICHER_SETTINGS={
                        'enabled': True,
                        'chunk_size': 1000,
                        'sleep_ms': 0,
                        'no_enrich_after_lag_seconds': 3600,
                        'billing_service_ids': ['651'],
                        'allow_no_billing_client_id': False,
                        'allow_no_contracts': False,
                        'allow_many_contracts': False,
                        'allow_empty_person_id': False,
                        'allow_no_person': False,
                    },
                )
            ),
        ),
        pytest.param(
            0,
            'skipped',
            id='no_zones_allowed',
            marks=(
                pytest.mark.config(
                    CARGO_CLAIMS_CARRIER_INFO_ENRICHER_SETTINGS={
                        'enabled': True,
                        'chunk_size': 1000,
                        'sleep_ms': 0,
                        'no_enrich_after_lag_seconds': 3600,
                        'billing_service_ids': ['651'],
                        'allow_no_billing_client_id': False,
                        'allow_no_contracts': False,
                        'allow_many_contracts': False,
                        'allow_empty_person_id': False,
                        'allow_no_person': False,
                        'allowed_zones': [],
                    },
                )
            ),
        ),
        pytest.param(
            1,
            'processing',
            id='my_zone_allowed',
            marks=(
                pytest.mark.config(
                    CARGO_CLAIMS_CARRIER_INFO_ENRICHER_SETTINGS={
                        'enabled': True,
                        'chunk_size': 1000,
                        'sleep_ms': 0,
                        'no_enrich_after_lag_seconds': 3600,
                        'billing_service_ids': ['651'],
                        'allow_no_billing_client_id': False,
                        'allow_no_contracts': False,
                        'allow_many_contracts': False,
                        'allow_empty_person_id': False,
                        'allow_no_person': False,
                        'allowed_zones': ['moscow'],
                    },
                )
            ),
        ),
        pytest.param(
            0,
            'skipped',
            id='another_zone_allowed',
            marks=(
                pytest.mark.config(
                    CARGO_CLAIMS_CARRIER_INFO_ENRICHER_SETTINGS={
                        'enabled': True,
                        'chunk_size': 1000,
                        'sleep_ms': 0,
                        'no_enrich_after_lag_seconds': 3600,
                        'billing_service_ids': ['651'],
                        'allow_no_billing_client_id': False,
                        'allow_no_contracts': False,
                        'allow_many_contracts': False,
                        'allow_empty_person_id': False,
                        'allow_no_person': False,
                        'allowed_zones': ['spb'],
                    },
                )
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    ('stq_park_id', 'stq_expect_fail'),
    [('park_id1', False), ('park_id2', True)],
)
@pytest.mark.now('2020-10-01T10:01:10.01')
async def test_basic(
        state_controller,
        run_task_once,
        stq,
        pgsql,
        stq_times_called,
        status,
        stq_runner,
        stq_park_id,
        stq_expect_fail,
        mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_parks_list(request):
        return {
            'parks': [
                {
                    'id': 'park_id',
                    'login': 'login',
                    'is_active': True,
                    'city_id': 'city',
                    'locale': 'locale',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'demo_mode': False,
                    'country_id': 'country_id',
                    'name': 'some park name',
                    'org_name': 'some park org name',
                    'provider_config': {'clid': 'parl_clid1', 'type': 'none'},
                    'geodata': {'lat': 0, 'lon': 1, 'zoom': 0},
                },
            ],
        }

    @mockserver.json_handler(
        'parks-replica/v1/parks/billing_client_id/retrieve',
    )
    def _mock_billing_client_id_retrieve(request):
        assert request.query['consumer'] == 'cargo-claims'
        assert request.query['park_id'] == 'parl_clid1'
        return mockserver.make_response(
            json={'billing_client_id': 'billing_client_id_1'}, status=200,
        )

    @mockserver.json_handler('/billing-replication/v1/active-contracts/')
    def _mock_active_contracts(request):
        assert request.query['client_id'] == 'billing_client_id_1'
        assert request.query['service_id'] == '651'
        assert request.query['actual_ts'] == '2020-10-01T10:01:10.01+0000'
        assert request.query['active_ts'] == '2020-10-01T10:01:10.01+0000'
        return mockserver.make_response(
            json=[{'ID': 111, 'PERSON_ID': 42}], status=200,
        )

    @mockserver.json_handler('/billing-replication/person/')
    def _mock_person(request):
        return [
            {
                'ID': '42',
                'INN': '424242424242',
                'NAME': 'ООО КАРГО',
                'LEGALADDRESS': 'Карго, дом 1',
            },
        ]

    state_controller.use_create_version('v2')
    claim_info = await state_controller.apply(target_status='performer_found')

    # Test job
    await run_task_once(JOB_NAME)

    queue = stq.cargo_claims_enrich_carrier_info
    assert queue.times_called == stq_times_called
    if stq_times_called > 0:
        stq = queue.next_call()
        assert stq['id'] == f'{claim_info.claim_id}/park_id1'
        stq_kwargs = stq['kwargs']
        stq_kwargs.pop('log_extra')
        assert stq_kwargs == {
            'claim_uuid': claim_info.claim_id,
            'park_id': 'park_id1',
        }

    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        'SELECT claim_uuid, park_id, status, name, address, inn '
        'FROM cargo_claims.carrier_info',
    )
    assert list(cursor) == [
        (claim_info.claim_id, 'park_id1', status, None, None, None),
    ]

    # Test STQ - call first time
    await stq_runner.cargo_claims_enrich_carrier_info.call(
        task_id='task',
        kwargs={'claim_uuid': claim_info.claim_id, 'park_id': stq_park_id},
        expect_fail=stq_expect_fail,
    )
    cursor.execute(
        'SELECT claim_uuid, park_id, status, name, address, inn '
        'FROM cargo_claims.carrier_info',
    )
    if stq_times_called == 0:
        assert list(cursor) == [
            (claim_info.claim_id, 'park_id1', 'skipped', None, None, None),
        ]
    else:
        if stq_expect_fail:
            assert list(cursor) == [
                (
                    claim_info.claim_id,
                    'park_id1',
                    'processing',
                    None,
                    None,
                    None,
                ),
            ]
        else:
            # First time call result
            assert list(cursor) == [
                (
                    claim_info.claim_id,
                    'park_id1',
                    'processed',
                    'ООО КАРГО',
                    'Карго, дом 1',
                    '424242424242',
                ),
            ]
            # Test STQ - call again
            await stq_runner.cargo_claims_enrich_carrier_info.call(
                task_id='task',
                kwargs={
                    'claim_uuid': claim_info.claim_id,
                    'park_id': stq_park_id,
                },
                expect_fail=False,
            )
            cursor.execute(
                'SELECT claim_uuid, park_id, status, name, address, inn '
                'FROM cargo_claims.carrier_info',
            )
            assert list(cursor) == [
                (
                    claim_info.claim_id,
                    'park_id1',
                    'processed',
                    'ООО КАРГО',
                    'Карго, дом 1',
                    '424242424242',
                ),
            ]
