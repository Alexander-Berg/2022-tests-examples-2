import os
from shutil import copyfile
import unittest

from passport.backend.library.yalearn.gradient_boosting import MatrixNetClassifier
import yatest.common as yc


class TestIntervalCounters(unittest.TestCase):
    def setUp(self):
        copyfile(yc.work_path('test_data/pack/matrixnet'), '/tmp/matrixnet')
        os.chmod('/tmp/matrixnet', 0o500)
        self.matrixnet = MatrixNetClassifier(
            binary_name='/tmp/matrixnet',
        )

    def test_matrixnet(self):
        X = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]
        y = [0, 1, 1]
        self.matrixnet.fit(X, y)
        self.matrixnet.predict_proba(X)
