import uuid
import random

import os
import shutil
from dmp_suite.execution_utils import PidResolver


class TestPidResolver:
    _base_dir = '/tmp/yandex/taxi-dmp/pid-resolver/'

    def _get_file_name(self, run_id, pid):
        return os.path.join(self._base_dir, run_id, str(pid))

    def test_base_flow(self):
        run_id = str(uuid.uuid4())
        try:
            pid1 = random.randint(1000, 2000)
            pid2 = random.randint(2000, 40000)
            # проверим что создается файл при put-е
            pid1_w_suffix = self._put_w_assert(run_id, pid1)
            pid1_w_suffix1 = self._put_w_assert(run_id, pid1)
            pid2_w_suffix = self._put_w_assert(run_id, pid2)
            # проверим что возвращаются добавленные выше пиды
            self._assert_get(run_id, pid1, pid2)
            # проверим удаление файлов и каталога
            self._delete_w_assert(run_id, pid1_w_suffix, pid1_w_suffix1, pid2_w_suffix)
        finally:
            # подчищаем папку созданную для run_id
            run_id_path = f'{self._base_dir}{run_id}'
            # проверим что путь созданный вручную совпадает с путем возвращаемым классом
            assert PidResolver(self._base_dir)._get_dir_path(run_id) == run_id_path
            shutil.rmtree(run_id_path, ignore_errors=True)

    def _put_w_assert(self, run_id, pid):
        pid_resolver = PidResolver(self._base_dir)
        pid_w_suffix = pid_resolver.put(run_id, pid)
        fn = self._get_file_name(run_id, pid_w_suffix)
        assert os.path.exists(fn)
        return pid_w_suffix

    def _assert_get(self, run_id, pid1, pid2):
        pid_resolver = PidResolver(self._base_dir)
        pids = pid_resolver.get(run_id)
        assert sorted([pid1, pid2]) == sorted(pids)

    def _delete_w_assert(self, run_id, pid1_w_suffix, pid1_w_suffix1, pid2_w_suffix):
        pid_resolver = PidResolver(self._base_dir)
        pid_resolver.delete(run_id, pid1_w_suffix)

        # проверим что для первого pid-a первого вызова - файл удалился, а для второго вызова - остался
        assert not os.path.exists(self._get_file_name(run_id, pid1_w_suffix))
        assert os.path.exists(self._get_file_name(run_id, pid1_w_suffix1))
        pid_resolver.delete(run_id, pid1_w_suffix1)

        # удалим файл для второго пида и проверим что каталог удалился
        pid_resolver.delete(run_id, pid2_w_suffix)
        fn = self._get_file_name(run_id, pid2_w_suffix)
        assert not os.path.exists(os.path.dirname(fn))
