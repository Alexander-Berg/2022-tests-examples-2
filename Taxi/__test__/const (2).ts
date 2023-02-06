import {TariffClassInterval} from '../../../../types';

export const INTERVAL: TariffClassInterval = {
    category_type: 'call_center',
    time_from: '',
    time_to: '',
    name_key: '',
    day_type: 0,
    currency: 'RUB',
    minimal: 0,
    included_one_of: ['req1'],
    meters: [{trigger: 0}, {trigger: 1}],
    paid_cancel_fix: 0,
    waiting_price_type: 'fixed',
    special_taximeters: [
        {
            zone_name: 'moscow',
            price: {
                time_price_intervals: [],
                distance_price_intervals: [{step: 7, mode: 'prepay', begin: 8, price: 9}],
                time_price_intervals_meter_id: 0,
                distance_price_intervals_meter_id: 11,
            }
        }
    ],
    zonal_prices: [
        {
            price: {
                time_price_intervals: [{step: 1, mode: 'prepay', begin: 2, price: 5}],
                distance_price_intervals: [{step: 3, mode: 'prepay', begin: 4, price: 6}],
                time_price_intervals_meter_id: 12,
                distance_price_intervals_meter_id: 13,
            },
            source: 'moscow',
            destination: 'moscow',
            route_without_jams: false,
        },
        {
            price: {
                time_price_intervals: [{step: 1, mode: 'prepay', begin: 2, price: 5}],
                distance_price_intervals: [{step: 3, mode: 'prepay', begin: 4, price: 6}],
                time_price_intervals_meter_id: 12,
                distance_price_intervals_meter_id: 13,
            },
            source: null,
            destination: null,
            route_without_jams: false,
        }
    ],
    add_minimal_to_paid_cancel: false,
    summable_requirements: [
        {multiplier: 1, type: 'req1', max_price: 2},
        {type: 'req2', max_price: 4},
    ]
};
