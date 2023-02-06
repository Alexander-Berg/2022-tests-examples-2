# copy-paste
import hashlib

from replication.utils import data_helpers


def as_is(doc):
    return doc


def raw_bson(doc):
    """Returns raw bson doc from document."""
    raw_bson_doc = doc.get('__raw_bson')
    if raw_bson_doc is None:
        raise ValueError('Document does not provide __raw_bson')
    return raw_bson_doc


def bson_doc_hash(doc):
    """Calculated doc hash of bson document."""
    data = data_helpers.raw_bson(doc)
    return hashlib.sha1(data).hexdigest()


def testsuite_premap_raw(doc):
    for num in range(3):
        mapped_doc = doc.copy()
        mapped_doc['num'] = num
        mapped_doc.pop('id2')
        yield mapped_doc


def testsuite_premap_raw2(doc):
    for num2 in range(2):
        mapped_doc = doc.copy()
        mapped_doc['num_concatenated'] = str(doc['num']) + '_' + str(num2)
        yield mapped_doc


INPUT_TRANSFORM = {
    'as_is': as_is,
    'raw_bson': raw_bson,
    'bson_doc_hash': bson_doc_hash,
}

PREMAP = {
    'testsuite_premap_raw': testsuite_premap_raw,
    'testsuite_premap_raw2': testsuite_premap_raw2,
}
