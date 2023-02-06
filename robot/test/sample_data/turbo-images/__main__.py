import logging
# import os
import os.path
from os.path import join as pj
import click
import sys
import re
import shutil
import robot.rthub.test.sample_data.common as common


def _make_test_data(rthub_package_path, topic_path, topic_name):
    topic = pj(rthub_package_path, topic_path, topic_name)

    if not os.path.exists("test_data"):
        os.mkdir("test_data")

    shutil.copy(topic, pj("test_data", topic_name))

    with open("test_data/data.yql", "w") as w:
        with open(topic) as f:
            readnext = False
            for i in f.readlines():
                if readnext:
                    val = re.findall(r"http://[^\"]+", i.strip())
                    if len(val) > 0:
                        q = 'upsert into [MdsInfoTable](Url, UrlHash, MdsJson, Meta) ' \
                            'select "{url}" As Url, ' \
                            'Digest::CityHash("{url}") As UrlHash, ' \
                            '"" As MdsJson, "{{}}" As Meta;\n'.format(url=val[0])
                        w.write(q)
                    readnext = False

                if "URL" in i:
                    readnext = True


@click.command()
@click.option(
    'prepare',
    '--prepare',
    type=bool,
    help=(
        'Prepare rthub for sampling'
    ),
    default=False,
    is_flag=True
)
@click.option(
    'num_msg',
    '--num-msg',
    help=(
        'Number of messages used for test_data'
    ),
    type=int,
    default=10
)
def main(prepare, num_msg):
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(name)s:%(message)s')
    arcadia_root = common.detect_arcadia_root()
    local_rthub_path = "robot/rthub/tools/local_rthub"

    if prepare:
        common.build(arcadia_root, local_rthub_path)
        common.build_rthub_package(arcadia_root, local_rthub_path, "turbo-images")
    else:
        common.download_rthub_data(arcadia_root, local_rthub_path, "turbo-images", str(num_msg))
        rthub_package_path = common.find_built_package("rthub")
        _make_test_data(rthub_package_path, "data/pq", "zora--original-images")


if __name__ == '__main__':
    main()
