import logging
# import os
import os.path
from os.path import join as pj
import click
import sys
import re
import shutil
import ydb
import robot.rthub.test.sample_data.common as sdcommon

endpoint = "ydb-ru.yandex.net:2135"
database = "/ru/turbopages/prestable/data"


def _make_autoparser_data(session):
    logging.info("making autoparser data!")
    result_set = session.transaction().execute(
        "select Host, AutoparserByTitleEnabled, ModificationTime, UseFilter from autoparser_flags")[0]
    with open(pj("test_data", "data.yql"), "a") as f:
        q = 'upsert into [autoparser_flags](Host, AutoparserByTitleEnabled, ModificationTime, UseFilter)' \
            ' select "{}" As Host, "{}" As AutoparserByTitleEnabled, "{}" As ModificationTime , "{}" As UseFilter;\n'
        for i in result_set.rows:
            f.write(q.format(i.Host, i.AutoparserByTitleEnabled, i.ModificationTime, i.UseFilter))


def _make_top_filter_data(session, topic_name):
    with open(pj("test_data", topic_name)) as f:
        q = 'select UrlHash, Url, ModificationTime from top_filter where Url = "{}";'
        out_q = 'upsert into [top_filter](ModificationTime, Url, UrlHash) ' \
                ' select "{}" As ModificationTime, "{}" As Url, cast({} As Uint64) As UrlHash;\n'
        transaction = session.transaction()
        with open(pj("test_data", "data.yql"), "a") as out:
            for i in f.readlines():
                if "Url: \"" in i:
                    val = re.findall(r"http://[^\"]+", i.strip())
                    if len(val) > 0:
                        result_set = transaction.execute(q.format(val[0]))[0]
                        for j in result_set.rows:
                            out.write(out_q.format(str(j.ModificationTime), str(j.Url), str(j.UrlHash)))


def _make_mdsinfo_data(arcadia_root, local_rthub_path, session, local_kikimr_dict):
    os.environ["KIKIMR_PROXY"] = local_kikimr_dict['endpoint']
    os.environ["KIKIMR_DATABASE"] = local_kikimr_dict['database']
    os.environ["MDS_INFO_TABLE"] = "MdsInfoTable"
    os.environ["AUTOPARSER_FLAGS_TABLE"] = "autoparser_flags"
    os.environ["FEED_HASHES_TABLE"] = "feed_hashes"
    os.environ["BUTTON_FILTER_TABLE"] = "top_filter"
    os.environ["TEST_TIMESTAMP"] = "0"
    os.environ["YQL_CONFIG_NAME"] = "testing"

    logging.info(str(os.environ))
    logging.info("making mdsinfo data")

    yql_path = 'robot/rthub/test/turbo-pages/yql/table.yql'
    with open(pj(arcadia_root, yql_path)) as f:
        yql = f.read()

    session.execute_scheme(yql)

    sdcommon.patch_rthub_config(arcadia_root, local_rthub_path, "turbo-parser")
    sdcommon.run_rthub(arcadia_root, local_rthub_path, "turbo-parser")
    sdcommon.patch_rthub_config(arcadia_root, local_rthub_path, "turbo-postprocess")
    sdcommon.run_rthub(arcadia_root, local_rthub_path, "turbo-postprocess")

    result_set = session.transaction().execute(
        "select "
        "   UrlHash, "
        "   Url, "
        "   HttpCode, "
        "   MdsJson, "
        "   MimeType, "
        "   ModificationTime, "
        "   FailAttemptsCount, "
        "   OriginalPath, "
        "   Meta, "
        "   UploadTime, "
        "   IsRss "
        "from MdsInfoTable")[0]
    with open(pj("test_data", "data.yql"), "a") as f:
        q = 'upsert into [MdsInfoTable]' \
            '(UrlHash, Url, HttpCode, MdsJson, MimeType, ModificationTime, ' \
            'FailAttemptsCount, OriginalPath, Meta, UploadTime, IsRss)' \
            ' select ' \
            '   "{}" As UrlHash, ' \
            '   "{}" As Url, ' \
            '   "{}" As HttpCode, ' \
            '   "{}" As MdsJson, ' \
            '   "{}" As MimeType, ' \
            '   "{}" As ModificationTime, ' \
            '   "{}" As FailAttemptsCount, ' \
            '   "{}" As OriginalPath, ' \
            '   "{}" As Meta, ' \
            '   "{}" As UploadTime, ' \
            '   "{}" As IsRss;\n'
        for i in result_set.rows:
            f.write(q.format(
                i.UrlHash,
                i.Url,
                i.HttpCode,
                i.MdsJson,
                i.MimeType,
                i.ModificationTime,
                i.FailAttemptsCount,
                i.OriginalPath,
                i.Meta,
                i.UploadTime,
                i.IsRss))


def _get_driver(pendpoint, pdatabase, local=False):
    ydb_token = os.environ.get("YDB_TOKEN")
    if not ydb_token:
        raise RuntimeError('YDB_TOKEN not defined, set it via environment variable')

    if not local:
        params = ydb.DriverConfig(endpoint=pendpoint, database=pdatabase, auth_token=ydb_token)
    else:
        params = ydb.DriverConfig(endpoint=pendpoint, database=pdatabase)

    driver = ydb.Driver(params)
    driver.wait()
    return driver


def _make_test_data(arcadia_root,
                    local_rthub_path,
                    rthub_package_path,
                    topic_path,
                    topic_name,
                    prod_kikimr_dict,
                    local_kikimr_dict):
    logging.info("making test data")
    topic = pj(rthub_package_path, topic_path, topic_name)

    if not os.path.exists("test_data"):
        os.mkdir("test_data")

    shutil.copy(topic, pj("test_data", topic_name))

    driver = _get_driver(prod_kikimr_dict['endpoint'], prod_kikimr_dict['database'], False)
    session = driver.table_client.session().create()
    _make_autoparser_data(session)
    _make_top_filter_data(session, topic_name)
    driver.stop()

    logging.error("local kikimr" + str(local_kikimr_dict))
    driver = _get_driver(local_kikimr_dict['endpoint'], local_kikimr_dict['database'], True)
    session = driver.table_client.session().create()
    _make_mdsinfo_data(arcadia_root, local_rthub_path, session, local_kikimr_dict)
    driver.stop()


def _local_kikimr_endpoint(path):
    with open(pj(path, "ydb_endpoint.txt")) as f:
        return f.read()


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
    arcadia_root = sdcommon.detect_arcadia_root()
    local_rthub_path = "robot/rthub/tools/local_rthub"
    local_ydb_path = "kikimr/public/tools/local_ydb"
    kikimr_working_dir = pj(os.getcwd(), "kikimr_data")
    kikimr_stable = "kikimr/public/tools/package/stable"
    kikimr_stable_libs = pj(kikimr_stable, "Berkanavt/kikimr/libs")
    kikimr_driver = "kikimr/driver"

    if not os.path.exists(kikimr_working_dir):
        print "making path: " + kikimr_working_dir
        os.mkdir(kikimr_working_dir)

    if prepare:
        sdcommon.build(arcadia_root, local_rthub_path)
        sdcommon.build(arcadia_root, local_ydb_path, '-r')
        sdcommon.build(arcadia_root, kikimr_stable)
        sdcommon.build(arcadia_root, kikimr_driver)
        sdcommon.build_rthub_package(arcadia_root, local_rthub_path, "turbo-parser")
    else:
        sdcommon.download_rthub_data(arcadia_root, local_rthub_path, "turbo-parser", str(num_msg))
        rthub_package_path = sdcommon.find_built_package("rthub")
        try:
            sdcommon.start_ydb(
                arcadia_root,
                local_ydb_path,
                kikimr_driver,
                kikimr_working_dir,
                kikimr_stable_libs
            )

            _make_test_data(arcadia_root,
                            local_rthub_path,
                            rthub_package_path,
                            "data/pq",
                            "rthub--only-turbo-pages",
                            {'endpoint': endpoint, 'database': database},
                            {'endpoint': _local_kikimr_endpoint(kikimr_working_dir),
                             'database': "/local"})
        finally:
            pass
            sdcommon.stop_ydb(
                arcadia_root,
                local_ydb_path,
                kikimr_driver,
                kikimr_working_dir,
                kikimr_stable_libs
            )


if __name__ == '__main__':
    main()
