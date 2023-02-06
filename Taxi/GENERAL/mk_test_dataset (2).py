import argparse
import datetime

from projects.common.learning.feature_extraction.time_machine import (
    RangeTimepoints,
)
from projects.couriers_doxgety.data_context.data_context import DataContext
from projects.couriers_doxgety.mk_dataset import make_history_features
from projects.couriers_doxgety.model_config import WINDOWS
from projects.couriers_doxgety.project_config import (
    get_project_cluster,
    DEFAULT_MEMORY_LIMIT,
)
from projects.couriers_doxgety.timepoints import StatusRangeTimepoints


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', type=str, required=True)
    parser.add_argument('--path', type=str, required=True)
    parser.add_argument('--lagged', type=bool, required=False, default=False)

    args = parser.parse_args()

    cluster = get_project_cluster()
    job = cluster.job()
    job = job.env(
        bytes_decode_mode='strict', default_memory_limit=DEFAULT_MEMORY_LIMIT,
    )

    dttm = datetime.datetime.strptime(args.date, '%Y-%m-%d')

    features_data_context = DataContext(
        job, dttm - datetime.timedelta(days=max(WINDOWS)), dttm, dttm,
    )

    info = features_data_context.get_couriers_info()
    features_orders = features_data_context.get_orders()

    if args.lagged:
        status_history = features_data_context.get_status_history()
        timepoints = StatusRangeTimepoints(dttm, dttm, 'courier_id').apply(
            job, info, status_history,
        )
    else:
        couriers = features_data_context.get_couriers()
        timepoints = RangeTimepoints(dttm, dttm, 'courier_id').apply(couriers)

    features = make_history_features(
        job, features_orders, timepoints, info, lagged=args.lagged,
    )

    features.put(args.path)

    job.run()
