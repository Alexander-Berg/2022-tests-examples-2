import os
import shutil
import subprocess

import sys

import logs_tool as logs
import app_tool

QUASAR_ID_FOR_BUILDS_IN_TEAMCITY = '2a269aaa98724c64dca4-emulator'
QUASAR_ID_WITH_PROD_DROIDEKA = '2a269aaa98724c64dca4-emulator-prod'
DEFAULT_CENTAUR_DEVICE_ID = 'centaur_emulator_ci_01'
MARATHON_VERSION = '0.7.3'
# https://yav.yandex-team.ru/secret/sec-01fsrr8cgn5tq5bref1fecnx43
SECRET_ID = 'sec-01fsrr8cgn5tq5bref1fecnx43'
accounts_tus_uid = {"yndx-module-free": '1598872777',
                    "yndx-emulator-free": '1598911125',
                    "yndx-centaur-free": '1598980843',
                    "r4t552": '1427288149'}


def init_build_config(input_args):
    app_paths = app_tool.get_app_paths()
    config = {"android_home": os.getenv('ANDROID_HOME'),
              "build_number": os.getenv('BUILD_NUMBER'),
              "branch": input_args.branch,
              "teamcity_version": os.getenv('TEAMCITY_VERSION'),
              "path": os.getenv('PATH'),
              "testpalm_token": input_args.testpalm_token,
              "testpalm_report": input_args.testpalm_report,
              "serial_number": input_args.serial_number,
              "kolhoz_token": input_args.kolhoz_token,
              "kolhoz_device_id": input_args.kolhoz_device_id,
              "yav_token": os.getenv('ROBOT_YAV_TOKEN'),
              "signer_token": input_args.signer_token,
              "tus_token": input_args.tus_token,
              "is_sign_apps": input_args.is_sign_apps,
              "ya_login": input_args.ya_login,
              "ya_pass": input_args.ya_pass,
              "test_suite": input_args.test_suite,
              "test_class": input_args.test_class,
              "emulator_only": input_args.emulator_only,
              "emulator_api": input_args.emulator_api,
              "emulator_resolution": input_args.emulator_resolution,
              "delete_emulator": input_args.delete_emulator,
              "product": input_args.product,
              "centaur_device_id": input_args.centaur_device_id,
              "quasar_id": input_args.quasar_id,
              "localhost_url": 'http://localhost:8888',
              "droideka_url": input_args.droideka_url,
              "skip_build_services": input_args.skip_build_services,
              "skip_build_video_player": input_args.skip_build_video_player,
              "skip_build_updater": input_args.skip_build_updater,
              "skip_download_apps": input_args.skip_download_apps,
              "marathon_version": MARATHON_VERSION,
              "marathon_prefix_path": '../../..',
              "artifacts_home_path": 'tv/ci/ui-tests/build',
              "quasar_daemons_folder_path": 'tv/ci/ui-tests/build/quasar_bin/quasar'}

    config = dict(list(config.items()) + list(os.environ.items()))

    # init signer_token
    if config["is_sign_apps"] == 'true':
        if config["signer_token"] == 'NONE':
            token = get_signer_token()
            YANDEX_SIGNER_OAUTH = token
            config["signer_token"] = token
        else:
            YANDEX_SIGNER_OAUTH = config["signer_token"]

    # init serial_number
    if '.' in config["serial_number"]:
        config["serial_number"].replace(config["serial_number"], f'{config["serial_number"]}:5555')

    if config["teamcity_version"] == '' or config["teamcity_version"] is None:
        config["teamcity_version"] = 'NONE'
        config["is_teamcity"] = 'false'
        config["emulator_property"] = '-no-snapshot -partition-size 2048'
        config["emulator_resolution"] = '720'
        config['test_fail_retry_quantity'] = '0'
        config['uncompleted_test_retry_quantity'] = '0'
    else:
        config["is_teamcity"] = 'true'
        config["emulator_property"] = '-no-window -no-snapshot -no-boot-anim -partition-size 2048'
        config['test_fail_retry_quantity'] = '1'
        config['uncompleted_test_retry_quantity'] = '1'

    # init branch
    if config["branch"] == '<default>':
        config["branch"] = 'trunk'
    if 'releases/smart_devices' in config["branch"]:
        config["branch_for_download_apps"] = f'tv_apps_arcadia_branch:{config["branch"]}'
    else:
        config["branch_for_download_apps"] = f'tv_apps_arcadia_branch:trunk'

    # Increment value for fix error INSTALL_FAILED_VERSION_DOWNGRADE
    if config["build_number"] == '' or config["build_number"] is None:
        config["build_number"] = '30000777'
    else:
        config["build_number"] = str(int(config["build_number"]) + 30000000)

    # check if emulator
    if config["kolhoz_device_id"] == 'NONE' and config["serial_number"] == 'NONE':
        config["is_emulator"] = 'true'
    else:
        config["is_emulator"] = 'false'

    # init quasar_id
    if config["emulator_only"] == 'true' and config["quasar_id"] == 'NONE':
        config["quasar_id"] = QUASAR_ID_WITH_PROD_DROIDEKA
    elif os.getenv('QUASAR_ID') != '' and os.getenv('QUASAR_ID') is not None:
        config["quasar_id"] = os.getenv('QUASAR_ID')
    else:
        config["quasar_id"] = QUASAR_ID_FOR_BUILDS_IN_TEAMCITY

    # init centaur_device_id
    if config["centaur_device_id"] == 'NONE':
        config["centaur_device_id"] = DEFAULT_CENTAUR_DEVICE_ID

    # init kolhoz_token
    if config["kolhoz_token"] == 'NONE':
        config["kolhoz_token"] = os.getenv('KOLHOZ_TOKEN')

    # init tus_token
    if config["tus_token"] == 'NONE':
        config["tus_token"] = get_secret('test_user_service', config)

    # init testpalm_token
    if config["testpalm_token"] == 'NONE':
        config["testpalm_token"] = os.getenv('TESTPALM_TOKEN')

    # init marathon parameters for product
    config['test_filter_type'] = 'NONE'
    if config["product"] == 'centaur':
        config["tus_account_uid"] = accounts_tus_uid['yndx-centaur-free']
        config["package_name"] = 'ru.yandex.quasar.centaur_app'
        config['marathon_output_dir'] = os.path.join(config["marathon_prefix_path"],
                                                     'centaur-app/build/reports/marathon')

        config['main_app_path'] = os.path.join(config["marathon_prefix_path"],
                                               app_paths["CentaurApp"]["main_app_path"])
        config['test_app_path'] = os.path.join(config["marathon_prefix_path"],
                                               app_paths["CentaurApp"]["test_app_path"])
        config['test_fail_retry_quantity'] = '0'
    elif config["product"] == 'station':
        config["tus_account_uid"] = accounts_tus_uid['r4t552']
        config["package_name"] = 'ru.yandex.quasar.app'
        config['marathon_output_dir'] = os.path.join(config["marathon_prefix_path"],
                                                     'quasar-app/build/reports/marathon')

        if config["is_emulator"] == 'true':
            main_app_path = os.path.join(config["marathon_prefix_path"],
                                         app_paths["QuasarApp"]["main_app_path_x86"])
            test_app_path = os.path.join(config["marathon_prefix_path"],
                                         app_paths["QuasarApp"]["test_app_path_x86"])
        else:
            main_app_path = os.path.join(config["marathon_prefix_path"],
                                         app_paths["QuasarApp"]["main_app_path_v7"])
            test_app_path = os.path.join(config["marathon_prefix_path"],
                                         app_paths["QuasarApp"]["test_app_path_v7"])

        config['main_app_path'] = main_app_path
        config['test_app_path'] = test_app_path
        config['test_fail_retry_quantity'] = '0'
    elif config["product"] == 'tv-services':
        config["tus_account_uid"] = accounts_tus_uid['yndx-emulator-free']
        config["package_name"] = 'com.yandex.tv.services.testapp'
        config['marathon_output_dir'] = os.path.join(config["marathon_prefix_path"],
                                                     'tv/services/test-app-client',
                                                     'build/reports/marathon')
        config['test_filter_type'] = "package"
        config['test_filter_value'] = "com.yandex.tv.services.testapp"
        config['main_app_path'] = os.path.join(config["marathon_prefix_path"],
                                               'tv/services/test-app-client/build/outputs/apk',
                                               'debug/test-app-client-debug.apk')
        config['test_app_path'] = os.path.join(config["marathon_prefix_path"],
                                               'tv/services/test-app-client/build/outputs/apk',
                                               'androidTest/debug',
                                               'test-app-client-debug-androidTest.apk')
    elif config["product"] == 'tv-updater':
        config["tus_account_uid"] = accounts_tus_uid['yndx-emulator-free']
        config["package_name"] = 'com.yandex.launcher.updaterapp.ui'
        config['marathon_output_dir'] = os.path.join(config["marathon_prefix_path"],
                                                     'tv/updater-app/app/build/reports/marathon')
        config['test_filter_type'] = 'package'
        config['test_filter_value'] = 'com.yandex.launcher.updaterapp.ui'

        config['main_app_path'] = os.path.join(config["marathon_prefix_path"],
                                               'tv/updater-app/app/build/outputs/apk',
                                               'localTvTestUiLogged/debug',
                                               f'tv-updater-app-v2.1000.1000.'
                                               f'tvTest-b{config["build_number"]}-local-tvTest-'
                                               f'ui-logged-debug.apk')
        config['test_app_path'] = os.path.join(config["marathon_prefix_path"],
                                               'tv/updater-app/app/build/outputs/apk',
                                               'androidTest/localTvTestUiLogged/debug',
                                               'app-local-tvTest-ui-logged-debug-androidTest.apk')
    else:
        config["tus_account_uid"] = accounts_tus_uid['yndx-emulator-free']
        config["package_name"] = 'com.yandex.tv.home'
        config['marathon_output_dir'] = os.path.join(config["marathon_prefix_path"],
                                                     'tv/home-app/app/build/reports/marathon')
        config['main_app_path'] = os.path.join(config["marathon_prefix_path"],
                                               'tv/home-app/app/build/outputs/apk/debug',
                                               f'tv-home-app-v2.1000.1000-'
                                               f'b{config["build_number"]}-debug.apk')
        config['test_app_path'] = os.path.join(config["marathon_prefix_path"],
                                               'tv/home-app/app/build/outputs/apk',
                                               'androidTest/debug/app-debug-androidTest.apk')

    # init test filter for marathon
    if config['test_filter_type'] != 'package':
        if config["test_class"] == 'NONE':
            config['test_filter_type'] = 'annotation'
            config['test_filter_value'] = \
                f'com.yandex.tv.common.utility.ui.tests.suites.{config["test_suite"]}'
        elif '#' not in config["test_class"]:
            config['test_filter_type'] = 'fully-qualified-class-name'
            config['test_filter_value'] = f'{config["package_name"]}.{config["test_class"]}'
        else:
            config['test_filter_type'] = 'fully-qualified-test-name'
            config['test_filter_value'] = f'{config["package_name"]}.{config["test_class"]}'

    # init yandex password
    if config["ya_login"] == 'NONE' or config["ya_pass"] == 'NONE':
        import tus_client
        tus_client.init_account(config)

    # init NoneType objects
    for i in config.keys():
        if config[i] is None:
            config[i] = 'NONE'

    return config


def get_signer_token():
    if os.getenv('YANDEX_SIGNER_OAUTH') != '' and os.getenv('YANDEX_SIGNER_OAUTH') is not None:
        return os.getenv('YANDEX_SIGNER_OAUTH')
    else:
        home_path = os.path.expanduser('~')
        props_path = home_path + '/.yandex/yandex-signer.properties'
        print('SIGNER_TOKEN not provided, trying to take value from local yandex-signer.properties')
        if os.path.isfile(props_path):
            with open(props_path, 'r') as file:
                token = file.read().replace('\n', '')
                return token.rsplit('=', 1)[1].rstrip()
        else:
            print('Error! Please provide SIGNER_TOKEN in yandex-signer.properties!')
            print('https://wiki.yandex-team.ru/yandexmobile/techdocs/mobbuild/'
                  'yandex-signer/#kakukazattoken')
            sys.exit(1)


def get_secret(key, config):
    if config["is_teamcity"] == 'true':
        return subprocess.getoutput(f'yav get version {SECRET_ID} '
                                    f'-o {key} '
                                    f'--oauth {config["yav_token"]}')
    else:
        return subprocess.getoutput(f'yav get version {SECRET_ID} -o {key}')


def print_env(config):
    logs.echo_title('Build config')
    java_version = subprocess.getoutput('java -version')
    print(f'JAVA_VERSION:\n{java_version}')
    print(f'PYTHON - {sys.version}')
    for i in config.keys():
        if 'token' not in i and 'TOKEN' not in i and i != 'ya_pass':
            print(f'{i} - {config[i]}')
    if config["is_teamcity"] == 'false':
        check_marathon_version(MARATHON_VERSION)


def check_marathon_version(version):
    actual_version = subprocess.getoutput('marathon -v')
    if version not in actual_version:
        logs.echo_title(f'Install marathon v{version}')
        marathon_folder_path = os.path.join(os.getenv("HOME"), 'Android')
        if not os.path.exists(marathon_folder_path):
            os.system(f'mkdir {marathon_folder_path}')
        download_url = f'https://github.com/MarathonLabs/marathon/releases/' \
                       f'download/{version}/marathon-{version}.zip'
        os.system(f'curl -L  {download_url} -o marathon.zip')
        os.system(f'unzip -qq marathon.zip -d marathon')
        os.system(f'mv marathon/marathon-{version} {marathon_folder_path}/')
        os.system(f'rm marathon.zip')
        os.system(f'rm -rf marathon')

        logs.echo_title(f'Please create symlink for execute marathon')
        print(f'sudo ln -s {marathon_folder_path}/marathon-{version}/bin/marathon '
              f'/usr/bin/marathon\n')
        sys.exit(1)


def check_apksigner():
    status = subprocess.getoutput('apksigner | grep EXAMPLE')
    if 'EXAMPLE' not in status:
        logs.echo_title(f'apksigner not found in environment')
        list_of_installed_build_tools = subprocess.getoutput("sdkmanager --list_installed | grep "
                                                             "build-tools | awk '{print $1}'")
        if list_of_installed_build_tools == '':
            print('Please install build-tools for use apksigner')
            print('command: yes | sdkmanager "build-tools;33.0.0"\n')
            print('And add path to .bashrc')
            print('export PATH=${PATH}:$ANDROID_HOME/build-tools/33.0.0')
            sys.exit(1)
        else:
            print('List of installed build_tools:\n')
            print(list_of_installed_build_tools)
            print('\nSelect any installed version and add path to .bashrc')
            print('export PATH=${PATH}:$ANDROID_HOME/build-tools/YOUR_VERSION\n')
            sys.exit(1)


def check_avd_manager():
    status = subprocess.getoutput('avdmanager | grep Usage')
    if 'Usage' not in status:
        logs.echo_title(f'avdmanager not found in environment')
        installation_status_of_cmdline_tools = subprocess.getoutput(
            "sdkmanager --list_installed | grep cmdline")
        if installation_status_of_cmdline_tools == '':
            print('Please install cmdline-tools for use avdmanager')
            print('command: yes | sdkmanager "cmdline-tools;latest"\n')
            print('And add path to .bashrc')
            print('export PATH=${PATH}:$ANDROID_HOME/cmdline-tools/latest/bin\n')
            sys.exit(1)
        else:
            print('cmdline-tools is already installed:')
            print(installation_status_of_cmdline_tools)
            print('\nPlease add path to .bashrc')
            print('export PATH=${PATH}:$ANDROID_HOME/cmdline-tools/latest/bin\n')
            sys.exit(1)


def generate_allure_report(is_teamcity):
    if is_teamcity == 'true':
        logs.echo_title('Generate allure report')
        report_dir = 'tv/home-app/app/build/reports/marathon/allure-report'
        subprocess.run(f'''allure generate tv/home-app/app/build/reports/marathon/allure-results \
            -o {report_dir}''', shell=True)
        shutil.make_archive(report_dir, 'zip', os.path.dirname(report_dir),
                            os.path.basename(report_dir))
        os.system(f'rm -rf {report_dir}')
