from __future__ import absolute_import, print_function, unicode_literals

import time
import collections

import six
import mock
import pytest
import threading

from sandbox.common import patterns


class TestPatterns(object):

    # noinspection PyUnresolvedReferences
    def test__singleton_property(self):

        class Meta(type):
            @patterns.singleton_property
            def cls_prop(cls):
                # noinspection PyUnresolvedReferences
                cls.cls_counter += 1
                return 42

        @six.add_metaclass(Meta)
        class C(object):
            cls_counter = 0

            def __init__(self, prop_value):
                self.counter = 0
                self.__prop = prop_value

            @patterns.singleton_property
            def prop(self):
                self.counter += 1
                return self.__prop

        c1 = C(123)
        c2 = C(321)

        del c1.prop
        del C.cls_prop

        assert c1.counter == 0
        assert c1.prop == 123
        assert c1.counter == 1
        assert c1.prop == 123
        assert c1.counter == 1

        assert c2.counter == 0
        assert c2.prop == 321
        assert c2.counter == 1
        assert c2.prop == 321
        assert c2.counter == 1

        del c1.prop
        del c1.prop

        assert C.cls_counter == 0
        assert C.cls_prop == 42
        assert C.cls_counter == 1
        assert C.cls_prop == 42
        assert C.cls_counter == 1

        del C.cls_prop
        del C.cls_prop

        assert type(C.prop) is patterns.singleton_property

    def test__classproperties(self):

        m = mock.Mock()

        class C(object):
            constant = 43

            @patterns.classproperty
            def cprop(self):
                m.classproperty()
                return m

            @patterns.singleton_classproperty
            def scprop(self):
                m.singleton_classproperty()
                return m

            @property
            def prop(self):
                return 42

        for _ in range(5):
            assert C.cprop is m
            assert C.scprop is m

        assert m.classproperty.call_count == 5
        assert m.singleton_classproperty.call_count == 1

        assert patterns.is_classproperty(C, "cprop")
        assert patterns.is_classproperty(C, "scprop")
        assert patterns.is_classproperty(C, "prop")
        assert not patterns.is_classproperty(C, "constant")
        assert not patterns.is_classproperty(C, "fooo")

    def test__threadlocalmeta(self):

        class Sample(object):
            def __init__(self, *args, **kwargs):
                """ do nothing """

        samplesingleton = six.add_metaclass(patterns.ThreadLocalMeta)(Sample)

        all_ids = set()

        for _ in range(5):
            objs = (
                samplesingleton(1, 2, 4, foo="bar"),
                samplesingleton(another_one=True),
                samplesingleton(yet_another_one=4.2),
            )
            ids = tuple(id(obj) for obj in objs)
            assert len(set(ids)) == 3  # differently initialised objects are different
            all_ids.add(ids)

        assert len(all_ids) == 1  # a single triple of objects

    def test__singletonmeta(self):

        m = mock.Mock()

        class Sample(object):
            def __init__(self, *args, **kwargs):
                m.created()

        samplesingleton = six.add_metaclass(patterns.SingletonMeta)(Sample)

        ids = set(id(samplesingleton(i, i + i, foo=i)) for i in range(3))

        assert len(ids) == 1  # same objects, even if initialised differently
        assert m.created.call_count == 1

        with pytest.raises(AttributeError):
            samplesingleton.instance = 123

    def test__threadsafesingletonmeta(self):

        m = mock.Mock()

        class Sample(object):
            def __init__(self):
                m.created()

        samplesingleton = six.add_metaclass(patterns.ThreadSafeSingletonMeta)(Sample)

        runs = []
        ids = set()

        def new_object_id():
            runs.append(True)
            ids.add(id(samplesingleton()))

        new_object_id()

        thread = threading.Thread(target=new_object_id)
        thread.start()
        thread.join(timeout=1.0)

        assert len(runs) == 2  # ensure the thread has been run
        assert len(ids) == 1
        assert m.created.call_count == 1

    def test__namedtuple(self):

        class WithDefaults(patterns.NamedTuple):
            aaa = 1
            bbb = 1
            __slots__ = ("foo", "bar")
            __defs__ = (False, 42)

        data = WithDefaults()
        assert data.foo is data[0] is False
        assert data.bar == data[1] == 42
        assert tuple(data) == (False, 42)
        assert data.aaa == 1
        assert data.bbb == 1

        data = WithDefaults(True, 43)
        assert tuple(data) == (True, 43)

        class NoDefaults(patterns.NamedTuple):
            __slots__ = ("foo", "bar")

        with pytest.raises(TypeError):
            NoDefaults()

        with pytest.raises(AssertionError):
            class A(patterns.NamedTuple):
                pass

        with pytest.raises(AssertionError):
            class B(patterns.NamedTuple):
                __slots__ = ("foo", "bar")
                __defs__ = (False, )

        with pytest.raises(AttributeError):
            class C(patterns.NamedTuple):
                __slots__ = ("foo", "bar")
                _make = None

    @pytest.mark.parametrize("fields", ["foo bar buz", ("foo", "bar", "buz")])
    def test__namedlist(self, fields):
        import msgpack

        cls = patterns.namedlist("SomeList", fields)

        nl = cls((1, 2, 3.14))
        assert list(nl) == [1, 2, 3.14]

        assert nl[0] == nl.foo == 1
        assert nl[1] == nl.bar == 2
        assert nl[2] == nl.buz == 3.14

        assert repr(nl) == "SomeList(foo=1, bar=2, buz=3.14)"

        nl.buz = 4.2
        assert nl[2] == nl.buz == 4.2

        msgpack.dumps(nl)  # namedlists, unlike tuples, are serializable

    def test_api(self):

        tasks = set()

        @six.add_metaclass(patterns.Api)
        class Sandbox(object):

            @patterns.Api.register
            @staticmethod
            def start():
                tasks.add(42)

            @patterns.Api.register
            @classmethod
            def stop(cls):
                tasks.discard(42)

        class YetAnotherAPI(Sandbox):

            @patterns.Api.register
            @staticmethod
            def click():
                """ click """

            @classmethod
            def stop(cls):
                """ overload """

        cls = patterns.Api['Sandbox']
        cls().start()
        cls().stop()

        assert {("Sandbox", Sandbox), ("YetAnotherAPI", YetAnotherAPI)} <= set(patterns.Api)
        assert Sandbox.api_methods == {"start", "stop"}

    @pytest.mark.parametrize("external_cache", [None, collections.OrderedDict()])
    def test__ttl_cache(self, monkeypatch, external_cache):
        current_time = time.time()
        monkeypatch.setattr(time, "time", lambda: current_time)

        log = mock.Mock()

        def func(name, *args, **kwargs):
            getattr(log, name)(*args, **kwargs)

        cached_func = patterns.ttl_cache(10, external_cache=external_cache)(func)

        with pytest.raises(TypeError):
            cached_func("a", {1, 2, 3})  # unhashable arguments are not supported

        cached_func("a", foo=3)
        cached_func("a", 1, 2, 3)
        assert log.a.call_count == 2

        for _ in range(3):
            cached_func("b", foo=3)
            cached_func("c", foo=5)

        assert log.b.call_count == log.c.call_count == 1

        current_time += 8
        cached_func("b", foo=3)
        assert log.b.call_count == 1

        current_time += 3
        cached_func("b", foo=3)
        assert log.b.call_count == 2

        if not external_cache:
            cached_func = patterns.ttl_cache(3)(func)  # internal cache is reused
            cached_func("b", foo=3)
            assert log.b.call_count == 2

    def test__singleton(self, monkeypatch):
        current_time = time.time()
        monkeypatch.setattr(time, "time", lambda: current_time)

        log = mock.Mock()

        def func(name, *args, **kwargs):
            getattr(log, name)(*args, **kwargs)

        singleton = patterns.singleton(func)

        with pytest.raises(TypeError):
            singleton("a", {1, 2, 3})  # unhashable arguments are not supported

        singleton("a", foo=3)
        singleton("a", 1, 2, 3)
        assert log.a.call_count == 2

        for _ in range(3):
            singleton("b", foo=3)
            singleton("c", foo=5)

        assert log.b.call_count == log.c.call_count == 1

        current_time += 24 * 3600
        singleton("b", foo=3)
        assert log.b.call_count == 1

    def test__abstract(self):

        class Dataclass(patterns.Abstract):
            __slots__ = ('a', 'b', 'c')
            __defs__ = (0, [], {})

        args = (0, [1, 2], {100: 200})

        obj = Dataclass(*args)
        assert (obj.a, obj.b, obj.c) == args
        assert "Dataclass" in repr(obj) and "{100: 200}" in repr(obj)
        assert tuple(obj.itervalues()) == args

        objcopy = obj.copy()
        assert type(objcopy) is Dataclass
        assert tuple(objcopy.itervalues()) == args

        defaultobj = Dataclass(a=3)
        assert defaultobj.c == {} and id(defaultobj.c) != id(Dataclass.__defs__[2])
        assert defaultobj.b == [] and id(defaultobj.b) != id(Dataclass.__defs__[1])
