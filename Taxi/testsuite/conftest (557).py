# pylint: disable=import-error

# root conftest for service reposition-matcher
pytest_plugins = ['reposition_matcher_plugins.pytest_plugins']

# DO NOT place code here - there is no access to testsuite plugins provided
# by libraries (e.g. client-routing) from this file. Instead, use
# tests_reposition_matcher/conftest.py file
