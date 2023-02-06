# -*- coding: utf-8 -*-

import pytest


pytest_plugins = 'common.libs.plugins.terminalreport',\
                 'common.libs.plugins.myjunitxml',\
                 'common.libs.plugins.pytest_timeout',\
                 'common.libs.plugins.reporter',\
#                 'plugins.calc_server',\
#                 'plugins.calc_client'
# dont use it now 

def pytest_funcarg__sandbox_log(request):
    import os.path
    return os.path.dirname(request.config.option.perfreportpath)


def pytest_addoption(parser):
    parser.addoption("--kiwipath",          help="path, where find binaries")
    parser.addoption("--port-shift",        help="add this parameter to all services ports", type=int)
    parser.addoption("--ornilibs",          help="path to ornithology libs")
    parser.addoption("--udfpath",           help="test udf path")
    parser.addoption("--udfdata",           help="path to data for udf")
    parser.addoption("--udfquery",          help="path to test query to call udf")
    parser.addoption("--udfreply",          help="path to expected reply from udf")
    parser.addoption("--kwnestdata",        help="path to data.tgz for kwnest")
    parser.addoption("--perfreportpath",    help="path for preformance report")
    parser.addoption("--runseq",            help="path for run sequence")
    parser.addoption("--htmlpath",          help="path for html report")
    parser.addoption("--logurl",            help="url for log viewing")
    parser.addoption("--sitapath",          help="path, where find sita binaries")
    parser.addoption("--sitastuff",         help="path for directory with mirrors.trie, url-shorteners.txt and squota.sb00-sita.xml")
    parser.addoption("--runslow", action="store_true", help="run slow tests")
    parser.addoption("--queries",          help="path for configuration file")
    parser.addoption("--geminipath",          help="path, where find gemini binaries")
    parser.addoption("--geministuff",         help="path for directory with mirrors.trie squotasquota.gemini.xml ect.")
    parser.addoption("--fast-teardown",       help="stop daemons in threads", action="store_true",)
    parser.addoption("--generated",         help="path to generated data")
    parser.addoption("--experimental",         help="experimental feature")


def pytest_runtest_setup(item):
    if 'slow' in item.keywords and not item.config.getvalue("runslow"):
        pytest.skip("need --runslow option to run")

