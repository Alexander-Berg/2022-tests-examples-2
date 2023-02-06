# coding: utf-8
from taxi.core import db


def main():
    collection = db.reaction_tests.pymongo_collection
    collection.ensure_index('updated', background=True)
    assert len(collection.index_information()) == 3


if __name__ == '__main__':
    main()
