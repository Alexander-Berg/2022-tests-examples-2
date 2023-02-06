import pytest


@pytest.mark.parametrize(
    'menu_data, menu_data_result',
    [
        ('menu_data.json', 'menu_data_result.json'),
        ('menu_rest_data.json', 'menu_rest_data_result.json'),
    ],
)
async def test_validators(
        library_context, load_json, patch, menu_data, menu_data_result,
):
    menu = library_context.menu_validator.transform(load_json(menu_data))
    assert menu == load_json(menu_data_result)
