import contextlib
import os
import shutil
import tempfile

import pytest

import dmp_suite.datetime_utils as dtu
from dmp_suite.maintenance.accident import local_storage
from dmp_suite.maintenance.accident import Accident


@contextlib.contextmanager
def _create_tmpdir():
    tmp_path = None
    try:
        tmp_path = tempfile.mkdtemp(prefix='accident_test')

        yield tmp_path
    finally:
        if tmp_path is not None:
            shutil.rmtree(tmp_path)


class TestAccident(object):

    def test_lazy_filesystem_accident(self):
        accident_path = os.path.join(os.path.dirname(__file__), 'data')
        client = local_storage.LocalFileAccidentClient(accident_path)

        # file is not exists
        with pytest.raises(Exception):
            local_storage._LazyLocalAccident(client, '20180322082510_not_exists')

        accident = local_storage._LazyLocalAccident(
            client, '20190502000001_header_v1'
        )
        assert bool(accident.accident_id)
        assert accident.task == 'test'
        assert accident.run_id == '12345'
        assert (
            accident.creation_dttm == dtu.parse_datetime('2019-05-02 00:00:01')
        )

        accident = local_storage._LazyLocalAccident(
            client, '20190502000001_header_v2'
        )
        assert accident.accident_id == '635eda0e-b458-466b-8c34-40e05857ee02'
        assert accident.task == 'test'
        assert accident.run_id == '12345'
        assert (
            accident.creation_dttm == dtu.parse_datetime('2019-05-02 00:00:01')
        )

    def test_file_name(self):
        client = local_storage.LocalFileAccidentClient(os.path.dirname(__file__))

        accident = Accident(
            task='accident_test',
            creation_dttm=dtu.parse_datetime('2018-03-22 08:25:10'),
            description='test'
        )

        name = client.to_file_name(accident)
        assert  name.startswith('20180322082510')
        assert len(name) == 51

        name = client.to_file_name(accident, as_temp=True)
        assert  name.startswith('.20180322082510')
        assert len(name) == 52

    def _assert_accidents(self, saved_accidents, result_accidents):
        assert len(saved_accidents) == len(result_accidents)
        saved_accidents = sorted(saved_accidents, key=lambda a: a.creation_dttm)
        result_accidents = sorted(result_accidents, key=lambda a: a.creation_dttm)
        for index in range(0, len(result_accidents)):
            sa = saved_accidents[index]
            ra = result_accidents[index]
            assert sa.task == ra.task
            assert sa.creation_dttm == ra.creation_dttm
            assert sa.description == ra.description

    def test_save_and_get(self):
        with _create_tmpdir() as path:
            client = local_storage.LocalFileAccidentClient(path)
            accident = Accident(
                task='accident_test',
                creation_dttm=dtu.parse_datetime('2018-03-22 08:25:10'),
                description='test\nHello world'
            )
            client.save(accident)
            accidents = list(client.get_all())
            self._assert_accidents(accidents, [accident])

    def test_get_by_period(self):
        with _create_tmpdir() as path:
            client = local_storage.LocalFileAccidentClient(path)
            accident1 = Accident(
                task='accident_test',
                creation_dttm=dtu.parse_datetime('2018-03-22 10:00:00'),
                description='test\nHello world')
            accident2 = Accident(
                task='accident_test',
                creation_dttm=dtu.parse_datetime('2018-03-22 11:00:00'),
                description='test\nHello world')
            accident3 = Accident(
                task='accident/test',
                creation_dttm=dtu.parse_datetime('2018-03-22 12:00:00'),
                description='test\nHello world')

            accidents = [accident1, accident2, accident3]
            list(map(client.save, accidents))

            saved_accidents = list(client.get_by_period())
            self._assert_accidents(saved_accidents, accidents)

            saved_accidents = list(client.get_by_period(
                end_date=dtu.parse_datetime('2018-03-22 10:00:00')
            ))
            self._assert_accidents(saved_accidents, [accident1])

            saved_accidents = list(client.get_by_period(
                end_date=dtu.parse_datetime('2018-03-22 10:00:01')
            ))
            self._assert_accidents(saved_accidents, [accident1])

            saved_accidents = list(client.get_by_period(
                end_date=dtu.parse_datetime('2018-03-22 09:59:59')
            ))
            self._assert_accidents(saved_accidents, [])

            saved_accidents = list(client.get_by_period(
                start_date=dtu.parse_datetime('2018-03-22 09:59:59')
            ))
            self._assert_accidents(saved_accidents, accidents)

            saved_accidents = list(client.get_by_period(
                start_date=dtu.parse_datetime('2018-03-22 10:00:00')
            ))
            self._assert_accidents(saved_accidents, accidents)

            saved_accidents = list(client.get_by_period(
                start_date=dtu.parse_datetime('2018-03-22 10:00:01')
            ))
            self._assert_accidents(saved_accidents, [accident2, accident3])

            saved_accidents = list(client.get_by_period(
                start_date=dtu.parse_datetime('2018-03-22 10:00:01'),
                end_date=dtu.parse_datetime('2018-03-22 11:00:01')
            ))
            self._assert_accidents(saved_accidents, [accident2])

        with _create_tmpdir() as path:
            client = local_storage.LocalFileAccidentClient(path)
            saved_accidents = list(client.get_by_period())
            self._assert_accidents(saved_accidents, [])
