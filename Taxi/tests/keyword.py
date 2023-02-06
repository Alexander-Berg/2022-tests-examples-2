import random

_db = None # pylint: disable=invalid-name


def _load_db():
    # pylint: disable=global-statement,invalid-name
    global _db
    if not _db:
        _db = {'orig': {}}
        with open('hire/addons/hire/backend/utils/data/nouns.txt') as fh:
            _db['orig']['nouns'] = set(x.strip() for x in fh.readlines())
        with open('hire/addons/hire/backend/utils/data/adjectives.txt') as fh:
            _db['orig']['adjectives'] = set(
                x.strip() for x in fh.readlines())


def keyword():
    '''
       Generates a pair of English words
    '''
    _load_db()

    if 'keyword' not in _db:
        _db['keyword'] = {}
        _db['keyword']['nouns'] = list(_db['orig']['nouns'])
        _db['keyword']['adjectives'] = list(_db['orig']['adjectives'])


    radj = _db['keyword']['adjectives'].pop(
        random.randrange(0, len(_db['keyword']['adjectives'])))
    rnoun = _db['keyword']['nouns'].pop(
        random.randrange(0, len(_db['keyword']['nouns'])))

    if not _db['keyword']['adjectives']:
        del _db['keyword']
    elif not _db['keyword']['nouns']:
        del _db['keyword']

    return f'{radj} {rnoun}'


def noun():
    '''
       Generates English noun
    '''
    _load_db()

    if 'noun' not in _db:
        _db['noun'] = {}
        _db['noun'] = list(_db['orig']['nouns'])


    rnoun = _db['noun'].pop(random.randrange(0, len(_db['noun'])))

    if not _db['noun']:
        del _db['noun']
    return rnoun
