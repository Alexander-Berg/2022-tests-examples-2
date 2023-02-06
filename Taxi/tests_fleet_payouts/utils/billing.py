# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import dateutil.parser


def doc_pk_of(doc):
    return (doc['external_obj_id'], doc['external_event_ref'])


def doc_id_of(doc):
    return doc['doc_id']


class DocStore:
    def __init__(self, docs=None):
        self.docs = []
        for doc in docs or []:
            self.add(doc)

    def by_pk(self, doc_pk):
        for doc in self.docs:
            if doc_pk_of(doc) == doc_pk:
                return doc
        return None

    def by_id(self, doc_id):
        for doc in self.docs:
            if doc_id_of(doc) == doc_id:
                return doc
        return None

    def add(self, new_doc):
        new_doc_pk = doc_pk_of(new_doc)
        new_doc_id = doc_id_of(new_doc)
        if self.by_pk(new_doc_pk):
            raise ValueError(f'Document with PK {new_doc_pk} already exists')
        if self.by_id(new_doc_id):
            raise ValueError(f'Document with ID {new_doc_id} already exists')
        self.docs.append(new_doc)

    def select(self, topic, ref, since, until):
        since = dateutil.parser.parse(since)
        until = dateutil.parser.parse(until)

        docs = []
        for doc in self.docs:
            event_at = dateutil.parser.parse(doc['event_at'])
            if doc['external_obj_id'] != topic:
                continue
            if ref is not None and ref != doc['external_event_ref']:
                continue
            if event_at < since or event_at > until:
                continue
            docs.append(doc)

        return docs
