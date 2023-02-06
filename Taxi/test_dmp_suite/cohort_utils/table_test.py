import pytest

from dmp_suite.cohort_utils import (
    NewbieGPTable,
    CohortGPTable,
)
from dmp_suite.cohort_utils.cohort import Cohort
from dmp_suite.cohort_utils.exceptions import (
    NoNewbieException,
    InvalidCohortError,
    TotalDimensionNotInDimensionsException,
)
from dmp_suite.greenplum import String
from dmp_suite import scales


def test_newbie_table_throws_when_invalid_cohort_accessed():
    class BullshitNewbieTable(NewbieGPTable):
        a = String()

    with pytest.raises(InvalidCohortError):
        BullshitNewbieTable.cohort


def test_cohort_table_throws_without_newbie():
    class BullshitCohortTable(CohortGPTable):
        a = String()

        __dimensions__ = [a]

    with pytest.raises(NoNewbieException):
        BullshitCohortTable.cohort


def test_cohort_throws_with_total_node_id():
    with pytest.raises(InvalidCohortError):
        Cohort(
            scale=scales.day,
            unit_key=['phone_pd_id'],
            poly_attrs=['node_id'],
            poly_attrs_w_total=['node_id']
        )


def test_cohort_table_throws_with_total():
    class NewbieTable(NewbieGPTable):
        p = String()

        __cohort_unit_key__ = ['p']
        __cohort_scale__ = scales.WeekScale

    with pytest.raises(TotalDimensionNotInDimensionsException):
        class BullshitCohortTable(CohortGPTable):
            a = String()

            __newbie__ = NewbieTable
            __dimensions__ = []
            __dimensions_w_total__ = [a]
