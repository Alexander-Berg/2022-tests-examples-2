import pytest

from arc_api import components as arc_api


@pytest.fixture(name='patch_arc_read_file')
def _patch_arc_read_file(load, patch):
    def _wrapper(path, filename):
        @patch('arc_api.components.ArcClient.read_file')
        async def _read_file(*args, **kwargs):
            if kwargs:
                assert kwargs['path'] == path
            try:
                yaml_data = load(filename)
                return arc_api.ReadFileResponse(
                    header=None, content=yaml_data.encode(),
                )
            except FileNotFoundError:
                raise arc_api.ArcClientBaseError('Error')

        return _read_file

    return _wrapper


@pytest.fixture(name='patch_arc_read_file_with_path')
def _patch_arcadia_single_file_with_path(load, patch):
    def _wrapper(path):
        @patch('arc_api.components.ArcClient.read_file')
        async def _read_file(*args, **kwargs):
            filename = path.split('/')[-1] if path else ''
            try:
                yaml_data = load(filename)
                return arc_api.ReadFileResponse(
                    header=None, content=yaml_data.encode(),
                )
            except FileNotFoundError:
                raise arc_api.ArcClientBaseError('Error')

        return _read_file

    return _wrapper
