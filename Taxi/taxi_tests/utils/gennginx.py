import argparse
import os
import string
import sys


class CustomTemplate(string.Template):
    delimiter = '%'


CONFIG_TPL_FILENAME = 'nginx.conf.in'
SERVICE_TPL_FILENAME = 'nginx_service.conf.in'
TEMPLATE_FILENAME = 'nginx.conf.tpl'


def _parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='Commands')

    create_parser = subparsers.add_parser(
        'create', help='Create nginx config template',
    )
    create_parser.set_defaults(mode='create', required=True)
    create_parser.add_argument(
        '-i', '--input-dir',
        help='Directory, that contains nginx.conf.in and nginx '
             'services.conf.in templates',
        required=True,
    )
    create_parser.add_argument(
        '-o', '--output-dir',
        help='Path to output directory',
        required=True,
    )
    create_parser.add_argument(
        '-b', '--nginx-build-dir',
        help='Root nginx build and config files directory, typically '
             'build/nginx',
        required=True,
    )
    create_parser.add_argument(
        '-s', '--services',
        help='List of services, aimed to be generated in configs',
        nargs='+',
        required=True,
    )

    substitute_parser = subparsers.add_parser(
        'substitute',
        help='Prepare nginx config from generated by this script template',
    )
    substitute_parser.set_defaults(mode='substitute')
    substitute_parser.add_argument(
        'template',
        help='Path to generated by this script nginx config template',
    )
    substitute_parser.add_argument(
        '-o', '--output-dir',
        help='Path to output directory',
        required=True,
    )
    substitute_parser.add_argument(
        '-p', '--port',
        help='Port for listen by nginx',
        default=8009,
    )
    substitute_parser.add_argument(
        '-w', '--worker-id',
        help='Worker id (for running with XDist)',
        default='master',
    )

    args = parser.parse_args()

    if not hasattr(args, 'mode'):
        parser.print_help()
        sys.exit(0)

    return args


def _substitute_services(services, template, context):
    res = ''
    for service in services:
        res += CustomTemplate(template).substitute(
            context, SERVICE_NAME=service,
        )
    return res


def _construct_output_filename(output_dir):
    config_filename, _ = os.path.splitext(TEMPLATE_FILENAME)
    return os.path.join(output_dir, config_filename)


def create_nginx_template(input_dir, output_dir, nginx_build_dir, services):
    if not services:
        raise ValueError('Services list cannot be empty.')

    with open(os.path.join(input_dir, CONFIG_TPL_FILENAME), 'r') as fconf:
        nginx_conf = fconf.read()

    with open(os.path.join(input_dir, SERVICE_TPL_FILENAME), 'r') as fsrvs:
        nginx_srvs = fsrvs.read()

    context = {
        'OUTPUT_DIR': nginx_build_dir,
        'INPUT_DIR': input_dir,
        'PORT': '@@PORT@@',
        'WORKER_SUFFIX': '@@WORKER_SUFFIX@@',
    }
    serv_gen = _substitute_services(services, nginx_srvs, context)

    context['NGINX_SERVICES'] = serv_gen
    nginx_conf = CustomTemplate(nginx_conf).substitute(context)

    output_filepath = os.path.join(output_dir, TEMPLATE_FILENAME)
    with open(output_filepath, 'w') as fconfig:
        fconfig.write(nginx_conf)


def process_template(template, output_dir, port, worker_id):
    with open(template, 'r') as ftemplate:
        template = ftemplate.read()

    worker_suffix = '_' + worker_id if worker_id != 'master' else ''
    output_filepath = _construct_output_filename(output_dir)

    config = template
    config = config.replace('@@PORT@@', str(port))
    config = config.replace('@@WORKER_SUFFIX@@', worker_suffix)

    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
    with open(output_filepath, 'w') as fconf:
        fconf.write(config)


def main():
    args = _parse_args()

    if args.mode == 'create':
        create_nginx_template(
            input_dir=args.input_dir,
            output_dir=args.output_dir,
            nginx_build_dir=args.nginx_build_dir,
            services=args.services,
        )
    else:
        process_template(
            template=args.template,
            output_dir=args.output_dir,
            port=args.port,
            worker_id=args.worker_id,
        )


if __name__ == '__main__':
    main()