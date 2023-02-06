import pytest

from taxi.billing.pgstorage import Storage

from taxi_billing_accounts.db import EntityStore


@pytest.mark.pgsql('billing_accounts@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_vshard_id_from_key(billing_accounts_storage):
    storage = billing_accounts_storage
    total = storage.meta.vshard_count

    cases = [
        ('unique_driver_id/583d4789250dd4071d3f6c09', 0x00),
        ('unique_driver_id/5b0913df30a2e52b7633b3e6', 0x01),
        ('unique_driver_id/5b6c154741e102a72fddf926', 0x02),
        ('unique_driver_id/5adf9c23a3ddb1256a8542b8', 0x03),
        ('unique_driver_id/5b6b177a41e102a72fa4e223', 0x04),
        ('unique_driver_id/598c4d2689216ea4eee49939', 0x05),
        ('unique_driver_id/5b4f48a941e102a72fefe30e', 0x06),
        ('unique_driver_id/5b60199b41e102a72fe8268c', 0x07),
        ('unique_driver_id/5b5ac3bf41e102a72f2a3792', 0x08),
        ('unique_driver_id/57de4f0f45af870f17c32702', 0x09),
        ('unique_driver_id/59d3b21816e5302735033b82', 0x0A),
        ('unique_driver_id/5a1115f551baddbf5b37dfea', 0x0B),
        ('unique_driver_id/5867bfec43e7eac9b3cbed76', 0x0C),
        ('unique_driver_id/5866185c43e7eac9b3a65e9e', 0x0D),
        ('unique_driver_id/5a12c77351baddbf5b8e4519', 0x0D),
        ('unique_driver_id/5ad4a877e342c7944bf54437', 0x0E),
        ('unique_driver_id/579202b5b10260a108ea996c', 0x0F),
        ('unique_driver_id/595d01429932ff77acea443f', 0x11),
        ('unique_driver_id/5a02ef51e222fb3650ec2d97', 0x12),
        ('unique_driver_id/5b0eeb0530a2e52b7639bd87', 0x13),
        ('unique_driver_id/5b630b4d41e102a72fb13629', 0x17),
        ('unique_driver_id/5a3a8853e696290a95cc915f', 0x1C),
        ('unique_driver_id/5b61777841e102a72f0bdaa0', 0x1E),
        ('unique_driver_id/5abce2afe342c7944ba12940', 0x1F),
        ('unique_driver_id/5acd989ae342c7944ba0d7c9', 0x2A),
        ('unique_driver_id/5a24397451baddbf5be9033b', 0x2D),
        ('unique_driver_id/56d40c466334f81564e80feb', 0x2F),
        ('unique_driver_id/5acf55aae342c7944b1a32ae', 0x38),
        ('unique_driver_id/58c27f3ab008e0bbfec66927', 0x30),
        ('unique_driver_id/59a7bf177b1e151abc0425cf', 0x3C),
        ('unique_driver_id/5a795a235fa63cc49dff5b15', 0x3E),
        ('unique_driver_id/5b3de6e3d5d94417808c8535', 0x40),
        ('unique_driver_id/59d5daddff419bf8e3378e32', 0x42),
        ('unique_driver_id/5a687f8890e5d644b1b3e89d', 0x46),
        ('unique_driver_id/5a853267278f188c76bfefb5', 0x47),
        ('unique_driver_id/58f608b54bfc0a7f34a5f63f', 0x48),
        ('unique_driver_id/59d34cc116e5302735372d8f', 0x4A),
        ('unique_driver_id/595f853c9932ff77ac4682b6', 0x57),
        ('unique_driver_id/5b117dacebac901d04adb16f', 0x57),
        ('unique_driver_id/5af5810cb14b1dc01a86093b', 0x5B),
        ('unique_driver_id/59e3c6045d11639a74fc7efa', 0x5A),
        ('unique_driver_id/5a4357c051baddbf5b3e959e', 0x60),
        ('unique_driver_id/5a30e62ae696290a957e595c', 0x61),
        ('unique_driver_id/59a99b387b1e151abca6ebbc', 0x61),
        ('unique_driver_id/56b4bee36334f81564fc7068', 0x66),
        ('unique_driver_id/5a129a5e51baddbf5b490945', 0x7A),
        ('unique_driver_id/59fd9127e222fb365056f55b', 0x7B),
        ('unique_driver_id/58ec25184bfc0a7f34915cc7', 0x7D),
        ('unique_driver_id/5a28fa94e696290a95c4cd2b', 0x81),
        ('unique_driver_id/58ff5bf34bfc0a7f34b28232', 0x83),
        ('unique_driver_id/5b4df82f41e102a72fb27e6e', 0x85),
        ('unique_driver_id/58ea638f4bfc0a7f34694634', 0x86),
        ('unique_driver_id/593bf6c143d523c4a2b91e1e', 0x88),
        ('unique_driver_id/59b273847b1e151abc3a01bf', 0x8A),
        ('unique_driver_id/5b3b8e41d5d94417806ac77c', 0x8A),
        ('unique_driver_id/5a72e3898ffdaf4b24a4ab15', 0x9F),
        ('unique_driver_id/5b1a588cebac901d04397ce9', 0xA3),
        ('unique_driver_id/5968f3539932ff77aca12794', 0xA5),
        ('unique_driver_id/5943d09e43d523c4a2aea0eb', 0xAB),
        ('unique_driver_id/5a604f70e696290a95767e2a', 0xAE),
        ('unique_driver_id/5a7d6746e696290a959346a5', 0xBC),
        ('unique_driver_id/56d1ceca6334f81564d90b60', 0xBE),
        ('unique_driver_id/59d891352f48a19996fe960c', 0xBF),
        ('unique_driver_id/5b6c608f41e102a72f65227e', 0xC7),
        ('unique_driver_id/5b6aa69841e102a72f97ed43', 0xC8),
        ('unique_driver_id/5a8fc672e342c7944b4af744', 0xCD),
        ('unique_driver_id/58ff5c7e4bfc0a7f34b2b6cf', 0xCE),
        ('unique_driver_id/57a0492c3c9cdde275b49c26', 0xD3),
        ('unique_driver_id/5af95654b14b1dc01a62f17f', 0xD7),
        ('unique_driver_id/59c2391216e530273556d5b1', 0xD9),
        ('unique_driver_id/5a5f1d0fe696290a9560562e', 0xDA),
        ('unique_driver_id/580613f721586f10feae580d', 0xE3),
        ('unique_driver_id/5b17f161ebac901d045843c4', 0xE3),
        ('unique_driver_id/5a8bcfa3278f188c7698b543', 0xE5),
        ('unique_driver_id/5a7d7995e696290a95fbfb46', 0xE6),
        ('unique_driver_id/5a1ff28751baddbf5b2a0d2f', 0xE8),
        ('unique_driver_id/5b4fa06041e102a72ff0330f', 0xEB),
        ('unique_driver_id/5addcf90a3ddb1256a84d594', 0xFE),
        ('unique_driver_id/5b67f03b41e102a72f63186c', 0xF5),
        ('unique_driver_id/59fc8994e222fb3650561293', 0xF5),
    ]

    for key, shard_id in cases:
        assert EntityStore.vshard_id(storage, key) == shard_id % total


async def test_vshard_id_from_id():
    for i in range(256):
        assert i == Storage.vshard_from_id(100000 + i)
