# coding: utf-8

from sandbox import sdk2

from sandbox.projects.resource_types.releasers import marty


class TesterResource(sdk2.Resource):
    """
    wbjk res
    """
    releasable = False
    any_arch = False
    releasers = marty
    auto_backup = True


class TesterBinary(TesterResource):
    """
    wbjk_srv binary
    """
    arcadia_build_path = 'search/mon/tester/src'
