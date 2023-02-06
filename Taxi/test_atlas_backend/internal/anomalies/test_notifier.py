from atlas_backend.domain import anomaly as _anomalies
from atlas_backend.internal.crontasks.anomalies import startrek_notifier as stn


def test_formatter_source_priority_keys():
    assert stn.SOURCE_PRIORITY.keys() == set(
        _anomalies.TaxiDowntimeOrderSource,
    )


def test_formatter():
    formatter = stn.TicketDescriptionFormatter('unittests')
    anomalies = [
        _anomalies.Anomaly(
            _id='aaaaaaa',
            start_ts=1617366480,
            end_ts=1617367130,
            status='created',
            source='all',
        ),
        _anomalies.Anomaly(
            _id='bbbbbbbb',
            start_ts=1617366980,
            end_ts=1617368130,
            status='created',
            source='vezet',
        ),
        _anomalies.Anomaly(
            _id='cccccccc',
            start_ts=1617366680,
            end_ts=1617367830,
            status='created',
            source='all',
        ),
    ]
    result = formatter.format_description(anomalies)
    expected = """
You have **3** new problems:

===[all]

(($mockserver/atlas-backend/anomalies/aaaaaaa?filters%5Bdaterange_type%5D=custom&filters%5Bdaterange_start%5D=1617366480&filters%5Bdaterange_end%5D=1617367130&filters%5Bstatuses%5D%5Bcreated%5D=true&filters%5Bstatuses%5D%5Bconfirmed%5D=true&filters%5Bstatuses%5D%5Brejected%5D=true&filters%5Bsources%5D%5Ball%5D=true aaaaaaa [2021-04-02 15:28:00; 2021-04-02 15:38:50]))
(($mockserver/atlas-backend/anomalies/cccccccc?filters%5Bdaterange_type%5D=custom&filters%5Bdaterange_start%5D=1617366680&filters%5Bdaterange_end%5D=1617367830&filters%5Bstatuses%5D%5Bcreated%5D=true&filters%5Bstatuses%5D%5Bconfirmed%5D=true&filters%5Bstatuses%5D%5Brejected%5D=true&filters%5Bsources%5D%5Ball%5D=true cccccccc [2021-04-02 15:31:20; 2021-04-02 15:50:30]))

===[vezet]

(($mockserver/atlas-backend/anomalies/bbbbbbbb?filters%5Bdaterange_type%5D=custom&filters%5Bdaterange_start%5D=1617366980&filters%5Bdaterange_end%5D=1617368130&filters%5Bstatuses%5D%5Bcreated%5D=true&filters%5Bstatuses%5D%5Bconfirmed%5D=true&filters%5Bstatuses%5D%5Brejected%5D=true&filters%5Bsources%5D%5Ball%5D=false&filters%5Bsources%5D%5Bvezet%5D=true bbbbbbbb [2021-04-02 15:36:20; 2021-04-02 15:55:30]))
"""  # noqa: E501
    assert result == expected
