# -*- coding: utf-8 -*-
from contextlib import contextmanager
import difflib
from functools import wraps
import inspect
from os import path
import re
import unittest

import mock
from nose.tools import (
    eq_,
    ok_,
    with_setup,
)
from passport.backend.core.lazy_loader import LazyLoader
from passport.backend.core.test.test_utils.mock_objects import (
    mock_hosts,
    mock_redis_config,
)
from passport.backend.utils.string import (
    smart_bytes,
    smart_text,
)
from passport.backend.utils.warnings import enable_strict_bytes_mode
import six
from six import iteritems
from six.moves.urllib.parse import (
    parse_qs,
    urlparse,
)


if six.PY2:
    OPEN_PATCH_TARGET = '__builtin__.open'
else:
    OPEN_PATCH_TARGET = 'builtins.open'


_DIFF_OPCODE_TO_PREFIX = {
    'equal': ' ',
    'delete': '-',
    'insert': '+',
}


def _get_default_settings_patches():
    # при выполнении тестов следующие настройки всегда должны быть замоканы
    patches = {
        'NOTIFY_TESTER_ONLY': False,
        'PUSH_2FA_CHALLENGE_ENABLED': False,
    }
    try:
        import yatest.common as yc
        patches.update({
            'GEOBASE_LOOKUP_FILE': yc.work_path('test_data/geodata4.bin'),
            'GEOBASE_AS_NAME_FILE': yc.work_path('test_data/as_name'),
            'GEOBASE_IPV4_ORIGIN_FILE': yc.work_path('test_data/ipv4_origin'),
            'GEOBASE_IPV6_ORIGIN_FILE': yc.work_path('test_data/ipv6_origin'),
            'IPREG_LOOKUP_FILE': yc.work_path('test_data/layout-passport-ipreg.json'),
            'UATRAITS_BROWSER_FILE': yc.work_path('test_data/browser.xml'),
            'UATRAITS_PROFILES_FILE': yc.work_path('test_data/profiles.xml'),
            'UATRAITS_EXTRA_FILE': yc.work_path('test_data/extra.xml'),
            'LANGDETECT_DATA_FILE': yc.work_path('test_data/lang_detect_data.txt'),
        })
    except ImportError:
        # Работаем вне аркадии: проект, использующий core, замокает эти настройки сам, если надо
        pass

    return patches


class PassportTestCase(unittest.TestCase):
    MOCKED_SETTINGS = _get_default_settings_patches()
    maxDiff = None

    @staticmethod
    def try_get_real_settings():
        try:
            from passport.backend.api.settings import settings as real_settings
        except ImportError:
            real_settings = None
        return real_settings

    @classmethod
    def setUpClass(cls):
        super(PassportTestCase, cls).setUpClass()
        enable_strict_bytes_mode()

        real_settings = cls.try_get_real_settings()
        cls._settings_patches = [
            mock.patch('passport.backend.core.conf.settings._settings', real_settings),
            mock.patch('passport.backend.core.conf.settings._options', cls.MOCKED_SETTINGS),
        ]
        for patch in cls._settings_patches:
            patch.start()

    @classmethod
    def tearDownClass(cls):
        for patch in reversed(cls._settings_patches):
            patch.stop()
        super(PassportTestCase, cls).tearDownClass()

    def setUp(self):
        LazyLoader.flush()

    def tearDown(self):
        LazyLoader.flush()

    def shortDescription(self):
        module_path = path.relpath(inspect.getsourcefile(type(self)))
        class_path, method_name = self.id().rsplit('.', 1)
        _, class_name = class_path.rsplit('.', 1)
        return '%s:%s.%s' % (module_path, class_name, method_name)


def skip(reason):
    def wrapper(f):
        @wraps(f)
        def _wrapper(*args, **kwargs):
            raise unittest.SkipTest('Test %s is skipped: %s' % (f.__name__, reason.encode('utf-8')))

        return _wrapper

    return wrapper


def single_entrant_patch(cls):
    def wrap_init(old_init):
        def new_init(self, *args, **kwargs):
            old_init(self, *args, **kwargs)
            self._is_started = False
            self._name = cls.__name__
        return new_init

    def wrap_start(old_start):
        def new_start(self, *args, **kwargs):
            if self._is_started:
                raise RuntimeError('Cannot start %s - already running' % self._name)
            retval = old_start(self, *args, **kwargs)
            self._is_started = True
            return retval
        return new_start

    def wrap_stop(old_stop):
        def new_stop(self, *args, **kwargs):
            if not self._is_started:
                raise RuntimeError('Cannot stop %s - not running' % self._name)
            retval = old_stop(self, *args, **kwargs)
            self._is_started = False
            return retval
        return new_stop

    cls.__init__ = wrap_init(cls.__init__)
    cls.start = wrap_start(cls.start)
    cls.stop = wrap_stop(cls.stop)
    return cls


def _get_settings_patches(real_settings=None, inherit_if_set=None, inherit_all_existing=False, **kwargs):
    """
    Создаем патчи для настроек, используемых библиотекой Core.
    По умолчанию настройки инициализируются модулем passport_settings. Если в проекте используется
    другой модуль настроек, его нужно проимпортировать и передать в параметре real_settings в соответствующий
    декоратор (with_settings, with_settings_hosts).
    В параметре kwargs передаются явно заданные в конкретном тесте настройки, переопределяющие
    настройки по умолчанию.
    Пример переопределения модуля настроек:
        >>> from passport.backend.core.test import utils
        >>>
        >>> from passport_adm_api import settings
        >>>
        >>>
        >>> def with_settings(*args, **kwargs):
        >>>     return utils.with_settings(*args, real_settings=settings, **kwargs)

    Если есть потребность унаследовать часть текущих настроек, если они определены, надо передать их
    как список в параметре inherit_if_set.
    Если же нужно унаследовать все текущие настройки, надо передать inherit_all_existing=True
    """

    patches = _get_default_settings_patches()
    for k, v in iteritems(patches):
        if k not in kwargs:
            kwargs[k] = v

    if real_settings is None:
        try:
            from passport.backend.api.settings import settings as real_settings
        except ImportError:
            pass

    if inherit_if_set:
        declared_settings = set(dir(real_settings))
        settings_to_inherit = set(inherit_if_set) & declared_settings
        for k in settings_to_inherit:
            kwargs[k] = getattr(real_settings, k)

    options = kwargs
    if inherit_all_existing:
        from passport.backend.core.conf import settings as settings_obj
        options = {
            attr: getattr(settings_obj, attr)
            for attr in dir(settings_obj)
            if attr.isupper()
        }
        options.update(kwargs)

    return [
        mock.patch('passport.backend.core.conf.settings._settings', real_settings),
        mock.patch('passport.backend.core.conf.settings._options', options),
    ]


def with_settings(*args, **kwargs):
    patches = _get_settings_patches(**kwargs)

    def _test_function_with_settings(testcase, patches):
        def setup():
            for patch in patches:
                patch.start()
            LazyLoader.flush()

        def teardown():
            for patch in reversed(patches):
                patch.stop()

        return with_setup(setup, teardown)(testcase)

    def _test_class_with_settings(testcase, patches):
        def wrap_setup(old_setup):
            def new_setup(*args):
                for patch in patches:
                    patch.start()
                old_setup()
                LazyLoader.flush()

            return classmethod(new_setup)

        def wrap_teardown(old_teardown):
            def new_teardown(*args):
                old_teardown()
                for patch in reversed(patches):
                    patch.stop()

            return classmethod(new_teardown)

        if issubclass(testcase, PassportTestCase):
            testcase.MOCKED_SETTINGS = dict(
                testcase.MOCKED_SETTINGS,
                **kwargs
            )
        else:
            testcase.setUpClass = wrap_setup(testcase.setUpClass)
            testcase.tearDownClass = wrap_teardown(testcase.tearDownClass)

        return testcase

    def _wrapper(testcase):
        if inspect.isclass(testcase):
            return _test_class_with_settings(testcase, patches)
        else:
            return _test_function_with_settings(testcase, patches)

    if args and (not kwargs) and (callable(args[0])):
        return _wrapper(args[0])
    else:
        return _wrapper


def with_settings_hosts(*args, **kwargs):
    _wrapper = with_settings(
        HOSTS=mock_hosts(),
        REDIS_CONFIG=mock_redis_config(),
        *args,
        **kwargs
    )
    if args and (not kwargs) and (callable(args[0])):
        return _wrapper(args[0])
    else:
        return _wrapper


@contextmanager
def settings_context(**kwargs):
    kwargs.setdefault('HOSTS', mock_hosts())
    kwargs.setdefault('REDIS_CONFIG', mock_redis_config())

    patches = _get_settings_patches(**kwargs)
    for patch in patches:
        patch.start()
    try:
        yield
    finally:
        for patch in reversed(patches):
            patch.stop()


def uniq(src, filter_):
    return list(set(src) - set(filter_))


def iterdiff(f):
    def wrapper(a, b, *args, **kwargs):
        try:
            f(a, b, *args, **kwargs)
        except AssertionError as e:
            if isinstance(a, dict) and isinstance(b, dict):
                a = sorted(a.items())
                b = sorted(b.items())

            if isinstance(a, set) and isinstance(b, set):
                e.args = tuple(['\nIn first: %s\nIn second: %s' % (
                    uniq(a, b),
                    uniq(b, a),
                )] + list(e.args[1:]))
            elif isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
                matcher = _SequenceMatcher(a=b, b=a)
                messages = []
                for tag, start_b, end_b, start_a, end_a in matcher.get_opcodes():
                    messages += _diff_opcode_to_messages(tag, a[start_a:end_a], b[start_b:end_b])
                e.args = tuple([
                    'sequences not equal\n'
                    'Do the transformations in order to get first from second:\n'
                    '%s\n' % '\n'.join(messages),
                ])
            raise e
    return wrapper


def _diff_opcode_to_messages(tag, actual_slice, expected_slice):
    messages = []
    for item in expected_slice:
        messages.append('%s %r' % (_DIFF_OPCODE_TO_PREFIX.get(tag, '-'), item))
    if tag != 'equal':
        for item in actual_slice:
            messages.append('%s %r' % (_DIFF_OPCODE_TO_PREFIX.get(tag, '+'), item))
    return messages


def get_unicode_query_dict_from_url(url, keep_blank_values=True):
    query_string = urlparse(url).query
    if six.PY2:
        # parse_qs('domain=.%D1%80%D1%84&method=hosted_domains&format=json')
        # ожидается domain=u'.\u0440\u0444'
        # на деле domain=u'.\xd1\x80\xd1\x84'
        # через smart_text всё ок
        query_string = smart_bytes(query_string, encoding='ascii', strings_only=True)
        query_dict = parse_qs(query_string, keep_blank_values=keep_blank_values)
        unicode_query_dict = dict()
        for arg, val_list in query_dict.items():
            unicode_query_dict[smart_text(arg)] = [smart_text(val) for val in val_list]
        return unicode_query_dict
    else:
        # на PY3 вышеобозаченной проблемы нету
        if isinstance(query_string, bytes):
            query_string = query_string.decode('utf-8')
        return parse_qs(query_string, keep_blank_values=keep_blank_values)


def _normalize_query_dict(query_dict):
    """
    Если значение на ключе словаря не является списком, то преобразовать его
    в список из одного элемента.
    """
    normal_query_dict = {}
    for arg in query_dict:
        if not isinstance(query_dict[arg], list):
            val_list = [query_dict[arg]]
        else:
            val_list = query_dict[arg]
        normal_query_dict[arg] = val_list
    return normal_query_dict


def _decode_query_dict(query_dict):
    """Декодирует значения-строки из словаря списков значений."""
    unicode_query_dict = {}
    for arg in query_dict:
        val_list = []
        for val in query_dict[arg]:
            if isinstance(val, six.string_types):
                val = smart_text(val)
            val_list.append(val)
        unicode_query_dict[arg] = val_list
    return unicode_query_dict


def check_data_contains_params(data, expected_params):
    for key, value in expected_params.items():
        ok_(key in data, [key, data])
        eq_(
            data[key],
            value,
            'Key=%s %r != %r' % (
                key,
                data[key],
                value,
            ),
        )


def check_url_contains_params(called_url, expected_params, keep_blank_values=True):
    """
    Проверяет нестрогое соответствие параметров query_string.

    Достаточно того чтобы все ожидаемые параметры были представлены в url
    с верными значениями.
    Спокойно относится к тому, чтобы в url было много других параметров кроме
    ожидаемых.
    """
    data = get_unicode_query_dict_from_url(
        called_url,
        keep_blank_values=keep_blank_values,
    )
    expected_params = _decode_query_dict(_normalize_query_dict(expected_params))
    check_data_contains_params(data, expected_params)


def check_all_url_params_match(called_url, expected_params, keep_blank_values=True):
    actual_params = get_unicode_query_dict_from_url(
        called_url,
        keep_blank_values=keep_blank_values,
    )
    expected_params = _decode_query_dict(_normalize_query_dict(expected_params))

    iterdiff(eq_)(actual_params, expected_params)


def check_statbox_log_entry(logger_handler_mock, statbox_line, entry_index=-1):
    call_arg = logger_handler_mock.call_args_list[entry_index]
    line = re.sub(r'^tskv', '', call_arg[0][0]).strip().split('\t')
    result_line = dict()
    for field in line:
        name, value = field.split('=')
        result_line.update({name: value})

    try:
        iterdiff(eq_)(result_line, statbox_line)
    except AssertionError as e:
        raise AssertionError('Line %d (expected %s): %s' % (entry_index, statbox_line, e))


def check_statbox_log_entries(logger_handler_mock, statbox_lines):
    eq_(
        len(statbox_lines),
        logger_handler_mock.call_count,
        msg='%d statbox log entries expected, %d found:\n%s\n  vs\n%s' % (
            len(statbox_lines),
            logger_handler_mock.call_count,
            statbox_lines,
            logger_handler_mock.call_args_list,
        ),
    )
    for index, statbox_line in enumerate(statbox_lines):
        check_statbox_log_entry(logger_handler_mock, statbox_line, entry_index=index)


def assert_call_has_kwargs(call_mock, **assert_kwargs):
    """
    Утверждает, что assert_kwargs является подмножеством множеста именованных
    параметров переданных call_mock в момент вызовам.

    call_mock     -- объект класса mock.Mock или mock.call.__class__
    assert_kwargs -- именованные параметры и их значения

    >>> m = mock.Mock()
    >>> m.hello(foo=1, bar=2)
    >>> assert_call_has_kwargs(m.hello, foo=1, bar=2)
    >>> assert_call_has_kwargs(m.hello.call_args_list[0], bar=2)
    >>> assert_call_has_kwargs(m.hello, bar=1)
    AssertionError: Asserted set of keyword arguments is not subset of keyword
    arguments in the call: (bar=2, foo=1) is not subset of (bar=1)
    """
    def format_(kwargs):
        return ', '.join('%s=%s' % kv for kv in sorted(iteritems(kwargs)))

    if isinstance(call_mock, mock.call.__class__):
        call_kwargs = call_mock[2]
    elif isinstance(call_mock, mock.Mock):
        call_kwargs = call_mock.call_args[1]

    for key in assert_kwargs:
        if key not in call_kwargs or call_kwargs[key] != assert_kwargs[key]:
            is_subset = False
            break
    else:
        is_subset = True

    if not is_subset:
        raise AssertionError(
            'Asserted set of keyword arguments is not subset of keyword '
            'arguments in the call: (%s) is not subset of (%s)' % (
                format_(assert_kwargs),
                format_(call_kwargs),
            ),
        )


class _Call(mock.call.__class__):
    """Дополняет класс Call из библиотеки Mock"""
    def arg(self, argnum):
        """Вернуть порядковый параметр вызова

        Исключение:
            AssertionError, если в вызове не было такого параметра
        """
        try:
            args = self[1]
            arg = args[argnum]
        except IndexError:
            raise AssertionError(
                'Call has only {args_number}, but you asked {asked_arg} '
                '(zero-based)'.format(args_number=len(args), asked_arg=argnum),
            )
        return arg

    def kwarg(self, argname):
        """
        Вернуть именованный параметр вызова

        Исключения:
            AssertionError, если в вызове не было такого параметра
        """
        kwargs = self[2]
        try:
            kwarg = kwargs[argname]
        except KeyError:
            raise AssertionError(
                'Call does not have kwarg "{kwarg}"'.format(kwarg=argname),
            )
        return kwarg


def nth_call(mock, callnum):
    """n-ый вызов mock

    Исключения:
        AssertionError, если такого количества вызовов не было
    """
    try:
        call = mock.call_args_list[callnum]
    except IndexError:
        raise AssertionError(
            'There was only {total_calls}, but you asked the {callnum}th call'.
            format(total_calls=len(mock.call_args_list), callnum=callnum),
        )
    return _Call(call)


def last_call(mock):
    """Последний вызов mock

    Исключения:
        AssertionError, если вызовов не было совсем
    """
    return nth_call(mock, -1)


def check_url_equals(actual_url, expected_url):
    actual_parsed_url = urlparse(actual_url)
    expected_parsed_url = urlparse(expected_url)

    if actual_parsed_url.scheme != expected_parsed_url.scheme:
        raise AssertionError(
            u'Schemes are different: "{actual}" != "{expected}"'.format(
                actual=actual_url,
                expected=expected_url,
            ),
        )
    if actual_parsed_url.netloc != expected_parsed_url.netloc:
        raise AssertionError(
            u'Netlocs are different: "{actual}" != "{expected}"'.format(
                actual=actual_url,
                expected=expected_url,
            ),
        )
    if actual_parsed_url.path != expected_parsed_url.path:
        raise AssertionError(
            u'Paths are different: "{actual}" != "{expected}"'.format(
                actual=actual_url,
                expected=expected_url,
            ),
        )
    if actual_parsed_url.params != expected_parsed_url.params:
        raise AssertionError(
            u'Parameters are different: "{actual}" != "{expected}"'.format(
                actual=actual_url,
                expected=expected_url,
            ),
        )
    expected_query = get_unicode_query_dict_from_url(expected_url)
    check_all_url_params_match(actual_url, expected_query)


class _SequenceMatcher(difflib.SequenceMatcher):
    """
    Добавляет возможность сравнивать последовательности из нехешируемых
    объектов.
    """

    class SetWithoutContains(set):
        def __contains__(self, _item):
            return False

    def set_seq2(self, b):
        if b is self.b:
            return
        self.b = b
        self.matching_blocks = self.opcodes = None
        self.fullbcount = None
        self.__chain_b()

    def __chain_b(self):
        b = self.b
        self.b2j = b2j = _B2j()

        for i, elt in enumerate(b):
            indices = b2j.setdefault(elt, [])
            indices.append(i)

        # Purge junk elements
        self.bjunk = junk = set()
        isjunk = self.isjunk
        if isjunk:
            for elt in b2j.keys():
                if isjunk(elt):
                    junk.add(elt)
            for elt in junk:  # separate loop avoids separate list of keys
                del b2j[elt]

        # Purge popular elements that are not junk
        self.bpopular = popular = set()
        n = len(b)
        if self.autojunk and n >= 200:
            ntest = n // 100 + 1
            for elt, idxs in b2j.items():
                if len(idxs) > ntest:
                    popular.add(elt)
            for elt in popular:  # ditto; as fast for 1% deletion
                del b2j[elt]

        # Now for x in b, isjunk(x) == x in junk, but the latter is much faster.
        # Since the number of *unique* junk elements is probably small, the
        # memory burden of keeping this set alive is likely trivial compared to
        # the size of b2j.
        self.bjunk = self.SetWithoutContains(junk)  # для py-3
        self.isbjunk = self.bjunk.__contains__  # для py-2
        self.isbpopular = popular.__contains__


class _B2j(object):
    """
    Вспомогательный класс имитирующий часть интерфейса словаря, но способный
    хранить в качестве ключей нехешируемые объекты.

    Нужен для того, чтобы минимальными изменениями научить
    difflib.SequenceMatcher сравнивать последовательности из нехешируемых
    объектов.
    """
    def __init__(self):
        self._keys = []
        self._values = []
        return

    def setdefault(self, key, default):
        try:
            i = self._keys.index(key)
        except ValueError:
            self._keys.append(key)
            self._values.append(default)
            return default
        else:
            return self._values[i]

    def keys(self):
        return self._keys

    def items(self):
        return zip(self._keys, self._values)

    def get(self, key, default):
        try:
            i = self._keys.index(key)
        except ValueError:
            return default
        else:
            return self._values[i]

    def __delitem__(self, key):
        try:
            i = self._keys.index(key)
        except ValueError:
            raise KeyError(key)
        else:
            del self._keys[i]
            del self._values[i]


def _format_entry(item, indent=4, step=4):
    indent_str = ' ' * indent

    prev_indent = indent - step
    if prev_indent < 0:
        prev_indent = 0
    next_indent = indent + step

    if isinstance(item, dict):
        elements = sorted([
            u'%s%r: %s,' % (
                indent_str,
                smart_text(k),
                _format_entry(v, indent=next_indent, step=step),
            )
            for k, v in iteritems(item)
        ])
        left_bracket, right_bracket = '{', '}'
    elif isinstance(item, list):
        left_bracket, right_bracket = '[', ']'
        elements = [
            u'%s%s,' % (
                indent_str,
                _format_entry(part, indent=next_indent, step=step),
            )
            for part in item
        ]
    elif isinstance(item, six.binary_type):
        return smart_text(repr(item.decode('utf-8')))
    else:
        return smart_text(repr(item))

    end_indent_str = ' ' * prev_indent
    return u'%s\n%s\n%s%s' % (
        left_bracket,
        '\n'.join(elements),
        end_indent_str,
        right_bracket,
    )


def pseudo_diff(s1, s2):
    """
    Сравнение двух значений (словарей, списков) путем преобразования
    их в отформатированную структурированную форму и прогон через
    стандартный алгоритм поиска различий в наборе текстовых строк.

    "Псевдо" из-за следующих отличий:
    - сравниваются не файлы, а специально подготовленные куски текста;
    - при конвертации в текстовую форму допускаются определенные вольности,
    вроде принудительной конвертации строк в unicode.
    """
    lines_s1 = _format_entry(s1).splitlines()
    lines_s2 = _format_entry(s2).splitlines()

    diff = difflib.unified_diff(
        lines_s1,
        lines_s2,
        fromfile='expected',
        tofile='actual',
        n=10,
    )
    return '\n'.join(list(diff))


def traverse_dict_from_leaves_to_root(main_dict):
    """
    Рекурсивно обходит словарь и его подсловари, начиная с самых вложенных.

    Итератор возвращает пары (словарь, ключ).
    """
    for key in main_dict:
        if isinstance(main_dict[key], dict):
            for sub_dict, sub_key in traverse_dict_from_leaves_to_root(main_dict[key]):
                yield sub_dict, sub_key

    for key in sorted(main_dict.keys()):
        yield main_dict, key


class NotInitializedMock(Exception):
    """
    Тестовому объекту недостаточно данных, чтобы имитировать поведение.
    """


class AnyMatcher(object):
    """
    Выдаёт __eq__ True для любого значения
    """
    def __str__(self):
        return '<Any>'

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return True
