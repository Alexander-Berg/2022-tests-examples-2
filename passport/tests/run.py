from pprint import pprint
from StringIO import StringIO
import unittest

from passport.backend.profile.tests.test_profile import BuildProfileTestCase


def main():
    stream = StringIO()
    runner = unittest.TextTestRunner(stream=stream)
    result = runner.run(unittest.makeSuite(BuildProfileTestCase))
    print('Tests run ', result.testsRun)
    print('Errors ', result.errors)
    pprint(result.failures)
    stream.seek(0)
    print('Test output ', stream.read())
