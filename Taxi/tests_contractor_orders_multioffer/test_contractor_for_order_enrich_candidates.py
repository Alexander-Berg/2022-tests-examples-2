import copy

import pytest

from tests_contractor_orders_multioffer import contractor_for_order as cfo
from tests_contractor_orders_multioffer import mock_candidates as mc
from tests_contractor_orders_multioffer import pg_helpers as pgh


@pytest.mark.driver_tags_match(
    dbid='7f74df331eb04ad78bc2ff25ff88a8f2',
    uuid='4bb5a0018d9641c681c1a854b21ec9ab',
    tags=['uberdriver', 'some_other_tag'],
)
@pytest.mark.driver_tags_match(
    dbid='a3608f8f7ee84e0b9c21862beef7e48d',
    uuid='e26e1734d70b46edabe993f515eda54e',
    tags=['uberdriver', 'some_other_tag'],
)
@pytest.mark.parametrize('enrich_candidate', [True, False])
async def test_enrich(
        taxi_contractor_orders_multioffer,
        pgsql,
        taxi_config,
        experiments3,
        lookup,
        enrich_candidate,
):
    taxi_config.set_values(cfo.create_version_settings('1.00'))
    taxi_config.set_values(
        {
            'CONTRACTOR_ORDERS_MULTIOFFER_ENRICH_CANDIDATE_FROM_LOOKUP': (
                enrich_candidate
            ),
        },
    )
    experiments3.add_config(
        **cfo.experiment3(tag='uberdriver', enable_doaa=True),
    )

    lookup.enriched = copy.deepcopy(mc.CANDIDATES)
    if enrich_candidate:
        for candidate in lookup.enriched:
            candidate['some_field'] = 'some_value'
    response = await taxi_contractor_orders_multioffer.post(
        '/v1/contractor-for-order', json=cfo.DEFAULT_PARAMS,
    )
    assert response.status_code == 200

    driver = pgh.select_driver(
        pgsql,
        '7f74df331eb04ad78bc2ff25ff88a8f2',
        '4bb5a0018d9641c681c1a854b21ec9ab',
    )
    assert driver['candidate_json'] == mc.CANDIDATES[0]
    if enrich_candidate:
        assert driver['enriched_json'] == lookup.enriched[0]
