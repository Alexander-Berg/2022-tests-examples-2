import pytest

from favicon.mutation import Mutation, target, yt


class Stateful(Mutation):
    MAX_STATES = 5

    def on_prepare(self):
        self.deep_mapping = dict()

    @target
    def foo(self):
        self.foo_done = True
        self.deep_mapping["first"] = dict()
        self.deep_mapping["first"]["second"] = 5

    @target
    def bar(self):
        assert self.foo_done
        assert self.deep_mapping["first"]["second"] == 5

    def on_cleanup(self):
        assert self.foo_done


def test_do_before_prepare(config):
    with pytest.raises(RuntimeError):
        Stateful.foo()


def test_prepare_finish(config):
    Stateful.prepare()
    time = Stateful('wip')._time
    ftime = Stateful('wip')._ftime
    assert ftime in yt.list(Stateful.tmp_mutation_path())
    Stateful.finish()
    assert Stateful()._time == time
    assert ftime not in yt.list(Stateful.tmp_mutation_path())


def test_saveload_attrs(config):
    Stateful.prepare()
    Stateful.foo()
    Stateful.bar()
    Stateful.finish()
    assert Stateful().foo_done


class TestTagged(object):
    @pytest.fixture(autouse=True)
    def two_tags(self, config):
        self.time_a = Stateful.prepare()._time
        Stateful.foo()
        Stateful.finish()
        Stateful(self.time_a).tag('a')

        self.time_b = Stateful.prepare()._time
        Stateful(self.time_b).tag('b')
        Stateful.foo()
        Stateful.finish()

    def test_load(self):
        assert Stateful('a')._time == self.time_a
        assert Stateful('b')._time == self.time_b

    def test_untag(self):
        Stateful('a').untag('a')
        with pytest.raises(RuntimeError):
            Stateful('a')
        s = Stateful('b')
        with pytest.raises(RuntimeError):
            s.untag('z')

    def test_cleanup(self):
        states = []
        undone = []
        for i in xrange(10):
            states.append(Stateful.prepare()._time)
            Stateful.foo()
            Stateful.finish()

            Stateful.prepare()
            undone.append(Stateful.foo()._ftime)

        Stateful.cleanup()

        # Tagged states have not removed
        Stateful('a')
        Stateful('b')

        # All untagged too old states removed
        for i in xrange(7):
            with pytest.raises(RuntimeError):
                Stateful(states[i])

        # All temporary not-wip states removed
        for i in xrange(9):
            with pytest.raises(RuntimeError):
                Stateful(undone[i])
        Stateful(undone[9])

        # Newest states kept:
        # len([wip, 9, 8, a, b]) == MAX_STATES
        for i in [9, 8]:
            Stateful(states[i])

    def test_archive(self):
        pass
