import logging

from taxi.core import db
from taxi.core import async


logger = logging.getLogger(__name__)
logging.basicConfig()


IDS = {
    # Emulator
    '999': {
        'express': '7',
        'econom': '1',
        'universal': '6',
        'minivan': '4',
        'business': '2',
        'comfortplus': '5',
        'vip': '3',
    },
    # Testing Mode RiT
    '519': {
        'express': '7',
        'econom': 'a05a2a087295e211bb790030487e046b',
        'universal': '4373091324213423421f2134df1342321',
        'minivan': '906623e56d174848be555de15ea94bcd',
        'business': 'a55a2a087295e211bb790030487e046b',
        'comfortplus': '361305488ec6450d96b137195dc0ee06',
        'vip': 'a85a2a087295e211bb790030487e046b',
    }
}


@async.inline_callbacks
def main():
    parks = yield db.parks.find({'tariffs_mrt': {'$exists': True}}).run()
    changes = db.parks.initialize_unordered_bulk_op()
    for park in parks:
        for category, mrt in park['tariffs_mrt'].iteritems():
            if 'id' not in mrt:
                park_id = park['_id']
                ids_list = IDS[park_id[:3]]
                key = 'tariffs_mrt.{0}.id'.format(category)
                update = {'$set': {key: ids_list[category]}}
                changes.find({'_id': park_id}).update(update)
                logger.error('park = %s, update = %r', park_id, update)
    yield changes.execute()


if __name__ == '__main__':
    main()

