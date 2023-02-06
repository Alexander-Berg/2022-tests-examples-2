import pytest

from eats_retail_globus_parser.components.workers import availability
from eats_retail_globus_parser.generated.service.swagger.models import (
    api as models,
)


@pytest.mark.config(EATS_RETAIL_GLOBUS_PARSER_AVAILABILITY_LIMIT=1)
@pytest.mark.config(EATS_RETAIL_GLOBUS_PARSER_JOIN_STOCKS_TO_AVAILABILITY=True)
async def test_join_stocks_to_availabilities(
        stq3_context, mds_mocks, parser_mocks, proxy_mocks, load_json,
):
    task_details = models.RequestDetail.deserialize(
        load_json('task_details.json'),
    )
    worker = availability.AvailabilityWorker(stq3_context)
    data = await worker.get_data_from_partner(task_details)
    assert len(data) == 4
    data = await worker.transform_data(task_details, data)
    assert len(data['items']) == 8
    assert data == load_json('response.json')
