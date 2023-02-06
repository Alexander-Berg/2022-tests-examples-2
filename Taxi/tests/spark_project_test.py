import os

from tools.service_utils import collect_services, ServiceType
from sources_root import SOURCES_ROOT


# проверяем, что для всех etl сервисов есть соответствующий проект в spark
# т.е. при заведении нового etl сервиса, нужно сразу заводить и минимальный spark
def test_spark_project_exists():
    for service_yaml in collect_services(ServiceType.ETL.value):
        assert os.path.exists(
            os.path.join(SOURCES_ROOT, 'spark', service_yaml['name'])
        )
