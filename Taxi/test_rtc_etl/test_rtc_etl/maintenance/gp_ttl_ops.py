from dmp_suite.greenplum.maintenance.partition import drop_expired, relocation_nvme_to_ssd
from init_py_env import service


drop_partition_task = drop_expired.create_task(service)
nvme_to_ssd_task = relocation_nvme_to_ssd.create_task(service)
