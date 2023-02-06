import os
import subprocess
from datetime import datetime

import sys
import time

import kolhoz
import logs_tool as logs

ADB_COMMAND_TIMEOUT = 3


def root_device(serial_number):
    print(f'\nRoot device {serial_number}')
    os.system(f'adb -s {serial_number} root')
    time.sleep(ADB_COMMAND_TIMEOUT)
    connect_to_device_if_needed(serial_number, False)


def root_remount(serial_number):
    root_device(serial_number)
    print(f'\nRemount device {serial_number}')
    os.system(f'adb -s {serial_number} remount')
    time.sleep(ADB_COMMAND_TIMEOUT)
    connect_to_device_if_needed(serial_number, False)


def root_remount_custom_emulator(serial_number):
    root_device(serial_number)
    print(f'\nadb -s {serial_number} shell avbctl disable-verification')
    os.system(f'adb -s {serial_number} shell avbctl disable-verification')
    time.sleep(ADB_COMMAND_TIMEOUT)
    connect_to_device_if_needed(serial_number, False)
    reboot(serial_number, None)
    root_remount(serial_number)
    reboot(serial_number, None)
    root_remount(serial_number)


def reboot(serial_number, custom_boot_status):
    print(f'\nreboot {serial_number}')
    os.system(f'adb -s {serial_number} reboot')
    time.sleep(ADB_COMMAND_TIMEOUT)
    wait_for_boot_device(serial_number, custom_boot_status)


def is_device_online(device_id):
    output = subprocess.getoutput(f'adb devices | tail -n +2 | grep {device_id}')
    if output == '':
        return False
    else:
        return True


def connect_to_device_if_needed(serial_number, is_print_logs):
    if is_print_logs:
        logs.echo_title(f'Trying connect to {serial_number}')
    if is_device_online(serial_number):
        if is_print_logs:
            print(f'Already connected to {serial_number}')
            fingerprint = subprocess.getoutput(
                f'adb -s {serial_number} shell getprop ro.bootimage.build.fingerprint')
            print(f'Build fingerprint: {fingerprint}')
    else:
        print(f'Trying connect to {serial_number}')
        os.system(f'adb connect {serial_number}')
        time.sleep(ADB_COMMAND_TIMEOUT)
        result = subprocess.getoutput(f'adb connect {serial_number} | grep connected')
        if result == '':
            print(f'Cannot connect to device {serial_number}')
            sys.exit(1)


def get_device_serial_number(adb_device_id):
    if '.' in adb_device_id:
        return f'{adb_device_id}:5555'
    else:
        return adb_device_id


def get_station_version(serial_number, config):
    product_model = subprocess.getoutput(f'adb -s {serial_number} shell getprop ro.product.model')
    if product_model == 'yandexstation_2':
        return '2'
    else:
        config['system_quasar_base_path'] = '/system/priv-app/Quasar-Webmusic/Quasar-Webmusic.apk'
        config[
            'system_quasar_backup_path'] = '/system/priv-app/Quasar-Webmusic/Quasar-Webmusic.base'
        return '1'


def backup_system_quasar_app_on_station(serial_number, config):
    logs.echo_title('Backup quasar system app')
    root_remount(serial_number)
    print('\nrename quasar system app')
    os.system(f'adb -s {serial_number} shell mv {config["system_quasar_base_path"]} '
              f'{config["system_quasar_backup_path"]}')
    reboot(serial_number, '')
    root_remount(serial_number)
    print(f'\nadb -s {serial_number} shell setprop dalvik.vm.dex2oat-filter verify-none')
    os.system(f'adb -s {serial_number} shell setprop dalvik.vm.dex2oat-filter verify-none')


def restore_system_quasar_app_on_station(serial_number, config):
    logs.echo_title('Restore quasar system app')
    print('\nrename quasar system app')
    os.system(f'adb -s {serial_number} shell mv '
              f'{config["system_quasar_backup_path"]} '
              f'{config["system_quasar_base_path"]}')
    reboot(serial_number, None)


def get_emulator_serial_number():
    fail_counter = 0
    fail_time_in_sec = 60
    timeout_in_sec = 5
    while True:
        serial_number = subprocess.getoutput(
            "adb devices | tail -n +2 | grep emulator | awk '{print $1}'")
        print_status = f'(serial_number - {serial_number})'
        if 'emulator' in serial_number:
            print(f'serial number defined {print_status}')
            break
        else:
            fail_counter = fail_counter + timeout_in_sec
            print(f'Waiting for device in {fail_counter} seconds {print_status}')
            if fail_counter > fail_time_in_sec:
                print('!!!WARNING!!! Timeout reached; failed to start device')
                break
        time.sleep(timeout_in_sec)
    return serial_number


def wait_wifi_connection_on_emulator(serial_number, emulator_api):
    if emulator_api == '30':
        wait_for_wifi()
        print('wait quasar config 10 sec')
        time.sleep(10)
        reboot(serial_number, None)
        wait_for_wifi()


def wait_for_wifi():
    fail_counter = 0
    fail_time_in_sec = 120
    timeout_in_sec = 5
    while True:
        wifi_status = subprocess.getoutput("adb shell dumpsys wifi | grep lastConnected")
        print_status = f'(wifi_status - {wifi_status})'
        if 'lastConnected' in wifi_status:
            print(f'WiFi connected')
            break
        else:
            fail_counter = fail_counter + timeout_in_sec
            print(f'Waiting for wifi in {fail_counter} seconds {print_status}')
            if fail_counter > fail_time_in_sec:
                print('!!!WARNING!!! Timeout reached; failed connect to wifi')
                break
        time.sleep(timeout_in_sec)


def install_python_requirements(package, version):
    current_installed_version = subprocess.getoutput(f'pip show {package} | grep Version')
    if version not in current_installed_version:
        logs.echo_title(f'Install {package}=={version}')
        subprocess.call(
            [sys.executable, '-m', 'pip', 'install', package, '--upgrade', '--user', '-i',
             'https://pypi.yandex-team.ru/simple/'])


def disconnect_from_device_in_kolhoz(config):
    logs.echo_title(f'Disconnect from {config["kolhoz_device_id"]}')
    return kolhoz.release_device(config["kolhoz_token"], config["kolhoz_device_id"])


def disconnect_from_device(device_id):
    logs.echo_title(f'Disconnect from {device_id}')
    os.system(f'adb disconnect {device_id}')


def connect_to_device_in_kolhoz(config):
    logs.echo_title(f'Trying connect to {config["kolhoz_device_id"]} in kolhoz')
    if config["product"] == 'station':
        duration_of_occupy_in_hours = 3
    else:
        duration_of_occupy_in_hours = 9
    device_id = kolhoz.occupy_device(config["kolhoz_token"],
                                     config["kolhoz_device_id"],
                                     duration_of_occupy_in_hours)
    print(f'Ping device {device_id}')
    os.system(f'adb connect {device_id}')
    time.sleep(ADB_COMMAND_TIMEOUT)
    config['serial_number'] = device_id
    return device_id


def wait_for_boot_device(serial_number, custom_boot_status):
    logs.echo_title(f'Waiting for device {serial_number} stop booting')
    fail_counter = 0
    fail_time_in_sec = 700
    timeout_in_sec = 10
    if custom_boot_status is not None:
        expected_boot_status = custom_boot_status
    else:
        expected_boot_status = '1'
    while True:
        boot_status = subprocess.getoutput(f'adb -s {serial_number} shell getprop dev.bootcomplete')
        print_status = f'(Device status - {boot_status})'
        if boot_status == expected_boot_status:
            print(f'Device is ready {print_status}')
            break
        else:
            fail_counter = fail_counter + timeout_in_sec
            print(f'Waiting for device in {fail_counter} seconds {print_status}')
            if 'not found' in boot_status:
                os.system(f'adb connect {serial_number}')
            if fail_counter > fail_time_in_sec:
                print('!!!WARNING!!! Timeout reached; failed to start device')
                break
        time.sleep(timeout_in_sec)


def disable_animations(serial_number):
    print('Disable window animation scale')
    os.system(f'adb -s {serial_number} shell settings put global window_animation_scale 0')
    print('Disable transition animation scale')
    os.system(f'adb -s {serial_number} shell settings put global transition_animation_scale 0')
    print('Disable animator duration scale')
    os.system(f'adb -s {serial_number} shell settings put global animator_duration_scale 0')


def disable_suw(serial_number, is_teamcity):
    setup_wizard_activity = 'com.yandex.tv.setupwizard/com.yandex.tv.setupwizard.SetupActivity'
    if is_teamcity == 'true':
        logs.echo_title(f'Disable SUW on device {serial_number}')
        print('Settings put secure user_setup_complete 1')
        os.system(f'adb -s {serial_number} shell settings put secure user_setup_complete 1')
        time.sleep(ADB_COMMAND_TIMEOUT)
        print('Settings put global device_provisioned 1')
        os.system(f'adb -s {serial_number} shell settings put global device_provisioned 1')
        time.sleep(ADB_COMMAND_TIMEOUT)
        print('Disable com.yandex.tv.setupwizard/com.yandex.tv.setupwizard.SetupActivity')
        os.system(f'adb -s {serial_number} shell pm disable {setup_wizard_activity}')
        time.sleep(ADB_COMMAND_TIMEOUT)
    else:
        print('Skip disable SUW')


def update_time_on_device(serial_number, is_teamcity):
    if is_teamcity == 'true':
        date_text = datetime.today().strftime("%m%d%H%M%Y")
        logs.echo_title(f'Set time {date_text} on device {serial_number}')
        root_remount(serial_number)
        os.system(f'adb -s {serial_number} shell "date {date_text}.00; '
                  f'am broadcast -a android.intent.action.TIME_SET"')
        print('\nCurrent time on device:')
        os.system(f'adb -s {serial_number} shell date')
    else:
        print('Skip update time')


def add_media_fast_forward_keycode_for_emulator(serial_number):
    print('\nAdd MEDIA_FAST_FORWARD keycode for emulator')
    keycode = 'key 208 MEDIA_FAST_FORWARD'
    key_layout_path = '/system/usr/keylayout/qwerty.kl'
    os.system(f'adb -s {serial_number} shell "echo {keycode} >> {key_layout_path}"')


def change_settings_on_device(serial_number):
    logs.echo_title(f'Change settings on device {serial_number}')
    disable_animations(serial_number)
    print('Disable device sleep')
    os.system(f'adb -s {serial_number} shell settings put secure sleep_timeout -1')
    print('Disable screen saver')
    os.system(f'adb -s {serial_number} shell settings put system screen_off_timeout 2147483647')
    print('Enable stay awake')
    os.system(f'adb -s {serial_number} shell settings put global stay_on_while_plugged_in 3')
    print('Clear logcat')
    os.system(f'adb -s {serial_number} logcat -c')


def chmod_file_on_device(serial_number, path, permission):
    print(f'adb -s {serial_number} shell chmod {permission} {path}')
    os.system(f'adb -s {serial_number} shell chmod {permission} {path}')


def change_permissions_for_files_on_device(serial_number):
    logs.echo_title(f'Change permissions for files on device {serial_number}')
    chmod_file_on_device(serial_number, '/system/vendor/quasar/activate_adb.sh', '775')
    chmod_file_on_device(serial_number, '/system/vendor/quasar/device_ota_update.sh', '775')
    chmod_file_on_device(serial_number, '/system/vendor/quasar/gen_keys.sh', '775')
    chmod_file_on_device(serial_number, '/system/vendor/quasar/updater_switcher', '775')
    chmod_file_on_device(serial_number, '/system/vendor/quasar/mem_monitor.sh', '775')
    chmod_file_on_device(serial_number, '/system/vendor/quasar/ntp_sync.sh', '775')
    chmod_file_on_device(serial_number, '/system/vendor/quasar/ntpclient_aarch64', '775')
    chmod_file_on_device(serial_number, '/system/vendor/quasar/onboot.sh', '775')
    chmod_file_on_device(serial_number, '/system/vendor/quasar/performance_test.sh', '775')
    chmod_file_on_device(serial_number, '/system/vendor/quasar/play_pattern.sh', '775')
    chmod_file_on_device(serial_number, '/system/vendor/quasar/q', '775')
    chmod_file_on_device(serial_number, '/system/vendor/quasar/quasar_launcher2', '775')
    chmod_file_on_device(serial_number, '/system/vendor/quasar/run.sh', '775')
    chmod_file_on_device(serial_number, '/system/vendor/quasar/set_monotonic_time.sh', '775')
    chmod_file_on_device(serial_number, '/system/vendor/quasar/keymaster_proxy_app', '775')
    chmod_file_on_device(serial_number, '/system/vendor/quasar/led_util', '775')
    chmod_file_on_device(serial_number, '/system/vendor/quasar/quasar_client', '775')
    chmod_file_on_device(serial_number, '/system/vendor/quasar/quasar.cfg', '644')


def change_logs_buffer(serial_number):
    logs.echo_title(f'Change logs buffer on device {serial_number}')
    print('Current buffer size:')
    os.system(f'adb -s {serial_number} logcat -g')

    board = subprocess.getoutput(f'adb -s {serial_number} shell getprop ro.yndx.build.board')
    if board == 'rt2871' or 'emulator' in serial_number:
        buffer = '16'
    else:
        buffer = '1'
    print(f'\nSet log buffer size to {buffer}M')
    os.system(f'adb -s {serial_number} logcat -G {buffer}M')

    print('\nLog buffer size after change:')
    os.system(f'adb -s {serial_number} logcat -g')


def delete_app(package, serial_number):
    print(f'Delete package {package}')
    os.system(f'adb -s {serial_number} uninstall {package}')


def clear_data_in_app(package, serial_number):
    print(f'Clear data in package {package}')
    os.system(f'adb -s {serial_number} shell pm clear {package}')


def clear_logs_and_delete_bugreports(serial_number):
    logs.echo_title(f'Reset logs on device {serial_number}')
    print('Clear device logcat')
    os.system(f'adb -s {serial_number} logcat -c')
    print('Delete old bugreports')
    os.system(
        f'adb -s {serial_number} shell rm -rf /data/user_de/0/com.android.shell/files/bugreports')
    print('Delete anr traces')
    os.system(f'adb -s {serial_number} shell rm -rf data/anr')


def clear_data_in_apps(serial_number, test_class):
    logs.echo_title(f'Clear data in apps on device {serial_number}')
    os.system(f'adb -s {serial_number} shell input keyevent 4')
    os.system(f'adb -s {serial_number} shell input keyevent 4')
    clear_data_in_app('com.yandex.tv.home', serial_number)
    clear_data_in_app('com.yandex.tv.services', serial_number)
    clear_data_in_app('com.yandex.io.sdk', serial_number)
    clear_data_in_app('com.yandex.tv.ytplayer', serial_number)
    clear_data_in_app('com.yandex.tv.webplayer', serial_number)
    clear_data_in_app('com.yandex.tv.videoplayer', serial_number)
    clear_data_in_app('com.yandex.tv.live', serial_number)
    clear_data_in_app('com.yandex.tv.bugreportsender', serial_number)
    clear_data_in_app('ru.yandex.androidkeyboard.tv', serial_number)
    clear_data_in_app('com.android.tv.settings', serial_number)
    clear_data_in_app('com.cvte.tv.setting', serial_number)
    clear_data_in_app('com.yandex.tv.alice', serial_number)
    clear_data_in_app('com.mediatek.wwtv.tvcenter', serial_number)
    clear_data_in_app('com.yandex.launcher.updaterapp', serial_number)
    if test_class == 'NONE' or 'Updater' in test_class:
        clear_data_in_app('com.android.providers.tv', serial_number)
        clear_data_in_app('com.yandex.tv.input.efir', serial_number)


def delete_apps_and_old_screenshots(serial_number):
    logs.echo_title(f'Delete apps and old screenshots on device {serial_number}')
    print('Delete folder /sdcard/app_spoon-screenshots')
    os.system(f'adb -s {serial_number} shell rm -rf /sdcard/app_spoon-screenshots')
    delete_app('net.megogo.tv.preinstall', serial_number)
    delete_app('tv.okko.androidtv', serial_number)
    delete_app('ru.tvigle.tvapp', serial_number)
    delete_app('ru.ivi.client', serial_number)
    delete_app('ru.mts.mtstv', serial_number)
    delete_app('ru.tv1.android.tv', serial_number)
    delete_app('ru.rt.video.app.tv', serial_number)
    delete_app('com.ctcmediagroup.videomore', serial_number)
    delete_app('com.cloudmosa.puffinTV', serial_number)
    delete_app('yandex.egalkin.demoapp1', serial_number)
    delete_app('com.yandex.launcher.updaterapp', serial_number)


def stop_and_clear_home_app(serial_number):
    logs.echo_title(f'Stop home-app on device {serial_number}')
    package_name = 'com.yandex.tv.home'
    settings_activity = 'android.settings.APPLICATION_DETAILS_SETTINGS'
    clear_data_in_app(package_name, serial_number)
    os.system(
        f'adb -s {serial_number} shell "am start -a {settings_activity} -d package:{package_name}"')
    os.system(f'adb -s {serial_number} shell "am force-stop com.yandex.tv.home"')


def take_screenshot(serial_number, file_name):
    folder_path = '/sdcard/app_spoon-screenshots/ci'
    os.system(f'adb -s {serial_number} shell mkdir -p {folder_path}')
    print(f'\ntake screenshot to {folder_path}/{file_name}.png')
    os.system(f'adb -s {serial_number} shell screencap -p {folder_path}/{file_name}.png')
    logs.get_screenshots(serial_number, 'true')
