# -*- coding: utf-8 -*-

from sandbox.projects.common import templates


UNSPECIFIED = '[unspecified-test-name]'

# TODO(mvel): Investigate the difference
JSON_REQID_KEY = 'reqdata.reqid'
JSON_RDAT_REQID_KEY = 'rdat.reqid'

# Kosher data that is passed to templates renderer
# please do not mix with search.context.data.Grouping that is debug-only
# See SEARCH-9546 and SEARCH-9548 for details.
SEARCHDATA_DOCS = 'searchdata.docs'

CHECK_FIELD = 'check_field'

OUTPUT_NAME = 'xml_search_report.html'
XML_SEARCH_TEMPLATE = templates.get_html_template(OUTPUT_NAME)


JSON = 'json'
JSON_QUERY = 'json_query'
XML = 'xml'

QUERY_DATA = {
    'web': {
        JSON: '/search/',
        JSON_QUERY: SEARCHDATA_DOCS,

        XML: '/search/xml/',
        # not used
        # 'xml_query': 'yandexsearch.response.results',
    },
    'images': {
        JSON: '/images/search/',
        JSON_QUERY: 'searchdata.images',

        XML: '/images-xml/',
        # not used
        # 'xml_query': 'yandexsearch.response.results',
    },
    'video': {
        JSON: '/video/search/',
        JSON_QUERY: 'searchdata.clips',
        # no more video xml search (since SEARCH-9953)
    },
}

RAMBLER_VAULT_KEY = "rambler_xml_key"
