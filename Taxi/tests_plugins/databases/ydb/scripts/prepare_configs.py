import argparse
import pathlib


CONFIG_TPL_DIR = pathlib.Path('/usr/lib/yandex/taxi-ydb-local/etc/ydb/')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--working-dir', required=True)
    parser.add_argument('--grpc-port', required=True, type=int)
    parser.add_argument('--ic-port', required=True, type=int)
    args = parser.parse_args()

    prepare_config_files(args)


def prepare_config_files(args):
    pathlib.Path(args.working_dir).mkdir(parents=True, exist_ok=True)

    # pdisk_path = (
    #    pathlib.Path(args.working_dir)
    #    .joinpath('ydb-local')
    #    .joinpath('testsuite')
    #    .joinpath('pdisk1tmp.data')
    # )

    pdisk_path = 'SectorMap:{pdisk_id}:{max_gb_size}'.format(
        pdisk_id=1, max_gb_size=32,
    )

    subs = {
        'YDB_LOCAL_DATA_PATH': str(pdisk_path),
        'YDB_LOCAL_GRPC_PORT': str(args.grpc_port),
        'YDB_LOCAL_IC_PORT': str(args.ic_port),
    }

    prepare_config_file('bs_format.txt', args.working_dir, subs)
    prepare_config_file('grpc.txt', args.working_dir, subs)
    prepare_config_file('names.txt', args.working_dir, subs)
    prepare_config_file('bs_config.txt', args.working_dir, subs)


def prepare_config_file(file_name, working_dir, format_options):
    in_path = str(CONFIG_TPL_DIR.joinpath(file_name + '.tpl'))
    out_path = str(pathlib.Path(working_dir).joinpath(file_name))

    with open(in_path, 'r') as in_file:
        data = in_file.read()
    with open(out_path, 'w') as out_file:
        out_file.write(data.format(**format_options))


if __name__ == '__main__':
    main()
