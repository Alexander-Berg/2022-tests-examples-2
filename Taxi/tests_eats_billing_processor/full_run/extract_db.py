#!/usr/bin/env python3

# pylint: disable=import-only-modules
import argparse
from datetime import datetime
import json

import psycopg2
from psycopg2.extras import RealDictCursor
# pylint: enable=import-only-modules


class DateTimeEncoder(json.JSONEncoder):
    # pylint: disable=E0202
    def default(self, o):
        if isinstance(o, datetime):
            return o.strftime('%Y-%m-%dT%H:%M:%SZ')

        return json.JSONEncoder.default(self, o)


def main():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('host', help='Database host name')
        parser.add_argument('port', help='Database port number')
        parser.add_argument('user', help='Database username')
        parser.add_argument('password', help='Password')
        parser.add_argument('database', help='Database name')
        parser.add_argument(
            '--ids', '-i', type=int, nargs='+', help='List of IDs',
        )
        parser.add_argument('--order_nr', '-n', help='Order number')
        # input.json as default output is intended
        parser.add_argument(
            '--output', '-o', help='Output file', default='input.json',
        )
        args = parser.parse_args()

        if (args.ids) and (args.order_nr):
            raise RuntimeError(
                'ID and order number can not be provided simultaneously',
            )

        if (not args.ids) and (not args.order_nr):
            raise RuntimeError('ID or order number must be provided')

        connection = psycopg2.connect(
            host=args.host,
            port=args.port,
            user=args.user,
            password=args.password,
            database=args.database,
        )

        cursor = connection.cursor(cursor_factory=RealDictCursor)

        result = get_json_from_db(cursor, args)

    finally:
        if connection:
            cursor.close()
            connection.close()

    save_to_output(args.output, result)


def get_json_from_db(cursor, args):
    if args.order_nr:
        cursor.execute(
            f"""select order_nr, external_id, event_at, kind, data
            from eats_billing_processor.input_events
            where order_nr = '{args.order_nr}'""",
        )
    if args.ids:
        cursor.execute(
            f"""select order_nr, external_id, event_at,
            kind, data from eats_billing_processor.input_events
            where id = ANY(ARRAY{args.ids})""",
        )

    result = []
    for raw_result in cursor:
        raw_result['data'] = json.loads(raw_result['data'])
        result.append(raw_result)

    return json.dumps(result, indent=4, cls=DateTimeEncoder)


def save_to_output(filename, data):
    with open(filename, 'w') as outfile:
        outfile.write(data)


if __name__ == '__main__':
    main()
