import dataclasses
import typing

from test_taxi_billing_audit import conftest as tst

STATUS_COMPLETED = 'COMPLETED'
STATUS_CANCELLED = 'CANCELLED'
STATUS_ERROR = 'ERROR'

MARKER_DISABLED = 'Task disabled by fallback config'
MARKER_OK = 'check finished with no issues'
MARKER_FOUND_MISSING = 'missing identifiers found'
MARKER_FOUND_NO_MISSING = 'no missing identifiers found'
MARKER_FOUND_DUPLICATES = 'duplicate identifiers found'
MARKER_FOUND_NO_DUPLICATES = 'no duplicate identifiers found'
MARKER_FOUND_DIFFERENCES = 'differences found'
MARKER_FOUND_NO_DIFFERENCES = 'no differences found'
MARKER_FOUND_CHECK_SKIPPED = 'check skipped'


@dataclasses.dataclass(frozen=True)
class Markers:
    disabled: bool = False
    success: bool = False
    missing: bool = False
    duplicates: bool = False
    differences: typing.Optional[bool] = False

    @classmethod
    def from_db(cls, db: tst.MockedDB) -> 'Markers':
        _missing: bool = False
        _duplicates: bool = False
        _differences: bool = False
        _docs_vs_yt_failed: bool = False
        rows = db.read_table(tst.YT_DIR + 'results').rows
        for row in rows:
            sig = row[2:4]
            print(f'SIG = {sig}')
            _missing |= sig == ['CHECK_MISSING', 'FAILED']
            _duplicates |= sig == ['CHECK_DUPLICATES', 'FAILED']
            _differences |= sig == ['CHECK_DIFFERENCES', 'FAILED']
            _docs_vs_yt_failed |= sig == ['CHECK_DOCS_VS_YT_ISSUES', 'FAILED']

        return Markers(
            disabled=not rows,
            success=(
                bool(rows)
                and not (_missing or _duplicates or _docs_vs_yt_failed)
            ),
            missing=_missing,
            duplicates=_duplicates,
            differences=_differences,
        )

    @classmethod
    def from_log(cls, lines: typing.List[str]) -> 'Markers':
        _disabled: bool = False
        _success: bool = False
        _missing: bool = False
        _duplicates: bool = False
        _differences: bool = False

        for line in lines:
            _disabled |= MARKER_DISABLED in line
            _success |= MARKER_OK in line
            _missing |= (
                MARKER_FOUND_MISSING in line
                and MARKER_FOUND_NO_MISSING not in line
            )
            _duplicates |= (
                MARKER_FOUND_DUPLICATES in line
                and MARKER_FOUND_NO_DUPLICATES not in line
            )
            _differences |= (
                MARKER_FOUND_DIFFERENCES in line
                and MARKER_FOUND_NO_DIFFERENCES not in line
            )
        return Markers(
            disabled=_disabled,
            success=_success,
            missing=_missing,
            duplicates=_duplicates,
            differences=_differences,
        )
