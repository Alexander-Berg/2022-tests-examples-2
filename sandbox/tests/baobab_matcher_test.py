from baobab_matcher import BaobabMatcher, SkipEventException
import pytest


class TestBaobabMatcher(object):
    class TestGetKeys(object):
        def test_returns_empty_set_when_unparsable(self):
            matcher = BaobabMatcher(['$none'])
            result = matcher.get_keys('{')
            assert result == set()

        def test_returns_empty_set_when_no_rules(self):
            matcher = BaobabMatcher([])
            result = matcher.get_keys('{"event":"show","tree":{"name":"$page","id":"ba0bab"}}')
            assert result == set()

        def test_returns_empty_set_when_no_matches(self):
            matcher = BaobabMatcher(['$none'])
            result = matcher.get_keys('{"event":"show","tree":{"name":"$page","id":"ba0bab"}}')
            assert result == set()

        def test_returns_matching_keys(self):
            matcher = BaobabMatcher(['$none', '$header'])
            result = matcher.get_keys('{"event":"show","tree":{"name":"$page","id":"ba0bab","children":[{"name":"$header","id":"ba0bac"}]}}')
            assert result == set(['$header'])

        def test_raises_exception_when_tree_is_granny(self):
            matcher = BaobabMatcher(['$page'])
            with pytest.raises(SkipEventException):
                matcher.get_keys('{"event":"show","tree":{"name":"$page","id":"ba0bab","attrs":{"service":"web","subservice":"granny"}}}')

        def test_matches_multiple_blocks(self):
            matcher = BaobabMatcher(['$page', '$header'])
            result = matcher.get_keys('{"event":"show","tree":{"name":"$page","id":"ba0bab","children":[{"name":"$header","id":"ba0bac"}]}}')
            assert result == set(['$page', '$header'])

        def test_matches_blocks_in_sequence(self):
            matcher = BaobabMatcher(['$page', '$header'])
            root_result = matcher.get_keys('{"event":"show","tree":{"name":"$page","id":"ba0bab"}}')
            assert root_result == set(['$page'])
            header_result = matcher.get_keys('{"event":"show","tree":{"name":"$root","id":"ba0bab","children":[{"name":"$header","id":"ba0bac"}]}}')
            assert header_result == set(['$header'])

        def test_returns_no_more_than_max_keys(self):
            matcher = BaobabMatcher(['$page', '$header'], 3)
            root_result = matcher.get_keys('{"event":"show","tree":{"name":"$page","id":"ba0bab"}}')
            assert root_result == set(['$page'])
            root_result = matcher.get_keys('{"event":"show","tree":{"name":"$page","id":"ba1bab"}}')
            assert root_result == set(['$page'])
            root_result = matcher.get_keys('{"event":"show","tree":{"name":"$page","id":"ba2bab"}}')
            assert root_result == set(['$page'])
            root_result = matcher.get_keys('{"event":"show","tree":{"name":"$page","id":"ba3bab"}}')
            assert root_result == set()

        def test_returns_no_more_than_max_keys_per_factor(self):
            matcher = BaobabMatcher(['$page', '$header'], 1)
            root_result = matcher.get_keys('{"event":"show","tree":{"name":"$page","id":"ba0bab"}}', 'ru:desktop')
            assert root_result == set(['$page'])
            root_result = matcher.get_keys('{"event":"show","tree":{"name":"$page","id":"ba1bab"}}', 'ru:desktop')
            assert root_result == set()
            root_result = matcher.get_keys('{"event":"show","tree":{"name":"$page","id":"ba2bab"}}', 'com:desktop')
            assert root_result == set(['$page'])
            root_result = matcher.get_keys('{"event":"show","tree":{"name":"$page","id":"ba3bab"}}', 'com:desktop')
            assert root_result == set()

        def test_returns_no_more_than_max_keys_when_sliced(self):
            matcher = BaobabMatcher(['$page', '$header'], 3, 1)
            root_result = matcher.get_keys('{"event":"show","tree":{"name":"$page","id":"ba0bab"}}')
            assert root_result == set(['$page'])
            root_result = matcher.get_keys('{"event":"show","tree":{"name":"$page","id":"ba1bab"}}')
            assert root_result == set(['$page'])
            root_result = matcher.get_keys('{"event":"show","tree":{"name":"$page","id":"ba2bab"}}')
            assert root_result == set(['$page'])
            root_result = matcher.get_keys('{"event":"show","tree":{"name":"$page","id":"ba3bab"}}')
            assert root_result == set()

        def test_returns_no_more_than_max_keys_per_factor_when_sliced(self):
            matcher = BaobabMatcher(['$page', '$header'], 1, 1)
            root_result = matcher.get_keys('{"event":"show","tree":{"name":"$page","id":"ba0bab"}}', 'ru:desktop')
            assert root_result == set(['$page'])
            root_result = matcher.get_keys('{"event":"show","tree":{"name":"$page","id":"ba1bab"}}', 'ru:desktop')
            assert root_result == set()
            root_result = matcher.get_keys('{"event":"show","tree":{"name":"$page","id":"ba2bab"}}', 'com:desktop')
            assert root_result == set(['$page'])
            root_result = matcher.get_keys('{"event":"show","tree":{"name":"$page","id":"ba3bab"}}', 'com:desktop')
            assert root_result == set()
