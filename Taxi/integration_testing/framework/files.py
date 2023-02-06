import io
from library.python import resource
import os
import tarfile
from typing import Callable, List


class TarBuilder:
    def __init__(self):
        pass

    def __enter__(self):
        self.in_memory_file = io.BytesIO()
        self.tarfile = tarfile.open(fileobj=self.in_memory_file, mode='w')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.tarfile.closed:
            self.tarfile.close()
        if not self.in_memory_file.closed:
            self.in_memory_file.close()

    def add_file(self, src: str, dst: str, mode: int = None):
        filters: List[Callable[[tarfile.TarInfo], None]] = []
        if not os.path.exists(src):
            raise FileNotFoundError(
                f'{src} does not exists.',
            )
        if mode is not None:
            filters.append(TarBuilder.set_mode(mode))
        self.tarfile.add(src, dst, filter=TarBuilder.set_permissions)

    def add_resource(self, prefix: str, strip_prefix: bool = False, mode: int = None):
        for key, value in resource.iteritems(prefix, strip_prefix=strip_prefix):
            tar_info = tarfile.TarInfo(name=key)
            tar_info.mode = mode
            tar_info.size = len(value)
            self.tarfile.addfile(tar_info, io.BytesIO(value))

    def add_dir(self, path: str, mode: int = None):
        dir_info = tarfile.TarInfo(path)
        dir_info.type = tarfile.DIRTYPE
        dir_info.mode = mode
        self.tarfile.addfile(dir_info)

    def get_bytes(self):
        if not self.tarfile.closed:
            self.tarfile.close()

        self.in_memory_file.seek(0)
        result = self.in_memory_file.read()
        self.in_memory_file.close()

        return result

    @staticmethod
    def set_permissions(tarinfo: tarfile.TarInfo):
        tarinfo.mode = 0o777
        return tarinfo

    @staticmethod
    def apply_filters(filters: List[Callable[[tarfile.TarInfo], None]]):
        if filters is None or not any(filters):
            return None

        def apply_filters_filter(tarinfo: tarfile.TarInfo):
            for f in filters:
                f(tarinfo)

        return apply_filters_filter

    @staticmethod
    def set_mode(mode: int):
        def set_mode_filter(tarinfo: tarfile.TarInfo):
            tarinfo.mode = mode

        return set_mode_filter
