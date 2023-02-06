from document_templator import repositories
from document_templator.generated.api import web_context
from test_document_templator.test_request import common


async def test_cache_load_requests():
    context = web_context.Context()
    await context.on_startup()
    request_repository = repositories.RequestRepository(context)
    request_repository.context.config.DOCUMENT_TEMPLATOR_REQUESTS = (
        common.CONFIG['DOCUMENT_TEMPLATOR_REQUESTS']
    )
    request_id = common.REQUEST_ID_BY_NAME[common.TARIFF]
    requests = await request_repository.load_requests({request_id})
    second_requests = await request_repository.load_requests({request_id})

    assert requests is second_requests
    await context.on_shutdown()
