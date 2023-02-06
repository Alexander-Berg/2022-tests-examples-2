import pytest

from fleet_common.utils import colors as colors_util

TRANSLATIONS = {'CarHelper_Color_Красный': {'ru': 'Красный', 'en': 'Red'}}


@pytest.mark.translations(taximeter_backend_driver_messages=TRANSLATIONS)
async def test_colors():
    ru_colors = colors_util.get_colors('ru')
    en_colors = colors_util.get_colors('en')

    assert ru_colors.get_color_name('Красный') == 'Красный'
    assert en_colors.get_color_name('Красный') == 'Red'

    assert en_colors.get_color_name('asd') == 'asd'


async def test_colors_without_translations():
    ru_colors = colors_util.get_colors('ru')
    en_colors = colors_util.get_colors('en')

    assert ru_colors.get_color_name('Красный') == 'Красный'
    assert en_colors.get_color_name('Красный') == 'Красный'

    assert en_colors.get_color_name('asd') == 'asd'
