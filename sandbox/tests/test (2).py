from sandbox import sdk2
from sandbox.projects.common.binary_task import LastRefreshableBinary, LastBinaryTaskRelease
from sandbox.projects.metrika.utils.base_metrika_task import with_parents, exclude_parents
from sandbox.sdk2.internal.task import TaskMeta


class TestWithParents:
    @classmethod
    def setup_class(cls):
        TaskMeta.__overridable__.add('__init__')

        class B(sdk2.Task):
            on_execute = on_save = on_create = on_enqueue = on_terminate = lambda self: self.calls.append('B')

        class C:
            on_execute = on_save = on_prepare = on_create = on_enqueue = lambda self: self.calls.append('C')

        class D:
            on_terminate = lambda self: self.calls.append('D')

        class E(D):
            pass

        class G(LastRefreshableBinary):
            on_save = on_enqueue = lambda self: self.calls.append('G')

        @with_parents
        class A(B, C, E, G):
            def __init__(self):
                self.calls = []

            @exclude_parents(LastBinaryTaskRelease)
            def on_execute(self):
                self.calls.append('A')

            @exclude_parents(C, LastBinaryTaskRelease)
            def on_save(self):
                self.calls.append('A')

            @exclude_parents(C, B, LastRefreshableBinary)
            def on_enqueue(self):
                self.calls.append('A')

            @exclude_parents
            def on_prepare(self):
                self.calls.append('A')

        cls.A = A

    @classmethod
    def teardown_class(cls):
        TaskMeta.__overridable__.remove('__init__')

    def test_parents(self):
        a = self.A()
        a.on_execute()
        assert a.calls == ['B', 'C', 'A']

    def test_exclude_all(self):
        a = self.A()
        a.on_prepare()
        assert a.calls == ['A']

    def test_exclude_one(self):
        a = self.A()
        a.on_save()
        assert a.calls == ['G', 'B', 'A']

    def test_exclude_many(self):
        a = self.A()
        a.on_enqueue()
        assert a.calls == ['G', 'A']

    def test_inherited(self):
        a = self.A()
        a.on_create()
        assert a.calls == ['B', 'C']

    def test_mro_inherited(self):
        a = self.A()
        a.on_terminate()
        assert a.calls == ['B', 'D']
