import pandas as pd

from projects.autoorder.ab_infra.categories_processing import (
    clean_brand_name,
    clean_product_name,
    count_items_in_categs,
    get_category_string,
)


def test_clean_brand_name():

    assert (
        clean_brand_name('ООО "БУГРОВСКИЕ МЕЛЬНИЦЫ"') == 'бугровские мельницы'
    )
    assert clean_brand_name('3 КОРОЧКИ') == '3 корочки'
    assert clean_brand_name('J’ECO') == 'j eco'
    assert clean_brand_name('ЯНДЕКС.ШЕФ') == 'яндекс шеф'
    assert clean_brand_name('Хлебозавод №3') == 'хлебозавод 3'
    assert clean_brand_name('ТМ Радость вкуса') == 'радость вкуса'
    assert clean_brand_name('ООО ТД "Каравай Кубани"') == 'каравай кубани'
    assert clean_brand_name('Бренд\n "АБ&В"') == 'бренд аб в'
    assert clean_brand_name('Хоп-Хей') == 'хоп хей'
    assert clean_brand_name('Бренд\n "АБё"') == 'бренд абе'


def test_clean_product_name():

    assert (
        clean_product_name(
            'Печенье «Юбилейное» Традиционное молочное, 112 г',
            clean_brand_name('ЮБИЛЕЙНОЕ'),
        )
        == 'печенье традиционное молочное'
    )
    assert (
        clean_product_name(
            'Творожок 4,2% «Чудо»  Черника', clean_brand_name('Чудо'),
        )
        == 'творожок черника'
    )
    assert (
        clean_product_name(
            'Плюшка Московская «Хлебозавод 3», 200 г',
            clean_brand_name('Хлебозавод №3'),
        )
        == 'плюшка московская'
    )
    assert (
        clean_product_name(
            'Сыр «Лёгкий» 35% «Радость вкуса»',
            clean_brand_name('ТМ Радость вкуса'),
        )
        == 'сыр легкий'
    )
    assert (
        clean_product_name(
            'Печенье сдобное миндальное от «Север-Метрополь»',
            clean_brand_name('Север-Метрополь'),
        )
        == 'печенье сдобное миндальное'
    )
    assert (
        clean_product_name(
            'Молоко отборное «Просто Молоко» 3,4-6% халяль',
            clean_brand_name('Просто молоко'),
        )
        == 'молоко отборное халяль'
    )
    assert (
        clean_product_name(
            'Рогалик «К чаю» «Каравай Кубани»',
            clean_brand_name('ООО ТД "Каравай Кубани"'),
        )
        == 'рогалик чаю'
    )


def test_count_items_in_categs():
    test_input = pd.DataFrame(
        columns=['item_id', 'big_categ', 'categ', 'small_categ', 'other'],
        data=[
            [1, 'a1', 'b1', 'c1', '-'],
            [2, 'a1', 'b2', 'c2', '-'],
            [3, 'a1', 'b2', 'c3', '-'],
            [4, 'a2', 'b2', 'c4', '-'],
            [5, 'a2', 'b2', 'c5', '-'],
            [6, 'a2', 'b2', 'c5', '-'],
            [7, 'a2', 'b2', 'c5', '-'],
        ],
    )

    right_order_of_cols = [
        'big_categ',
        'big_categ_cnt',
        'categ',
        'categ_cnt',
        'small_categ',
        'small_categ_cnt',
        'item_id',
        'other',
    ]

    expected_output = pd.DataFrame(
        columns=[
            'item_id',
            'big_categ',
            'big_categ_cnt',
            'categ',
            'categ_cnt',
            'small_categ',
            'small_categ_cnt',
            'other',
        ],
        data=[
            [1, 'a1', 3, 'b1', 1, 'c1', 1, '-'],
            [2, 'a1', 3, 'b2', 2, 'c2', 1, '-'],
            [3, 'a1', 3, 'b2', 2, 'c3', 1, '-'],
            [4, 'a2', 4, 'b2', 4, 'c4', 1, '-'],
            [5, 'a2', 4, 'b2', 4, 'c5', 3, '-'],
            [6, 'a2', 4, 'b2', 4, 'c5', 3, '-'],
            [7, 'a2', 4, 'b2', 4, 'c5', 3, '-'],
        ],
    )[right_order_of_cols]

    pd.testing.assert_frame_equal(
        count_items_in_categs(
            test_input, ['big_categ', 'categ', 'small_categ'], ['other'],
        ),
        expected_output,
    )


def test_get_category_string():
    inputs = pd.DataFrame(
        columns=[
            'item_id',
            'big_categ',
            'big_categ_cnt',
            'categ',
            'categ_cnt',
            'small_categ',
            'small_categ_cnt',
        ],
        data=[
            [11, 'a1', 3, 'b1', 1, 'c1', 1],
            [22, 'aa', 23, 'b b', 17, 'c', 10],
            [33, 'a1', 18, 'b2', 5, 'c3', 3],
            [44, 'a1', 20, 'b2', 17, 'c3', 15],
        ],
    )
    categs = ['big_categ', 'categ', 'small_categ']

    assert get_category_string(inputs.iloc[0], categs, 5, 10) == 'a1'
    assert get_category_string(inputs.iloc[1], categs, 5, 10) == 'aa_b_b_c'
    assert get_category_string(inputs.iloc[2], categs, 5, 10) == 'a1_b2'
    assert get_category_string(inputs.iloc[3], categs, 5, 10) == '44'
