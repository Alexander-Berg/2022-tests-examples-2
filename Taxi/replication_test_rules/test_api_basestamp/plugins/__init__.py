def _premap_new_doc(doc):
    yield {'id': doc['id'], 'doc': 'premapper_not_skipped'}


PREMAP = {'premap_new_doc': _premap_new_doc}
