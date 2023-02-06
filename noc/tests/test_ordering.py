import pytest

from annlib import patching, filter_acl, tabparser
from annlib.rbparser import ordering
from . import conftest


@pytest.mark.parametrize(
    "test_file", conftest.dataglob("data/test_ordering_*.yaml")
)
def test_ordering(test_file: str):
    test_data = conftest.dataparse(test_file)
    vendor: str = test_data["vendor"]
    input: str = test_data["input"]
    output: str = test_data["output"]
    ordering_text: str = test_data["order"]
    output = conftest.strip(output)

    fmtr: tabparser.CommonFormatter
    fmtr = filter_acl.tabparser.make_formatter(vendor)
    rb = ordering.compile_ordering_text(ordering_text, vendor)
    orderer = patching.Orderer(rb, vendor)

    tree = tabparser.parse_to_tree(input, fmtr.split)
    tree = orderer.order_config(tree)
    result = fmtr.join(tree)
    open("/tmp/c", "w").write(result)

    assert result == output
