import pytest

from eats_report_sender.components import report_sender_config


@pytest.mark.parametrize(
    'brand_id, place_id, expected_type',
    [
        ('any', None, 'sftp'),
        ('brand_id', None, 'email'),
        ('not_exist', None, 'sftp'),
        ('not_exist', 'any', 'sftp'),
        ('brand_with_places', 'place_id', 'unique_type'),
        ('brand_with_places', 'not_exist', 'email'),
    ],
)
async def test_should_return_correct_type(
        web_context, brand_id, place_id, expected_type, load_json,
):

    actual_type = web_context.report_sender_config.get_report_type(
        brand_id, place_id,
    )

    assert actual_type == expected_type


@pytest.mark.parametrize(
    'brand_id, expected_name', [('brand_id', 'brand_name')],
)
async def test_should_return_correct_brand_name(
        web_context, brand_id, expected_name,
):
    actual_name = web_context.report_sender_config.get_brand_name(brand_id)

    assert actual_name == expected_name


async def test_should_raise_exception_if_cannot_find_brand_settings_for_brand_name(  # noqa: E501
        web_context,
):
    with pytest.raises(report_sender_config.CannotFindBrandSettingsException):
        web_context.report_sender_config.get_brand_name('any')
