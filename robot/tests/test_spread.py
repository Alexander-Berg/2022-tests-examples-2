from datetime import datetime
from os.path import join as pj

import pytest
from hamcrest import assert_that, contains

from favicon.mutation import yt
from favicon import TImageRecord, ESpreadTableTag
from favicon.targets import Manual, Spread

from utils import upload_table


def test_png_bomb(config):
    spark = TImageRecord()
    spark.Url = "http://example.org/spark.png"
    spark.ImageDoc = open("spark.png").read()
    spark.Timestamp = -int(datetime.utcnow().strftime("%s"))
    spark.TableTag = ESpreadTableTag.Value("STT_DELTA")

    yt.create_table(yt.Table(config.Home + "/base", TImageRecord))
    yt.run_sort(yt.Table(config.Home + "/base", TImageRecord), sort_by=["Url", "Timestamp", "Layer"])

    yt.write_table(yt.Table(config.Home + "/delta", TImageRecord), [spark])
    yt.run_sort(yt.Table(config.Home + "/delta", TImageRecord), sort_by=["Url", "Timestamp", "Layer"])

    assert bool(config.BinDir), "Invalid binary dir"
    op = yt.run_operation([
        pj(config.BinDir, config.JobBinary),
        "Spread", "MergeImageDelta",
        "--delta", config.Home + "/delta",
        "--old-state", config.Home + "/base",
        "--new-state", config.Home + "/result"])

    errors = op.get_job_statistics()["custom"]["Errors"]
    assert errors["$"]["completed"]["sorted_reduce"]["sum"] == 1
    assert_that(yt.read_table(config.Home + "/result"), contains())


# How to generate test data:
# 1. Run https://yql.yandex-team.ru/Queries/58bc3fcf5971b8b4efb24c1d
# 2. Download result tables and place them into "exports" directory.
# 3. Upload directory into sandbox and link it via CMakeLists.txt
class TestSmoke(object):
    @pytest.fixture(autouse=True)
    def init(self, config):
        self.export_path = config.Home + "/export"
        config.Spread.ImageImportPrefix = self.export_path
        Manual.install()

    def upload(self, what):
        yt.create("map_node", self.export_path, ignore_existing=True)
        table = "%s/%s" % (self.export_path, what)
        upload_table("exports/%s.yson.gz" % what, table)
        return table

    def check_unique(self, spread):
        yt.run_sort(spread.image_table().sorted(by=["Url", "Timestamp", "Layer"], unique=True))

    def run_graph(self, num):
        self.upload("%d" % num)
        spread = Spread.prepare()
        Spread.import_images()
        Spread.sort_images()
        Spread.merge_images()
        self.check_unique(spread)
        Spread.finish()

    def test_spread_smoke(self):
        self.run_graph(1)
        self.run_graph(2)
