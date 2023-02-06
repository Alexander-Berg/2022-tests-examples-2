import os
import subprocess
import shutil

import sys

import logs_tool as logs


def get_app_paths():
    """
    Warning! Use device_path only for push to the emulator.
    Some apps can be in different paths on real device: /system/priv-app/ or /vendor/priv-app/
    """
    apps_paths = {
        'YandexTvHome': {'package': 'com.yandex.tv.home',
                         'downloaded_path': 'vendor_yandex_prebuit/downloadable/YandexTvHome.apk',
                         'source_path': 'tv/home-app/app/build/outputs/apk/debug',
                         'device_path': '/system/app/YandexTvHome/YandexTvHome.apk',
                         'device_path_api30': '/product/app/YandexTvHome/YandexTvHome.apk'},
        'ServicesIosdk': {'package': 'com.yandex.io.sdk',
                          'downloaded_path': 'vendor_yandex_prebuit/downloadable/ServicesIosdk.apk',
                          'source_path': 'tv/services/services-iosdk-app/build/outputs/apk/emulator/debug',
                          'device_path': '/system/priv-app/ServicesIosdk/ServicesIosdk.apk'},
        'TvServices': {'package': 'com.yandex.tv.services',
                       'downloaded_path': 'vendor_yandex_prebuit/downloadable/YandexTvServices.apk',
                       'source_path': 'tv/services/services-app/build/outputs/apk/debug',
                       'device_path': '/system/priv-app/YandexTvServices/YandexTvServices.apk'},
        'TvPlatformServices': {'package': 'com.yandex.tv.services.platform',
                               'downloaded_path': 'vendor_yandex_prebuit/downloadable/YandexTvPlatformServices.apk',
                               'source_path': 'tv/services/services-platform-app/build/outputs/apk/debug',
                               'device_path': '/system/priv-app/YandexTvPlatformServices/YandexTvPlatformServices.apk'},
        'BugReportSender': {'package': 'com.yandex.tv.bugreportsender',
                            'downloaded_path': 'vendor_yandex_prebuit/downloadable/YandexTvBugReportSender.apk',
                            'source_path': 'tv/services/bugreportsender-app/build/outputs/apk/debug',
                            'device_path': '/system/priv-app/YandexTvBugReportSender/YandexTvBugReportSender.apk'},
        'AndroidTvSettings': {'package': 'com.android.tv.settings',
                              'downloaded_path_api_25': 'vendor_yandex_prebuit/downloadable/TvSettingsApi25.apk',
                              'downloaded_path_api_28': 'vendor_yandex_prebuit/downloadable/TvSettingsApi28.apk',
                              'downloaded_path_api_30': 'vendor_yandex_prebuit/downloadable/TvSettingsApi30.apk',
                              'device_path': '/system/priv-app/TvSettings/TvSettings.apk',
                              'device_path_api30': '/system/system_ext/priv-app/TvSettings/TvSettings.apk'},
        'YandexTvSettings': {'package': 'com.yandex.tv.settings',
                             'downloaded_path_api_25': 'vendor_yandex_prebuit/downloadable/YandexTvSettingsApi25.apk',
                             'downloaded_path_api_28': 'vendor_yandex_prebuit/downloadable/YandexTvSettingsApi28.apk',
                             'downloaded_path_api_30': 'vendor_yandex_prebuit/downloadable/YandexTvSettingsApi30.apk',
                             'device_path': '/system/priv-app/YandexTvSettings/YandexTvSettings.apk'},
        'YandexLiveTv': {'package': 'com.yandex.tv.live',
                         'downloaded_path': 'vendor_yandex_prebuit/downloadable/YandexLiveTv.apk',
                         'source_path': 'tv/video-player/tv/build/outputs/apk/debug',
                         'device_path': '/system/priv-app/YandexLiveTv/YandexLiveTv.apk'},
        'YandexTvInputService': {'package': 'com.yandex.tv.input.efir',
                                 'downloaded_path': 'vendor_yandex_prebuit/downloadable/YandexTvInputService.apk',
                                 'source_path': 'tv/video-player/input-service/build/outputs/apk/debug',
                                 'device_path': '/system/priv-app/YandexTvInputService/YandexTvInputService.apk'},
        'YandexVideoPlayer': {'package': 'com.yandex.tv.videoplayer',
                              'downloaded_path': 'vendor_yandex_prebuit/downloadable/YandexVideoPlayer.apk',
                              'source_path': 'tv/video-player/video/build/outputs/apk/debug',
                              'device_path': '/system/app/YandexVideoPlayer/YandexVideoPlayer.apk'},
        'YandexWebPlayer': {'package': 'com.yandex.tv.webplayer',
                            'downloaded_path': 'vendor_yandex_prebuit/downloadable/YandexWebPlayer.apk',
                            'source_path': 'tv/video-player/web/build/outputs/apk/x86/debug',
                            'device_path': '/system/app/YandexWebPlayer/YandexWebPlayer.apk'},
        'YandexAdvid': {'package': 'com.yandex.android.advid',
                        'downloaded_path': 'vendor_yandex_prebuit/downloadable/YandexAdvid.apk',
                        'device_path': '/system/priv-app/YandexAdvid/YandexAdvid.apk'},
        'Kinopoisk': {'package': 'ru.kinopoisk.yandex.tv',
                      'downloaded_path': 'vendor_yandex_prebuit/downloadable/Kinopoisk.apk',
                      'device_path': '/system/app/Kinopoisk/Kinopoisk.apk'},
        'YtPlayer': {'package': 'com.yandex.tv.ytplayer',
                     'downloaded_path': 'vendor_yandex_prebuit/downloadable/YtPlayer.apk',
                     'device_path': '/system/app/YtPlayer/YtPlayer.apk'},
        'YandexTvAlice': {'package': 'com.yandex.tv.alice',
                          'downloaded_path': 'vendor_yandex_prebuit/downloadable/YandexTvAlice.apk',
                          'device_path': '/system/app/YandexTvAlice/YandexTvAlice.apk'},
        'TvMusicApp': {'package': 'com.yandex.tv.music',
                       'downloaded_path': 'vendor_yandex_prebuit/downloadable/TvMusicApp.apk',
                       'device_path': '/system/app/TvMusicApp/TvMusicApp.apk'},
        'YandexSetupWizard': {'package': 'com.yandex.tv.setupwizard',
                              'downloaded_path': 'vendor_yandex_prebuit/downloadable/YandexSetupWizard.apk',
                              'source_path': 'tv/setup-wizard/app/build/outputs/apk/emulator/debug',
                              'device_path': '/system/priv-app/YandexSetupWizard/YandexSetupWizard.apk'},
        'YandexTvKeyboard': {'package': 'ru.yandex.androidkeyboard.tv',
                             'downloaded_path': 'vendor_yandex_prebuit/downloadable/YandexTvKeyboard.apk',
                             'device_path': '/system/app/YandexTvKeyboard/YandexTvKeyboard.apk'},
        'Updater': {'package': 'com.yandex.launcher.updaterapp',
                    'downloaded_path': 'vendor_yandex_prebuit/downloadable/YandexUpdater.apk',
                    'source_path': 'tv/updater-app/app/build/outputs/apk/alexandriaTvUiLogged/release',
                    'device_path': '/system/priv-app/YandexUpdater/YandexUpdater.apk'},
        'CentaurApp': {'package': 'ru.yandex.quasar.centaur_app',
                       'main_app_path': 'centaur-app/build/outputs/apk/demoX86/debug/centaur-app-demo-x86-debug.apk',
                       'test_app_path': 'centaur-app/build/outputs/apk/androidTest/demoX86/debug/centaur-app-demo-x86-debug-androidTest.apk'},
        'QuasarApp': {'package': 'ru.yandex.quasar.app',
                      'main_app_path_x86': 'quasar-app/build/outputs/apk/prodX86/debug/quasar-app-prod-x86-debug.apk',
                      'main_app_path_v7': 'quasar-app/build/outputs/apk/prodV7/debug/quasar-app-prod-v7-debug.apk',
                      'test_app_path_x86': 'quasar-app/build/outputs/apk/androidTest/prodX86/debug/quasar-app-prod-x86-debug-androidTest.apk',
                      'test_app_path_v7': 'quasar-app/build/outputs/apk/androidTest/prodV7/debug/quasar-app-prod-v7-debug-androidTest.apk'}
    }
    return apps_paths


def sign_app_via_aosp_platform_key(apk_path):
    print(f'\nSign {apk_path} with aosp platform keys')
    process = subprocess.run(f'''apksigner sign \
        --key keystore/aosp-platform/platform.pk8 \
        --cert keystore/aosp-platform/platform.x509.pem \
        {apk_path}''', shell=True)
    if process.returncode != 0:
        logs.echo_title(f'Sign {apk_path} failed')
        sys.exit(1)


def prepare_and_push_permission_for_enable_child_mode(serial_number):
    permission_file_name = 'com.yandex.tv.software.child_mode.xml'
    logs.echo_title(f'Prepare {permission_file_name} and push on device {serial_number}')
    local_path = 'vendor_yandex_prebuit/downloadable/'
    os.system(f'mkdir -p {local_path}')
    path_on_device = f'/etc/permissions/{permission_file_name}'
    permission = ('''<?xml version="1.0" encoding="utf-8"?>
<permissions>
    <!-- Child mode is supported -->
    <feature name="com.yandex.tv.software.child_mode" />
</permissions>''')
    f = open(local_path + permission_file_name, "w+")
    f.write(permission)
    f.close()
    push_to_device(serial_number, local_path + permission_file_name, path_on_device)


def prepare_and_push_permission_for_enable_brick_mode(serial_number):
    file_path = 'tv/ci/ui-tests/brick-mode/android.software.device_admin.xml'
    logs.echo_title(f'Push {file_path} on device {serial_number}')
    print('set device_provisioned 0')
    os.system(f'adb -s {serial_number} shell settings put global device_provisioned 0')
    status = subprocess.getoutput(
        f'adb -s {serial_number} shell settings list global | grep device_provisioned')
    print(f'status device_provisioned = {status}')
    path_on_device = f'/etc/permissions/android.software.device_admin.xml'
    push_to_device(serial_number, file_path, path_on_device)


def prepare_and_push_device_owner_for_enable_brick_mode(serial_number):
    file_path = 'tv/ci/ui-tests/brick-mode/device_owner_2.xml'
    logs.echo_title(f'Push {file_path} on device {serial_number}')
    path_on_device = f'/data/system/device_owner_2.xml'
    push_to_device(serial_number, file_path, path_on_device)


def add_privapp_permissions_for_emulator(serial_number):
    print('\nAdd privapp-permissions-platform.xml for emulator')
    permission_file_name = 'privapp-permissions-platform.xml'
    local_path = 'tv/ci/emulator_api30/'
    path_on_device = '/system/etc/permissions/privapp-permissions-platform.xml'
    push_to_device(serial_number, local_path + permission_file_name, path_on_device)


def start_app_activity(serial_number, activity):
    print(f'\nStart app activity {activity}')
    os.system(f'adb -s {serial_number} shell am start -n "{activity}"')


def download_apps_for_regression(config):
    logs.echo_title(f'Download apps for regression')
    if config["skip_download_apps"] == 'false':
        if config["is_teamcity"] == 'true':
            username = 'robot-edi'
        else:
            username = os.environ.get('USER')

        os.system('rm -rf vendor_yandex_prebuit')
        git_clone_process = subprocess.run(
            f'git clone ssh://{username}@gerrit.yandex-team.ru/tv/vendor_yandex_prebuit',
            shell=True)
        if git_clone_process.returncode != 0:
            logs.echo_title(
                f'git clone ssh://{username}@gerrit.yandex-team.ru/tv/vendor_yandex_prebuit failed')
            sys.exit(1)

        print('\nInstall pip requirements:')
        install_requirements_process = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', 'artifact_downloader/requirements.txt',
             '--user', '-i',
             'https://pypi.yandex-team.ru/simple/'],
            cwd='vendor_yandex_prebuit')
        if install_requirements_process.returncode != 0:
            logs.echo_title('Install artifact_downloader/requirements.txt failed')
            sys.exit(1)

        download_apps_process = subprocess.run(
            [sys.executable, '-m', 'artifact_downloader.main',
             '--build_variant', 'userdebug',
             '--def_branches', config["branch_for_download_apps"],
             '--out_dir', 'downloadable/',
             '--user', username,
             '--yaml_config', 'artifacts-emulator.yaml'], cwd='vendor_yandex_prebuit')

        if download_apps_process.returncode != 0:
            logs.echo_title('Download apps failed')
            sys.exit(1)


def push_all_apps_for_regression(serial_number, config):
    path = get_app_paths()
    home_app_device_path, settings_local_path, android_settings_device_path = get_apps_path_for_emulator_api(
        config["emulator_api"])
    prepare_and_push_permission_for_enable_child_mode(serial_number)
    logs.echo_title(f'Push yandex apps on device {serial_number}')

    push_to_device(serial_number,
                   path['AndroidTvSettings'][settings_local_path],
                   path['AndroidTvSettings'][android_settings_device_path])
    push_to_device(serial_number,
                   path['YandexTvHome']['downloaded_path'],
                   path['YandexTvHome'][home_app_device_path])
    push_app(serial_number, 'YandexTvSettings', settings_local_path)
    push_app(serial_number, 'YandexAdvid', 'downloaded_path')
    push_app(serial_number, 'Kinopoisk', 'downloaded_path')
    push_app(serial_number, 'YtPlayer', 'downloaded_path')
    push_app(serial_number, 'TvMusicApp', 'downloaded_path')
    push_app(serial_number, 'YandexTvKeyboard', 'downloaded_path')

    if 'ChildMode' not in config["test_class"]:
        sign_app_via_aosp_platform_key(path['TvPlatformServices']['downloaded_path'])
        push_app(serial_number, 'TvPlatformServices', 'downloaded_path')
        push_app(serial_number, 'TvServices', 'downloaded_path')
        push_app(serial_number, 'ServicesIosdk', 'downloaded_path')
    if 'Bugreport' not in config["test_class"]:
        sign_app_via_aosp_platform_key(path['BugReportSender']['downloaded_path'])
        push_app(serial_number, 'BugReportSender', 'downloaded_path')
    if 'SetupWizard' not in config["test_class"]:
        push_app(serial_number, 'YandexSetupWizard', 'downloaded_path')
    if 'Player' not in config["test_class"] and 'Tv' not in config["test_class"]:
        push_app(serial_number, 'YandexVideoPlayer', 'downloaded_path')
        push_app(serial_number, 'YandexTvInputService', 'downloaded_path')
        sign_app_via_aosp_platform_key(path['YandexLiveTv']['downloaded_path'])
        push_app(serial_number, 'YandexLiveTv', 'downloaded_path')
        push_app(serial_number, 'YandexWebPlayer', 'downloaded_path')
    if config["emulator_only"] == 'true':
        push_app(serial_number, 'Updater', 'downloaded_path')


def get_version_of_app(serial_number, package):
    return subprocess.getoutput("adb -s " + serial_number + " shell dumpsys package "
                                + package + " | grep versionName | awk '{print $1}' | awk -F'=' '{print $2}'")


def get_build_number_of_app(serial_number, package):
    return subprocess.getoutput("adb -s " + serial_number + " shell dumpsys package "
                                + package + " | grep versionCode | awk '{print $1}' | awk -F'=' '{print $2}'")


def print_app_version(serial_number, package):
    version = get_version_of_app(serial_number, package)
    build_number = get_build_number_of_app(serial_number, package)
    print(f'{package} - build #{build_number} - version #{version}')


def print_installed_apps(serial_number):
    logs.echo_title(f'Apps on device {serial_number}')
    print_app_version(serial_number, get_app_paths()["YandexTvHome"]["package"])
    print_app_version(serial_number, get_app_paths()["Updater"]["package"])
    print_app_version(serial_number, get_app_paths()["ServicesIosdk"]["package"])
    print_app_version(serial_number, get_app_paths()["TvServices"]["package"])
    print_app_version(serial_number, get_app_paths()["TvPlatformServices"]["package"])
    print_app_version(serial_number, get_app_paths()["YandexLiveTv"]["package"])
    print_app_version(serial_number, get_app_paths()["YandexTvInputService"]["package"])
    print_app_version(serial_number, get_app_paths()["YandexVideoPlayer"]["package"])
    print_app_version(serial_number, get_app_paths()["YandexWebPlayer"]["package"])
    print_app_version(serial_number, get_app_paths()["YandexAdvid"]["package"])
    print_app_version(serial_number, get_app_paths()["Kinopoisk"]["package"])
    print_app_version(serial_number, get_app_paths()["YtPlayer"]["package"])
    print_app_version(serial_number, get_app_paths()["TvMusicApp"]["package"])
    print_app_version(serial_number, get_app_paths()["BugReportSender"]["package"])
    print_app_version(serial_number, get_app_paths()["AndroidTvSettings"]["package"])
    print_app_version(serial_number, get_app_paths()["YandexTvSettings"]["package"])
    print_app_version(serial_number, get_app_paths()["YandexSetupWizard"]["package"])
    print_app_version(serial_number, get_app_paths()["YandexTvKeyboard"]["package"])


def check_if_app_installed(serial_number, package):
    result = subprocess.getoutput(
        f'adb -s {serial_number} shell "pm list packages | grep {package}"')
    if result is None or result == '':
        return False
    else:
        return True


def install_app(serial_number, apk_path):
    print(f'\nInstall {apk_path} on device {serial_number}')
    process = subprocess.run(f'adb -s {serial_number} install -r -d -t -g {apk_path}', shell=True)
    if process.returncode != 0:
        logs.echo_title('Install failed. Stop Script. Exit.')
        sys.exit(1)


def disable_app(serial_number, app_package):
    print(f'disable {app_package} on device {serial_number}')
    os.system(f'adb -s {serial_number} shell pm disable {app_package}')


def uninstall_app(serial_number, app_package_name):
    print(f'uninstall {app_package_name} from device {serial_number}')
    os.system(f'adb -s {serial_number} uninstall {app_package_name}')


def remove_app(serial_number, app_package_path):
    print(f'Remove {app_package_path} on device {serial_number}')
    os.system(f'adb -s {serial_number} shell rm {app_package_path}')


def remove_google_launcher_and_keyboard_on_device(serial_number, config):
    if config["product"] == 'station':
        logs.echo_title(f'Remove Nexus launcher on device {serial_number}')
        remove_app(serial_number,
                   '/system/priv-app/NexusLauncherPrebuilt/NexusLauncherPrebuilt.apk')
    else:
        logs.echo_title(f'Remove google launcher and keyboard on device {serial_number}')
        if config["emulator_api"] == '25':
            remove_app(serial_number, '/system/priv-app/LeanbackLauncher/LeanbackLauncher.apk')
            remove_app(serial_number, '/system/app/LeanbackIme/LeanbackIme.apk')
        elif config["emulator_api"] == '28':
            remove_app(serial_number, '/system/priv-app/TVLauncher/TVLauncher.apk')
            remove_app(serial_number,
                       '/system/app/LatinIMEGoogleTvPrebuilt/LatinIMEGoogleTvPrebuilt.apk')
        elif config["emulator_api"] == '30':
            remove_app(serial_number,
                       '/system_ext/priv-app/Launcher3QuickStep/Launcher3QuickStep.apk')
        else:
            remove_app(serial_number,
                       '/system/product/priv-app/TvSampleLeanbackLauncher/TvSampleLeanbackLauncher.apk')


def push_to_device(serial_number, local_path, system_path):
    print(f'\nPush {local_path} to {system_path}')
    process = subprocess.run(f'adb -s {serial_number} push {local_path} {system_path}', shell=True)
    if process.returncode != 0:
        logs.echo_title('Push failed. Stop Script. Exit.')
        sys.exit(1)


def push_app(serial_number, app_name, local_path):
    paths = get_app_paths()
    push_to_device(serial_number, paths[app_name][local_path], paths[app_name]['device_path'])


def get_full_path_to_apk(app_name, app_type):
    path = get_app_paths()
    local_path = path[app_name]["source_path"]
    apk_name = subprocess.getoutput(f'ls {local_path} | grep "{app_type}.apk"')
    return f'{local_path}/{apk_name}'


def build_and_push_services(serial_number, config):
    app_path = get_app_paths()
    iosdk_apk_path, services_app_apk_path, platform_services_apk_path = \
        build_services(config)

    logs.echo_title(f'Push services apps on device {serial_number}')
    push_to_device(serial_number, iosdk_apk_path, app_path["ServicesIosdk"]["device_path"])

    push_to_device(serial_number, services_app_apk_path,
                   app_path["TvServices"]["device_path"])

    sign_app_via_aosp_platform_key(platform_services_apk_path)
    push_to_device(serial_number, platform_services_apk_path,
                   app_path["TvPlatformServices"]["device_path"])


def build_and_push_video_player_apps(serial_number, config):
    app_path = get_app_paths()
    input_service_apk_path, tv_apk_path, video_apk_path, web_apk_path = \
        build_video_player(config)

    logs.echo_title(f'Push video player apps on device {serial_number}')
    push_to_device(serial_number, input_service_apk_path,
                   app_path["YandexTvInputService"]["device_path"])
    push_to_device(serial_number, video_apk_path,
                   app_path["YandexVideoPlayer"]["device_path"])
    push_to_device(serial_number, web_apk_path, app_path["YandexWebPlayer"]["device_path"])

    sign_app_via_aosp_platform_key(tv_apk_path)
    push_to_device(serial_number, tv_apk_path, app_path["YandexLiveTv"]["device_path"])


def build_and_push_bugreportsender(serial_number, config):
    app_path = get_app_paths()
    bugreport_apk_path = build_bugreportsender(config)
    logs.echo_title(f'Push bugreportsender app on device {serial_number}')
    sign_app_via_aosp_platform_key(bugreport_apk_path)
    push_to_device(serial_number, bugreport_apk_path,
                   app_path["BugReportSender"]["device_path"])


def build_and_push_setup_wizard(serial_number, config):
    app_path = get_app_paths()
    setup_wizard_apk_path = build_setup_wizard(config)
    logs.echo_title(f'Push setup_wizard app on device {serial_number}')
    push_to_device(serial_number, setup_wizard_apk_path,
                   app_path["YandexSetupWizard"]["device_path"])


def build_updater(config):
    logs.echo_title('Build Updater app')
    if config["skip_build_updater"] == 'false':
        process = subprocess.run(f'''./gradlew assembleAlexandriaTvUiLoggedRelease \
            -p tv/updater-app/app \
            -PupdateChannel=updater \
            -Pproduct=tv \
            --no-daemon \
            -Pupdater.config.server=local \
            -Pupdater.config.port=8888 \
            -Pupdater.config.ssl_enabled=false \
            -Pyandex_signer.sign_release={config["is_sign_apps"]}''', shell=True)
        if process.returncode != 0:
            logs.echo_title('Build Updater app failed')
            sys.exit(1)

    return get_full_path_to_apk('Updater', 'release')


def build_video_player(config):
    logs.echo_title('Build Video Player apps')
    if config["skip_build_video_player"] == 'false':
        tasks = [
            'input-service:assembleDebug',
            'tv:assembleDebug',
            'video:assembleDebug',
            'web:assembleX86Debug'
        ]
        for task in tasks:
            process = subprocess.run(f'''./gradlew \
                {task} \
                -p tv/video-player \
                -Pproduct=tv \
                -Pyandex_signer.sign_debug={config["is_sign_apps"]}''', shell=True)
            if process.returncode != 0:
                logs.echo_title(f'Build {task} failed')
                sys.exit(1)

    input_service_apk_path = get_full_path_to_apk('YandexTvInputService', 'debug')
    tv_apk_path = get_full_path_to_apk('YandexLiveTv', 'debug')
    video_apk_path = get_full_path_to_apk('YandexVideoPlayer', 'debug')
    web_apk_path = get_full_path_to_apk('YandexWebPlayer', 'debug')
    return input_service_apk_path, tv_apk_path, video_apk_path, web_apk_path


def build_bugreportsender(config):
    logs.echo_title('Build bugreportsender app')
    if config["skip_build_services"] == 'false':
        process = subprocess.run(f'''./gradlew \
            bugreportsender-app:assembleDebug \
            -p tv/services \
            -Pproduct=tv \
            -Pyandex_signer.sign_debug={config["is_sign_apps"]}''', shell=True)
        if process.returncode != 0:
            logs.echo_title('Build bugreportsender app failed')
            sys.exit(1)

    return get_full_path_to_apk('BugReportSender', 'debug')


def build_setup_wizard(config):
    logs.echo_title('Build setup-wizard app')
    if config["skip_build_services"] == 'false':
        process = subprocess.run(f'''./gradlew \
            assembleEmulatorDebug \
            -p tv/setup-wizard \
            -Pproduct=tv \
            -Pyandex_signer.sign_debug={config["is_sign_apps"]}''', shell=True)
        if process.returncode != 0:
            logs.echo_title('Build setup-wizard app failed')
            sys.exit(1)

    return get_full_path_to_apk('YandexSetupWizard', 'debug')


def build_services(config):
    logs.echo_title('Build Services apps')
    if config["skip_build_services"] == 'false':
        process = subprocess.run(f'''./gradlew \
            services-platform-app:assembleDebug \
            app:assembleDebug \
            services-iosdk-app:assembleEmulatorDebug \
            -p tv/services \
            -Pproduct=tv \
            -Pyandex_signer.sign_debug={config["is_sign_apps"]}''', shell=True)
        if process.returncode != 0:
            logs.echo_title('Build Services apps failed')
            sys.exit(1)

    iosdk = get_full_path_to_apk('ServicesIosdk', 'debug')
    services_app = get_full_path_to_apk('TvServices', 'debug')
    platform_services = get_full_path_to_apk('TvPlatformServices', 'debug')
    return iosdk, services_app, platform_services


def build_services_test_app():
    logs.echo_title('Build services test_app')
    process = subprocess.run(f'''./gradlew assembleDebug -p tv/services/test-app''', shell=True)
    if process.returncode != 0:
        logs.echo_title('Build services test app failed')
        sys.exit(1)


def install_services_test_app(serial_number):
    logs.echo_title('Install services test_app')
    process = subprocess.run(f'''ANDROID_SERIAL="{serial_number}" ./gradlew installDebug \
            -p tv/services/test-app''', shell=True)
    if process.returncode != 0:
        logs.echo_title('Install services test app failed')
        sys.exit(1)


def build_services_test_app_client(gradle_task):
    logs.echo_title(f'Build services test_app_client {gradle_task}')
    process = subprocess.run(f'''./gradlew {gradle_task} -p tv/services/test-app-client''',
                             shell=True)
    if process.returncode != 0:
        logs.echo_title(f'Build {gradle_task} failed')
        sys.exit(1)


def build_updater_tests_app(gradle_task, build_config):
    logs.echo_title(f'Build {gradle_task}')
    process = subprocess.run(f'''BUILD_NUMBER="{build_config["build_number"]}" \
                ./gradlew -p tv/updater-app/app {gradle_task} \
                -Pgradle.minify_debug=false \
                -Pyandex_signer.sign_debug={build_config["is_sign_apps"]} \
                -Pyandex_account.test.login="{build_config["ya_login"]}" \
                -Pyandex_account.test.password="{build_config["ya_pass"]}"''', shell=True)
    if process.returncode != 0:
        logs.echo_title(f'Build {gradle_task} failed')
        sys.exit(1)


def build_quasar_app(gradle_task, build_config):
    logs.echo_title(f'Build {gradle_task}')
    if build_config["is_sign_apps"] == 'true' and build_config["is_emulator"] == 'false':
        oauth = f'-Pyandex-signer-oauth={build_config["signer_token"]}'
    else:
        oauth = ''
    process = subprocess.run(f'''BUILD_NUMBER="{build_config["build_number"]}" \
                ./gradlew -p quasar-app {gradle_task} {oauth}''', shell=True)
    if process.returncode != 0:
        logs.echo_title(f'Build {gradle_task} failed')
        sys.exit(1)


def build_quasar_daemons():
    logs.echo_title('Build quasar daemons')
    quasar_daemons_folder_path = 'tv/ci/ui-tests/build/quasar_bin'
    # remove old build folder
    if os.path.exists(quasar_daemons_folder_path):
        os.system(f'rm -rf {quasar_daemons_folder_path}')

    process = subprocess.run(f'''../../ya package \
                ../platforms/yandexstation_2/emulator/packages/daemons.json \
                --build minsizerel \
                --raw-package-path {quasar_daemons_folder_path}''', shell=True)
    if process.returncode != 0:
        logs.echo_title(f'Build quasar daemons failed')
        sys.exit(1)
    shutil.move(os.path.join(quasar_daemons_folder_path, 'install_root'),
                os.path.join(quasar_daemons_folder_path, 'quasar'))


def start_quasar_daemons(serial_number):
    logs.echo_title(f'Start quasar daemons on device {serial_number}')
    print('execute ./vendor/quasar/onboot.sh')
    subprocess.Popen(f'adb -s {serial_number} shell "./vendor/quasar/onboot.sh"',
                     shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def restart_quasar_daemons_if_needed(serial_number):
    command = 'ps -Af | grep maind | grep -v grep'
    process_list = subprocess.getoutput(f'adb -s {serial_number} shell "{command}"')
    if process_list == '':
        logs.echo_title("Quasar daemons are not running! Try to re-run")
        print('execute ./vendor/quasar/run.sh')
        os.system(f'adb -s {serial_number} shell "./vendor/quasar/run.sh"')
        print('process list:')
        os.system(f'adb -s {serial_number} shell "{command}"')
    else:
        logs.echo_title("Quasar daemons are already running:")
        print(process_list)


def build_centaur_app(gradle_task, build_config):
    logs.echo_title(f'Build {gradle_task}')
    process = subprocess.run(f'''BUILD_NUMBER="{build_config["build_number"]}" \
                ./gradlew -p centaur-app {gradle_task} \
                -Pyandex_signer.sign_debug={build_config["is_sign_apps"]} \
                -Pyandex_account.test.login="{build_config["ya_login"]}" \
                -Pyandex_account.test.password="{build_config["ya_pass"]}" \
                -PisTestOnEmulator=true''', shell=True)
    if process.returncode != 0:
        logs.echo_title(f'Build {gradle_task} failed')
        sys.exit(1)


def build_home_app(gradle_task, build_config):
    logs.echo_title(f'Build {gradle_task}')
    process = subprocess.run(f'''BUILD_NUMBER="{build_config["build_number"]}" \
                ./gradlew -p tv/home-app/app {gradle_task} \
                -Pproduct=tv \
                -Pgradle.minify_debug=false \
                -Pyandex_signer.sign_debug={build_config["is_sign_apps"]} \
                -Pyandex_account.test.login="{build_config["ya_login"]}" \
                -Pyandex_account.test.password="{build_config["ya_pass"]}" \
                -PlocalhostUrlForTests='"'{build_config["localhost_url"]}'"' \
                -PdroidekaUrlForTests='"'{build_config["droideka_url"]}'"' \
                {build_config["gradle_property_for_emulator"]}''', shell=True)
    if process.returncode != 0:
        logs.echo_title(f'Build {gradle_task} failed')
        sys.exit(1)


def download_and_install_orchestrator(serial_number):
    orchestrator_url = 'https://maven.google.com/androidx/test/orchestrator/1.4.1/orchestrator-1.4.1.apk'
    orchestrator_local_path = 'tv/ci/ui-tests/build/orchestrator.apk'
    services_url = 'https://maven.google.com/androidx/test/services/test-services/1.4.1/test-services-1.4.1.apk'
    services_local_path = 'tv/ci/ui-tests/build/test-services.apk'

    if not check_if_app_installed(serial_number, 'androidx.test.orchestrator'):
        print('\nDownload and install orchestrator app:')
        os.system(f'mkdir -p tv/ci/ui-tests/build')
        if not os.path.isfile(orchestrator_local_path):
            print(f'Download orchestrator from {orchestrator_url}')
            os.system(f'wget --quiet {orchestrator_url} -O {orchestrator_local_path}')
        install_app(serial_number, orchestrator_local_path)

    if not check_if_app_installed(serial_number, 'androidx.test.services'):
        print('\nDownload and install test-services app:')
        os.system(f'mkdir -p tv/ci/ui-tests/build')
        if not os.path.isfile(services_local_path):
            print(f'Download test-services from {services_url}')
            os.system(f'wget --quiet {services_url} -O {services_local_path}')
        install_app(serial_number, services_local_path)


def get_apps_path_for_emulator_api(api):
    if api == '25':
        yandex_tv_home_device_path = 'device_path'
        all_settings_apk_local_path = 'downloaded_path_api_25'
        android_tv_settings_device_path = 'device_path'
    elif api == '28':
        yandex_tv_home_device_path = 'device_path'
        all_settings_apk_local_path = 'downloaded_path_api_28'
        android_tv_settings_device_path = 'device_path'
    else:
        yandex_tv_home_device_path = 'device_path_api30'
        all_settings_apk_local_path = 'downloaded_path_api_30'
        android_tv_settings_device_path = 'device_path_api30'

    return yandex_tv_home_device_path, all_settings_apk_local_path, android_tv_settings_device_path
