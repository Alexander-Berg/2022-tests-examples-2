# -*- coding: utf-8 -*-
import mock
from nose.tools import (
    eq_,
    raises,
)
from passport.backend.oauth.core.db.eav.differ import differ
from passport.backend.oauth.core.test.framework import BaseTestCase


def mock_model(id, attributes):
    model = mock.Mock()
    model.id = id
    model._attributes = attributes
    return model


def mock_diff(added=None, changed=None, removed=None):
    return {
        'added': added or {},
        'changed': changed or {},
        'removed': removed or {},
    }


class TestDiffer(BaseTestCase):
    @raises(ValueError)
    def test_uncomparable(self):
        differ(
            mock_model(1, {}),
            mock_model(2, {}),
        )

    def test_not_changed(self):
        eq_(
            differ(
                mock_model(1, {}),
                mock_model(1, {}),
            ),
            mock_diff(),
        )

    def test_none_vs_none(self):
        eq_(
            differ(None, None),
            mock_diff(),
        )

    def test_model_created_without_attributes(self):
        eq_(
            differ(
                None,
                mock_model(1, {}),
            ),
            mock_diff(),
        )

    def test_model_created(self):
        eq_(
            differ(
                None,
                mock_model(1, {'foo': 1}),
            ),
            mock_diff(added={'foo': 1}),
        )

    def test_model_deleted(self):
        eq_(
            differ(
                mock_model(1, {'foo': 1}),
                None,
            ),
            mock_diff(removed={'foo': None}),
        )

    def test_attr_created(self):
        eq_(
            differ(
                mock_model(1, {}),
                mock_model(1, {'foo': 1}),
            ),
            mock_diff(added={'foo': 1}),
        )

    def test_attr_changed(self):
        eq_(
            differ(
                mock_model(1, {'foo': 1}),
                mock_model(1, {'foo': 2}),
            ),
            mock_diff(changed={'foo': 2}),
        )

    def test_attr_removed(self):
        eq_(
            differ(
                mock_model(1, {'foo': '1'}),
                mock_model(1, {}),
            ),
            mock_diff(removed={'foo': None}),
        )

    def test_all(self):
        eq_(
            differ(
                mock_model(1, {'foo': 1, 'bar': 1}),
                mock_model(1, {'bar': 2, 'zar': 1}),
            ),
            mock_diff(added={'zar': 1}, changed={'bar': 2}, removed={'foo': None}),
        )
