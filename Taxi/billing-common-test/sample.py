# coding: utf8
from sampling import sampler


class TestSampler(sampler.YtSampler):
    def process_row(self, row: dict):
        data = row.get('data')
        if not data:
            return None
        data['performer'][
            'driver_license_personal_id'
        ] = 'driver_license_personal_id'
        if data['zone'] == 'samara':
            data['performer']['zone'] = 'samara'
            data['performer']['db_id'] = '6c1d3ae91fbc4de4abc2d002ffb6c8d4'
            data['performer']['unique_driver_id'] = '5cc7dfecd0be228bcea375bb'
            data['performer'][
                'tariff_category_id'
            ] = '3a6ff8341498444180ecd297be9a19a5'
        elif data['zone'] == 'moscow':
            data['tariff_class'] = 'econom'
            data['performer']['zone'] = 'moscow'
            data['performer']['db_id'] = '53c5fd41ff49404b87ab4870af6bcff6'
            data['performer']['unique_driver_id'] = '56386152135f0475720a1929'
            data['performer'][
                'tariff_category_id'
            ] = '648500062d3b461eac88f6da29c5b58e'
        else:
            data['zone'] = 'samara'
            data['performer']['zone'] = 'samara'
            data['performer']['db_id'] = '6c1d3ae91fbc4de4abc2d002ffb6c8d4'
            data['performer']['unique_driver_id'] = '5cc7dfecd0be228bcea375bb'
            data['performer'][
                'tariff_category_id'
            ] = '3a6ff8341498444180ecd297be9a19a5'
