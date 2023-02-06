#!/usr/bin/env python

import tempfile
import logging
import os
import unittest

import robot.library.yuppie as yp


class TestDownloadYt(unittest.TestCase):
    def test_download_yt(self):

        yt = yp.Async(yp.Yt.up)
        test_files = yp.Async(yp.IO.get_test_resource, "BIKE_SAMPLE_FILES")

        yt = yt.result()
        test_files = test_files.result()

        temp_dir = tempfile.mkdtemp()
        logging.info("Got temp directory: %s", temp_dir)
        yt.upload(test_files, "//home/blah")
        yt.download("//home/blah", temp_dir)

        self.assertEqual(os.listdir(test_files), os.listdir(temp_dir))


if __name__ == '__main__':
    unittest.main()
