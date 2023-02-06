# flake8: noqa
# pylint: disable=import-error,wildcard-import

import os
import time
import tarfile
import yatest.common
from datetime import datetime

from market.proto.abo.BlueOfferFilter_pb2 import BlueOfferInfo, BlueOfferFilter
from market.pylibrary.pbufsn_utils import make_pbufsn


ABO_MAGIC = b'BOFR'
PERIODIC_TASKS_NUM = 5  # abo, cpa, cpc, supplier, mmap


def server_error(request, mockserver):
    if request.method == 'GET':
        return mockserver.make_response('', 500)
    return mockserver.make_response('Wrong method', 500)


def empty_response(request, mockserver):
    if request.method == 'GET':
        return mockserver.make_response('', 200)
    return mockserver.make_response('Wrong method', 500)


def generate_last_modified(time_point):
    seconds = time_point.second

    # Here is some delay to emulate real-life
    if seconds == 0:
        time.sleep(1)
    else:
        seconds = seconds - 1

    last_modified = datetime(
        time_point.year,
        time_point.month,
        time_point.day,
        time_point.hour,
        time_point.minute,
        seconds,
        time_point.microsecond,
    )

    return last_modified.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'


def shops_mbi_s3_bucket_response(time):
    last_modified = generate_last_modified(time)

    response = '<?xml version="1.0" encoding="UTF-8"?>'
    response += (
        '<ListBucketResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">'
    )
    response += '<KeyCount>2</KeyCount>'
    response += '<Name>dynamic/2022-05-19</Name>'
    response += '<Prefix></Prefix>'
    response += '<Delimiter>%2F</Delimiter>'
    response += '<MaxKeys>1000</MaxKeys>'
    response += '<IsTruncated>false</IsTruncated>'
    response += '<EncodingType>url</EncodingType>'

    for file, time in [
            (
                'dynamic_2022-05-19_00-47-08_e837d567.tar.gz',
                last_modified,
            ),  # TODO:
            (
                'dynamic_2022-05-19_00-58-08_361faab5.tar.gz',
                last_modified,
            ),  # TODO:
    ]:
        response += '<Contents>'
        response += '<Key>'
        response += file
        response += '</Key>'
        response += '<LastModified>'
        response += last_modified
        response += '</LastModified>'
        response += '<Owner>'
        response += '<ID>1</ID>'
        response += '<DisplayName>1</DisplayName>'
        response += '</Owner>'
        response += '<ETag>&#34;1ce971408a99471b7dd113a0f95b428d&#34;</ETag>'
        response += '<Size>1</Size>'
        response += '<StorageClass>STANDARD</StorageClass>'
        response += '</Contents>'

    response += '</ListBucketResult>'

    return response


def shops_mbi_dynamic_response(data, dir, file):
    path = yatest.common.work_path() + '/' + dir + '.mds-s3'
    if not os.path.exists(path):
        os.mkdir(path)

    dynamic_path = path + '/' + file
    with open(dynamic_path, 'w') as f:
        f.write(data)

    tar_path = path + '/dynamic.tar.gz'
    with tarfile.open(tar_path, 'w:gz') as tar:
        tar.add(dynamic_path, os.path.basename(dynamic_path))

    with open(tar_path, mode='rb', encoding=None) as f:
        content = f.read()

    return content


def abo_s3_bucket_response(time):
    last_modified = generate_last_modified(time)

    response = '<?xml version="1.0" encoding="UTF-8"?>'
    response += (
        '<ListBucketResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">'
    )
    response += '<KeyCount>2</KeyCount>'
    response += '<Name>dynamic/2022-05-19</Name>'
    response += '<Prefix></Prefix>'
    response += '<Delimiter>%2F</Delimiter>'
    response += '<MaxKeys>1000</MaxKeys>'
    response += '<IsTruncated>false</IsTruncated>'
    response += '<EncodingType>url</EncodingType>'

    for file, time in [
            (
                'market-sku-filters/current_market-sku-filters.pbuf',
                last_modified,
            ),
    ]:
        response += '<Contents>'
        response += '<Key>'
        response += file
        response += '</Key>'
        response += '<LastModified>'
        response += time
        response += '</LastModified>'
        response += '<Owner>'
        response += '<ID>1</ID>'
        response += '<DisplayName>1</DisplayName>'
        response += '</Owner>'
        response += '<ETag>&#34;1ce971408a99471b7dd113a0f95b428d&#34;</ETag>'
        response += '<Size>1</Size>'
        response += '<StorageClass>STANDARD</StorageClass>'
        response += '</Contents>'

    response += '</ListBucketResult>'

    return response


def abo_dynamic_response(path, shop_sku, times_called):
    data = [
        BlueOfferFilter(
            Infos=[
                BlueOfferInfo(
                    MarketSku=times_called,
                    SupplierId=times_called,
                    ShopSku=shop_sku,
                    ModelId=times_called,
                ),
            ],
        ),
    ]

    make_pbufsn(path=path, magic=ABO_MAGIC, proto_iter=data)
    with open(path, mode='rb', encoding=None) as f:
        reposnse = f.read()

    return reposnse


def is_bucket_list(request):
    return 'max-keys=1000&prefix=' in request.url


def mmap_s3_bucket_response(time):
    last_modified = generate_last_modified(time)

    response = '<?xml version="1.0" encoding="UTF-8"?>'
    response += (
        '<ListBucketResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">'
    )
    response += '<KeyCount>2</KeyCount>'
    response += '<Name>dynamic/2022-05-19</Name>'
    response += '<Prefix></Prefix>'
    response += '<Delimiter>%2F</Delimiter>'
    response += '<MaxKeys>1000</MaxKeys>'
    response += '<IsTruncated>false</IsTruncated>'
    response += '<EncodingType>url</EncodingType>'

    for file, time in [
            ('current_market-sku-filters.pbuf', last_modified),
            ('backup_market-sku-filters.pbuf-1', last_modified),
            ('backup_market-sku-filters.pbuf-2', last_modified),
    ]:
        response += '<Contents>'
        response += '<Key>'
        response += file
        response += '</Key>'
        response += '<LastModified>'
        response += time
        response += '</LastModified>'
        response += '<Owner>'
        response += '<ID>1</ID>'
        response += '<DisplayName>1</DisplayName>'
        response += '</Owner>'
        response += '<ETag>&#34;1ce971408a99471b7dd113a0f95b428d&#34;</ETag>'
        response += '<Size>1</Size>'
        response += '<StorageClass>STANDARD</StorageClass>'
        response += '</Contents>'

    response += '</ListBucketResult>'

    return response
