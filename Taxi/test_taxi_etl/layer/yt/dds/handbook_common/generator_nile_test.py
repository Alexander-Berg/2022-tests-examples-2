from mock import patch

from test_dmp_suite.testing_utils import NileJobTestCase
from test_taxi_etl.layer.yt.dds.handbook_common.generator_test_vars import MAKE_MERGE_EXPECTED_DICT, \
    MAKE_AGGREGATIONS_EXPECTED_DICT, TEST_NILE_ORDER_HANDBOOK_GENERATOR


def mocked_first(field, by, missing=None, predicate=None):
    return {"field": field, "by": by, "missing": missing, "predicate": predicate, "type": "first"}


def mocked_last(field, by, missing=None, predicate=None):
    return {"field": field, "by": by, "missing": missing, "predicate": predicate, "type": "last"}


class NileHandbookQueryGeneratorTest(NileJobTestCase):

    @patch("nile.api.v1.aggregators.first", mocked_first)
    @patch("nile.api.v1.aggregators.last", mocked_last)
    def test_make_merge_dict(self):
        generator = TEST_NILE_ORDER_HANDBOOK_GENERATOR
        res_dict = generator._make_merge_dict(generator.get_groups())
        assert res_dict == MAKE_MERGE_EXPECTED_DICT

    def test_make_aggregations_dict(self):
        generator = TEST_NILE_ORDER_HANDBOOK_GENERATOR
        aggregations_dict = generator._make_aggregations_dict(generator.get_groups())
        assert MAKE_AGGREGATIONS_EXPECTED_DICT == aggregations_dict
