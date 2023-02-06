import pytest

from mapreduce.yt.python.yt_stuff import YtConfig


@pytest.fixture(scope="module")
def yt_config(request):
    return YtConfig(
        wait_tablet_cell_initialization=True,
    )
