import dateutil.parser

DATETIME_FIELDS = ['accrued_at', 'last_created']


def normalize_datetimes(data):
    if isinstance(data, dict):
        return {
            k: (
                dateutil.parser.parse(v)
                if k in DATETIME_FIELDS
                else normalize_datetimes(v)
            )
            for k, v in data.items()
        }

    if isinstance(data, list):
        return [normalize_datetimes(v) for v in data]

    return data
