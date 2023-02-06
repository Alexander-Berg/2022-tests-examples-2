import datetime
import os

import pytest

from .. import utils_v2


@pytest.mark.xfail(
    os.getenv('IS_TEAMCITY'),
    strict=False,
    reason='some problems in CI with YT',
)
@pytest.mark.yt(dyn_table_data=['yt_raw_denorm.yaml'])
@pytest.mark.pgsql(
    'cargo_claims', files=['pg_raw_denorm.sql', 'alter_sequence.sql'],
)
@pytest.mark.usefixtures('yt_apply')
@pytest.mark.config(
    CARGO_CLAIMS_DENORM_READ_SETTINGS_V2={
        '__default__': {
            'enabled': True,
            'yt-use-runtime': False,
            'yt-timeout-ms': 1000,
            'ttl-days': 10,
        },
    },
)
async def test_corp_search_v2(
        taxi_cargo_claims, get_default_headers, state_controller, pgsql,
):
    state_controller.use_create_version('v2')
    request = utils_v2.get_create_request()
    state_controller.handlers().create.request = request
    claim_info = await state_controller.apply(target_status='new')

    claim_id = claim_info.claim_id
    corp_client_id = claim_info.claim_full_response['corp_client_id']

    # corp_client_id is only used in searching claim_uuids in pg
    # so, that's fine to change corp_client_id for denorm claim only in pg,
    # but in response there would be old copr_client_id
    # modify updated_ts is also fine, it's only used in choosing yt, or not
    past_updated_ts = datetime.datetime.now() - datetime.timedelta(days=15)
    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        f"""
            ALTER TABLE cargo_claims.claims DISABLE TRIGGER ALL;
            UPDATE cargo_claims.claims
            SET
                corp_client_id = '{corp_client_id}',
                updated_ts = '{past_updated_ts}'
            WHERE uuid_id = '9756ae927d7b42dc9bbdcbb832924343';
            ALTER TABLE cargo_claims.claims ENABLE TRIGGER ALL;
        """,
    )
    cursor.close()

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/search',
        json={'offset': 0, 'limit': 10},
        headers=get_default_headers(),
    )

    assert response.status_code == 200

    json = response.json()
    assert len(json['claims']) == 2
    assert [json['claims'][0]['id'], json['claims'][1]['id']] == [
        claim_id,
        '9756ae927d7b42dc9bbdcbb832924343',
    ]
