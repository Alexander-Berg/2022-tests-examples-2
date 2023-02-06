import argparse
import datetime

from projects.autoorder.data_context.data_context import DataContext
from projects.autoorder.project_config import get_project_cluster


SECONDS_IN_HOUR = 3600
SECONDS_IN_DAY = 24 * 3600


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--date', type=str, required=True)
    parser.add_argument('--n-days', type=int, required=True)
    parser.add_argument('--path', type=str, required=True)

    args = parser.parse_args()

    cluster = get_project_cluster(parallel_operations_limit=20, pool='taxi_ml')
    job = cluster.job()
    job = job.env(bytes_decode_mode='strict')

    begin = datetime.datetime.strptime(args.date, '%Y-%m-%d')
    end = begin + datetime.timedelta(days=args.n_days)

    data_context = DataContext(job, begin, end)

    dataset = data_context.get_dataset(hourly=False)

    places = data_context.common_context.get_places()

    pim = data_context.logs_context.get_pim()

    targets = (
        dataset.join(pim, type='inner', by=['code'], assume_small_right=True)
        .join(
            places,
            type='inner',
            by=['organization_id'],
            assume_small_right=True,
        )
        .project(
            'code',
            'date',
            'n_units_of_sku',
            'residuals_distribution',
            'shelf_life',
            'category',
            'city',
            lavka_id='organization_id',
        )
    )

    targets.put(args.path)

    job.run()
