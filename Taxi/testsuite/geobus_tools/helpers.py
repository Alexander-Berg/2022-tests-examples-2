# pylint: disable=import-error,invalid-name,useless-object-inheritance
# pylint: disable=undefined-variable,unused-variable,too-many-lines
# pylint: disable=no-name-in-module
# flake8: noqa F501 F401 F841 F821
import flatbuffers

import io
import gzip
import sys

import geobus.fbs.DataFormat as FbsDataFormat
import geobus.fbs.Protocol as FbsProtocol
import geobus.fbs.Message as FbsMessage
from tests_plugins import utils


def gen_gzipped_channel_message(gziped_data, now, protocol):
    data_len = len(gziped_data)

    timestamp = int(utils.timestamp(now))
    builder = flatbuffers.Builder(0)
    FbsMessage.MessageStartDataVector(builder, data_len)
    for i in reversed(gziped_data):
        builder.PrependByte(i)
    fbs_data = builder.EndVector(data_len)

    FbsMessage.MessageStart(builder)
    FbsMessage.MessageAddTimestamp(builder, timestamp)
    FbsMessage.MessageAddDataFormat(builder, FbsDataFormat.DataFormat.Gzip)
    FbsMessage.MessageAddProtocol(builder, protocol)
    FbsMessage.MessageAddData(builder, fbs_data)
    obj = FbsMessage.MessageEnd(builder)

    builder.Finish(obj)
    return bytes(builder.Output())


def gzip_builder(builder):
    object_bytes = bytes(builder.Output())

    data = io.BytesIO()
    with gzip.GzipFile(mode='wb', fileobj=data) as zfle:
        zfle.write(object_bytes)
    return data.getvalue()


def _gzip_decompress(message):
    data = io.BytesIO(message)
    with gzip.GzipFile(mode='rb', fileobj=data) as zfle:
        return zfle.read()


def parse_and_decompress_message(binary_data):
    fbs_message = FbsMessage.Message.GetRootAsMessage(binary_data, 0)
    potentially_compressed_data = fbs_message.DataAsNumpy()
    data_format = fbs_message.DataFormat()
    if data_format == FbsDataFormat.DataFormat.Gzip:
        decompressed_data = bytearray(
            _gzip_decompress(potentially_compressed_data),
        )
    if data_format == FbsDataFormat.DataFormat.NoCompression:
        decompressed_data = potentially_compressed_data
    return decompressed_data
