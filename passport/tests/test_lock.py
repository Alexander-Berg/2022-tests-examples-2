# -*- coding: utf-8 -*-
import unittest

from passport.backend.utils.lock import (
    get_lock_manager,
    lock,
    lock_mock,
)
import ylock


TEST_LOCK_NAME = 'lock1'


class TestLock(unittest.TestCase):
    def setUp(self):
        super(TestLock, self).setUp()
        self.config = {
            'backend': 'zookeeper',
            'hosts': ['test_host_1'],
        }

    def test_create_lock_manager(self):
        lock_manager = get_lock_manager(self.config)
        self.assertTrue(isinstance(lock_manager, ylock.backends.zookeeper.Manager))
        self.assertListEqual(
            lock_manager.hosts,
            [
                'test_host_1',
            ],
        )

    def test_acquire_lock(self):
        with lock_mock():
            with lock(self.config, TEST_LOCK_NAME) as acquired1:
                self.assertTrue(acquired1)

                with lock(self.config, TEST_LOCK_NAME) as acquired2:
                    self.assertFalse(acquired2)
