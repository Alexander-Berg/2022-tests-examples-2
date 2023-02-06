import os
import json

from sandbox import sdk2
from sandbox.common.enum import Enum
from sandbox.common.errors import TaskFailure
from sandbox.projects.common import binary_task
from sandbox.projects.common.BaseCompareYaMakeOutputsTask import BaseCompareYaMakeOutputsTask


PATCHED_SUFFIX = '_patched'
MAX_DIFF_LINES_PER_TEST_CASE = 500


class State(Enum):
    Enum.lower_case()

    Added = None
    Removed = None
    Modified = None
    NotChanged = None


class ColumnsNames(Enum):
    TestCase = 'TestCase'
    State = 'State'
    SOLOMON_CLUSTER = 'SolomonCluster'
    MODEL = 'Model'
    EXTRA_LABELS = 'ExtraLabels'
    METRIC_NAME = 'MetricName'
    EVENT_TIMESTAMP = 'EventTimestamp'
    DEVICE_ID = 'DeviceID'
    EVENT_NUMBER = 'EventNumber'
    EVENT_TIME_BUCKET = 'EventTimeBucket'
    RECEIVE_TIMESTAMP = 'ReceiveTimestamp'
    AGGREGATOR = 'Aggregator'


KEY_COLUMNS = [
    ColumnsNames.TestCase,
    ColumnsNames.SOLOMON_CLUSTER,
    ColumnsNames.MODEL,
    ColumnsNames.DEVICE_ID,
    ColumnsNames.EXTRA_LABELS,
    ColumnsNames.METRIC_NAME,
    ColumnsNames.EVENT_TIMESTAMP,
    ColumnsNames.EVENT_NUMBER,
    ColumnsNames.EVENT_TIME_BUCKET,
    ColumnsNames.RECEIVE_TIMESTAMP,
    ColumnsNames.AGGREGATOR,
]

SEARCH_COLUMNS = [
    ColumnsNames.State,
    ColumnsNames.TestCase,
    ColumnsNames.SOLOMON_CLUSTER,
    ColumnsNames.EXTRA_LABELS,
    ColumnsNames.METRIC_NAME,
]


def get_column_diff(canon_df, patched_df):
    removed_columns = set(canon_df.columns) - set(patched_df.columns)
    added_columns = set(patched_df.columns) - set(canon_df.columns)

    res = []
    for column in removed_columns:
        res.append({
            'name': column,
            'state': State.Removed,
        })

    for column in added_columns:
        res.append({
            'name': column,
            'state': State.Added,
        })

    return res


def render_diff(row_diff, column_diff):
    from jinja2 import Environment, PackageLoader

    env = Environment(
        loader=PackageLoader(__name__),
        trim_blocks=True, lstrip_blocks=True,
    )
    template = env.get_template('diff.html')

    return template.render(
        row_diff={
            'data': row_diff.to_json(orient='records'),
            'columns': [
                {
                    'name': column,
                    'visible': column != 'State' and not column.endswith(PATCHED_SUFFIX),
                    'searchable': column in SEARCH_COLUMNS,
                }
                for column in row_diff.columns
            ]
        },
        column_diff=column_diff,
    )


def read_tests_results(path):
    import pandas as pd

    results = []

    for filename in os.listdir(path):
        with open(os.path.join(path, filename)) as f:
            data = json.load(f)

        df = pd.DataFrame.from_records(data)
        df[ColumnsNames.TestCase] = os.path.splitext(filename)[0]
        results.append(df)
    return pd.concat(results)


def get_rows_diff(canon, patched):
    import pandas as pd

    def non_keys(columns):
        return [column for column in columns if column not in KEY_COLUMNS]

    merged = canon.merge(
        patched, how='outer', on=KEY_COLUMNS,
        suffixes=('', PATCHED_SUFFIX)
    )

    # Cut excess diff lines
    merged = merged.groupby(by=ColumnsNames.TestCase) \
        .head(MAX_DIFF_LINES_PER_TEST_CASE) \
        .reset_index(drop=True)

    # Re-order columns
    merged = merged[KEY_COLUMNS + sorted(non_keys(merged.columns))]

    columns_to_check = [
        column for column in non_keys(canon.columns)
        if {column, column + PATCHED_SUFFIX} <= set(merged.columns)
    ]

    def is_close(a, b, rel_tolerance=1e-9):
        return abs(a - b) <= rel_tolerance * max(abs(a), abs(b))

    def get_state(row):
        if pd.isna(row.MetricValue):
            return State.Added
        if pd.isna(row.MetricValue_patched):
            return State.Removed

        for column in columns_to_check:
            canon_value = row[column]
            patched_value = row[column + PATCHED_SUFFIX]

            if pd.isnull(canon_value) and pd.isnull(patched_value):
                changed = False
            elif isinstance(canon_value, float):
                changed = not is_close(canon_value, patched_value)
            else:
                changed = canon_value != patched_value

            if changed:
                return State.Modified
        else:
            return State.NotChanged

    merged[ColumnsNames.State] = merged.apply(get_state, axis=1)
    return merged[merged.State != State.NotChanged]


class QuasarCompareAggregatedMetrics(binary_task.LastBinaryTaskRelease, BaseCompareYaMakeOutputsTask):
    class Parameters(BaseCompareYaMakeOutputsTask.Parameters):
        binary_params = binary_task.binary_release_parameters(stable=True)
        fail_on_diff = sdk2.parameters.Bool('Fail task when diff is detected', default=False)

    def on_execute(self):
        binary_task.validate_resource_executor(self)
        BaseCompareYaMakeOutputsTask.on_execute(self)
        if self.Parameters.fail_on_diff and self.Context.has_diff:
            raise TaskFailure("Diff found (while fail_on_diff mode is enabled)")

    def compare(self, build_output1, build_output2, testing_out_stuff_dir):
        results_dir = os.path.join(testing_out_stuff_dir, "results")

        canon = read_tests_results(os.path.join(build_output1, results_dir))
        patched = read_tests_results(os.path.join(build_output2, results_dir))

        column_diff = get_column_diff(canon, patched)
        rows_diff = get_rows_diff(canon, patched)

        if len(column_diff) or len(rows_diff):
            diff = render_diff(rows_diff, column_diff)
            return diff.encode()
