from ciso8601 import parse_datetime_as_naive

from nile.api.v1 import clusters
from projects.support.data_context.plotva_loader import (
    DataContext as PlotvaLogsContext,
)


def test_plotva_loader(load_json):
    job = clusters.MockCluster().job()
    dc = PlotvaLogsContext(
        job=job,
        begin_dttm=parse_datetime_as_naive('2020-02-02T00:00:00Z'),
        end_dttm=parse_datetime_as_naive('2020-02-12T00:00:00Z'),
    )
    dc.get_ml_requests(
        fields=['first', 'second'], models_uri=['first_uri', 'second_uri'],
    )
    dc.get_http_requests(
        fields=['first', 'second'], models_uri=['first_uri', 'second_uri'],
    )
