# coding: utf-8

from sandbox import sdk2


class TESTPALM_FRONTEND(sdk2.Resource):
    """
        TestPalm frontend
    """
    auto_backup = True
    any_arch = False


class TESTPALM_SAMOGON_PLUGIN(sdk2.Resource):
    """
        TestPalm package
    """
    auto_backup = True
    any_arch = False


class PORTO_LAYER_TESTPALM_MONGODB(sdk2.resource.AbstractResource):
    """
        TestPalm porto layer for MongoDB
    """
    releasable = True
    any_arch = True
    auto_backup = True
    releasers = ["deniskuzin"]
    ttl = 'inf'


class PORTO_LAYER_TESTPALM_ELASTICSEARCH(sdk2.resource.AbstractResource):
    """
        TestPalm porto layer for Elasticsearch
    """
    releasable = True
    any_arch = True
    auto_backup = True
    releasers = ["deniskuzin"]
    ttl = 'inf'


class PORTO_LAYER_TESTPALM_COMPARE_OLD(sdk2.resource.AbstractResource):
    """
        TestPalm porto layer for old Compare
    """
    releasable = True
    any_arch = True
    auto_backup = True
    releasers = ["deniskuzin"]
    ttl = 'inf'


class PORTO_LAYER_TESTPALM_COMPARE_NEW(sdk2.resource.AbstractResource):
    """
        TestPalm porto layer for new Compare
    """
    releasable = True
    any_arch = True
    auto_backup = True
    releasers = ["deniskuzin"]
    ttl = 'inf'


class PORTO_LAYER_TESTPALM_BALANCER(sdk2.resource.AbstractResource):
    """
        TestPalm porto layer for balancer
    """
    releasable = True
    any_arch = True
    auto_backup = True
    releasers = ["deniskuzin"]
    ttl = 'inf'


class TESTPALM_PROFILER(sdk2.Resource):
    """
        YourKit Java Profiler
    """
    auto_backup = True
    any_arch = False
