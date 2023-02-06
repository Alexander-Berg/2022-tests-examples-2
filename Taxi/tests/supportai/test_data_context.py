import datetime

from nile.api.v1 import clusters, Record
from nile.api.v1.local import StreamSource, ListSink

from projects.supportai.data_context import supportai_logs


def test_flow():
    job = clusters.MockCluster().job()
    data_context = supportai_logs.DataContext(
        job,
        begin_dttm=datetime.datetime.now(),  # not important
        end_dttm=datetime.datetime.now(),  # not important
        service_name='supportai',
    )

    logs = data_context.requests_responses()

    logs.label('output')
    output = []

    job.local_run(
        sources={
            'supportai_logs': StreamSource(
                [
                    Record(
                        link=b'2115ca19cf65421393b57858b8a4ca2e',
                        uri=b'/supportai/v1/support?project_id=ya_market_support/v1',  # noqa: E501
                        _type=b'request',
                        body=b'{}',
                        iso_eventtime=b'2020-12-08 03:00:23',
                    ),
                    Record(
                        link=b'2115ca19cf65421393b57858b8a4ca2e',
                        uri=b'/supportai/v1/support?project_id=ya_market_support/v1',  # noqa: E501
                        _type=b'response',
                        body=b'{}',
                        iso_eventtime=b'2020-12-08 03:00:24',
                        meta_code=b'200',
                    ),
                    Record(
                        link=b'2115ca19cf65421393b57858b8a4ca2f',
                        uri=b'/supportai/v1/support?project_id=detmir_dialog',
                        _type=b'request',
                        body=b'{}',
                        iso_eventtime=b'2020-12-08 03:00:25',
                        meta_code=b'200',
                    ),
                    Record(
                        link=b'2115ca19cf65421393b57858b8a4ca2f',
                        uri=b'/supportai/v1/support?project_id=detmir_dialog',
                        _type=b'response',
                        body=b'{}',
                        iso_eventtime=b'2020-12-08 03:00:25',
                        meta_code=b'200',
                    ),
                ],
            ),
        },
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 2

    assert output[0]['project'] == b'ya_market_support'
    assert output[1]['project'] == b'detmir_dialog'


def test_uris_filter():
    job = clusters.MockCluster().job()
    data_context = supportai_logs.DataContext(
        job,
        begin_dttm=datetime.datetime.now(),  # not important
        end_dttm=datetime.datetime.now(),  # not important
        service_name='plotva-ml',
    )

    logs = data_context.requests(
        uris=['/ya_market_support/v1', '/ya_drive_dialog/v1'],
    )

    logs.label('output')
    output = []

    job.local_run(
        sources={
            'supportai_logs': StreamSource(
                [
                    Record(
                        link=b'2115ca19cf65421393b57858b8a4ca2a',
                        uri=b'/ya_market_support/v1',
                        _type=b'request',
                        body=b'not important body',
                        iso_eventtime=b'2020-12-08 03:00:23',
                    ),
                    Record(
                        link=b'2115ca19cf65421393b57858b8a4ca2b',
                        uri=b'/ya_drive_dialog/v1',
                        _type=b'request',
                        body=b'not important body2',
                        iso_eventtime=b'2020-12-08 03:00:24',
                    ),
                    Record(
                        link=b'2115ca19cf65421393b57858b8a4ca2c',
                        uri=b'/smm_eats/v1',
                        _type=b'request',
                        body=b'not important body3',
                        iso_eventtime=b'2020-12-08 03:00:25',
                    ),
                ],
            ),
        },
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 2
