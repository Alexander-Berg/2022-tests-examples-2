from unittest import TestCase

import pytest
from dmp_suite.ctl import types, Parameter
from dmp_suite.ctl.storage import BufferedBatch, ParamChange, ReplicatedBatch


class AssertStorage(object):
    def __init__(self):
        self.batch_handled = 0
        self.result = None

    def handle_batch(self, batch_iterator):
        self.batch_handled += 1
        self.result = list(batch_iterator)

    def assert_(self, expected):
        assert expected == self.result

    def assert_empty(self):
        assert not self.result


class AssertRetryStorage(AssertStorage):

    def __init__(self):
        super(AssertRetryStorage, self).__init__()
        self.raised = False

    def handle_batch(self, batch_iterator):
        if not self.raised:
            self.raised = True
            raise RuntimeError('test')

        super(AssertRetryStorage, self).handle_batch(batch_iterator)


class TestBufferedBatch(TestCase):

    def setUp(self):
        self.entity1 = type("", (), {})()
        self.int_parameter1 = Parameter('parameter1', types.Integer)
        self.entity2 = type("", (), {})()
        self.int_parameter2 = Parameter('parameter2', types.Double)
        self.value = 1

    def test_context_manager(self):
        storage = AssertStorage()
        with BufferedBatch(storage) as ctl_batch:
            ctl_batch.set_param(
                self.entity1, self.int_parameter1, self.value
            )
            ctl_batch.set_param(
                self.entity1, self.int_parameter2, self.value
            )
            ctl_batch.set_param(
                self.entity2, self.int_parameter1, self.value
            )
        storage.assert_([
            ParamChange(self.entity1, self.int_parameter1, self.value),
            ParamChange(self.entity1, self.int_parameter2, self.value),
            ParamChange(self.entity2, self.int_parameter1, self.value),
        ])

    def test_flush(self):
        storage = AssertStorage()
        ctl_batch = BufferedBatch(storage)
        ctl_batch.set_param(
            self.entity1, self.int_parameter1, self.value
        )
        ctl_batch.set_param(
            self.entity1, self.int_parameter2, self.value
        )
        ctl_batch.set_param(
            self.entity2, self.int_parameter1, self.value
        )
        ctl_batch.flush()
        storage.assert_([
            ParamChange(self.entity1, self.int_parameter1, self.value),
            ParamChange(self.entity1, self.int_parameter2, self.value),
            ParamChange(self.entity2, self.int_parameter1, self.value),
        ])

    def test_retry_flush(self):
        # check unbroken internal state after first exception
        # for example, timeout exception
        storage = AssertRetryStorage()
        ctl_batch = BufferedBatch(storage)
        ctl_batch.set_param(
            self.entity1, self.int_parameter1, self.value
        )
        ctl_batch.set_param(
            self.entity1, self.int_parameter2, self.value
        )
        ctl_batch.set_param(
            self.entity2, self.int_parameter1, self.value
        )

        with pytest.raises(RuntimeError):
            ctl_batch.flush()

        ctl_batch.flush()
        storage.assert_([
            ParamChange(self.entity1, self.int_parameter1, self.value),
            ParamChange(self.entity1, self.int_parameter2, self.value),
            ParamChange(self.entity2, self.int_parameter1, self.value),
        ])

    def test_multiple_flush(self):
        storage = AssertStorage()
        ctl_batch = BufferedBatch(storage)
        ctl_batch.set_param(
            self.entity1, self.int_parameter1, self.value
        )
        ctl_batch.flush()
        storage.assert_([
            ParamChange(self.entity1, self.int_parameter1, self.value)
        ])

        ctl_batch.set_param(
            self.entity1, self.int_parameter2, self.value
        )
        ctl_batch.set_param(
            self.entity2, self.int_parameter1, self.value
        )
        ctl_batch.flush()
        storage.assert_([
            ParamChange(self.entity1, self.int_parameter2, self.value),
            ParamChange(self.entity2, self.int_parameter1, self.value),
        ])
        assert 2 == storage.batch_handled

    def test_mixin_call(self):
        storage = AssertStorage()
        ctl_batch = BufferedBatch(storage)
        ctl_batch.set_param(
            self.entity1, self.int_parameter1, self.value
        )
        with ctl_batch:
            ctl_batch.set_param(
                self.entity1, self.int_parameter2, self.value
            )
            ctl_batch.set_param(
                self.entity2, self.int_parameter1, self.value
            )
        storage.assert_([
            ParamChange(self.entity1, self.int_parameter1, self.value),
            ParamChange(self.entity1, self.int_parameter2, self.value),
            ParamChange(self.entity2, self.int_parameter1, self.value),
        ])

    def test_exit(self):
        storage = AssertStorage()
        with pytest.raises(RuntimeError):
            with BufferedBatch(storage):
                raise RuntimeError('test ctl_batch.__exit__()')
        assert not storage.batch_handled


class MockBatch(BufferedBatch):
    def __init__(self, storage, raise_on=None):
        super(MockBatch, self).__init__(storage)
        self.raise_on = set(raise_on) if raise_on else set()
        self.result = []

    def raise_on_method(self, method_name):
        if method_name in self.raise_on:
            raise RuntimeError()

    def flush(self):
        self.raise_on_method('flush')
        super(MockBatch, self).flush()

    def __enter__(self):
        self.raise_on_method('__enter__')
        return super(MockBatch, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.raise_on_method('__exit__')
        super(MockBatch, self).__exit__(exc_type, exc_val, exc_tb)

    def set_param(self, storage_entity, parameter, value):
        self.raise_on_method('set_param')
        super(MockBatch, self).set_param(storage_entity, parameter, value)


class TestReplicatedBatch(TestCase):
    def setUp(self):
        self.entity1 = type("", (), {})()
        self.int_parameter1 = Parameter('parameter1', types.Integer)
        self.entity2 = type("", (), {})()
        self.int_parameter2 = Parameter('parameter2', types.Double)
        self.value = 1

    def test_context_manager_success(self):
        primary_storage = AssertStorage()
        replica_storage = AssertStorage()
        primary_batch = MockBatch(primary_storage)
        replica_batch = MockBatch(replica_storage)

        with ReplicatedBatch(primary_batch, replica_batch) as ctl_batch:
            ctl_batch.set_param(
                self.entity1, self.int_parameter1, self.value
            )
            ctl_batch.set_param(
                self.entity1, self.int_parameter2, self.value
            )
            ctl_batch.set_param(
                self.entity2, self.int_parameter1, self.value
            )
        result = [
            ParamChange(self.entity1, self.int_parameter1, self.value),
            ParamChange(self.entity1, self.int_parameter2, self.value),
            ParamChange(self.entity2, self.int_parameter1, self.value),
        ]
        primary_storage.assert_(result)
        replica_storage.assert_(result)

    def test_context_manager_primary_enter_fail(self):
        primary_storage = AssertStorage()
        replica_storage = AssertStorage()
        primary_batch = MockBatch(primary_storage, ('__enter__',))
        replica_batch = MockBatch(replica_storage)
        with pytest.raises(RuntimeError):
            with ReplicatedBatch(primary_batch, replica_batch) as ctl_batch:
                ctl_batch.set_param(
                    self.entity1, self.int_parameter1, self.value
                )
                ctl_batch.set_param(
                    self.entity1, self.int_parameter2, self.value
                )
                ctl_batch.set_param(
                    self.entity2, self.int_parameter1, self.value
                )
        primary_storage.assert_empty()
        replica_storage.assert_empty()

    def test_context_manager_primary_exit_fail(self):
        primary_storage = AssertStorage()
        replica_storage = AssertStorage()
        primary_batch = MockBatch(primary_storage, ('__exit__',))
        replica_batch = MockBatch(replica_storage)
        with pytest.raises(RuntimeError):
            with ReplicatedBatch(primary_batch, replica_batch) as ctl_batch:
                ctl_batch.set_param(
                    self.entity1, self.int_parameter1, self.value
                )
                ctl_batch.set_param(
                    self.entity1, self.int_parameter2, self.value
                )
                ctl_batch.set_param(
                    self.entity2, self.int_parameter1, self.value
                )
        primary_storage.assert_empty()
        replica_storage.assert_empty()

    def test_context_manager_replica_enter_fail(self):
        primary_storage = AssertStorage()
        replica_storage = AssertStorage()
        primary_batch = MockBatch(primary_storage)
        replica_batch = MockBatch(replica_storage, ('__enter__',))
        with ReplicatedBatch(primary_batch, replica_batch) as ctl_batch:
            ctl_batch.set_param(
                self.entity1, self.int_parameter1, self.value
            )
            ctl_batch.set_param(
                self.entity1, self.int_parameter2, self.value
            )
            ctl_batch.set_param(
                self.entity2, self.int_parameter1, self.value
            )
        primary_storage.assert_([
            ParamChange(self.entity1, self.int_parameter1, self.value),
            ParamChange(self.entity1, self.int_parameter2, self.value),
            ParamChange(self.entity2, self.int_parameter1, self.value),
        ])
        replica_storage.assert_empty()

    def test_context_manager_replica_exit_fail(self):
        primary_storage = AssertStorage()
        replica_storage = AssertStorage()
        primary_batch = MockBatch(primary_storage)
        replica_batch = MockBatch(replica_storage, ('__exit__',))
        with ReplicatedBatch(primary_batch, replica_batch) as ctl_batch:
            ctl_batch.set_param(
                self.entity1, self.int_parameter1, self.value
            )
            ctl_batch.set_param(
                self.entity1, self.int_parameter2, self.value
            )
            ctl_batch.set_param(
                self.entity2, self.int_parameter1, self.value
            )

        primary_storage.assert_([
            ParamChange(self.entity1, self.int_parameter1, self.value),
            ParamChange(self.entity1, self.int_parameter2, self.value),
            ParamChange(self.entity2, self.int_parameter1, self.value),
        ])
        replica_storage.assert_empty()

    def test_flush(self):
        primary_storage = AssertStorage()
        replica_storage = AssertStorage()
        primary_batch = MockBatch(primary_storage)
        replica_batch = MockBatch(replica_storage)
        ctl_batch = ReplicatedBatch(primary_batch, replica_batch)

        ctl_batch.set_param(
            self.entity1, self.int_parameter1, self.value
        )
        ctl_batch.set_param(
            self.entity1, self.int_parameter2, self.value
        )
        ctl_batch.set_param(
            self.entity2, self.int_parameter1, self.value
        )
        ctl_batch.flush()
        result = [
            ParamChange(self.entity1, self.int_parameter1, self.value),
            ParamChange(self.entity1, self.int_parameter2, self.value),
            ParamChange(self.entity2, self.int_parameter1, self.value),
        ]
        primary_storage.assert_(result)
        replica_storage.assert_(result)

    def test_flush_primary_fail(self):
        primary_storage = AssertStorage()
        replica_storage = AssertStorage()
        primary_batch = MockBatch(primary_storage, ('flush',))
        replica_batch = MockBatch(replica_storage)
        ctl_batch = ReplicatedBatch(primary_batch, replica_batch)

        ctl_batch.set_param(
            self.entity1, self.int_parameter1, self.value
        )
        ctl_batch.set_param(
            self.entity1, self.int_parameter2, self.value
        )
        ctl_batch.set_param(
            self.entity2, self.int_parameter1, self.value
        )
        with pytest.raises(RuntimeError):
            ctl_batch.flush()

        primary_storage.assert_empty()
        replica_storage.assert_empty()

    def test_flush_replica_fail(self):
        primary_storage = AssertStorage()
        replica_storage = AssertStorage()
        primary_batch = MockBatch(primary_storage)
        replica_batch = MockBatch(replica_storage, ('flush',))
        ctl_batch = ReplicatedBatch(primary_batch, replica_batch)

        ctl_batch.set_param(
            self.entity1, self.int_parameter1, self.value
        )
        ctl_batch.set_param(
            self.entity1, self.int_parameter2, self.value
        )
        ctl_batch.set_param(
            self.entity2, self.int_parameter1, self.value
        )
        ctl_batch.flush()
        primary_storage.assert_([
            ParamChange(self.entity1, self.int_parameter1, self.value),
            ParamChange(self.entity1, self.int_parameter2, self.value),
            ParamChange(self.entity2, self.int_parameter1, self.value),
        ])
        replica_storage.assert_empty()

    def test_multiple_flush(self):
        primary_storage = AssertStorage()
        replica_storage = AssertStorage()
        primary_batch = MockBatch(primary_storage)
        replica_batch = MockBatch(replica_storage)
        ctl_batch = ReplicatedBatch(primary_batch, replica_batch)

        ctl_batch.set_param(
            self.entity1, self.int_parameter1, self.value
        )
        ctl_batch.flush()
        result = [ParamChange(self.entity1, self.int_parameter1, self.value)]
        primary_storage.assert_(result)
        replica_storage.assert_(result)

        ctl_batch.set_param(
            self.entity1, self.int_parameter2, self.value
        )
        ctl_batch.set_param(
            self.entity2, self.int_parameter1, self.value
        )
        ctl_batch.flush()
        result = [
            ParamChange(self.entity1, self.int_parameter2, self.value),
            ParamChange(self.entity2, self.int_parameter1, self.value),
        ]
        primary_storage.assert_(result)
        replica_storage.assert_(result)
