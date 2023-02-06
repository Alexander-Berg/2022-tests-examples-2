# -*- coding: utf-8 -*-

from sandbox.projects.EntitySearch import resource_types
from sandbox.projects.EntitySearch.ner_data_build.ner_prod import EntitySearchNerDataBuild

class EntitySearchNerTestDataBuild(EntitySearchNerDataBuild):
    type = "ENTITYSEARCH_NER_TEST_DATA_BUILD"

    @property
    def targets_description(self):
        return [
            ('search/wizard/entitysearch/data/ner_test/search/wizard/entitysearch/data/ner_test', 'ner_test', \
                resource_types.ENTITY_SEARCH_NER_TEST_DATA, 'search/wizard/entitysearch/data/ner_test')
        ]
