import os.path


def pytest_addoption(parser):
    parser.addoption(
        '--configs-dir',
        default=os.path.join(
            os.path.dirname(__file__), os.pardir, os.pardir,
            'infra-cfg-graphs', 'dorblu',
        ),
        help='Path to directory containing yaml configs for dorblu.'
    )


def pytest_generate_tests(metafunc):
    if 'config_file_path' in metafunc.fixturenames:
        parameters = []
        graphs_dir = metafunc.config.getoption('--configs-dir')
        for dir_path, _, file_names in os.walk(graphs_dir):
            for file_name in file_names:
                if file_name.endswith('.yaml'):
                    parameters.append(os.path.join(dir_path, file_name))
        metafunc.parametrize('config_file_path', parameters)
