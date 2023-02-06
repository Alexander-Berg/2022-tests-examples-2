import pytest

from fleet_enums.enums import translatable
from fleet_enums.utils import order_category


class MyEnum(translatable.TranslatableEnum):
    ENUM1 = 'e1'
    None_ = 'none'


@pytest.mark.translations(
    opteum_enums={
        'MyEnum.ENUM1': {'ru': 'Перечисляемое значение №1'},
        'MyEnum.None': {'ru': 'Перечисляемое значение с неудобным именем'},
    },
)
def test_translatable_enums(library_context):
    assert MyEnum.ENUM1.translate() == 'Перечисляемое значение №1'
    assert MyEnum('e1').translate() == 'Перечисляемое значение №1'
    assert (
        MyEnum.None_.translate() == 'Перечисляемое значение с неудобным именем'
    )
    assert (
        MyEnum('none').translate()
        == 'Перечисляемое значение с неудобным именем'
    )


@pytest.mark.translations(
    opteum_enums={
        'OrderCategory.Vip': {'ru': 'VIP'},
        'OrderCategory.ComfortPlus': {'ru': 'Комфорт+'},
        'OrderCategory.None': {'ru': '-'},
    },
)
@pytest.mark.parametrize(
    'category_name, int_category, expected_translation',
    [
        ('vip', 512, 'VIP'),
        (None, 512, 'Комфорт+'),
        ('comfort_plus', 0, 'Комфорт+'),
        (None, 0, '-'),
    ],
)
async def test_translate_category_with_fallback(
        library_context, category_name, int_category, expected_translation,
):
    tranlate = await order_category.translate_with_fallback(
        library_context, category_name, int_category, locale='ru',
    )
    assert tranlate == expected_translation
