from pytest import mark
import json

from dmp_suite.func_utils import lru_cache
from taxi_etl.layer.yt.ods.yandex_form.cross_service_tag import (
    loader
)
from dmp_suite.file_utils import from_same_directory


@lru_cache(5)
def _get_raw():
    with open(from_same_directory(__file__, "data/raw.json")) as f:
        doc = json.load(f)
    return doc


def _get_doc_msg_type_untag():
    return {
        "msg_type": {
            "value": [
                {
                    "key": "819790",
                    "slug": "695699",
                    "text": "Снять тег"
                }
            ]
        }
    }


@mark.parametrize(
    "custom_node, extractor, expected", (
        ({}, 'action_code', 'tag'),
        ({}, 'id_value', 'pd_id_777'),
        ({}, 'tag_name', 'celebrity'),
        (_get_doc_msg_type_untag(), 'action_code', 'untag'),
    ))
def test_mapper(custom_node, extractor, expected):
    doc = _get_raw()
    doc['answer']['data'].update(custom_node)
    actual = loader.EXTRACTORS[extractor](doc)
    assert actual == expected
