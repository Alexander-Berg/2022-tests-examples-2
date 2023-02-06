from taxi.ml import dataloader


def test():
    loader = dataloader.SimpleDataLoader('base_path')

    assert loader.full_path('file.pth') == 'base_path/file.pth'
    assert loader.full_path('dir', 'file.pth') == 'base_path/dir/file.pth'
