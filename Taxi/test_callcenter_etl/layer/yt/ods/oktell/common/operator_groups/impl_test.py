# coding: utf-8
from callcenter_etl.layer.yt.ods.oktell.common.operator_groups.impl import extract_parent_group_name


def test_fixed_price_order_flg():
    assert extract_parent_group_name('КЦ Везет Уфа') == 'КЦ Везет Уфа'
    assert extract_parent_group_name('КЦ Везет Уфа_Я') == 'КЦ Везет Уфа'
    assert extract_parent_group_name('КЦ Везет Уфа_дом') == 'КЦ Везет Уфа'
    assert extract_parent_group_name('КЦ Везет Уфа_СП') == 'КЦ Везет Уфа'
    assert extract_parent_group_name('КЦ Везет Уфа_Я_дом') == 'КЦ Везет Уфа'
    assert extract_parent_group_name('КЦ Везет Уфа_zzzzz') == 'КЦ Везет Уфа'

    assert extract_parent_group_name('КЦ Волгоград') == 'КЦ Яндекс Волгоград'
    assert extract_parent_group_name('КЦ Волгоград_Я_дом') == 'КЦ Яндекс Волгоград'
    assert extract_parent_group_name('КЦ Волгоград_zzzzz') == 'КЦ Яндекс Волгоград'
    assert extract_parent_group_name('КЦ Волгоград_дом') == 'КЦ Яндекс Волгоград'

    assert extract_parent_group_name('КЦ Краснодар') == 'КЦ Яндекс Краснодар'
    assert extract_parent_group_name('КЦ Краснодар_Я_дом') == 'КЦ Яндекс Краснодар'
    assert extract_parent_group_name('КЦ Краснодар_zzzzz') == 'КЦ Яндекс Краснодар'
    assert extract_parent_group_name('КЦ Краснодар_дом') == 'КЦ Яндекс Краснодар'
    assert extract_parent_group_name('НАЙМ') == 'КЦ Яндекс Краснодар'
    assert extract_parent_group_name('zzzz') == 'КЦ Яндекс Краснодар'
    assert extract_parent_group_name('rekrutment') == 'КЦ Яндекс Краснодар'
    assert extract_parent_group_name('line_1') == 'КЦ Яндекс Краснодар'
    assert extract_parent_group_name('1_line') == 'КЦ Яндекс Краснодар'
