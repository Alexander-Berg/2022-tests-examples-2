import json

import pytest


@pytest.mark.yt(dyn_table_data=['yt_rs_scoring.yaml'])
@pytest.mark.config(
    PROCESS_AUTOMATION_SALESFORCE_ESB_RS_SCORING_FILTER_FIELDS=[
        'brand_sf_id',
        'geo_sf_id',
    ],
)
async def test_get_rs_scoring(web_app_client, yt_client, yt_apply):
    data = {
        'filter': {
            'brand_sf_id': '0013X00002nOjSRQA0',
            'geo_sf_id': '0MI3X000000kgBrWAI',
        },
    }
    response = await web_app_client.post(
        'v1/yt/rs-scoring?', data=json.dumps(data),
    )

    assert response.status == 200
    content = await response.json()
    assert content == {
        'activation_date': '2017-01',
        'churn': 1.0,
        'number_of_fleet_cars': 0.1,
        'utilization': 0.01,
    }
