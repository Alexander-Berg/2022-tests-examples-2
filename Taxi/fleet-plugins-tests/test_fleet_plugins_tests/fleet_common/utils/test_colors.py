from fleet_plugins_tests.generated.web.fleet_common.utils import (
    colors as colors_util,
)


async def test_colors():
    ru_colors = colors_util.get_colors('ru')
    en_colors = colors_util.get_colors('en')

    assert ru_colors.get_color_name('Красный') == 'Красный'
    assert en_colors.get_color_name('Красный') == 'Red'

    assert en_colors.get_color_name('asd') == 'asd'
