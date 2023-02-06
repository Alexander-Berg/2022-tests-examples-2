from zoo.optimal_offer.run_driver_offers.create_draft import (
    create_draft, create_description
)
from zoo.optimal_offer.config import get_project_cluster

BASE_PATH = '//home/taxi-analytics/driver_offers/2019-12-16_1576507329/'

if __name__ == '__main__':
    cluster = get_project_cluster()
    job = cluster.job()

    print create_draft(
        BASE_PATH + 'test',
        create_description(job.table(BASE_PATH + 'summary_table')),
        host="taxi-api-admin.taxi.tst.yandex.net"
    )
