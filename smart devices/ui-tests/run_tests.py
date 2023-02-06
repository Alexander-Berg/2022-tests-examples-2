import argparse
import subprocess

import sys

import app_tool
import device
import emulator
import logs_tool as logs
import utils

parser = argparse.ArgumentParser()
# env:
parser.add_argument('--branch', metavar='Var', type=str, default='trunk',
                    help='Branch for build apps')
parser.add_argument('--signer_token', metavar='Var', type=str, default='NONE', help='Signer token')
parser.add_argument('--tus_token', metavar='Var', type=str, default='NONE', help='TUS token')
parser.add_argument('--testpalm_token', metavar='Var', type=str, default='NONE',
                    help='Testpalm token')

# options for tests:
parser.add_argument('--droideka_url', metavar='Var', type=str,
                    default='https://droideka.smarttv.yandex.net',
                    help='API url: prod, prestable, testing')
parser.add_argument('--ya_login', metavar='Var', type=str, default='NONE',
                    help='Login for yandex account in tests')
parser.add_argument('--ya_pass', metavar='Var', type=str, default='NONE',
                    help='Password for yandex account in tests')
parser.add_argument('--test_suite', metavar='Var', type=str, default='Acceptance',
                    help='Acceptance, Regression, DroidekaRegression, '
                         'ModuleRegression, UpdaterAcceptance, ServicesSdkTests')
parser.add_argument('--test_class', metavar='Var', type=str, default='NONE',
                    help='For run all tests in class > provide class name. '
                         'Example: SearchScreen. '
                         'For run only one test > provide test name. '
                         'Example: SearchScreen#checkAllElements')
parser.add_argument('--testpalm_report', metavar='Var', type=str, default='false',
                    help='Send report to testpalm')
parser.add_argument('--centaur_device_id', metavar='Var', type=str,
                    default='NONE',
                    help='Centaur device id')
parser.add_argument('--product', metavar='Var', type=str, default='tv',
                    help='tv, station, centaur, tv-updater, tv-services')

# emulator:
parser.add_argument('--emulator_api', metavar='Var', type=str, default='25',
                    help='Android API for start emulator')
parser.add_argument('--emulator_resolution', metavar='Var', type=str, default='1080',
                    help='Emulator resolution. 1080 for use 1920x1080 and 720 for use 1280x720')

# kolhoz:
parser.add_argument('--kolhoz_token', metavar='Var', type=str, default='NONE', help='Kolhoz token')
parser.add_argument('--kolhoz_device_id', metavar='Var', type=str, default='NONE',
                    help='Kolhoz device id')

# real device
parser.add_argument('--serial_number', metavar='Var', type=str, default='NONE',
                    help='Device IP or ID of module')

# for debugging
parser.add_argument('--emulator_only', metavar='Var', type=str, default='false',
                    help='Run emulator with yandex apps')
parser.add_argument('--delete_emulator', metavar='Var', type=str, default='true',
                    help='Stop and delete emulator after tests')
parser.add_argument('--skip_build_services', metavar='Var', type=str, default='false',
                    help='If already built, you can skip this step')
parser.add_argument('--skip_build_updater', metavar='Var', type=str, default='false',
                    help='If already built, you can skip this step')
parser.add_argument('--skip_build_video_player', metavar='Var', type=str, default='false',
                    help='If already built, you can skip this step')
parser.add_argument('--skip_download_apps', metavar='Var', type=str, default='false',
                    help='If already built, you can skip this step')
parser.add_argument('--is_sign_apps', metavar='Var', type=str, default='true',
                    help=f'''Attention! Yandex passport will not work without sign apps.
                         And iosdk don't get the config from quasmodrom.''')
parser.add_argument('--quasar_id', metavar='Var', type=str,
                    default='NONE',
                    help='''You can set your own quasar ID.
                        You need to create a config here:
                        https://quasmodrom-test.quasar-int.yandex-team.ru/admin/development/device/
                        ''')

input_args = parser.parse_args()


def run_sdk_tests_in_services():
    # build test_app
    app_tool.build_services_test_app()
    # build test_app_client
    app_tool.build_services_test_app_client('assembleDebug')
    # build test_app_client with android tests
    app_tool.build_services_test_app_client('assembleDebugAndroidTest')

    # start and prepare emulator
    app_tool.download_apps_for_regression(BUILD_CONFIG)
    serial_number = emulator.run_tv_emulator(BUILD_CONFIG)
    app_tool.push_all_apps_for_regression(serial_number, BUILD_CONFIG)
    app_tool.prepare_and_push_permission_for_enable_brick_mode(serial_number)
    device.reboot(serial_number, None)
    device.root_remount(serial_number)
    app_tool.prepare_and_push_device_owner_for_enable_brick_mode(serial_number)
    device.reboot(serial_number, None)
    device.root_remount(serial_number)
    device.disable_suw(serial_number, 'true')
    device.root_remount(serial_number)
    app_tool.print_installed_apps(serial_number)

    # install test_app
    app_tool.install_services_test_app(serial_number)

    # run tests
    return run_marathon_tests(BUILD_CONFIG)


def run_tests_on_centaur_emulator():
    # build apps
    app_tool.build_centaur_app("assembleDemoX86Debug", BUILD_CONFIG)
    app_tool.build_centaur_app("assembleDemoX86DebugAndroidTest", BUILD_CONFIG)

    # start and prepare emulator
    serial_number = emulator.run_centaur_emulator(BUILD_CONFIG)
    logcat_process, log_file = logs.start_get_logs(serial_number, BUILD_CONFIG["is_teamcity"])

    # run tests
    status = run_marathon_tests(BUILD_CONFIG)

    # get logs
    logs.stop_get_logs(logcat_process, log_file, BUILD_CONFIG["is_teamcity"])
    logs.get_screenshots(serial_number, BUILD_CONFIG["is_teamcity"])
    logs.get_anr_logs(serial_number, BUILD_CONFIG["is_teamcity"])
    return status.returncode


def run_tests_on_station(serial_number):
    # build apps
    app_tool.build_quasar_app("assembleProdV7Debug", BUILD_CONFIG)
    app_tool.build_quasar_app("assembleProdV7DebugAndroidTest", BUILD_CONFIG)

    # prepare device
    device.connect_to_device_if_needed(serial_number, True)
    station_version = device.get_station_version(serial_number, BUILD_CONFIG)
    device.change_logs_buffer(serial_number)
    if station_version == '1':
        device.backup_system_quasar_app_on_station(serial_number, BUILD_CONFIG)

    # run tests
    status = run_marathon_tests(BUILD_CONFIG)

    if station_version == '1':
        device.restore_system_quasar_app_on_station(serial_number, BUILD_CONFIG)

    # get logs
    logs.echo_title('Remove test apps')
    app_tool.uninstall_app(serial_number, 'ru.yandex.quasar.app')
    app_tool.uninstall_app(serial_number, 'ru.yandex.quasar.app.test')
    return status.returncode


def run_tests_on_station_emulator():
    # build apps
    app_tool.build_quasar_app("assembleProdX86Debug", BUILD_CONFIG)
    app_tool.build_quasar_app("assembleProdX86DebugAndroidTest", BUILD_CONFIG)
    app_tool.build_quasar_daemons()

    # sign apps
    app_paths = app_tool.get_app_paths()
    app_tool.sign_app_via_aosp_platform_key(app_paths["QuasarApp"]["main_app_path_x86"])
    app_tool.sign_app_via_aosp_platform_key(app_paths["QuasarApp"]["test_app_path_x86"])

    # run emulator
    serial_number = emulator.run_station_emulator(BUILD_CONFIG)
    logcat_process, log_file = logs.start_get_logs(serial_number, BUILD_CONFIG["is_teamcity"])

    # run tests
    status = run_marathon_tests(BUILD_CONFIG)

    # get logs
    logs.get_quasar_daemons_logs(serial_number)
    device.take_screenshot(serial_number, 'screen_after_tests')
    logs.stop_get_logs(logcat_process, log_file, BUILD_CONFIG["is_teamcity"])
    logs.get_screenshots(serial_number, BUILD_CONFIG["is_teamcity"])
    logs.get_anr_logs(serial_number, BUILD_CONFIG["is_teamcity"])

    return status.returncode


def run_updater_isolated_tests_on_emulator():
    # build apps
    app_tool.build_updater_tests_app("assembleLocalTvTestUiLoggedDebug", BUILD_CONFIG)
    app_tool.build_updater_tests_app("assembleLocalTvTestUiLoggedDebugAndroidTest", BUILD_CONFIG)

    # start and prepare emulator
    serial_number = emulator.run_tv_emulator(BUILD_CONFIG)
    logcat_process, log_file = logs.start_get_logs(serial_number, BUILD_CONFIG["is_teamcity"])
    app_tool.build_and_push_services(serial_number, BUILD_CONFIG)
    device.reboot(serial_number, None)
    device.wait_wifi_connection_on_emulator(serial_number, BUILD_CONFIG["emulator_api"])
    app_tool.print_installed_apps(serial_number)

    # run tests
    status = run_marathon_tests(BUILD_CONFIG)

    # get logs
    logs.stop_get_logs(logcat_process, log_file, BUILD_CONFIG["is_teamcity"])
    logs.get_screenshots(serial_number, BUILD_CONFIG["is_teamcity"])
    logs.get_anr_logs(serial_number, BUILD_CONFIG["is_teamcity"])
    return status.returncode


def run_tests_on_tv_emulator():

    BUILD_CONFIG['gradle_property_for_emulator'] = '-PisTestOnEmulator=true'
    app_tool.build_home_app("assembleDebug", BUILD_CONFIG)
    app_tool.build_home_app("assembleDebugAndroidTest", BUILD_CONFIG)

    serial_number = emulator.run_tv_emulator(BUILD_CONFIG)
    device.change_logs_buffer(serial_number)

    # Build abd push servicesIosdk, tvServices and tvPlatformServices
    if BUILD_CONFIG["test_suite"] == 'Acceptance' or 'ChildMode' in BUILD_CONFIG["test_class"]:
        app_tool.build_and_push_services(serial_number, BUILD_CONFIG)

    # Build abd push yandex updater
    if BUILD_CONFIG["test_suite"] != 'Acceptance' or (
            BUILD_CONFIG["test_suite"] != 'Acceptance' and BUILD_CONFIG["emulator_only"] != 'true'):
        updater_apk_path = app_tool.build_updater(BUILD_CONFIG)
        app_tool.push_to_device(serial_number, updater_apk_path,
                                app_tool.get_app_paths()["Updater"]["device_path"])

    # Build abd push yandex bugReportSender
    if 'Bugreport' in BUILD_CONFIG["test_class"]:
        app_tool.build_and_push_bugreportsender(serial_number, BUILD_CONFIG)

    # Build abd push yandex SetupWizard
    if 'SetupWizard' in BUILD_CONFIG["test_class"]:
        app_tool.build_and_push_setup_wizard(serial_number, BUILD_CONFIG)

    # Build abd push YandexVideoPlayer, YandexTvInputService, YandexWebPlayer and YandexLiveTv
    if 'Player' in BUILD_CONFIG["test_class"] or 'Tv' in BUILD_CONFIG["test_class"]:
        app_tool.build_and_push_video_player_apps(serial_number, BUILD_CONFIG)

    # Build abd push other yandex apps
    if BUILD_CONFIG["test_suite"] != 'Acceptance':
        app_tool.download_apps_for_regression(BUILD_CONFIG)
        app_tool.push_all_apps_for_regression(serial_number, BUILD_CONFIG)

    device.reboot(serial_number, None)
    device.wait_wifi_connection_on_emulator(serial_number, BUILD_CONFIG["emulator_api"])

    if BUILD_CONFIG["test_suite"] != 'Acceptance':
        device.root_remount(serial_number)
        device.disable_suw(serial_number, 'true')

    device.stop_and_clear_home_app(serial_number)
    app_tool.print_installed_apps(serial_number)
    logcat_process, log_file = logs.start_get_logs(serial_number, BUILD_CONFIG["is_teamcity"])

    BUILD_CONFIG['annotation_for_block_tests_1'] = 'androidx.test.filters.RequiresDevice'
    BUILD_CONFIG['annotation_for_block_tests_2'] = 'androidx.test.filters.SdkSuppress'

    # run tests
    status = run_marathon_tests(BUILD_CONFIG)

    # get logs
    logs.stop_get_logs(logcat_process, log_file, BUILD_CONFIG["is_teamcity"])
    logs.get_screenshots(serial_number, BUILD_CONFIG["is_teamcity"])
    logs.get_anr_logs(serial_number, BUILD_CONFIG["is_teamcity"])
    logs.rename_reports(serial_number, BUILD_CONFIG)

    if BUILD_CONFIG["delete_emulator"] == 'true':
        emulator.stop_emulator(serial_number)
        emulator.delete_emulator(BUILD_CONFIG["emulator_name"])
    return status


def run_tests_on_tv(serial_number):
    # build apps
    BUILD_CONFIG['gradle_property_for_emulator'] = '-PisTestOnEmulator=false'
    app_tool.build_home_app("assembleDebug", BUILD_CONFIG)
    app_tool.build_home_app("assembleDebugAndroidTest", BUILD_CONFIG)

    # prepare device
    device.connect_to_device_if_needed(serial_number, True)
    device.change_settings_on_device(serial_number)
    device.update_time_on_device(serial_number, BUILD_CONFIG["is_teamcity"])
    device.disable_suw(serial_number, BUILD_CONFIG["is_teamcity"])
    device.delete_apps_and_old_screenshots(serial_number)
    device.clear_data_in_apps(serial_number, BUILD_CONFIG["test_class"])
    device.change_logs_buffer(serial_number)
    if BUILD_CONFIG["test_suite"] == 'UpdaterAcceptance' or BUILD_CONFIG["test_class"] == 'NONE' \
            or 'Updater' in BUILD_CONFIG["test_class"]:
        updater_apk_path = app_tool.build_updater(BUILD_CONFIG)
        app_tool.install_app(serial_number, updater_apk_path)
    device.stop_and_clear_home_app(serial_number)
    device.clear_logs_and_delete_bugreports(serial_number)
    app_tool.print_installed_apps(serial_number)
    logcat_process, log_file = logs.start_get_logs(serial_number, BUILD_CONFIG["is_teamcity"])

    # run tests
    status = run_marathon_tests(BUILD_CONFIG)

    # get logs
    logs.stop_get_logs(logcat_process, log_file, BUILD_CONFIG["is_teamcity"])
    device.delete_app('com.yandex.launcher.updaterapp', serial_number)
    logs.get_screenshots(serial_number, BUILD_CONFIG["is_teamcity"])
    logs.get_anr_logs(serial_number, BUILD_CONFIG["is_teamcity"])
    logs.rename_reports(serial_number, BUILD_CONFIG)
    return status


def run_tests(serial_number, is_on_emulator):
    if serial_number is None:
        serial_number = BUILD_CONFIG["serial_number"]
    else:
        serial_number = serial_number

    if BUILD_CONFIG["product"] == 'station':
        if is_on_emulator is True:
            return run_tests_on_station_emulator()
        else:
            return run_tests_on_station(serial_number)
    else:
        if is_on_emulator is True:
            return run_tests_on_tv_emulator()
        else:
            return run_tests_on_tv(serial_number)


def run_marathon_tests(environment):
    logs.echo_title('Run tests')
    return subprocess.run(f'''marathon \
        --analyticsTracking=false \
        --bugsnag=false \
        --marathonfile="tv/ci/ui-tests/Marathonfile"''', env=environment, shell=True)


if __name__ == '__main__':
    device.install_python_requirements('requests', '2.27.1')
    device.install_python_requirements('retrying', '1.3.3')
    BUILD_CONFIG = utils.init_build_config(input_args)
    utils.print_env(BUILD_CONFIG)
    utils.check_apksigner()
    utils.check_avd_manager()

    if BUILD_CONFIG["emulator_only"] == 'true':
        build_status = emulator.run_emulator_only(BUILD_CONFIG)
    elif BUILD_CONFIG["product"] == 'centaur':
        build_status = run_tests_on_centaur_emulator()
    elif BUILD_CONFIG["kolhoz_device_id"] != 'NONE':
        serial = device.connect_to_device_in_kolhoz(BUILD_CONFIG)
        build_status = run_tests(serial_number=serial, is_on_emulator=False)
        device.disconnect_from_device_in_kolhoz(BUILD_CONFIG)
    elif BUILD_CONFIG["serial_number"] != 'NONE':
        build_status = run_tests(serial_number=None, is_on_emulator=False)
    elif BUILD_CONFIG["product"] == 'tv-services':
        build_status = run_sdk_tests_in_services()
    elif BUILD_CONFIG["product"] == 'tv-updater':
        build_status = run_updater_isolated_tests_on_emulator()
    else:
        build_status = run_tests(serial_number=None, is_on_emulator=True)

    utils.generate_allure_report(BUILD_CONFIG["is_teamcity"])
    logs.send_report_to_testpalm(BUILD_CONFIG)
    logs.echo_title('Build finished')
    if build_status == 1:
        sys.exit(1)
