import os
import subprocess
from datetime import date

ARTIFACTS_HOME_PATH = 'tv/ci/ui-tests/build'


def echo_title(title):
    print('\n*************************************************************************************')
    print(f'   {title}:')
    print('*************************************************************************************')


def rename_reports(serial_number, config):
    if config["is_teamcity"] == 'true':
        echo_title('Rename reports for testpalm')

        if config["droideka_url"] == 'https://droideka.tst.smarttv.yandex.net':
            api_name = 'testing'
        elif config["droideka_url"] == 'https://droideka.pre.smarttv.yandex.net':
            api_name = 'prestable'
        else:
            api_name = 'prod'

        if 'releases/smart_devices/' in config["branch"]:
            branch_name = config["branch"].replace('releases/smart_devices/', '')
        else:
            branch_name = config["branch"]

        date_text = date.today().strftime("%d.%m.%y")
        platform = subprocess.getoutput(
            f'adb -s {serial_number} shell getprop ro.yndx.build.platform')
        board = subprocess.getoutput(f'adb -s {serial_number} shell getprop ro.yndx.build.board')
        device = f'{platform}_{board}'
        print(f'device - {device}')
        report_names = {
            '_': {'old_name': f'{config["emulator_resolution"]}_API_{config["emulator_api"]}(AVD)',
                  'new_name': f'Emulator TV {config["emulator_resolution"]}p (API_{config["emulator_api"]}) ({date_text}).xml'},
            'hikeen_rt2871': {'old_name': 'SmartTV',
                              'new_name': f'Realtek 2871 (api_{api_name}) (branch_{branch_name}) ({date_text}).xml'},
            'cvte_hisi351': {'old_name': 'TEST351',
                             'new_name': f'HiSi 351 (api_{api_name}) (branch_{branch_name}) ({date_text}).xml'},
            'cv_mt9632': {'old_name': '9632',
                          'new_name': f'Cultraview 9632 (api_{api_name}) (branch_{branch_name}) ({date_text}).xml'},
            'cv_mt6681': {'old_name': '6681',
                          'new_name': f'Cultraview 6681 (api_{api_name}) (branch_{branch_name}) ({date_text}).xml'},
            'cvte_mt6681': {'old_name': '6681',
                            'new_name': f'cvte 6681 (api_{api_name}) (branch_{branch_name}) ({date_text}).xml'},
            'cvte_mt9632': {'old_name': '9632',
                            'new_name': f'cvte 9632 (api_{api_name}) (branch_{branch_name}) ({date_text}).xml'},
            'gntch_amlS905Y2': {'old_name': 'Module2',
                                'new_name': f'Module 2 (api_{api_name}) (branch_{branch_name}) ({date_text}).xml'}
        }

        xml_report_path = 'tv/home-app/app/build/outputs/androidTest-results/connected'
        os.system(f'mkdir -p {xml_report_path}')
        marathon_xml_path = 'tv/home-app/app/build/reports/marathon/tests/omni'
        new_name = report_names[device]['new_name']
        print(f'new_name - {new_name}')
        if config["test_suite"] == 'DroidekaRegression':
            full_new_name = f'Droideka regression on {new_name}'
        else:
            full_new_name = new_name
        os.system(f'cp {marathon_xml_path}/*"marathon_junit_report"*.xml {xml_report_path}/"{full_new_name}"')
        print('Reports after rename')
        os.system(f'ls {xml_report_path} -al')


def start_get_logs(serial_number, is_teamcity):
    echo_title(f'Start get logs from device {serial_number}')
    if is_teamcity == 'true':
        os.system(f'mkdir -p {ARTIFACTS_HOME_PATH}/logs')
        print('Start logcat...')
        log_file = open(f'{ARTIFACTS_HOME_PATH}/logs/device-log.txt', 'w')
        logcat_process = subprocess.Popen(
            ['adb', '-s', serial_number, 'logcat', '-v', 'threadtime'], stdout=log_file)
        print(f'Logcat process id: {logcat_process.pid}')
        return logcat_process, log_file
    else:
        print('Skip logs capture for local build')
        return None, None


def stop_get_logs(logcat_process, log_file, is_teamcity):
    if is_teamcity == 'true':
        echo_title('Stop get logs')
        print(f'Kill process id: {logcat_process.pid}')
        logcat_process.kill()
        print(f'Close file {ARTIFACTS_HOME_PATH}/logs/device-log.txt')
        log_file.close()


def get_screenshots(serial_number, is_teamcity):
    if is_teamcity == 'true':
        echo_title(f'Get Screenshots from device {serial_number}')
        local_path_for_screenshots = f'{ARTIFACTS_HOME_PATH}/screenshots/'
        os.system(f'mkdir -p {ARTIFACTS_HOME_PATH}/screenshots')
        os.system(
            f'adb -s {serial_number} pull sdcard/app_spoon-screenshots/ "{local_path_for_screenshots}"')


def get_quasar_daemons_logs(serial_number):
    echo_title(f'Get quasar daemons logs from device {serial_number}')
    local_path_for_logs = f'{ARTIFACTS_HOME_PATH}/logs'
    os.system(f'mkdir -p {local_path_for_logs}')
    os.system(f'adb -s {serial_number} pull tmp/logs/ {local_path_for_logs}/daemons-logs')


def get_anr_logs(serial_number, is_teamcity):
    if is_teamcity == 'true':
        echo_title(f'Get ANR logs from device {serial_number}')
        local_path_for_anr_logs = f'{ARTIFACTS_HOME_PATH}/ANR'
        os.system(f'mkdir -p {ARTIFACTS_HOME_PATH}/ANR')
        # create init file for fix sandbox error "empty artifacts directory"
        os.system(f'echo empty > {ARTIFACTS_HOME_PATH}/ANR/init.file')
        os.system(f'adb -s {serial_number} pull /data/anr "{local_path_for_anr_logs}"')


def send_report_to_testpalm(config):
    if config["testpalm_report"] == 'true':
        echo_title('Send report to testpalm')
        subprocess.run(f'''./gradlew testPalmSendDebugReport -p tv/home-app \
        -Ptoken={config["testpalm_token"]}''', shell=True)
