from pahtest.folder import _flatten, Folder


def test_flatten():
    files = _flatten('tests/unit/assets/flatten')
    shorten = [f[len('tests/unit/assets/flatten/'):] for f in files]
    assert 6 == len(shorten), shorten
    should = [
        'dict.yml', 'file.yml', 'list.yml',
        'recursive/child.yml',
        'recursive/parent.yml',
        'recursive/parent_with_relative.yml',
    ]
    assert set(should) == set(shorten), shorten


def test_files_count():
    """Count correct test files in the folder."""
    path = 'tests/unit/assets/files_count'
    assert 4 == Folder(path=path).files_count


def test_files_count_nested():
    path = 'tests/functional/assets/nested/'
    test = Folder(path=path)
    assert 3 == test.files_count
