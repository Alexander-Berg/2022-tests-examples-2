from ciso8601 import parse_datetime_as_naive

from nile.api.v1 import clusters
from projects.support.data_context.union_loader import (
    DataContext as UnionDataContext,
)


def test_union_loader(load_json):
    job = clusters.MockCluster().job()
    dc = UnionDataContext(
        job=job,
        begin_dttm=parse_datetime_as_naive('2020-02-02T00:00:00Z'),
        end_dttm=parse_datetime_as_naive('2020-02-12T00:00:00Z'),
    )
    dc.get_tickets(
        dwh_fields=['first', 'second'],
        plotva_logs=True,
        plotva_fields=['third'],
    )
