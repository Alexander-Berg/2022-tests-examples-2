import argparse
import time
import os
import subprocess
import device
import app_tool
import logs_tool as logs

TEAMCITY_VERSION = os.getenv('TEAMCITY_VERSION')
parser = argparse.ArgumentParser()
parser.add_argument('--branch', metavar='Var', type=str, default='master', help='Branch for build apps')
parser.add_argument('--ota_build_number', metavar='Var', type=str, default='NONE', help='Build number')
parser.add_argument('--serial_number', metavar='Var', type=str, default='NONE', help='Device IP or ID of module')
args = parser.parse_args()

SERIAL_NUMBER = args.serial_number
OTA_BUILD_NUMBER = args.ota_build_number
BRANCH = args.branch

if TEAMCITY_VERSION == '' or TEAMCITY_VERSION is None:
    IS_TEAMCITY = False
else:
    IS_TEAMCITY = True


def init_ota_file_names():
    ota_file_names = {
        'hikeen_rt2871': f'240_RealtekATV_40in_RealtekATV_rt2871_{BRANCH}_userdebug_{OTA_BUILD_NUMBER}-OTA.zip',
        'cvte_hisi351': f'YANDEX_TEST_H24F8000Q_CVTE351_cvte351_{BRANCH}_userdebug_{OTA_BUILD_NUMBER}-OTA.zip',
        'cvte_mt6681': f'YANDEX_TV32_SK506S_PB802_PT320AT02_2_CS548913_cvte6681_{BRANCH}_userdebug_{OTA_BUILD_NUMBER}-OTA.zip',
        'cv_mt9632': f'YANDEX_DEBUG_TV50_WIFI-RTK88X2CU_cv9632_{BRANCH}_userdebug_{OTA_BUILD_NUMBER}-OTA.zip',
        'cv_mt6681': f'YTV_YH32CV6681.T320XVN02G_T320XVN02G_KVANT_cv6681_{BRANCH}_userdebug_{OTA_BUILD_NUMBER}-OTA.zip'
    }
    return ota_file_names


def print_env(serial_number):
    logs.echo_title('Container env')
    print(f'BRANCH - {BRANCH}')
    print(f'SERIAL_NUMBER - {SERIAL_NUMBER}')
    build_platform = subprocess.getoutput(f'adb -s {serial_number} shell getprop ro.yndx.build.platform')
    build_board = subprocess.getoutput(f'adb -s {serial_number} shell getprop ro.yndx.build.board')
    device_platform = f'{build_platform}_{build_board}'
    ota_name = init_ota_file_names()[device_platform]
    print(f'OTA_FILE_NAME - {ota_name}')
    return ota_name, device_platform


def clear_device(serial_number):
    device.root_remount(serial_number)
    print('\nDelete folder /cache/ota_package')
    os.system(f'adb -s {serial_number} shell "rm -rf /cache/ota_package"')
    print('Delete folder /cache/external_ota')
    os.system(f'adb -s {serial_number} shell "rm -rf /cache/external_ota"')
    device.delete_app('com.yandex.launcher.updaterapp', serial_number)


def push_ota_file_to_device(serial_number, ota_local_path):
    logs.echo_title(f'Push OTA file on {serial_number}')
    os.system(f'adb -s {serial_number} shell "mkdir cache/external_ota"')
    app_tool.push_to_device(device_id, ota_local_path, 'cache/external_ota/')


def start_ota_update(serial_number, ota_local_path, platform):
    logs.echo_title('Start OTA update')
    if platform == 'hikeen_rt2871':
        update_service = "startservice"
    else:
        update_service = "start-foreground-service"
    os.system(f'''adb -s {serial_number} shell am {update_service} -a com.yandex.launcher.updaterapp.SIDE_LOAD_OTA \
    -n "com.yandex.launcher.updaterapp/com.yandex.launcher.updaterapp.tv.utils.SideloadOtaService" \
    -e filename {ota_local_path}''')
    os.system(f'adb -s {serial_number} logcat -d -v threadtime | grep SideloadOtaService:')
    time.sleep(10)


def enable_power_setting_on_cvte351(serial_number):
    logs.echo_title('Enable power setting for cvte351')
    print('Press BACK')
    os.system(f'adb -s {serial_number} shell input keyevent 4')
    print('Press BACK')
    os.system(f'adb -s {serial_number} shell input keyevent 4')
    print('Press BACK')
    os.system(f'adb -s {serial_number} shell input keyevent 4')
    os.system(f'adb -s {serial_number} shell am start -n "com.yandex.tv.settings/.power.PowerActivity"')
    time.sleep(2)
    print('Press ENTER')
    os.system(f'adb -s {serial_number} shell input keyevent 23')
    print('Take screenshot')
    os.system(f'adb -s {serial_number} shell screencap -p /sdcard/screen.png')
    os.system(f'adb -s {serial_number} pull /sdcard/screen.png after_change_power_setting.png')
    print('Press BACK')
    os.system(f'adb -s {serial_number} shell input keyevent 4')


if __name__ == '__main__':
    device_id = device.get_device_serial_number(SERIAL_NUMBER)
    device.connect_to_device_if_needed(device_id, True)
    ota_file_name, platform_name = print_env(device_id)
    clear_device(device_id)
    push_ota_file_to_device(device_id, ota_file_name)
    start_ota_update(device_id, ota_file_name, platform_name)
    device.disconnect_from_device(device_id)
    device.wait_for_boot_device(device_id, None)
    device.connect_to_device_if_needed(device_id, False)
    device.change_settings_on_device(device_id)
    device.update_time_on_device(device_id, IS_TEAMCITY)
    clear_device(device_id)
    fingerprint = subprocess.getoutput(f'adb -s {device_id} shell getprop ro.bootimage.build.fingerprint')
    logs.echo_title('New build fingerprint')
    print(f'{fingerprint}\n')
    if platform_name == 'cvte_hisi351':
        enable_power_setting_on_cvte351(device_id)
