from datetime import datetime

import sources_root
from connection import ctl as conn_ctl
from dmp_suite.ctl import CTL_DISABLED_UNTIL_DTTM
from dmp_suite.ctl.core import StorageEntity
from dmp_suite.ctl.extensions.domain.task import TASK_DOMAIN
from dmp_suite import datetime_utils as dtu
from dmp_suite import decorators


@decorators.try_except(5)
def disable(ctl, service_name):
    entity = StorageEntity(
        domain=TASK_DOMAIN,
        name=f'{service_name}_sla_updater_task'
    )

    ctl.set_param(
        entity,
        CTL_DISABLED_UNTIL_DTTM,
        datetime(year=2022, month=3, day=2)
    )


def main():
    ctl = conn_ctl.get_ctl()
    for service_name in sources_root.ETL_SERVICES:
        disable(ctl, service_name)


if __name__ == '__main__':
    main()