from pymlaas.models import resource_downloaders


def test_product():
    downloader = resource_downloaders.ProductDownloader(
        'expected_etr',
        ['1_0', '1_1'],
        ['moscow', 'test'],
        ['.json', '.info']
    )
    filenames = [
        'moscow.json',
        'moscow.info',
        'test.json',
        'test.info'
    ]
    assert downloader.filenames == filenames


def test_version_folder():
    downloader = resource_downloaders.VersionFolderDownloader(
        'model_name', ['1_0', '1_1'])
    src_keys = [
        'model_name/v_1_0/',
        'model_name/v_1_1/'
    ]
    assert downloader.src_keys == src_keys
