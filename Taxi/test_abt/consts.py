import datetime

import pytz


DEFAULT_YT_CLUSTER = 'hahn'

DEFAULT_YT_PATH = '//home/testsuite/precomputes'

DEFAULT_SYS_FACETS = {
    'bucket': {'column': 'bucket'},
    'date': {'column': 'date'},
    'group': {'column': 'group'},
    'revision': {'column': 'revision'},
}

DEFAULT_VALUE_METRIC_PARAMS = {'type': 'value', 'value': 'value_column'}

DEFAULT_REVISION_STARTED_AT = datetime.datetime(
    2020, 10, 10, 10, 10, 10, tzinfo=pytz.utc,
)

DEFAULT_REVISION_ENDED_AT = None

DEFAULT_REVISION_DATA_AVAILABLE_DAYS = ['2020-09-03', '2020-10-20']

EXTENDED_REVISION_DATA_AVAILABLE_DAYS = [str(i).zfill(2) for i in range(100)]

DEFAULT_METRIC_GROUP_OWNERS = ['test_owner']

DEFAULT_METRICS_GROUP_SCOPE = 'test_scope'

DEFAULT_METRIC_GROUP_SCOPES = [DEFAULT_METRICS_GROUP_SCOPE]

DEFAULT_METRICS_GROUP_TITLE = 'test metrics group title'

DEFAULT_METRICS_GROUP_DESCRIPTION = 'test metrics group title description'

DEFAULT_METRICS_GROUP_IS_COLLAPSED = True

DEFAULT_METRICS_GROUP_ENABLED = True

DEFAULT_EXPERIMENT_NAME = 'test_experiment'

DEFAULT_EXPERIMENT_TYPE = 'experiment'

DEFAULT_EXPERIMENT_DESCRIPTION = 'test experiment description'

DEFAULT_EXPERIMENT_TRACKER_TASK = 'TEST-100500'

DEFAULT_REVISION_ID = 1

DEFAULT_REVISION_GROUP_ID = 1

DEFAULT_REVISION_GROUP_TITLE = 'test revision group'

DEFAULT_VALUE_METRIC_NAME = 'default_value_metric_name'

DEFAULT_VALUE_METRIC_TITLE = 'default_value_metric_title'

DEFAULT_VALUE_COLUMN = 'default_value_column'

DEFAULT_RATIO_METRIC_NAME = 'default_ratio_metric_name'

DEFAULT_RATIO_METRIC_TITLE = 'default_ratio_metric_title'

DEFAULT_NUMERATOR_COLUMN = 'default_numerator_column'

DEFAULT_DENOMINATOR_COLUMN = 'default_denominator_column'

DEFAULT_REVISION_COLUMN = 'revision'

DEFAULT_GROUP_COLUMN = 'group'

DEFAULT_BUCKET_COLUMN = 'bucket'

DEFAULT_DATE_COLUMN = 'date'

DEFAULT_METRIC_DESCRIPTION = 'default_metric_description'
DEFAULT_DOCS_URL_TEMPLATE = ''

DEFAULT_SORTED_BY = [
    DEFAULT_REVISION_COLUMN,
    DEFAULT_GROUP_COLUMN,
    DEFAULT_DATE_COLUMN,
    DEFAULT_BUCKET_COLUMN,
]

DEFAULT_IS_SORTED = True

DEFAULT_IS_DYNAMIC = False

DEFAULT_PRECOMPUTES_TABLE_SCHEMA = [
    {'name': 'revision', 'type': 'int64', 'sort_order': 'ascending'},
    {'name': 'group', 'type': 'uint64', 'sort_order': 'ascending'},
    {'name': 'date', 'type': 'string', 'sort_order': 'ascending'},
    {'name': 'bucket', 'type': 'int64', 'sort_order': 'ascending'},
]

SOME_FLOAT_VALUE = 1.2

UNIMPORTANT_VALUE = None

DEFAULT_BACKGROUND_COLOR = '#E7E5E1'

DEFAULT_FONT_COLOR = '#21201F'

DEFAULT_COLOR_ALIAS = 'unknown/unknown'

DEFAULT_WIKI_COLOR = 'black'

DEFAULT_METRICS_GROUP_POSITION = 0

DEFAULT_MEASURES_COL_TYPE = 'int64'

DEFAULT_OBSERVATIONS_ARGS = [{'arg': 'phone_id', 'column': 'phone_id'}]

DEFAULT_OBSERVATIONS_TIME = 'utc_dttm'

DEFAULT_OBSERVATIONS_MEASURES = ['order', 'trip']
