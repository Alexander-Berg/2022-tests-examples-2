# -*- coding: utf-8 -*-
import mock
from passport.backend.core.sync_utils.chunk_loader import ChunkLoader
from passport.backend.core.test.test_utils import PassportTestCase


TEST_STATE_FILE_PATH = '/certainly/non/existent/path/to/state'


class MockReader(mock.Mock):
    def __init__(self):
        super(MockReader, self).__init__(
            data=[],
            iter_called=False,
            pos=0,
            seek=mock.Mock(
                side_effect=lambda x: self._set_pos(x),
            ),
        )

    def _set_pos(self, pos):
        self.pos = pos

    def __iter__(self):
        return self

    def __next__(self):
        try:
            res = self.data[self.pos]
        except IndexError:
            raise StopIteration()
        self.pos += 1
        return res

    next = __next__


class ChunkLoaderTestCase(PassportTestCase):
    def setUp(self):
        self.mock_open = mock.mock_open(read_data='5')
        self.open_patch = mock.patch('passport.backend.core.sync_utils.chunk_loader.open', self.mock_open)
        self.open_patch.start()

        self.mock_os = mock.Mock(
            path=mock.Mock(
                exists=mock.Mock(
                    return_value=False,
                ),
            ),
        )
        self.os_patch = mock.patch('passport.backend.core.sync_utils.chunk_loader.os', self.mock_os)
        self.os_patch.start()

        self.mock_reader = MockReader()

    def tearDown(self):
        self.os_patch.stop()
        self.open_patch.stop()

    def setup_read_data(self, data):
        self.mock_reader.data = data

    def get_loader(self, load_state=False, chunk_size=10, save_state_chunk_threshold=2):
        return ChunkLoader(
            reader=self.mock_reader,
            state_file_path=TEST_STATE_FILE_PATH,
            load_state=load_state,
            chunk_size=chunk_size,
            save_state_chunk_threshold=save_state_chunk_threshold,
        )

    def assert_reads(self, loader, reads):
        real_reads = list(loader)
        self.assertEqual(real_reads, reads)

    def assert_state_open_called(self, n_calls=1):
        self.assertEqual(self.mock_open.call_count, n_calls)
        self.mock_open.assert_has_calls([mock.call(TEST_STATE_FILE_PATH)] * n_calls)

    def assert_saves(self, saves):
        write = self.mock_open().write
        self.assertEqual(write.call_count, len(saves))
        write.assert_has_calls([mock.call(str(save)) for save in saves])

    def test_load_state__ok(self):
        self.mock_os.path.exists.return_value = True
        loader = self.get_loader(load_state=True)

        self.mock_os.path.exists.assert_called_once_with(TEST_STATE_FILE_PATH)
        self.assert_state_open_called()
        self.mock_reader.seek.assert_called_once_with(5)
        self.assertEqual(loader.pos, 5)
        self.assertEqual(loader.reader.pos, 5)

    def test_load_state__file_does_not_exist__error(self):
        with self.assertRaisesRegexp(RuntimeError, 'State file doesn\'t exist'):
            self.get_loader(load_state=True)

    def test_no_load_state__ok(self):
        loader = self.get_loader()

        self.assert_state_open_called(0)
        self.assertEqual(loader.pos, 0)
        self.assertEqual(loader.reader.pos, 0)
        loader.reader.seek.assert_not_called()

    def test_no_load_state__state_file_already_exists__error(self):
        self.mock_os.path.exists.return_value = True
        with self.assertRaisesRegexp(RuntimeError, 'State file already exists'):
            self.get_loader()

    def test_read__ok(self):
        loader = self.get_loader()
        self.setup_read_data(list(range(100)))

        self.assert_reads(loader, [list(x) for x in [
            range(10),
            range(10, 20),
            range(20, 30),
            range(30, 40),
            range(40, 50),
            range(50, 60),
            range(60, 70),
            range(70, 80),
            range(80, 90),
            range(90, 100),
        ]])
        self.assert_saves([20, 40, 60, 80, 100])

    def test_read_with_load__ok(self):
        self.mock_os.path.exists.return_value = True
        loader = self.get_loader(load_state=True)
        self.setup_read_data(list(range(100)))

        self.assert_reads(loader, [list(x) for x in [
            range(5, 15),
            range(15, 25),
            range(25, 35),
            range(35, 45),
            range(45, 55),
            range(55, 65),
            range(65, 75),
            range(75, 85),
            range(85, 95),
            range(95, 100),
        ]])
        self.assert_saves([25, 45, 65, 85, 100])
