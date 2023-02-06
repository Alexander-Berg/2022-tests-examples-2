import pytest

from tests_contractor_orders_multioffer import contractor_for_order as cfo
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
async def test_saved_callback_request(
        taxi_contractor_orders_multioffer, experiments3, pgsql,
):
    experiments3.add_config(
        **cfo.experiment3(tag='uberdriver', enable_doaa=True),
    )

    response = await taxi_contractor_orders_multioffer.post(
        '/v1/contractor-for-order', json=cfo.DEFAULT_PARAMS,
    )
    assert response.status_code == 200

    multioffer = pgh.select_recent_multioffer(pgsql)
    assert multioffer
    assert multioffer['lookup_request'] == cfo.DEFAULT_PARAMS
