import argparse

from taxi.core import async
from taxi.core import db

@async.inline_callbacks
def main(args):
    collection = db.connections['antifraud'][0]['dbantifraud']['rules']
    result = yield collection.update(
        {
            '_id': {
                '$in': args.rules,
            }
        },
        {
            '$set': {'test': args.test}
        },
        multi=True,
    )
    print result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-r', '--rules',
        required=True,
        nargs='+',
        type=str,
    )
    parser.add_argument(
        '-t', '--test',
        required=True,
        type=lambda x: (str(x).lower() == 'true'),
    )
    main(parser.parse_args())
