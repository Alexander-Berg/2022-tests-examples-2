from aiohttp import web
import pytest


from supportai_api import common
from supportai_api.generated.service.swagger.models import api as api_models


@pytest.mark.pgsql('supportai_api_tokens', files=['tokens.sql'])
async def test_clickhouse_stats(
        web_context, mockserver, clickhouse_query_storage,
):
    @mockserver.json_handler('/supportai/supportai/v1/support')
    # pylint: disable=unused-variable
    async def handler(request):
        return web.json_response(
            data={'reply': {'text': 'hello', 'texts': ['hello']}},
        )

    await common.get_internal_support_response(
        body=api_models.SupportRequest(
            chat_id='123',
            features=[],
            dialog=api_models.Dialog(
                messages=[api_models.Message(text='Hello')],
            ),
        ),
        project_id='sample_project',
        context=web_context,
    )

    await web_context.api_metrics.refresh_cache()

    assert len(clickhouse_query_storage) == 1
