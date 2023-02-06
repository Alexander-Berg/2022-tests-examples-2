from argparse import ArgumentParser
import yt.wrapper as yt
import logging
from os.path import join as pj


SAMPLE_DATA_COUNT = 35000
STATE = '20170712-000000-000000'
FAVICON_PREFIX = '//home/favicon-robot'
HOST_EXPORT_NAME = 'HostExportFavicon_1'
IMAGE_EXPORT_NAME = 'ImageExportFavicon_1'


def sample_mapper(record):
    host_export_record = {
        '@table_index': 0,
        'key': record['Scheme'] + record['Host'],
        'Host': record['Host']
    }
    yield host_export_record

    url_export_record = {
        '@table_index': 1,
        'key': record['Url']
    }
    yield url_export_record

    joined_export_record = {
        '@table_index': 2,
        'Host': record['Scheme'] + record['Host'],
        'Url': record['Url']
    }
    yield joined_export_record

    # selected_record
    record['@table_index'] = 3
    yield record


def host_join_reducer(key, records):
    host = None
    value = None
    for record in records:
        if record['@table_index'] == 0:
            host = record['Host']
        if host and record['@table_index'] == 1:
            value = record['value']
    if host and value:
        yield {
            'key': host,
            'value': value
        }


def image_join_reducer(key, records):
    result = {}
    found_in_sample = False
    for record in records:
        if record['@table_index'] == 0:
            found_in_sample = True
        if found_in_sample and record['@table_index'] == 1:
            result['key'] = record['key']
            result['value'] = record['value']
    if result:
        yield result


def mirrors_reducer(key, records):
    found_in_sample = False
    for record in records:
        if record['@table_index'] == 0:
            found_in_sample = True
        if found_in_sample and record['@table_index'] == 1:
            record['@table_index'] = 0
            yield record


class TestGenerator(object):
    def gen(self, yt_dir):
        # creates 'tables_data' dir in yt_dir with required data for test-integration

        # TODO: support scheme, remove 'PRAGMA inferscheme;' from yql_templates,
        # add data for support error metrics

        # to avoid AttributeError: 'module' object has no attribute 'openssl_md_meth_names'
        # look https://wiki.yandex-team.ru/yt/userdoc/pythonwrapper/#primeryfiltraciimodulejj
        yt.config['pickling']['module_filter'] = lambda module: 'hashlib' not in getattr(module, '__name__', '')

        selected = pj(FAVICON_PREFIX, pj('Base', pj('_prod', 'selected')))
        yt_host_exports_dir = pj(FAVICON_PREFIX, pj('exports', 'host'))
        yt_image_exports_dir = pj(FAVICON_PREFIX, pj('exports', 'image'))
        mirrors = None
        for table in yt.list(pj(FAVICON_PREFIX, pj('Base', '_prod')), absolute=True):
            if table.find('mirrors') != -1:
                mirrors = table
        if not mirrors:
            raise Exception('no mirrors table found in Base/_prod')

        selected_count = yt.get_attribute(selected, 'row_count')
        sampling_rate = float(SAMPLE_DATA_COUNT) / float(selected_count)
        spec = {
            "job_io": {
                'table_reader': {
                    'sampling_rate': sampling_rate
                }
            }
        }
        host_sample = pj(yt_dir, 'host_sample')
        url_sample = pj(yt_dir, 'url_sample')
        joined_sample = pj(yt_dir, 'joined_sample')
        selected_sample = pj(yt_dir, 'selected_sample')

        yt.run_map(sample_mapper, selected, [host_sample, url_sample, joined_sample, selected_sample], spec=spec,
                   format=yt.YsonFormat(control_attributes_mode="row_fields"))
        yt.run_sort(selected_sample, sort_by=["Host", "TargetSize"])

        joined_host_exports = pj(yt_dir, 'joined_host_exports')
        joined_image_exports = pj(yt_dir, 'joined_image_exports')

        yt.run_merge(yt.list(yt_host_exports_dir, absolute=True), joined_host_exports)
        yt.run_merge(yt.list(yt_image_exports_dir, absolute=True), joined_image_exports)

        yt.run_sort(joined_host_exports, sort_by=['key'])
        yt.run_sort(joined_image_exports, sort_by=['key'])
        yt.run_sort(host_sample, sort_by=['key'])
        yt.run_sort(url_sample, sort_by=['key'])

        result_host_exports = pj(yt_dir, HOST_EXPORT_NAME)
        result_image_exports = pj(yt_dir, IMAGE_EXPORT_NAME)
        yt.run_reduce(host_join_reducer, [host_sample, joined_host_exports], result_host_exports, reduce_by=['key'],
                      format=yt.YsonFormat(control_attributes_mode="row_fields"))
        yt.run_reduce(image_join_reducer, [url_sample, joined_image_exports], result_image_exports, reduce_by=['key'],
                      format=yt.YsonFormat(control_attributes_mode="row_fields"))

        yt.run_sort(mirrors, sort_by=['Host'])
        yt.run_sort(joined_sample, sort_by=['Host'])
        mirrors_sample = pj(yt_dir, 'mirrors')
        yt.run_reduce(mirrors_reducer, [joined_sample, mirrors], mirrors_sample, reduce_by=['Host'],
                      format=yt.YsonFormat(control_attributes_mode="row_fields"))

        # prepare directory 'tables_data'
        tables_data = pj(yt_dir, 'tables_data')
        if yt.exists(tables_data):
            yt.remove(tables_data, recursive=True)
        yt.create('map_node', tables_data)

        yt.copy(result_host_exports, pj(tables_data, pj('exports', pj('host', HOST_EXPORT_NAME))), recursive=True)
        yt.copy(result_image_exports, pj(tables_data, pj('exports', pj('image', IMAGE_EXPORT_NAME))), recursive=True)

        # check '_trunk' tag and link after that
        manual_tables = ['link', 'image', 'link.startrek', 'image.startrek']
        for manual_table in manual_tables:
            yt.copy(pj(FAVICON_PREFIX, pj('Manual', pj('_trunk', manual_table))),
                    pj(tables_data, pj('Manual', pj(STATE, manual_table))),
                    recursive=True)

        # for test copy mirrors table in favicon-robot
        yt.copy(mirrors_sample, pj(tables_data, 'mirrors'))

        # check '_prod' tag and link after that
        yt.copy(selected_sample, pj(tables_data, pj('Base', pj(STATE, 'selected'))), recursive=True)
        yt.create('table', pj(tables_data, pj('Base', pj(STATE, 'smushables'))), recursive=True)

        # check data_spec json and all attributes after generating test_data and replace sandbox resource for the test


if __name__ == '__main__':
    _LOG_FORMAT = '%(asctime)s [%(threadName)s] [%(levelname)s]  %(message)-100s'
    logging.basicConfig(level=logging.INFO, format=_LOG_FORMAT)

    parser = ArgumentParser()
    parser.add_argument('--yt-dir', required=True)  # yt working dir

    args = parser.parse_args()

    TestGenerator().gen(args.yt_dir)

    # EXAMPLE:
    # python robot/favicon/tests/data_generator.py --yt-dir //home/jupiter-dev/pkholkin/favicon-test-data
    # use these tables and pack them into tables-data.tar for sb resource, follow the format carefully
