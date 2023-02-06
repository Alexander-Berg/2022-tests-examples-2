# -*- coding: utf-8 -*-
import string

from nose.tools import (
    eq_,
    raises,
)
from passport.backend.core.compare.equality.comparator import TransliteratedAndDistanceComparator
from passport.backend.core.compare.equality.xlit_compare import xlit_compare
from passport.backend.core.compare.equality.xlit_helper import build_replacements
import pytest
import six


@raises(ValueError)
def test_invalid_pairs_not_accepted():
    invalid_reps = {'ru': (('a', 'b'), ('b', 'b'))}
    build_replacements(invalid_reps)


DIFFERENT_XLIT_DATA = [
    (u'василий', u'алексей', u'василий', u'алексей'),
    (u'александр', u'алексей', u'андр', u'ей'),

    (u'alexander', u'алексей', u'nder', u''),  # ей == a
    (u'александр', u'alexey', u'андр', u'ey'),
    (u'евгений', u'evgenia', u'', u'a'),  # рекурсивные вызовы, кратчайший вариант окончания

    (u'вегений', u'evgeniy', u'вегений', u'evgeniy'),  # неприятные опечатки

    # случаи, вызванные ограниченностью алгоритма
    (u'eugeniy', u'eugeni', u'y', u''),  # iy == i
    (u'ira', u'iray', u'', u'y'),  # a == ay

    # Этот случай проверяет работу с unidecode() без ошибок
    (u'ivan\uffff', u'ivan', u'\uffff', u''),
]


EQUAL_XLIT_PAIRS = [
    (six.text_type(string.printable), six.text_type(string.printable)),
    (u'иван', u'ivan'),
    (u'петров', u'petrov'),
    (u'вася', u'vasia'),
    (u'pupkin', u'пупкин'),
    (u'козлов', u'kozlov'),
    (u'николай', u'nikolay'),
    (u'алексaндр', u'александр'),
    (u'кузнeцoв', u'kузнецов'),
    (u'цель', u'tsel'),
    (u'целина', u'tselina'),
    (u'дуюнов', u'dyunov'),

    (u'ц' * 25, u'tc' * 25),

    # Данные, для которых у нас нет своих транслитераций (только unidecode)
    (u'ひらがな', u'hiragana'),
    (u'北京市', u'bei jing shi '),
    (u'平仮名', u'ping jia ming '),

    # Данные от Епифановской Александры https://wiki.yandex-team.ru/aleksandraepifanovskaja/Brak#primerytranslita
    # Если другие данные стоят в комментарии - значит их здесь не матчим, думаем что делать!
    # Данные преобразованы в единый (нижний) регистр, xlit_compare работает только с нижним регистром!
    (u'лосик', u'losik'),
    (u'арбачакова', u'arbachakova'),
    (u'чужмарова', u'chuzhmarova'),
    (u'вольф', u'volf'),
    (u'барановская', u'baranovskaya'),
    (u'dzeboev', u'дзебоев'),
    (u'nechaev', u'нечаев'),
    (u'шилкин', u'shilkin'),
    (u'кирпиченко', u'kirpichenko'),
    (u'балакина', u'balakina'),
    (u'masckowa', u'маскова'),
    (u'кальченко', u'kaltchenko'),
    (u'прейгер', u'prager'),
    (u'arutyunyan', u'арутюнян'),  # (u'harutyunyan', u'арутюнян'), странная замена а-ha
    (u'козина', u'kozina'),
    (u'семенкова', u'semenkova'),
    (u'пинкасевич', u'pinkasevich'),
    (u'иванов', u'ivanov'),
    (u'потоцкий', u'pototskiy'),
    (u'манжурова', u'manzhurova'),
    (u'джанаева', u'dzhanayeva'),
    (u'mnogolet', u'многолет'),
    (u'евстратов', u'yewstratov'),
    (u'морозова', u'morozova'),
    (u'курсон', u'kurson'),
    (u'бондаренко', u'bondarenko'),
    (u'шпит', u'shpit'),
    (u'арсланова', u'arslanova'),
    (u'коломиец', u'kolomiets'),
    (u'каражов', u'karazhov'),
    (u'denisova', u'денисова'),
    (u'васильев', u'vasilyev'),
    (u'федина', u'fedina'),
    (u'чехов', u'chehov'),
    (u'доббельт', u'dobbelt'),
    (u'фирсов', u'firsov'),
    (u'бушуева', u'byshyeva'),
    (u'mironov', u'миронов'),
    (u'yarmoshevich', u'ярмошевич'),
    (u'беляченкова', u'beliatchenkova'),
    (u'klimova', u'климова'),
    (u'кулявцев', u'kuliavzev'),
    (u'витюгов', u'vityugov'),
    (u'сергиенко', u'sergienko'),
    (u'патронов', u'patronov'),
    (u'орлова', u'orlova'),
    (u'хасимов', u'hasimov'),
    (u'алексин', u'aleksin'),
    (u'goshin', u'гошин'),
    (u'иванова', u'ivanova'),
    (u'кадиева', u'kadieva'),
    (u'chibisov', u'чибисов'),
    (u'shikhaleva', u'шихалева'),
    (u'фаттахова', u'fattaxova'),
    (u'raevskaja', u'раевская'),
    (u'козина', u'kozina'),
    (u'shmakin', u'шмакин'),
    (u'кудряшов', u'kudrayshov'),
    (u'alimova', u'алимова'),
    (u'vivtash', u'вивташ'),
    (u'лобаченко', u'lobachenko'),
    (u'гиш', u'gish'),
    (u'стародуб', u'starodyb'),
    (u'chekurin', u'чекурин'),
    (u'ramanov', u'раманов'),
    (u'shikin', u'шикин'),
    (u'харченко', u'kharchenko'),
    (u'yun', u'юн'),
    (u'manasyan', u'манасян'),
    (u'маркелова', u'markelowa'),
    (u'kapinos', u'капинос'),
    (u'ruzaeva', u'рузаева'),
    (u'дерябин', u'deryabin'),
    (u'галентус', u'galentus'),
    (u'вдовина', u'vdovina'),
    (u'ренгевич', u'rengevich'),
    (u'пискунов', u'piskunov'),
    (u'ханнанова', u'khannanova'),
    (u'жуйков', u'zhujkov'),
    (u'войцеховский', u'voycexovskiy'),
    (u'лебедева', u'lebedeva'),
    (u'бычихин', u'bychihin'),
    (u'соломатов', u'solomatov'),
    (u'ivanov', u'иванов'),
    (u'zubakin', u'зубакин'),
    (u'василец', u'vasilets'),

    # Более хитрые данные - смесь кириллицы и ASCII, эквивалентные ASCII:
    (u'cмирнова', u'smirnova'),
    (u'vлadimir', u'wladymir'),
    (u'кosлов', u'kozlov'),
    (u'alexey', u'alexei'),
    (u'eugeny', u'eugeniy'),
    (u'eugeniy', u'eugeny'),
]


@pytest.mark.parametrize(('a', 'b'), EQUAL_XLIT_PAIRS)
def test_equal_xlit_pairs(a, b):
    eq_(xlit_compare(a, b), (True, '', ''), u'%s != %s' % (a, b))


@pytest.mark.parametrize(('a', 'b'), EQUAL_XLIT_PAIRS)
def test_equal_xlit_pairs_ru(a, b):
    eq_(TransliteratedAndDistanceComparator('ru').compare(a, b)[0], True, u'%s != %s' % (a, b))


@pytest.mark.parametrize(('a', 'b'), EQUAL_XLIT_PAIRS)
def test_equal_xlit_pairs_tr(a, b):
    eq_(TransliteratedAndDistanceComparator('tr').compare(a, b)[0], True, u'%s != %s' % (a, b))


@pytest.mark.parametrize(('a', 'b', 'a_suffix', 'b_suffix'), DIFFERENT_XLIT_DATA)
def test_different_xlit_pairs(a, b, a_suffix, b_suffix):
    res = xlit_compare(a, b)
    eq_(res[0], False, u'%s == %s' % (a, b))


@pytest.mark.parametrize(('a', 'b', 'a_suffix', 'b_suffix'), DIFFERENT_XLIT_DATA)
def test_different_xlit_pairs_suffix(a, b, a_suffix, b_suffix):
    res = xlit_compare(a, b)
    eq_(res[1:3], (a_suffix, b_suffix), u'Differing suffixes not matching: "%s" "%s" != "%s" "%s"' % (res[1], res[2], a_suffix, b_suffix))
