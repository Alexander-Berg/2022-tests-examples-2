import os
import pytest
from commands import getoutput
from commands import getstatusoutput

from common.libs.plugins.reporter import *

libpath = pytest.config.option.ornilibs
binpath = pytest.config.option.geminipath

def pytest_funcarg__html_config(request):
    return html_config(
        name="super_dups",
        description="""Test for super dups. Starts super_dups_test and checks different modes with dedicated data""",
        directory="super_dups"
    )

ldir = os.listdir("%s/../super_tests" % libpath)

@pytest.mark.parametrize("sup_dir", ldir)
def test_start_stop(sup_dir, html):
    
    html.comment(header="Check %s" % sup_dir, message="")
    
    sdir = sup_dir 
    os.chdir("%s/../super_tests/%s" % (libpath, sdir))
    (retcode, log) = getstatusoutput("%s/super_dups_test %s" % (binpath, sdir))
    
    assert retcode == 0, "\n\tRetcode: %s. \n\tMessage: %s" % (retcode, log) 
    
    flist = os.listdir(".")
    for f in flist:
        if len(f.split(".")) > 1 and f.split(".")[1] == "expected":
            expected = open(f).read().splitlines()
            received = sorted(open("%s" % f.split(".")[0]).read().splitlines())
            for (e, r) in zip(expected, received):
                assert e == r
