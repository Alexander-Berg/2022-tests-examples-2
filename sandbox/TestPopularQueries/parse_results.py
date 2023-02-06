import json
import inspect
import argparse
from yt import wrapper as yw
import features as response_features


class SoyOutputParser:
    def __init__(self, features):
        self.features = features

    def __call__(self, row):
        result = {'id': row['id'], 'ReqId': row['ReqId']}
        try:
            dump = json.loads(row['FetchedResult'])
            if 'tmpl_data' in dump:
                dump = dump['tmpl_data']
            features = json.loads(row['userdata'])['check_features']
            for feature in features:
                result.update(self.features[feature](dump))
            yield yw.create_table_switch(0)
            yield result
        except (ValueError, KeyError, AttributeError) as e:
            row['Cause'] = repr(e)
            yield yw.create_table_switch(1)
            yield row


def main(args):
    yw.config['pickling']['python_binary'] = '/skynet/python/bin/python'
    features = dict(inspect.getmembers(response_features, callable))
    yw.run_map(
        SoyOutputParser(features),
        args.input_path,
        [yw.ypath_join(args.output_dir, args.table_name), yw.ypath_join(args.error_dir, args.table_name)],
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get features from SoY output')
    parser.add_argument('--input-path', required=True, help='SoY output table')
    parser.add_argument('--output-dir', required=True, help='Results dir')
    parser.add_argument('--error-dir', help='Error dir')
    parser.add_argument('--table-name', required=True)
    args = parser.parse_args()
    if not args.error_dir:
        args.error_dir = '{}_err'.format(args.output_dir)
    main(args)
