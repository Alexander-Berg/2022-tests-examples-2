#!/usr/bin/env python3

import make_utils


def main():
    proc = make_utils.run_process(
        proc_args=[
            'docker-compose',
            'run',
            '-T',
            '--no-deps',
            '--rm',
            'grocery-tests',
        ],
        stderr_to_stdout=True,
    )

    if proc.returncode:
        make_utils.run_process(proc_args=['docker', 'ps', '-a'])

        bad_docker_info = make_utils.get_bad_docker_info()
        if bad_docker_info:
            make_utils.report_error(
                'Tests run failed. Containers in bad state. '
                + str(bad_docker_info),
            )
        else:
            # Probably some test failed.
            # Nothing to report here.
            pass
        exit(1)


if __name__ == '__main__':
    main()
