import os.path

from yt_upload import loaders
from yt_upload.validation import validators


INCLUDE_DIR = os.path.join(
    os.path.dirname(__file__),
    os.pardir,
    os.pardir,
    'uploads',
    'lib',
    'conf',
    'common',
    'yt_upload_settings',
    'include',
)


def test_validate_settings(pytestconfig):
    upload_settings = pytestconfig.getoption('--yt-upload-settings')
    if not upload_settings:
        return
    for settings_path in upload_settings:
        settings_dir = os.path.join(
            os.path.dirname(__file__), os.pardir, os.pardir, settings_path,
        )
        if not os.path.exists(settings_dir):
            continue
        for dir_path, _, file_names in os.walk(settings_dir):
            for file_name in file_names:
                if not file_name.endswith('.yaml'):
                    continue
                settings_path = os.path.join(dir_path, file_name)
                raw_settings = loaders.load_raw_upload_settings(
                    settings_path, INCLUDE_DIR, validate=False,
                )
                validators.validate_settings(raw_settings, name=settings_path)
