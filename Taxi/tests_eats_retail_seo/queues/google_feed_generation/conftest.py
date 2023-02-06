import re
import xml.etree.ElementTree as ET

import pytest

from ... import constants
from ... import models


@pytest.fixture
def normalize_google_feed_xml():
    def do_normalize(xml):
        def sort_xml_items(x):
            for child in x:
                # ET changes google tags
                # so they have prefixes
                if 'id' in child.tag:
                    return child.text
            return x.text

        # XML parser preserves original spacing between tags
        # (newlines and indentation) when the document is
        # serialized back to XML. When elements are re-ordered,
        # new indentation looks broken.
        # Since this is not important and only a test detail, the spaces
        # between tags are removed from the XML.
        no_indent_xml = re.sub(r'>\s+<', '>\n<', xml)
        root = ET.fromstring(no_indent_xml)
        items = root.find('channel')
        items[:] = sorted(items, key=sort_xml_items)
        return ET.tostring(root, encoding='unicode', method='xml')

    return do_normalize


@pytest.fixture
def load_result_google_feed(generate_feed_s3_path, mds_s3_storage):
    def do_load(brand: models.Brand):
        s3_path = generate_feed_s3_path(
            constants.S3_DIRS[constants.GOOGLE_FEED_TYPE], brand,
        )
        return mds_s3_storage.storage[s3_path].data.decode('utf-8')

    return do_load
