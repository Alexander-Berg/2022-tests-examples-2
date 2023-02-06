import random
import string
import sys
import argparse
import names

import cargo_newflow.consts as consts
from cargo_newflow.clients import parks
from cargo_newflow.clients import cargo_misc
from cargo_newflow import utils
from cargo_newflow import reporter


net_address = utils.guess_address()
reporter = reporter.ConsoleReporter()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p',
        '--phone',
        help='Courier phone. Should start with "+7000". Example: +7000XXXXXXX',
        required=False,
    )
    parser.add_argument(
        '--type',
        help='Walking or Auto courier',
        default='auto',
        choices=('auto', 'walking_courier'),
    )
    parser.add_argument(
        '--park_id', help='Park choice', default=consts.SEAM_BEAM_PARK_ID,
    )
    parser.add_argument(
        '--emulator',
        action='store_const',
        dest='park_id',
        const=consts.CHIRIK_PARK_ID,
        help='Use for adding drivers in taximeter-emulator',
    )
    parser.add_argument(
        '-n',
        '--drivers',
        help='Number of drivers to create (default: %(default)s).',
        default=1,
        type=int,
    )

    return parser.parse_args()


def make_phone_number():
    return '+7000{0}'.format(
        ''.join(random.choice(string.digits) for i in range(7)),
    )


def make_gos_number():
    allowed_letters = 'ABCEHKMOPTX'
    return '{0}{1}{2}{3}'.format(
        random.choice(allowed_letters),
        ''.join(random.choice(string.digits) for i in range(3)),
        ''.join(random.choice(allowed_letters) for i in range(2)),
        '77',
    )


def is_phone_exists(phone):
    client = parks.ParksClient(net_address=net_address)
    response = client.search_profile(phone=phone)
    if not response['profiles']:
        return False
    else:
        reporter.dump_json(f'Number {phone} already exists.')
        return True


def build_request(args, car_id=None, phone=None):

    phone = phone or args.phone or make_phone_number()

    if args.type == 'auto':
        request_body = utils.read_json('requests/create_profile.json')
        request_body['driver_profile']['car_id'] = car_id
        request_body['driver_profile']['park_id'] = args.park_id
        request_body['driver_profile']['phones'][0] = phone
        request_body['driver_profile']['first_name'] = names.get_first_name(
            gender='female',
        )
        request_body['driver_profile']['last_name'] = names.get_last_name()

        license_number = ''.join(
            random.choice('1234567890') for i in range(10)
        )
        request_body['driver_profile']['driver_license'][
            'number'
        ] = license_number
        request_body['driver_profile']['driver_license'][
            'normalized_number'
        ] = license_number

    elif args.type == 'walking_courier':
        request_body = utils.read_json('requests/create_walking_profile.json')
        request_body['operation_id'] = ''.join(
            random.choice(string.digits) for i in range(10)
        )
        request_body['first_name'] = names.get_first_name(gender='female')
        request_body['last_name'] = names.get_last_name()
        request_body['phone'] = phone

    return request_body


def main():
    args = parse_args()
    created = []
    phones = []

    if args.park_id not in consts.PARK_DIRECTOR_MAPPING.keys():
        reporter.section(f'Park {args.park_id} is not available')
        sys.exit()

    if args.drivers > 1:
        phones = ['+70004112%03d' % i for i in range(args.drivers)]

    for item in range(args.drivers):

        if args.type == 'walking_courier':
            cargo_misc_client = cargo_misc.CargoMiscClient(net_address=net_address)
            response = cargo_misc_client.create_profile(build_request(args))
            reporter.dump_json(response)
            created.append(response['driver_id'])

        elif args.type == 'auto':
            client = parks.ParksClient(net_address=net_address)

            phone = None
            if phones:
                phone = phones[item]
                if is_phone_exists(phone):
                    reporter.section('Try another mask.')
                    break

            car_request = utils.read_json('requests/create_car.json')
            car_request['number'] = make_gos_number()
            response = client.create_car(args.park_id, car_request)
            reporter.section('Car created!')
            reporter.dump_json(response)
            car_id = response['id']

            response = client.create_profile(
                park_id=args.park_id, json=build_request(args, car_id, phone),
            )

            reporter.dump_json(response)
            driver_id = response['driver_profile']['id']
            phone = response['driver_profile']['phones'][0]
            reporter.section(f'Driver created!')
            reporter.dump_json(response)
            reporter.section(f'Driver\'s phone: {phone}')
            reporter.section(f'Driver\'s uuid: {driver_id}')
            created.append(phone)

    reporter.section(f'Created drivers: \'\n\'.join({created})')


if __name__ == '__main__':
    main()
