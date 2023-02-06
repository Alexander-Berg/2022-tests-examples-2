import os


def test_cron_scripts_executable():
    scripts_dir = os.path.join(
        os.environ['SRC_ROOT'],
        'configs',
        'cron_scripts'
    )
    for script_name in os.listdir(scripts_dir):
        script_path = os.path.join(scripts_dir, script_name)
        print(script_path)
        assert os.path.isfile(script_path), \
            f'Script {script_path} should be file'
        assert os.access(script_path, os.X_OK), \
            f'File is not executable {script_path}'
