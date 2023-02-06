import os
import shutil

from lagg.state import param_from_state_file, read_params, update_state_file


TEST_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_DATA_DIR = os.path.join(TEST_DIR, 'test_data')
TEST_STATE_FILE = os.path.join(TEST_DATA_DIR, 'state')


def test_state(tap):
    with tap.plan(3, 'Проверяем функции для работы со стейт файлом'):
        if os.path.exists(TEST_DATA_DIR):
            shutil.rmtree(TEST_DATA_DIR)
        os.mkdir(TEST_DATA_DIR)

        with open(TEST_STATE_FILE, 'w') as f:
            pos, inode = '0', '0'
            f.write(f'inode={inode}\tpos={pos}')

        tap.eq_ok(read_params(TEST_STATE_FILE), {'pos': pos, 'inode': inode}, 'Чтение параметров')
        tap.eq_ok(param_from_state_file(TEST_STATE_FILE, 'pos'), pos, 'Чтение одного параметра')

        new_inode, new_pos = 1, 1
        update_state_file(TEST_STATE_FILE, 'inode', new_inode)
        update_state_file(TEST_STATE_FILE, 'pos', new_pos)

        with open(TEST_STATE_FILE) as f:
            tap.eq_ok(f.readline(), f'inode={new_inode}\tpos={new_pos}', 'Обновление параметров')

        shutil.rmtree(TEST_DATA_DIR)
