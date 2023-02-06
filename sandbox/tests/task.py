from __future__ import unicode_literals

import itertools

import six
import pytest

from sandbox.common.types import task as tt


class TestTypesTask:
    # TODO: Remove after complete transition to new statuses [SANDBOX-2654]
    ONLY_NEW_STATUSES = (
        tt.Status.FINISHING,
        tt.Status.NOT_RELEASED,
        tt.Status.RELEASING,
        tt.Status.RELEASED,
        tt.Status.NO_RES,
        tt.Status.PREPARING,
        tt.Status.SUSPENDING,
        tt.Status.SUSPENDED,
        tt.Status.RESUMING,
        tt.Status.TEMPORARY,
        tt.Status.TIMEOUT,
        tt.Status.EXPIRED,
        tt.Status.WAIT_TIME,
        tt.Status.ASSIGNED,
    )

    # TODO: Remove after complete transition to new statuses [SANDBOX-2654]
    def test__unambiguous_translation(self):
        assert set(
            tt.Status.new_status(tt.Status.old_status(st))
            for st in tt.Status
        ) == set(st for st in tt.Status if st not in self.ONLY_NEW_STATUSES)

    # TODO: Remove after complete transition to new statuses [SANDBOX-2654]
    def test__ambiguous_translation(self):
        old_to_new = {st: tt.Status.new_statuses(st) for st in tt.TaskStatus}
        for old_status, new_statuses in six.iteritems(old_to_new):
            assert all(tt.Status.old_status(st) == old_status for st in new_statuses)

    def test__can_switch(self):
        assert tt.Status.can_switch(tt.Status.EXECUTING, tt.Status.DELETED)
        assert not tt.Status.can_switch(tt.Status.PREPARING, tt.Status.SUCCESS)

    def test__expand(self):
        assert tt.Status.Group.expand((
            tt.Status.Group.BREAK,
            tt.Status.Group.EXECUTE,
            tt.Status.Group.FINISH
        )) == set(itertools.chain(
            tt.Status.Group.BREAK,
            tt.Status.Group.EXECUTE,
            tt.Status.Group.FINISH
        ))
        assert tt.Status.Group.expand((
            tt.Status.Group.QUEUE,
            tt.Status.Group.EXECUTE,
            tt.Status.Group.DRAFT
        )) == set(itertools.chain(
            tt.Status.Group.QUEUE,
            tt.Status.Group.EXECUTE,
            tt.Status.Group.DRAFT
        ))
        assert tt.Status.Group.expand((
            tt.Status.Group.DRAFT,
            tt.Status.Group.QUEUE,
            tt.Status.DRAFT,
            tt.Status.EXCEPTION
        )) == {tt.Status.DRAFT, tt.Status.ENQUEUING, tt.Status.ENQUEUED, tt.Status.EXCEPTION}
        st = {tt.Status.DRAFT, tt.Status.ENQUEUING, tt.Status.ENQUEUED, tt.Status.EXCEPTION}
        assert tt.Status.Group.expand(st) == st

    def test__collapse(self):
        assert tt.Status.Group.collapse(itertools.chain(gr for gr in tt.Status.Group)) == {gr for gr in tt.Status.Group}
        assert tt.Status.Group.collapse((
            tt.Status.DRAFT, tt.Status.ENQUEUING, tt.Status.ENQUEUED, tt.Status.EXCEPTION,
            tt.Status.SUCCESS, tt.Status.FAILURE,
            tt.Status.WAIT_RES, tt.Status.WAIT_TASK, tt.Status.WAIT_TIME, tt.Status.WAIT_OUT, tt.Status.WAIT_MUTEX,
        )) == {
            str(tt.Status.Group.DRAFT), str(tt.Status.Group.QUEUE), tt.Status.EXCEPTION,
            tt.Status.SUCCESS, tt.Status.FAILURE, str(tt.Status.Group.WAIT)
        }

    def test__collapse_primary(self):
        primary_groups = filter(lambda _: _.primary, iter(tt.Status.Group))
        secondary_groups = filter(lambda _: not _.primary, iter(tt.Status.Group))
        for group in primary_groups:
            assert tt.Status.Group.collapse(set(iter(group))) == {str(group)}
        for group in secondary_groups:
            statuses = set(iter(group))
            assert tt.Status.Group.expand(statuses) == statuses

    def test__priority(self):
        cls, scls = tt.Priority.Class, tt.Priority.Subclass

        with pytest.raises(ValueError):
            tt.Priority(cls="FOO", scls=scls.LOW)

        with pytest.raises(ValueError):
            tt.Priority(cls=cls.BACKGROUND, scls="FOO")

        assert int(tt.Priority(cls.SERVICE, scls.NORMAL)) == 11

        assert 20 > int(tt.Priority(cls.SERVICE, scls.NORMAL)) > 0

        assert tt.Priority(cls.USER, scls.LOW) > tt.Priority(cls.SERVICE, scls.NORMAL)
        assert tt.Priority(cls.USER, scls.LOW) == tt.Priority(cls.USER, scls.LOW)
        assert tt.Priority(cls.BACKGROUND, scls.HIGH) <= tt.Priority(cls.SERVICE, scls.LOW)

        assert tt.Priority(cls.BACKGROUND, scls.HIGH).as_dict() == {"class": "BACKGROUND", "subclass": "HIGH"}
        assert repr(tt.Priority(cls.BACKGROUND, scls.HIGH)) == "BACKGROUND: HIGH"

    def test__priority_iteration(self):
        cls, scls = tt.Priority.Class, tt.Priority.Subclass

        priority = tt.Priority(cls.BACKGROUND, scls.LOW)
        assert priority == priority.prev
        assert priority.next == tt.Priority(cls.BACKGROUND, scls.NORMAL)
        assert priority.next.next == tt.Priority(cls.BACKGROUND, scls.HIGH)
        assert priority.next.next.next == tt.Priority(cls.SERVICE, scls.LOW)

        priority = tt.Priority(cls.USER, scls.HIGH)
        assert priority == priority.next
        assert priority.prev == tt.Priority(cls.USER, scls.NORMAL)
        assert priority.prev.prev == tt.Priority(cls.USER, scls.LOW)
        assert priority.prev.prev.prev == tt.Priority(cls.SERVICE, scls.HIGH)

    def test__set_priority_state(self):
        cls, scls = tt.Priority.Class, tt.Priority.Subclass
        priority = tt.Priority()

        priority.__setstate__(12)
        assert priority == tt.Priority(cls.SERVICE, scls.HIGH)

        priority.__setstate__(("USER", "LOW"))
        assert priority == tt.Priority(cls.USER, scls.LOW)

        priority.__setstate__({"class": "SERVICE", "subclass": "HIGH"})
        assert priority == tt.Priority(cls.SERVICE, scls.HIGH)

        # special case: the priority is not supposed to change
        priority.__setstate__({"class": None, "subclass": None})
        assert priority == tt.Priority(cls.SERVICE, scls.HIGH)

        priority.__setstate__((cls.SERVICE, scls.NORMAL))
        assert priority == tt.Priority(cls.SERVICE, scls.NORMAL)

        priority.__setstate__(tt.Priority(cls.SERVICE, scls.LOW))
        assert priority == tt.Priority(cls.SERVICE, scls.LOW)

        with pytest.raises(ValueError):
            priority.__setstate__("highest priority")
        with pytest.raises(ValueError):
            priority.__setstate__(6)
        with pytest.raises(KeyError):
            priority.__setstate__(("USERZ", "LOW"))

        priority = tt.Priority(cls.SERVICE, scls.NORMAL)
        new_priority = tt.Priority()
        new_priority.__setstate__(priority.__getstate__())

        assert tt.Priority.make(priority.__getstate__()) == new_priority == priority

    @pytest.mark.parametrize(
        "kwargs", (
            {"acquires": ()},
            {"acquires": [("a", 1, 1)], "release": ()},
            {"acquires": [("a", 1, 1)], "release": ("FOO", "BAR")},
        )
    )
    def test__semaphores_invalid(self, kwargs):
        with pytest.raises(ValueError):
            tt.Semaphores(**kwargs)

    @pytest.mark.parametrize(
        "acquires", (
            ("a", 1, 1),
            ["a", 1, 1],
            {"name": "a", "weight": 1, "capacity": 1},
            tt.Semaphores.Acquire("a", weight=1, capacity=1)
        )
    )
    def test__semaphores_valid(self, acquires):
        sem = tt.Semaphores(acquires=[acquires], release=["SUCCESS", "FAILURE"])
        sem_dict = sem.to_dict()
        sem_dict["release"] = sorted(sem_dict["release"])
        assert sem_dict == {
            "acquires": [{"name": "a", "weight": 1, "capacity": 1, "public": False}],
            "release": ["FAILURE", "SUCCESS"]
        }

    @pytest.mark.parametrize(
        "kwargs", (
            {"name": 123},
            {"name": ""},
            {"name": "foo", "weight": -1},
            {"name": "foo", "weight": "foo"},
            {"name": "foo", "capacity": -1},
            {"name": "foo", "capacity": "foo"},
        )
    )
    def test__semaphores_acquire_invalid(self, kwargs):
        with pytest.raises(ValueError):
            tt.Semaphores.Acquire(**kwargs)

    def test__semaphores_acquire(self):
        kwargs = {"name": "foo", "weight": 10, "capacity": 100, "public": False}
        acq = tt.Semaphores.Acquire(**kwargs)
        assert acq == ("foo", 10, 100, False)
        assert acq.to_dict() == kwargs

    def test__task_tag(self):

        with pytest.raises(ValueError):
            tt.TaskTag.test(":AAA")  # does not start with a word character

        with pytest.raises(ValueError):
            tt.TaskTag.test("a" * 280)  # too long

        with pytest.raises(ValueError):
            tt.TaskTag.test("aaa+")  # invalid character

        tt.TaskTag.test("TAG")
        tt.TaskTag.test("yet:another-tag-1234")

    def test__relpath(self):
        assert tt.relpath(5) == ["5", "0", "5"]
        assert tt.relpath(50) == ["0", "5", "50"]
        assert tt.relpath(503) == ["3", "0", "503"]
        assert tt.relpath(5031) == ["1", "3", "5031"]

    def test__intervaltype(self):
        assert tt.IntervalType.close_order(tt.IntervalType.WAIT) == ['execute', 'queue', 'wait']
        assert tt.IntervalType.close_order(tt.IntervalType.QUEUE) == ['wait', 'execute', 'queue']
