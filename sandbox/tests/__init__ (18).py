from __future__ import absolute_import, unicode_literals

import io
import os
import gzip
import hashlib
import tarfile
import binascii

import six
import pytest
import requests

from sandbox.common import mds as common_mds
from sandbox.common.mds import stream as common_mds_stream
from sandbox.common.mds import compression as common_mds_compression
from sandbox.common import itertools as common_itertools
from sandbox.common.types import resource as ctr

from sandbox.tests.common.mds import random_data, tar_file, tgz_file


def _tar_mem(path, _):
    buf = io.BytesIO()
    listdir = os.listdir
    os.listdir = lambda _: sorted(listdir(_))
    try:
        with tarfile.open(fileobj=buf, mode="w", format=tarfile.GNU_FORMAT) as tar:
            tar.add(path, arcname=os.path.basename(path))
        buf.seek(0)
        return buf
    finally:
        os.listdir = listdir


def _sha1_blocks(dir_metadata):
    block_size = common_mds.HashCalculator.SHA1_BLOCK_SIZE
    blocks = []
    for i, sha1_block in enumerate(dir_metadata.sha1_blocks):
        size = block_size if block_size * (i + 1) <= dir_metadata.size else dir_metadata.size - block_size * i
        blocks.append((size, sha1_block))
    return blocks


class TestS3(object):
    def test__s3_upload_file_path(self, s3_simulator, sample_file):
        filename, filepath, filedata = sample_file

        s3_key1 = common_mds.S3().upload_file(filepath, filename, executable=False)[0]
        assert s3_key1 == filename
        assert requests.get(common_mds.s3_link(s3_key1)).content == filedata
        s3_key2 = common_mds.S3().upload_file(filepath, filename, executable=False)[0]
        assert s3_key1 == s3_key2

        resource_id = 123
        s3_key3 = common_mds.S3().upload_file(filepath, filename, executable=False, resource_id=resource_id)[0]
        assert s3_key3 == "{}/{}".format(resource_id, filename)
        assert requests.get(common_mds.s3_link(s3_key3)).content == filedata

        custom_backet = "mybucket"
        s3_key4 = common_mds.S3().upload_file(
            filepath, filename, executable=False, namespace=custom_backet
        )[0]
        assert s3_key4 == filename
        mds_url = common_mds.s3_link(s3_key4, namespace=custom_backet)
        assert requests.get(mds_url).content == filedata

    def test__s3_upload_file_object(self, s3_simulator, sample_file, tmpdir):
        filename, filepath, filedata = sample_file

        with open(filepath, "rb") as f, pytest.raises(AssertionError):
            common_mds.S3().upload_file(f, filename)
        with open(filepath, "rb") as f, pytest.raises(AssertionError):
            common_mds.S3().upload_file(f, filename, size=len(filedata))
        with open(filepath, "rb") as f, pytest.raises(AssertionError):
            common_mds.S3().upload_file(f, filename, executable=False)
        with open(filepath, "rb") as f:
            s3_key = common_mds.S3().upload_file(f, filename, size=len(filedata), executable=False)[0]
        assert requests.get(common_mds.s3_link(s3_key)).content == filedata

        for chunk_size in (1, 2, 3, 4, 5, 6, common_mds_stream.DEFAULT_CHUNK_SIZE):
            downloaded_filepath = os.path.join(str(tmpdir), "downloaded_resource" + str(chunk_size))
            os.mkdir(downloaded_filepath)
            fake_resource = {
                "id": 1,
                "mds": {
                    "key": s3_key,
                    "namespace": None
                },
                "file_name": filename,
                "multifile": False,
                "size": len(filedata),
                "executable": False,
                "md5": hashlib.md5(filedata).hexdigest()
            }

            downloaded_filename = common_mds_stream.read_from_mds(
                fake_resource, downloaded_filepath, chunk_size=chunk_size
            )
            assert downloaded_filename.endswith(filename)
            with open(downloaded_filename, "rb") as f:
                downloaded_filedata = f.read()
                assert downloaded_filedata == filedata, "{}\n{}".format(downloaded_filedata, filedata)

    def test__s3_upload_directory(self, s3_simulator, sample_dir, tmpdir, file1_data, file2_data):
        empty_dir = os.path.join(str(tmpdir), "empty")
        os.mkdir(empty_dir)
        resource_id = 1
        s3_key, metadata = common_mds.S3().upload_directory(empty_dir, resource_id=resource_id, tar_dir=True)
        empty_dir_name = os.path.basename(empty_dir)
        assert s3_key == "{}/{}.tar".format(resource_id, empty_dir_name)
        metadata = list(six.moves.map(dict, metadata))
        assert len(metadata) == 3
        assert metadata[0]["key"] == s3_key
        assert metadata[0]["path"] == empty_dir_name + ".tar"
        assert metadata[0]["type"] == ctr.FileType.TARDIR
        assert metadata[1:] == [
            dict(common_mds.schema.MDSFileMeta.create(
                type=ctr.FileType.DIR, path=""
            )),
            dict(common_mds.schema.MDSFileMeta.create(
                type=ctr.FileType.DIR, path=empty_dir_name
            ))
        ]
        assert requests.get(common_mds.s3_link(str(resource_id))).json() == metadata

        sample_dir_path, sample_dir_metadata = sample_dir
        resource_id = 2
        s3_key, metadata = common_mds.S3().upload_directory(sample_dir_path, resource_id=resource_id, tar_dir=True)
        assert s3_key == "{}/{}.tar".format(resource_id, os.path.basename(sample_dir_path))
        metadata[:] = list(six.moves.map(dict, metadata[2:]))
        metadata.sort(key=lambda _: _["path"])
        assert list(six.moves.map(lambda _: dict(_, offset=None), metadata)) == sample_dir_metadata
        dir_metadata = sorted(requests.get(common_mds.s3_link(str(resource_id))).json()[2:], key=lambda _: _["path"])
        assert dir_metadata == metadata
        tar_data = requests.get(common_mds.s3_link(s3_key)).content
        for item_index, data in ((2, file1_data), (4, file2_data)):
            item = dir_metadata[item_index]
            assert tar_data[item["offset"]:item["offset"] + item["size"]] == data

        def dir_list(path):
            cur_dir_list = []
            for root, dirs, files in os.walk(path):
                cur_dir_list.append(root[len(path):])
                for f in files:
                    cur_dir_list.append(os.path.join(root, f)[len(path):])
                for d in dirs:
                    dirname = os.path.join(root, d)
                    if os.path.islink(dirname):
                        cur_dir_list.append(dirname[len(path):])
            return sorted(cur_dir_list)
        sample_dir_list = dir_list(sample_dir_path)

        for chunk_size in (1024, 50000, 82324, common_mds_stream.DEFAULT_CHUNK_SIZE, 1 << 30):
            downloaded_filepath = os.path.join(str(tmpdir), "downloaded_resource" + str(chunk_size))
            os.mkdir(downloaded_filepath)
            fake_resource = {
                "id": 2,
                "mds": {
                    "key": s3_key,
                    "namespace": None
                },
                "file_name": "resource",
                "multifile": True,
                "size": dir_metadata[0]["size"],
                "executable": False
            }

            downloaded_dirname = common_mds_stream.read_from_mds(
                fake_resource, downloaded_filepath, chunk_size=chunk_size
            )
            assert downloaded_dirname.endswith("resource")
            downloaded_dir_list = dir_list(downloaded_dirname)
            assert sample_dir_list == downloaded_dir_list, "{}, {}".format(sample_dir_list, downloaded_dir_list)
            for sample_path, downloaded_path in zip(sample_dir_list, downloaded_dir_list):
                sample_full_path = os.path.join(sample_dir_path, sample_path)
                downloaded_full_path = os.path.join(downloaded_dirname, downloaded_path)
                if os.path.isfile(sample_full_path):
                    assert os.path.isfile(downloaded_full_path)
                    with open(sample_full_path) as f1:
                        with open(downloaded_full_path) as f2:
                            assert f1.read() == f2.read()
                elif os.path.isdir(sample_full_path):
                    assert os.path.isdir(downloaded_full_path)
                elif os.path.islink(sample_full_path):
                    assert os.path.islink(downloaded_full_path)
                    assert os.readlink(sample_full_path) == os.readlink(downloaded_full_path)

    @pytest.mark.parametrize("tar_packer", [tar_file], ids=["tar_file"])
    def test__s3_upload_tar(self, s3_simulator, tar_sample_dir, tmpdir, tar_packer, file1_data, file2_data):
        resource_id = 1
        s3_name = "test_tar"
        sample_dir_path, sample_dir_metadata = tar_sample_dir
        file_obj = tar_packer(sample_dir_path, tmpdir)
        file_obj.seek(0, os.SEEK_END)
        size = file_obj.tell()
        file_obj.seek(0)
        s3_key, metadata = common_mds.S3().upload_tar(file_obj, s3_name, resource_id=resource_id, size=size)
        assert s3_key == "{}/{}".format(resource_id, s3_name), s3_key

        mds_metadata = requests.get(common_mds.s3_link(str(resource_id))).json()
        metadata[:] = list(six.moves.map(dict, metadata))
        assert mds_metadata[0] == metadata[0], (mds_metadata[0], metadata[0])
        mds_metadata.pop(0)

        file_obj.seek(0)
        data = file_obj.read()

        item1 = mds_metadata[3]
        assert item1["type"] == ctr.FileType.FILE
        assert data[item1["offset"]:item1["offset"] + item1["size"]] == file1_data
        item2 = mds_metadata[5]
        assert item2["type"] == ctr.FileType.FILE
        assert data[item2["offset"]:item2["offset"] + item2["size"]] == file2_data

        assert sorted(
            [dict(_, offset=None) for _ in mds_metadata], key=lambda _: _["path"]
        ) == [dict(_, offset=None) for _ in sample_dir_metadata]

    @pytest.mark.parametrize("tar_packer", [tgz_file], ids=["file"])
    def test__s3_upload_tgz(self, s3_simulator, tar_sample_dir, tmpdir, tar_packer, file1_data, file2_data):
        resource_id = 1
        s3_name = "test_tgz"
        sample_dir_path, sample_dir_metadata = tar_sample_dir
        file_obj = tar_packer(sample_dir_path, tmpdir)
        file_obj.seek(0, os.SEEK_END)
        size = file_obj.tell()
        file_obj.seek(0)
        s3_key, metadata = common_mds.S3().upload_tar(
            file_obj, s3_name, resource_id=resource_id, size=size,
            compression_type=common_mds_compression.base.CompressionType.TGZ
        )
        assert s3_key == "{}/{}".format(resource_id, s3_name), s3_key

        mds_metadata = requests.get(common_mds.s3_link(str(resource_id))).json()
        metadata[:] = list(six.moves.map(dict, metadata))
        assert mds_metadata[0] == metadata[0], (mds_metadata[0], metadata[0])
        mds_metadata.pop(0)

        index_dump = requests.get(common_mds.s3_link(s3_key + ".index")).content
        index = common_mds_compression.gzip.Index.load(index_dump)

        for i, data in ((3, file1_data), (5, file2_data)):
            item = mds_metadata[i]
            assert item["type"] == ctr.FileType.FILE
            point = index.get_point(item["offset"])
            file_obj.seek(point.comp_offset)
            assert b"".join(iter(index.extract(file_obj, point, item["offset"], item["size"]))) == data

        assert sorted(
            [dict(_, offset=None) for _ in mds_metadata], key=lambda _: _["path"]
        ) == [dict(_, offset=None) for _ in sample_dir_metadata]

    def test__s3_upload_bad_tgz(self, s3_simulator):
        resource_id = 1
        s3_name = "test_tgz"
        data = b"\0" * 10240
        size = len(data)
        index = common_mds_compression.gzip.Index()
        with pytest.raises(common_mds_compression.gzip.ZException) as e:
            index.build(data)
        assert str(e.value) == "zlib error: DATA_ERROR"
        file_obj = io.BytesIO(data)
        s3_key, metadata = common_mds.S3().upload_tar(
            file_obj, s3_name, resource_id=resource_id, size=size,
            compression_type=common_mds_compression.base.CompressionType.TGZ
        )
        assert s3_key == "{}/{}".format(resource_id, s3_name), s3_key
        mds_metadata = requests.get(common_mds.s3_link(str(resource_id))).json()
        metadata[:] = list(six.moves.map(dict, metadata))
        assert mds_metadata[0] == metadata[0]
        assert len(mds_metadata) == 3
        error_meta = mds_metadata[2]
        assert error_meta["type"] == ctr.FileType.ERROR
        assert error_meta["path"] == "zlib error: DATA_ERROR"

    def test__s3_upload_bad_tar(self, s3_simulator):
        resource_id = 1
        s3_name = "test_tar"
        data = b"\1" * 10240
        size = len(data)
        file_obj = io.BytesIO(data)
        s3_key, metadata = common_mds.S3().upload_tar(
            file_obj, s3_name, resource_id=resource_id, size=size,
            compression_type=common_mds_compression.base.CompressionType.TAR
        )
        assert s3_key == "{}/{}".format(resource_id, s3_name), s3_key
        mds_metadata = requests.get(common_mds.s3_link(str(resource_id))).json()
        metadata[:] = list(six.moves.map(dict, metadata))
        assert mds_metadata[0] == metadata[0]
        assert len(mds_metadata) == 3
        error_meta = mds_metadata[2]
        assert error_meta["type"] == ctr.FileType.ERROR
        assert error_meta["path"] == "invalid header"

    def test__s3_upload_tgz_with_root_dir(self, s3_simulator):
        resource_id = 1
        s3_name = "test_tgz"
        file = io.BytesIO()
        tgz = tarfile.open(fileobj=file, mode="w:gz")
        tgz.add("/", recursive=False)
        file_data = b"some data"
        file_info = tarfile.TarInfo(name="file")
        file_info.size = len(file_data)
        tgz.addfile(file_info, fileobj=io.BytesIO(file_data))
        tgz.close()
        data = file.getvalue()
        size = len(data)
        file_obj = io.BytesIO(data)
        s3_key, metadata = common_mds.S3().upload_tar(
            file_obj, s3_name, resource_id=resource_id, size=size,
            compression_type=common_mds_compression.base.CompressionType.TGZ
        )
        assert s3_key == "{}/{}".format(resource_id, s3_name), s3_key
        mds_metadata = requests.get(common_mds.s3_link(str(resource_id))).json()
        metadata[:] = list(six.moves.map(dict, metadata))
        assert mds_metadata[0] == metadata[0]
        file_offset = mds_metadata[2]["offset"]
        assert file_offset
        assert mds_metadata == [
            dict(common_mds.schema.MDSFileMeta.create(
                type=ctr.FileType.FILE, path=s3_name, key=s3_key, md5=hashlib.md5(data).hexdigest(),
                sha1_blocks=metadata[0]["sha1_blocks"], size=len(data), mime="application/gzip"
            )),
            dict(common_mds.schema.MDSFileMeta.create(
                type=ctr.FileType.DIR, path=""
            )),
            dict(common_mds.schema.MDSFileMeta.create(
                type=ctr.FileType.FILE, path="file", size=len(file_data), offset=file_offset,
                mime=common_mds.MimeTypes.get_type("file", file_data)
            )),
        ]

    @pytest.mark.parametrize("tar_packer", [tar_file, _tar_mem], ids=["file", "mem"])
    def test__s3_upload_directory_from_tar(
        self, s3_simulator, sample_dir, tmpdir, tar_packer, file1_data, file2_data
    ):
        empty_dir = os.path.join(str(tmpdir), "empty")
        os.mkdir(empty_dir)
        empty_dir_name = os.path.basename(empty_dir)
        resource_id = 1
        s3_key, metadata = common_mds.S3().upload_directory(
            tar_packer(empty_dir, tmpdir), resource_id=resource_id, tar_dir=True
        )
        assert s3_key == "{}/{}.tar".format(resource_id, empty_dir_name)
        metadata = list(six.moves.map(dict, metadata))[2:]
        assert metadata == [dict(common_mds.schema.MDSFileMeta.create(
            type=ctr.FileType.DIR, path=empty_dir_name
        ))]
        assert requests.get(common_mds.s3_link(str(resource_id))).json()[2:] == metadata

        resource_id = 2
        s3_key, metadata = common_mds.S3().upload_directory(
            tar_packer(empty_dir, tmpdir), resource_id=resource_id, tar_dir=True
        )
        assert s3_key == "{}/{}.tar".format(resource_id, empty_dir_name)

        sample_dir_path, sample_dir_metadata = sample_dir

        resource_id = 3
        s3_key, metadata = common_mds.S3().upload_directory(
            tar_packer(sample_dir_path, tmpdir), resource_id=resource_id, tar_dir=True
        )
        assert s3_key == "{}/{}.tar".format(resource_id, os.path.basename(sample_dir_path))
        metadata[:] = map(dict, metadata[2:])
        metadata.sort(key=lambda _: _["path"])
        assert [
            dict(_, offset=None) for _ in metadata
        ] == [dict(_, offset=None) for _ in sample_dir_metadata]
        assert sorted(
            [dict(_, offset=None) for _ in requests.get(common_mds.s3_link(str(resource_id))).json()[2:]],
            key=lambda _: _["path"]
        ) == [dict(_, offset=None) for _ in metadata]
        tar_data = requests.get(common_mds.s3_link(s3_key)).content
        assert tar_data[metadata[2]["offset"]:metadata[2]["offset"] + metadata[2]["size"]] == file1_data
        assert tar_data[metadata[4]["offset"]:metadata[4]["offset"] + metadata[4]["size"]] == file2_data

    @pytest.mark.parametrize("tar_packer", [tar_file, _tar_mem], ids=["file", "mem"])
    def test__s3_upload_empty_file_as_directory_from_tar(self, s3_simulator, empty_file, tmpdir, tar_packer):
        file_path, file_metadata = empty_file
        resource_id = 1
        mds_key, metadata = common_mds.S3().upload_directory(
            tar_packer(file_path, tmpdir), resource_id=resource_id, tar_dir=True
        )
        empty_file_name = "{}/{}.tar".format(resource_id, os.path.basename(file_path))
        assert mds_key == empty_file_name
        metadata = list(six.moves.map(dict, metadata))[2:]
        assert metadata == file_metadata, metadata
        dir_metadata = requests.get(common_mds.s3_link(str(resource_id))).json()[2:]
        assert dir_metadata == metadata, (dir_metadata, metadata)

    def test__s3_delete_file(self, s3_simulator, sample_file):
        filename, filepath, filedata = sample_file
        s3_key = common_mds.S3().upload_file(filepath, filename)[0]
        assert requests.get(common_mds.s3_link(s3_key)).content == filedata
        assert common_mds.S3().delete(s3_key, False)
        assert requests.get(common_mds.s3_link(s3_key)).status_code == requests.codes.NOT_FOUND
        assert common_mds.S3().delete(s3_key, False)

    def test__s3_delete_old_style_directory(self, s3_simulator, sample_dir_old_style, file1_data, file2_data):
        sample_dir_path, sample_dir_metadata = sample_dir_old_style
        s3_key, metadata = common_mds.S3().upload_directory(sample_dir_path, tar_dir=False)
        assert s3_key == os.path.basename(sample_dir_path)
        metadata[:] = list(six.moves.map(dict, metadata))
        metadata.sort(key=lambda _: _["path"])
        assert metadata == sample_dir_metadata
        assert sorted(
            requests.get(common_mds.s3_link(s3_key)).json(),
            key=lambda _: _["path"]
        ) == metadata
        assert requests.get(common_mds.s3_link(metadata[2]["key"])).content == file1_data
        assert requests.get(common_mds.s3_link(metadata[4]["key"])).content == file2_data

        assert common_mds.S3().delete(metadata[2]["key"], False)
        assert requests.get(common_mds.s3_link(metadata[2]["key"])).status_code == requests.codes.NOT_FOUND

        assert common_mds.S3().delete(s3_key, True)
        assert requests.get(common_mds.s3_link(metadata[2]["key"])).status_code == requests.codes.NOT_FOUND
        assert requests.get(common_mds.s3_link(metadata[4]["key"])).status_code == requests.codes.NOT_FOUND
        assert requests.get(common_mds.s3_link(s3_key)).status_code == requests.codes.NOT_FOUND
        assert not common_mds.S3().delete(s3_key, True)

    def test__s3_prepare_skyboned_metadata(self, s3_simulator, sample_dir):
        sample_dir_path, _ = sample_dir
        resource_id = 1
        s3_key, _ = common_mds.S3().upload_directory(sample_dir_path, resource_id=resource_id, tar_dir=True)
        dir_metadata = [
            common_mds.schema.MDSFileMeta.create(__filter_empty__=True, **item)
            for item in requests.get(common_mds.s3_link(str(resource_id))).json()
        ]
        torrent_items, links, hashes = common_mds.S3().prepare_skyboned_metadata(dir_metadata)
        dir_metadata.sort(key=lambda _: _.path)
        assert torrent_items == {
            "resource": {"type": ctr.FileType.DIR},
            "resource/empty": {"type": ctr.FileType.DIR},
            "resource/file1": {
                "type": ctr.FileType.FILE,
                "md5": dir_metadata[4].md5,
                "size": dir_metadata[4].size,
                "executable": False,
            },
            "resource/subdir": {"type": ctr.FileType.DIR},
            "resource/subdir/file2": {
                "type": ctr.FileType.FILE,
                "md5": dir_metadata[6].md5,
                "size": dir_metadata[6].size,
                "executable": False,
            },
            "resource/subdir/symlink": {"type": ctr.FileType.SYMLINK, "target": b"../file1"},
            "resource/subdir_symlink": {"type": ctr.FileType.SYMLINK, "target": b"subdir"},
        }
        tar_link = common_mds.s3_link(s3_key)
        assert links == {
            item.md5: {tar_link: {"Range": "bytes={}-{}".format(item.offset, item.offset + item.size - 1)}}
            for item in (dir_metadata[4], dir_metadata[6])
        }
        assert hashes == {
            item.md5: b"".join(
                binascii.unhexlify(six.ensure_binary(_))
                for _ in item.sha1_blocks
            )
            for item in (dir_metadata[4], dir_metadata[6])
        }


class TestHashCalculator(object):
    def test__sha1_blocks(self):
        data = os.urandom(common_mds.HashCalculator.SHA1_BLOCK_SIZE * 4)

        reference_blocks = [
            hashlib.sha1(chunk).hexdigest()
            for chunk in common_itertools.chunker(data, common_mds.HashCalculator.SHA1_BLOCK_SIZE)
        ]

        for chunk_size in (
            common_mds.HashCalculator.SHA1_BLOCK_SIZE // 4,
            common_mds.HashCalculator.SHA1_BLOCK_SIZE // 2,
            common_mds.HashCalculator.SHA1_BLOCK_SIZE,
            common_mds.HashCalculator.SHA1_BLOCK_SIZE * 2,
            len(data)
        ):
            hashes = common_mds.HashCalculator()
            for chunk in common_itertools.chunker(data, chunk_size):
                hashes.update(chunk)
            hashes.stop()
            assert list(hashes.sha1_blocks) == reference_blocks

        data = os.urandom(common_mds.HashCalculator.SHA1_BLOCK_SIZE + 1)
        reference_blocks = [
            hashlib.sha1(chunk).hexdigest()
            for chunk in common_itertools.chunker(data, common_mds.HashCalculator.SHA1_BLOCK_SIZE)
        ]

        hashes = common_mds.HashCalculator()
        hashes.update(data[:1])
        hashes.update(data[1:])
        hashes.stop()
        assert list(hashes.sha1_blocks) == reference_blocks

        hashes = common_mds.HashCalculator()
        hashes.update(data[:common_mds.HashCalculator.SHA1_BLOCK_SIZE])
        hashes.update(data[common_mds.HashCalculator.SHA1_BLOCK_SIZE:])
        hashes.stop()
        assert list(hashes.sha1_blocks) == reference_blocks


class TestGzipIndex(object):
    DEFAULT_DATA_SIZE = 5 << 20  # 5 MiB
    MAX_SPAN_WITH_ZERO_ENTROPY = 4 << 20  # 4 MiB

    class BytesIO(io.BytesIO):
        def __init__(self, data=None):
            self.offset = None
            self.size = 0
            super(TestGzipIndex.BytesIO, self).__init__(data)

        def seek(self, offset, *_):
            self.offset = offset
            return super(TestGzipIndex.BytesIO, self).seek(offset, *_)

        def read(self, size=None):
            self.size += size
            return super(TestGzipIndex.BytesIO, self).read(size)

    @staticmethod
    def sample_data(size=DEFAULT_DATA_SIZE, entropy=0.):
        data = b"".join(random_data(size, entropy))
        comp_data_file_obj = io.BytesIO()
        with gzip.GzipFile(fileobj=comp_data_file_obj, mode="wb") as f:
            f.write(data)
        comp_data = comp_data_file_obj.getvalue()
        return data, comp_data

    @pytest.mark.parametrize(
        "data_size", (DEFAULT_DATA_SIZE, DEFAULT_DATA_SIZE + common_mds_compression.gzip.Index.WIN_SIZE // 2)
    )
    @pytest.mark.parametrize(
        "entropy", (0, .1, .5, .9, 1)
    )
    def test__build(self, data_size, entropy):
        data, comp_data = self.sample_data(data_size, entropy)
        index = common_mds_compression.gzip.Index()

        assert index.build(comp_data) == data
        total_points = data_size // (self.MAX_SPAN_WITH_ZERO_ENTROPY if entropy == 0 else index.DEFAULT_SPAN)
        assert total_points <= len(index) <= total_points + 1

        assert index.build(b"") == b""
        index.flush()
        with pytest.raises(common_mds_compression.gzip.ZException) as e:
            index.build(b"")
        assert str(e.value) == "zlib error: STREAM_END"

        for chunk_size in (common_mds_compression.gzip.Index.CHUNK_SIZE // 4, data_size // 100):
            index2 = common_mds_compression.gzip.Index()
            data2 = b"".join(map(index2.build, common_itertools.chunker(comp_data, chunk_size)))
            assert data2 == data
            assert index2 == index

    @pytest.mark.parametrize(
        "data_size", (DEFAULT_DATA_SIZE, DEFAULT_DATA_SIZE + common_mds_compression.gzip.Index.WIN_SIZE // 2)
    )
    @pytest.mark.parametrize(
        "entropy", (0, .1, .5, .9, 1)
    )
    def test__extract(self, data_size, entropy):
        data, comp_data = self.sample_data(data_size, entropy)
        index = common_mds_compression.gzip.Index()
        index.build(comp_data)
        buf = io.BytesIO(comp_data)
        point = index.get_point(0)

        buf.seek(point.comp_offset)
        assert b"".join(iter(index.extract(buf, point, 0, len(data)))) == data
        buf.seek(point.comp_offset)
        assert b"".join(iter(index.extract(buf, point, 0, len(data) + 100500))) == data

        win_size = common_mds_compression.gzip.Index.WIN_SIZE
        for offset, size in (
            (0, win_size // 2),
            (0, win_size),
            (0, win_size * 2),
            (win_size // 2, win_size // 2),
            (win_size // 2, win_size),
            (win_size // 2, win_size * 2),
            (data_size - win_size * 2, win_size * 2),
            (data_size - win_size, win_size),
            (data_size - win_size // 2, win_size // 2),
            (data_size - win_size * 2, win_size // 2),
            (data_size - win_size * 2, win_size - 1),
            (data_size - win_size * 2, win_size),
            (data_size - win_size * 2, win_size + 1),
        ):
            buf = self.BytesIO(comp_data)
            point = index.get_point(offset)
            buf.seek(point.comp_offset)
            extracted_data = b"".join(iter(index.extract(buf, point, offset, size)))
            assert extracted_data == data[offset:offset + size], (offset, size)
            assert buf.offset == point.comp_offset
            cur_point = index.get_point(offset + size - 1)
            assert cur_point.comp_offset <= buf.offset + buf.size

    def test__dump(self):
        data, comp_data = self.sample_data(entropy=.9)
        index = common_mds_compression.gzip.Index()
        index.build(comp_data)
        dump = index.dump()
        index2 = common_mds_compression.gzip.Index.load(dump)
        assert index == index2
        index3 = common_mds_compression.base.Index.load(dump)
        assert index == index3

        offsets = [len(data) // 3, len(data) * 2 // 3]
        size = len(data) // 3
        index4 = common_mds_compression.base.Index.load(index.dump(offsets))
        assert len(index4) == len(offsets)
        for offset in offsets:
            buf = io.BytesIO(comp_data)
            point = index.get_point(offset)
            buf.seek(point.comp_offset)
            extracted_data = b"".join(iter(index.extract(buf, point, offset, size)))
            assert extracted_data == data[offset:offset + size], (offset, size)


@pytest.fixture()
def patched_os_walk(monkeypatch):
    os_walk = os.walk

    def walk(*_, **__):
        for root, dirs, files in sorted(os_walk(*_, **__)):
            yield root, sorted(dirs), sorted(files)

    monkeypatch.setattr(os, "walk", walk)


@pytest.fixture()
def root_dir_path(tmpdir):
    dir_path = os.path.join(str(tmpdir), "dir")
    os.mkdir(dir_path)
    return dir_path


@pytest.fixture()
def file_data():
    return b"sample file data"


@pytest.fixture()
def short_file_path(root_dir_path, file_data):
    long_file_name = "short_file_name"
    long_file_path = os.path.join(root_dir_path, long_file_name)
    open(long_file_path, "wb").write(file_data)
    return long_file_path


@pytest.fixture()
def long_file_path(root_dir_path, file_data):
    long_file_name = "f" * (tarfile.LENGTH_NAME + 20)
    long_file_path = os.path.join(root_dir_path, long_file_name)
    open(long_file_path, "wb").write(file_data)
    return long_file_path


@pytest.fixture()
def long_symlink_to_short_file(root_dir_path, short_file_path):
    long_symlink_name = "l" * (tarfile.LENGTH_NAME + 10)
    long_symlink_path = os.path.join(root_dir_path, long_symlink_name)
    os.symlink(os.path.basename(short_file_path), long_symlink_path)
    return long_symlink_path


@pytest.fixture()
def short_symlink_to_long_file(root_dir_path, long_file_path):
    short_symlink_name = "short_symlink_name"
    short_symlink_path = os.path.join(root_dir_path, short_symlink_name)
    os.symlink(os.path.basename(long_file_path), short_symlink_path)
    return short_symlink_path


@pytest.fixture()
def long_symlink_to_long_file(root_dir_path, long_file_path):
    long_symlink_name = "l" * (tarfile.LENGTH_NAME + 10)
    long_symlink_path = os.path.join(root_dir_path, long_symlink_name)
    os.symlink(os.path.basename(long_file_path), long_symlink_path)
    return long_symlink_path


def tar_iter(data):
    for i in range(0, len(data), tarfile.BLOCKSIZE):
        yield data[i: i + tarfile.BLOCKSIZE]


@pytest.mark.usefixtures("patched_os_walk")
class TestTARBuilder(object):
    @staticmethod
    def test__long_file(root_dir_path, file_data, long_file_path):
        root_dir_name = os.path.basename(root_dir_path)
        long_file_name = os.path.join(root_dir_name, os.path.basename(long_file_path))

        tar_builder = common_mds.TARBuilder(root_dir_path)
        tar_data = tar_builder.read()
        assert len(tar_data) == tarfile.BLOCKSIZE * 5
        tar_data_it = tar_iter(tar_data)

        header = common_mds.tar_header(next(tar_data_it))
        assert header.type == tarfile.DIRTYPE
        assert header.name == root_dir_name

        header = common_mds.tar_header(next(tar_data_it))
        assert header.type == tarfile.GNUTYPE_LONGNAME
        assert header.size == len(long_file_name) + 1
        file_name = six.ensure_str(next(tar_data_it)[:header.size].rstrip(b"\0"))
        assert file_name == long_file_name

        header = common_mds.tar_header(next(tar_data_it))
        assert header.type == tarfile.REGTYPE
        assert header.name == long_file_name[:tarfile.LENGTH_NAME]
        assert header.size == len(file_data)
        assert next(tar_data_it)[:header.size] == file_data

    @staticmethod
    def test__long_symlink_to_short_file(root_dir_path, file_data, long_symlink_to_short_file, short_file_path):
        root_dir_name = os.path.basename(root_dir_path)
        file_base_name = os.path.basename(short_file_path)
        file_name = os.path.join(root_dir_name, file_base_name)
        symlink_name = os.path.join(root_dir_name, os.path.basename(long_symlink_to_short_file))

        tar_builder = common_mds.TARBuilder(root_dir_path)
        tar_data = tar_builder.read()
        assert len(tar_data) == tarfile.BLOCKSIZE * 6
        tar_data_it = tar_iter(tar_data)

        header = common_mds.tar_header(next(tar_data_it))
        assert header.type == tarfile.DIRTYPE
        assert header.name == root_dir_name

        header = common_mds.tar_header(next(tar_data_it))
        assert header.type == tarfile.GNUTYPE_LONGNAME
        assert header.size == len(symlink_name) + 1
        long_name = six.ensure_str(next(tar_data_it)[:header.size].rstrip(b"\0"))
        assert long_name == symlink_name

        header = common_mds.tar_header(next(tar_data_it))
        assert header.type == tarfile.SYMTYPE
        assert header.name == symlink_name[:tarfile.LENGTH_NAME]
        assert header.linkname == file_base_name

        header = common_mds.tar_header(next(tar_data_it))
        assert header.type == tarfile.REGTYPE
        assert header.name == file_name
        assert header.size == len(file_data)
        assert next(tar_data_it)[:header.size] == file_data

    @staticmethod
    def test__short_symlink_to_long_file(root_dir_path, file_data, short_symlink_to_long_file, long_file_path):
        root_dir_name = os.path.basename(root_dir_path)
        file_base_name = os.path.basename(long_file_path)
        file_name = os.path.join(root_dir_name, file_base_name)
        symlink_name = os.path.join(root_dir_name, os.path.basename(short_symlink_to_long_file))

        tar_builder = common_mds.TARBuilder(root_dir_path)
        tar_data = tar_builder.read()
        assert len(tar_data) == tarfile.BLOCKSIZE * 8
        tar_data_it = tar_iter(tar_data)

        header = common_mds.tar_header(next(tar_data_it))
        assert header.type == tarfile.DIRTYPE
        assert header.name == root_dir_name

        header = common_mds.tar_header(next(tar_data_it))
        assert header.type == tarfile.GNUTYPE_LONGNAME
        assert header.size == len(file_name) + 1
        name = six.ensure_str(next(tar_data_it)[:header.size].rstrip(b"\0"))
        assert name == file_name

        header = common_mds.tar_header(next(tar_data_it))
        assert header.type == tarfile.REGTYPE
        assert header.name == file_name[:tarfile.LENGTH_NAME]
        assert header.size == len(file_data)
        assert next(tar_data_it)[:header.size] == file_data

        header = common_mds.tar_header(next(tar_data_it))
        assert header.type == tarfile.GNUTYPE_LONGLINK
        assert header.size == len(file_base_name) + 1
        name = six.ensure_str(next(tar_data_it)[:header.size].rstrip(b"\0"))
        assert name == file_base_name

        header = common_mds.tar_header(next(tar_data_it))
        assert header.type == tarfile.SYMTYPE
        assert header.name == symlink_name
        assert header.linkname == file_base_name[:tarfile.LENGTH_LINK]

    @staticmethod
    def test__long_symlink_to_long_file(root_dir_path, file_data, long_symlink_to_long_file, long_file_path):
        root_dir_name = os.path.basename(root_dir_path)
        file_base_name = os.path.basename(long_file_path)
        file_name = os.path.join(root_dir_name, file_base_name)
        symlink_name = os.path.join(root_dir_name, os.path.basename(long_symlink_to_long_file))

        tar_builder = common_mds.TARBuilder(root_dir_path)
        tar_data = tar_builder.read()
        assert len(tar_data) == tarfile.BLOCKSIZE * 10
        tar_data_it = tar_iter(tar_data)

        header = common_mds.tar_header(next(tar_data_it))
        assert header.type == tarfile.DIRTYPE
        assert header.name == root_dir_name

        header = common_mds.tar_header(next(tar_data_it))
        assert header.type == tarfile.GNUTYPE_LONGNAME
        assert header.size == len(file_name) + 1
        name = six.ensure_str(next(tar_data_it)[:header.size].rstrip(b"\0"))
        assert name == file_name

        header = common_mds.tar_header(next(tar_data_it))
        assert header.type == tarfile.REGTYPE
        assert header.name == file_name[:tarfile.LENGTH_NAME]
        assert header.size == len(file_data)
        assert next(tar_data_it)[:header.size] == file_data

        header = common_mds.tar_header(next(tar_data_it))
        assert header.type == tarfile.GNUTYPE_LONGLINK
        assert header.size == len(file_base_name) + 1
        name = six.ensure_str(next(tar_data_it)[:header.size].rstrip(b"\0"))
        assert name == file_base_name

        header = common_mds.tar_header(next(tar_data_it))
        assert header.type == tarfile.GNUTYPE_LONGNAME
        assert header.size == len(symlink_name) + 1
        name = six.ensure_str(next(tar_data_it)[:header.size].rstrip(b"\0"))
        assert name == symlink_name

        header = common_mds.tar_header(next(tar_data_it))
        assert header.type == tarfile.SYMTYPE
        assert header.name == symlink_name[:tarfile.LENGTH_NAME]
        assert header.linkname == file_base_name[:tarfile.LENGTH_LINK]


@pytest.mark.usefixtures("patched_os_walk")
class TestTarMetaCollector(object):
    @staticmethod
    def test__long_file(root_dir_path, file_data, long_file_path):
        root_dir_name = os.path.basename(root_dir_path)
        file_name = os.path.join(root_dir_name, os.path.basename(long_file_path))

        tar_builder = common_mds.TARBuilder(root_dir_path)
        collector = common_mds.TarMetaCollector()
        collector.process(tar_builder.read())
        metadata = collector.metadata

        assert len(metadata) == 2
        items_it = iter(metadata)

        item = next(items_it)
        assert item.type == ctr.FileType.DIR
        assert item.path == root_dir_name

        item = next(items_it)
        assert item.type == ctr.FileType.FILE
        assert item.path == file_name
        assert item.size == len(file_data)

    @staticmethod
    def test__long_symlink_to_short_file(root_dir_path, file_data, long_symlink_to_short_file, short_file_path):
        root_dir_name = os.path.basename(root_dir_path)
        file_base_name = os.path.basename(short_file_path)
        file_name = os.path.join(root_dir_name, file_base_name)
        symlink_name = os.path.join(root_dir_name, os.path.basename(long_symlink_to_short_file))

        tar_builder = common_mds.TARBuilder(root_dir_path)
        collector = common_mds.TarMetaCollector()
        collector.process(tar_builder.read())
        metadata = collector.metadata

        assert len(metadata) == 3
        items_it = iter(metadata)

        item = next(items_it)
        assert item.type == ctr.FileType.DIR
        assert item.path == root_dir_name

        item = next(items_it)
        assert item.type == ctr.FileType.SYMLINK
        assert item.path == symlink_name
        assert item.symlink == file_base_name

        item = next(items_it)
        assert item.type == ctr.FileType.FILE
        assert item.path == file_name
        assert item.size == len(file_data)

    @staticmethod
    def test__short_symlink_to_long_file(root_dir_path, file_data, short_symlink_to_long_file, long_file_path):
        root_dir_name = os.path.basename(root_dir_path)
        file_base_name = os.path.basename(long_file_path)
        file_name = os.path.join(root_dir_name, file_base_name)
        symlink_name = os.path.join(root_dir_name, os.path.basename(short_symlink_to_long_file))

        tar_builder = common_mds.TARBuilder(root_dir_path)
        collector = common_mds.TarMetaCollector()
        collector.process(tar_builder.read())
        metadata = collector.metadata

        assert len(metadata) == 3
        items_it = iter(metadata)

        item = next(items_it)
        assert item.type == ctr.FileType.DIR
        assert item.path == root_dir_name

        item = next(items_it)
        assert item.type == ctr.FileType.FILE
        assert item.path == file_name
        assert item.size == len(file_data)

        item = next(items_it)
        assert item.type == ctr.FileType.SYMLINK
        assert item.path == symlink_name
        assert item.symlink == file_base_name

    @staticmethod
    def test__long_symlink_to_long_file(root_dir_path, file_data, long_symlink_to_long_file, long_file_path):
        root_dir_name = os.path.basename(root_dir_path)
        file_base_name = os.path.basename(long_file_path)
        file_name = os.path.join(root_dir_name, file_base_name)
        symlink_name = os.path.join(root_dir_name, os.path.basename(long_symlink_to_long_file))

        tar_builder = common_mds.TARBuilder(root_dir_path)
        collector = common_mds.TarMetaCollector()
        collector.process(tar_builder.read())
        metadata = collector.metadata

        assert len(metadata) == 3
        items_it = iter(metadata)

        item = next(items_it)
        assert item.type == ctr.FileType.DIR
        assert item.path == root_dir_name

        item = next(items_it)
        assert item.type == ctr.FileType.FILE
        assert item.path == file_name
        assert item.size == len(file_data)

        item = next(items_it)
        assert item.type == ctr.FileType.SYMLINK
        assert item.path == symlink_name
        assert item.symlink == file_base_name
