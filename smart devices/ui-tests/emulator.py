import os
import subprocess
import time

import sys

import app_tool
import device
import logs_tool as logs


def run_emulator_only(config):
    if config["product"] == 'station':
        run_station_emulator_only(config)
    elif config["product"] == 'centaur':
        run_centaur_emulator_only(config)
    else:
        run_yandex_tv_emulator_only(config)


def run_yandex_tv_emulator_only(config):
    status = app_tool.download_apps_for_regression(config)
    serial_number = run_tv_emulator(config)
    app_tool.push_all_apps_for_regression(serial_number, config)
    device.reboot(serial_number, None)
    device.wait_wifi_connection_on_emulator(serial_number, config["emulator_api"])
    device.clear_data_in_app('com.yandex.io.sdk', serial_number)
    device.clear_data_in_app('com.yandex.tv.home', serial_number)
    os.system(f'adb -s {serial_number} shell input keyevent 3')
    device.change_logs_buffer(serial_number)
    app_tool.print_installed_apps(serial_number)
    return status


def run_centaur_emulator_only(config):
    app_tool.build_centaur_app("assembleDemoX86Debug", config)
    serial_number = run_centaur_emulator(config)
    device.change_logs_buffer(serial_number)
    app_tool.install_app(serial_number, 'centaur-app/build/outputs/apk/demoX86/debug/'
                                        'centaur-app-demo-x86-debug.apk')
    app_tool.start_app_activity(serial_number,
                                'ru.yandex.quasar.centaur_app/ru.yandex.quasar.centaur_app.MainActivity')


def run_station_emulator_only(config):
    # build app
    app_tool.build_quasar_app("assembleProdX86Debug", config)
    # sign app
    app_tool.sign_app_via_aosp_platform_key(app_tool.get_app_paths()["QuasarApp"]["main_app_path_x86"])
    # build daemons
    app_tool.build_quasar_daemons()
    # run emulator
    serial_number = run_station_emulator(config)
    logs.get_quasar_daemons_logs(serial_number)


def run_tv_emulator(config):
    if config["emulator_api"] == '30' and config["product"] != 'centaur':
        download_emulator_image()
        emulator_name = run_custom_emulator(config)
    else:
        emulator_name = create_and_run_emulator(config)

    serial_number = device.get_emulator_serial_number()
    device.wait_for_boot_device(serial_number, None)
    change_settings_on_tv_emulator(serial_number, config)
    app_tool.remove_google_launcher_and_keyboard_on_device(serial_number, config)
    config['serial_number'] = serial_number
    config['emulator_name'] = emulator_name
    return serial_number


def run_centaur_emulator(config):
    config['emulator_api'] = '30'
    emulator_name = create_and_run_emulator(config)
    serial_number = device.get_emulator_serial_number()
    device.wait_for_boot_device(serial_number, None)
    change_settings_on_centaur_emulator(serial_number, config)
    config['serial_number'] = serial_number
    config['emulator_name'] = emulator_name
    return serial_number


def run_station_emulator(config):
    # start emulator
    emulator_name = create_and_run_emulator(config)
    serial_number = device.get_emulator_serial_number()
    device.wait_for_boot_device(serial_number, None)

    # prepare emulator
    device.root_remount(serial_number)
    device.change_logs_buffer(serial_number)
    device.disable_animations(serial_number)
    app_tool.disable_app(serial_number, 'com.google.android.apps.nexuslauncher')

    # push daemons
    os.system(f'adb -s {serial_number} shell mkdir /data/quasar_daemons')
    os.system(f'adb -s {serial_number} shell ln -s /data/quasar_daemons /system/vendor/quasar')
    app_tool.push_to_device(serial_number, config["quasar_daemons_folder_path"], '/system/vendor/')
    app_tool.push_to_device(serial_number,
                            os.path.join(config["quasar_daemons_folder_path"], 'quasar-dev.cfg'),
                            '/system/vendor/quasar/quasar.cfg')
    device.change_permissions_for_files_on_device(serial_number)

    # push props for authorization
    # todo: push tus.token only after fix ipv6 connect on emulator
    # os.system(f'adb -s {serial_number} shell setprop tus.token {config["tus_token"]}')
    os.system(f'adb -s {serial_number} shell setprop tus.login {config["ya_login"]}')
    os.system(f'adb -s {serial_number} shell setprop tus.password {config["ya_pass"]}')

    # start daemons
    app_tool.start_quasar_daemons(serial_number)

    # install quasar-app
    app_tool.install_app(serial_number, app_tool.get_app_paths()["QuasarApp"]["main_app_path_x86"])

    # todo: remove timeout after fix https://st.yandex-team.ru/QUASAR-9495
    timeout_for_wait_quasar_init = 15
    print(f'wait for init quasar-app - {timeout_for_wait_quasar_init} sec')
    time.sleep(timeout_for_wait_quasar_init)
    device.take_screenshot(serial_number, 'screen_after_auth')
    app_tool.restart_quasar_daemons_if_needed(serial_number)

    # update config
    config['serial_number'] = serial_number
    config['emulator_name'] = emulator_name
    return serial_number


def create_and_run_emulator(config):
    api = config["emulator_api"]
    if config["product"] == 'centaur':
        emulator_name = f'Centaur_API_30'
        android_abi = 'x86'
        emulator_package = f'system-images;android-30;google_apis;x86'
        emulator_config_path = f'tv/ci/ui-tests/avd-configs/Centaur_API30.avd.ini'
        additional_options = ''
    elif config["product"] == 'station':
        emulator_name = 'Station.Max'
        android_abi = 'x86_64'
        emulator_package = 'system-images;android-28;google_apis;x86_64'
        emulator_config_path = 'tv/ci/ui-tests/avd-configs/Station.Max.avd.ini'
        additional_options = '-wipe-data -selinux permissive'
    else:
        emulator_name = f'Android_TV_{config["emulator_resolution"]}_API_{api}'
        android_abi = 'android-tv/x86'
        emulator_package = f'system-images;android-{api};android-tv;x86'
        emulator_config_path = f'tv/ci/ui-tests/avd-configs/' \
                               f'Android_TV_{config["emulator_resolution"]}p_API_{api}.avd.ini'
        additional_options = ''

    check_emulator_package_is_installed(emulator_package)
    logs.echo_title('Create and Run emulator')
    process = subprocess.run(["java", "-jar", "tv/ci/ui-tests/swarmer_0.2.6.jar", "start",
                              "--emulator-name", emulator_name,
                              "--package", emulator_package,
                              "--android-abi", android_abi,
                              "--path-to-config-ini", emulator_config_path,
                              "--emulator-start-options", "-writable-system",
                              additional_options,
                              config["emulator_property"]])
    if process.returncode != 0:
        logs.echo_title('Create and Run emulator failed')
        sys.exit(1)
    return emulator_name


def run_custom_emulator(config):
    logs.echo_title('Run custom emulator')
    emulator_name = f'Android_TV_{config["emulator_resolution"]}_API_{config["emulator_api"]}'
    home_path = os.path.abspath(os.getcwd())
    subprocess.Popen(f'''ANDROID_BUILD_TOP="{home_path}" \
                    ANDROID_PRODUCT_OUT="{home_path}/tv/ci/emulator_api30" \
                    emulator -writable-system \
                    -wipe-data {config["emulator_property"]}''', shell=True,
                     stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL)
    return emulator_name


def change_settings_on_centaur_emulator(serial_number, config):
    logs.echo_title(f'Change settings on emulator {serial_number}')
    device.disable_animations(serial_number)
    device.root_device(serial_number)
    print('Setprop secure immersive_mode_confirmations confirmed')
    os.system(f'adb -s {serial_number} shell "settings put secure '
              f'immersive_mode_confirmations confirmed"')
    print(f'Echo {config["centaur_device_id"]} > /sdcard/Download/centaur_device_id')
    os.system(f'adb -s {serial_number} shell "echo {config["centaur_device_id"]} > '
              f'/sdcard/Download/centaur_device_id"')


def change_settings_on_tv_emulator(serial_number, config):
    logs.echo_title(f'Change settings on emulator {serial_number}')
    device.disable_animations(serial_number)
    if config["emulator_api"] == '30':
        device.root_remount_custom_emulator(serial_number)
        app_tool.add_privapp_permissions_for_emulator(serial_number)
    else:
        device.root_remount(serial_number)
    print(f'\nSetprop persist.debug.device_id {config["quasar_id"]}')
    os.system(
        f'adb -s {serial_number} shell setprop persist.debug.device_id {config["quasar_id"]}')
    print(f'\nSetprop persist.debug.quasar_backend localhost')
    os.system(f'adb -s {serial_number} shell setprop persist.debug.quasar_backend localhost')
    device.add_media_fast_forward_keycode_for_emulator(serial_number)
    print('Setprop.sys.language ru')
    os.system(f'adb -s {serial_number} shell "setprop persist.sys.language ru"')
    print('Setprop persist.sys.country RU')
    os.system(f'adb -s {serial_number} shell "setprop persist.sys.country RU"')
    print('Setprop persist.sys.locale ru-RU')
    os.system(f'adb -s {serial_number} shell "setprop persist.sys.locale ru-RU"')


def download_emulator_image():
    logs.echo_title(f'Download emulator image')
    emulator_path = 'tv/ci/emulator_api30'
    if os.path.isdir(emulator_path):
        print(f'folder {emulator_path} already exists')
    else:
        os.system(
            'wget https://proxy.sandbox.yandex-team.ru/2700674512 -O tv/ci/emulator_api30.zip')
        os.system('unzip tv/ci/emulator_api30.zip -d tv/ci/emulator_api30')
        os.system('rm tv/ci/emulator_api30.zip')


def check_emulator_package_is_installed(package):
    check_result = subprocess.getoutput(f'sdkmanager --list_installed | grep "{package}"')
    if check_result == '':
        logs.echo_title(f'Please install required package for emulator')
        print(f'command: yes | sdkmanager "{package}"\n')
        sys.exit(1)


def stop_emulator(serial_number):
    logs.echo_title(f'Stop {serial_number}')
    os.system(f'adb -s {serial_number} emu kill')


def delete_emulator(emulator_name):
    logs.echo_title(f'Delete {emulator_name}')
    os.system(f'avdmanager delete avd -n {emulator_name}')
