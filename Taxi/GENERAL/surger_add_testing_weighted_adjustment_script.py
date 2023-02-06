import pymongo

from taxi.core import async
from taxi.core import db

from taxi.internal.dbh import surge_zones as surge_zones_dbh


@async.inline_callbacks
def main():
    try:
        res = yield db.surge_scripts.insert({
            'name': 'production_testing',
            'type': 'weighted_adjustment',
            'state': 'approved',
            'source': """
                function check_is_present(fname, obj) {
                    if (!(fname in obj)) {
                        throw fname + ' is not present';
                    }
                }

                function formula(settings, dep_class) {
                    let weight = (x) => 1 / (1 + x);
                    let bound_weight = (x, l, r) => l + (r - l) * weight(x);
                    let adjusted_surge = (raw, coeff, base) => raw + coeff * (base - raw);

                    check_is_present('min_adjustment_coeff', settings);
                    check_is_present('max_adjustment_coeff', settings);

                    return adjusted_surge(
                        dep_class.coeffs.value_raw,
                        bound_weight(
                            dep_class.counts.drivers.total, settings.min_adjustment_coeff,
                            settings.max_adjustment_coeff),
                        base_class.coeffs.value);
                }
            """
        })

        print('surge_scripts:', res)
    except pymongo.errors.DuplicateKeyError:
        pass

    SURGE_ZONE_NAMES = ['MSK-BOOM', 'MSK-BOOM-TTK', 'MSKDOWNTOWN']
    EXPERIMENT_NAME = 'V8'

    res = yield db.surge_zones.update(
        {
            'n': {'$in': SURGE_ZONE_NAMES},
            'forced.experiment_name': EXPERIMENT_NAME
        },
        {
            '$set': {
                'forced.$.weighted_surge_adjustment_script': 'production_testing',
                'forced.$.rules.business.weighted_surge_adjustment': {
                    'enabled': True,
                    'settings': {
                        'min_adjustment_coeff': 0.0,
                        'max_adjustment_coeff': 2.0,
                    },
                }
            }
        },
        multi=True,
        upsert=False,
    )

    print('surge_zones:', res)

if __name__ == '__main__':
    main()
