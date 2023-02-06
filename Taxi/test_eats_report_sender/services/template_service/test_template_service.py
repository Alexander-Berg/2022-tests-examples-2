from eats_report_sender.services.template_service import template_service

CERTAIN_TEMPLATE_NAME = 'certain_template_name'
ConfigTemplateService = template_service.ConfigTemplateService


def test_get_template_name(stq3_context, report_with_certain_template):
    service = ConfigTemplateService(stq3_context, report_with_certain_template)
    assert service.get_template_name() == CERTAIN_TEMPLATE_NAME


async def test_get_template(stq3_context, report_with_default_template):
    service = ConfigTemplateService(stq3_context, report_with_default_template)
    assert 'subject' in service.template
    assert 'body' in service.template


async def test_get_base_template_context(
        stq3_context, report_with_default_template, load_json,
):
    service = ConfigTemplateService(stq3_context, report_with_default_template)
    template_context = service.get_base_template_context()

    assert template_context.brand.id == 'brand_with_default_template'
    assert template_context.brand.name == 'brand_with_default_template'
    assert template_context.report == report_with_default_template
    assert template_context.files == []


async def test_get_config_template_for_brand_with_certain_template(
        stq3_context, report_with_certain_template,
):
    service = ConfigTemplateService(stq3_context, report_with_certain_template)
    assert (
        await service.get_subject()
        == 'Certain subject for brand id brand_with_certain_template'
    )
    assert await service.get_body() == 'Certain body with report uuid__1'


async def test_get_config_template_for_brand_with_default_template(
        stq3_context, report_with_default_template,
):
    service = ConfigTemplateService(stq3_context, report_with_default_template)
    assert await service.get_subject() == 'Отчёт от Yandex Eda'
    assert await service.get_body() == 'Отчётность за период'
