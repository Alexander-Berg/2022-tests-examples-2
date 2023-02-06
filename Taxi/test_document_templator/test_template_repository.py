from document_templator import repositories
from document_templator.generated.api import web_context


async def test_cache_get_template():
    context = web_context.Context()
    await context.on_startup()
    template_repository = repositories.TemplateRepository(context, None)
    template_id = '000000000000000000000001'
    template = await template_repository.get_template(template_id)
    second_template = await template_repository.get_template(template_id)

    assert template is second_template
