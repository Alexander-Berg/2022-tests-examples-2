# pylint: disable=C0103
import argparse
import sys

import yaml

MONGO_ADDRESS = 'localhost:27217'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--userver-config',
        help='Path to userver base config file.',
        required=True,
    )
    parser.add_argument(
        '--userver-config-vars',
        help='Path to userver config vars file.',
        required=True,
    )
    parser.add_argument(
        '--userver-bootstrap-config',
        help='Path to userver bootstrap file.',
        required=True,
    )
    parser.add_argument(
        '--userver-fallbacks-config',
        help='Path to userver fallbacks file.',
        required=True,
    )
    parser.add_argument(
        '--userver-config-fs-cache',
        help='Path to config FS cache',
        required=True,
    )
    parser.add_argument(
        '--secdist', help='Path to secdist file.', required=True,
    )
    parser.add_argument('-o', '--output', help='Path to output file.')
    args = parser.parse_args()

    with open(args.userver_config) as fp:
        userver_config = yaml.safe_load(fp)

    userver_config['config_vars'] = args.userver_config_vars
    components = userver_config['components_manager']['components']

    tests_control = components['tests-control']
    tests_control['load-enabled'] = True

    for logger_name, logger in components['logging']['loggers'].items():
        logger['file_path'] = (
            '@stderr' if logger_name == 'default' else '@null'
        )

    components['secdist']['config'] = args.secdist

    components['dynamic-config'][
        'bootstrap-path'
    ] = args.userver_bootstrap_config
    components['dynamic-config'][
        'fs-cache-path'
    ] = args.userver_config_fs_cache

    client_upater = components['dynamic-config-client-updater']
    client_upater['fallback-path'] = args.userver_fallbacks_config

    output_data = yaml.safe_dump(userver_config, default_flow_style=False)
    if args.output is None:
        sys.stdout.write(output_data)
    else:
        with open(args.output, 'w') as fp:
            fp.write(output_data)


if __name__ == '__main__':
    main()
