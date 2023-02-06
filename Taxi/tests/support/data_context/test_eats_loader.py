from ciso8601 import parse_datetime_as_naive

from nile.api.v1 import clusters
from projects.support.data_context.eats_loader import (
    DataContext as EatsDataContext,
)


def test_eats_loader(load_json):
    job = clusters.MockCluster().job()
    dc = EatsDataContext(
        job=job,
        begin_dttm=parse_datetime_as_naive('2020-02-02T00:00:00Z'),
        end_dttm=parse_datetime_as_naive('2020-02-12T00:00:00Z'),
    )
    dc.get_tickets(plotva_fields=['first', 'second'])
