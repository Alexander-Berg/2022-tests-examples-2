#!/usr/bin/env python3
import argparse

import get_services
import make_utils


DOCKER_COMPOSE = 'docker-compose.yml'


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--service',
        type=str,
        required=False,
        default='',
        help='Load only necessary images for the service',
    )
    parser.add_argument(
        'docker_compose',
        default=[DOCKER_COMPOSE],
        type=str,
        nargs='*',
        metavar='DOCKER_FILE',
        help='Path to docker-compose.yml to be processed',
    )
    return parser.parse_args()


def main():
    print('Pull new images')

    args = parse_args()
    if args.service:
        services = get_services.load_services_recursively(
                        args.service,
                        docker_compose_files=args.docker_compose,
        )
    else:
        services = get_services.load_services(args.docker_compose)

    image_url_by_name = {}
    for name, params in get_services.iter_images(services):
        image_url_by_name[name] = get_services.prepare_image(params['image'])

    images_to_pull = []
    for image_name, image_url in image_url_by_name.items():
        images_proc = make_utils.run_docker(
            proc_args=['images', '-q', image_url], pipe_stdout=True,
        )

        if images_proc.returncode:
            # Not a reason to fail. Simply print
            # proc output back to stdout.
            print(images_proc.stdout)
        elif images_proc.stdout == '':
            images_to_pull.append(image_name)
        else:
            # Image already pulled -- do nothing.
            pass

    if images_to_pull:
        pull_proc = make_utils.run_docker_compose(
            args.docker_compose,
            proc_args=[
                'pull',
                '--parallel',
                '--ignore-pull-failures',
            ]
            + images_to_pull,
            stderr_to_stdout=True,
        )

        if pull_proc.returncode:
            make_utils.report_error('Error pulling new images')
            exit(1)

    print('Pull done')


if __name__ == '__main__':
    main()
