from dmp_suite.table import no_doc
from dmp_suite.yt import ETLTable, Datetime, Date, YTMeta, String
from taxi_etl.layer.yt.ods.salesforce.common.impl import convert_date_and_datetime


@no_doc(reason='Для теста')
class OdsTable(ETLTable):
    date = Date()
    string = String()
    datetime = Datetime()
    timezone_datetime = Datetime()
    incorrect = Datetime()


EXTRACTORS = dict(
    date='SimpleDate',
    string='SimpleString',
    datetime='SimpleDatetime',
    timezone_datetime='SimpleTimezoneDatetime',
    incorrect='Incorrect',
)
convert_date_and_datetime(EXTRACTORS, OdsTable)

DATA = [
    {
        'SimpleDate': '2022-01-01',
        'SimpleDatetime': '2021-03-11 15:14:30',
        'SimpleString': 'It is time',
        'SimpleTimezoneDatetime': '2022-03-01T14:35:52.053000+03:00',
        'Incorrect': 'Was ist das?'
    },
    {
        'SimpleDate': '2022-01-01 11:11:11',
        'SimpleDatetime': '2021-03-11T15:14:30.000Z',
        'SimpleString': 'It is time',
        'SimpleTimezoneDatetime': '2022-03-01T16:35:52.053000+05:00',
        'Incorrect': '2022-13-45'
    }
]

EXPECTED = {
    'date': '2022-01-01',
    'datetime': '2021-03-11 15:14:30',
    'string': b'It is time',
    'timezone_datetime': '2022-03-01 11:35:52',
    'incorrect': None,
}


def test():
    mapper = YTMeta(OdsTable).serializer(**EXTRACTORS).map
    results = mapper(DATA)
    for result in results:
        result.pop('etl_updated')
        assert result == EXPECTED
