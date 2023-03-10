import pytest


@pytest.fixture(name='original_allocation_request')
def _original_allocation_request():
    return {
        'annotations': [],
        'anonymousMemoryLimitMegabytes': 2030,
        'anonLimitPolicy': 'AUTO',
        'enableInternet': False,
        'gpus': [],
        'labels': [],
        'memoryGuaranteeMegabytes': 2048,
        'networkBandwidthGuaranteeMegabytesPerSec': 1,
        'networkBandwidthLimitMegabytesPerSec': 1,
        'networkMacro': '_TAXI_CLOWNDUCTOR_TEST_NETS_',
        'persistentVolumes': [
            {
                'bandwidthGuaranteeMegabytesPerSec': 12,
                'bandwidthLimitMegabytesPerSec': 30,
                'diskQuotaGigabytes': 0,
                'diskQuotaMegabytes': 20480,
                'mountPoint': '/cores',
                'storageClass': 'hdd',
                'storageProvisioner': 'SHARED',
                'virtualDiskId': '',
            },
        ],
        'podNamingMode': 'RANDOM',
        'replicas': 0,
        'resourceCaches': [],
        'rootBandwidthGuaranteeMegabytesPerSec': 5,
        'rootBandwidthLimitMegabytesPerSec': 10,
        'rootFsQuotaGigabytes': 0,
        'rootFsQuotaMegabytes': 20480,
        'rootVolumeStorageClass': 'hdd',
        'snapshotsCount': 3,
        'sysctlProperties': [],
        'threadLimit': 0,
        'vcpuGuarantee': 900,
        'vcpuLimit': 1000,
        'virtualDisks': [],
        'virtualServiceIds': [],
        'workDirQuotaGigabytes': 0,
        'workDirQuotaMegabytes': 512,
    }


@pytest.fixture(name='prepared_allocation_request')
def _prepared_allocation_request():
    return {
        'annotations': [],
        'anonLimitPolicy': 'AUTO',
        'enableInternet': False,
        'gpus': [],
        'labels': [],
        'memoryGuaranteeMegabytes': 2048,
        'networkBandwidthGuaranteeMegabytesPerSec': 2,
        'networkBandwidthLimitMegabytesPerSec': 2,
        'networkMacro': '_TAXI_CLOWNDUCTOR_TEST_NETS_',
        'persistentVolumes': [
            {
                'bandwidthGuaranteeMegabytesPerSec': 20,
                'bandwidthLimitMegabytesPerSec': 48,
                'diskQuotaGigabytes': 0,
                'diskQuotaMegabytes': 32768,
                'mountPoint': '/cores',
                'storageClass': 'hdd',
                'storageProvisioner': 'SHARED',
                'virtualDiskId': '',
            },
        ],
        'podNamingMode': 'RANDOM',
        'replicas': 0,
        'resourceCaches': [],
        'rootBandwidthGuaranteeMegabytesPerSec': 8,
        'rootBandwidthLimitMegabytesPerSec': 16,
        'rootFsQuotaGigabytes': 0,
        'rootFsQuotaMegabytes': 32768,
        'rootVolumeStorageClass': 'hdd',
        'snapshotsCount': 3,
        'sysctlProperties': [],
        'threadLimit': 0,
        'vcpuGuarantee': 1440,
        'vcpuLimit': 1600,
        'virtualDisks': [],
        'virtualServiceIds': [],
        'workDirQuotaGigabytes': 0,
        'workDirQuotaMegabytes': 820,
    }
