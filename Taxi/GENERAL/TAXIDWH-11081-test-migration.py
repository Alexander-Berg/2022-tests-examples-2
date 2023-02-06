from dmp_suite.migration import migration
from dmp_suite.task import PyTask


def do_nothing():
    print('Doing nothing')


step = PyTask('do-nothing', do_nothing)
step.idempotent = True

task = migration('TAXIDWH-11081', step)
