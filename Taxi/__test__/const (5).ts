import {MULTIZONE} from '../../../../../consts';
import {TariffClassInterval} from '../../../../../types';
import {REQ_TYPES} from '../../../../consts';

export const INTERVAL: TariffClassInterval = {
    minimal: '1' as any,
    waiting_price: '1' as any,
    waiting_included: '1' as any,
    round_distance_step: '1' as any,
    round_time_step: '1' as any,
    paid_cancel_fix: '1' as any,
    waiting_taximeter: '1',

    interval_index: 1,
    minimal_price: 1,

    category_type: 'call_center',
    time_from: '',
    time_to: '',
    name_key: '',
    day_type: 0,
    currency: 'RUB',
    included_one_of: ['req1'],
    meters: [{trigger: '0'} as any, {trigger: '1'} as any],
    waiting_price_type: 'fixed',
    special_taximeters: [
        {
            zone_name: 'moscow',
            time_common_taximeter: true,
            distance_common_taximeter: true,
            price: {
                time_price_intervals: [],
                distance_price_intervals: [{step: '7', mode: 'prepay', begin: '8', end: '10', price: '9'} as any],
                time_price_intervals_meter_id: 0,
                distance_price_intervals_meter_id: 11,
            }
        },
        {
            zone_name: 'moscow',
            price: {
                time_price_intervals: [],
                distance_price_intervals: [{step: '7', mode: 'prepay', begin: '8', end: '10', price: '9'} as any],
                time_price_intervals_meter_id: 0,
                distance_price_intervals_meter_id: 11,
            }
        }
    ],
    zonal_prices: [
        {
            price: {
                time_price_intervals: [{step: '1', mode: 'prepay', begin: '2', price: '5', end: '10'}],
                distance_price_intervals: [{step: '3', mode: 'prepay', begin: '4', price: '6', end: '10'}],
                time_price_intervals_meter_id: 12,
                distance_price_intervals_meter_id: 13,
                once: '2' as any,
                minimal: '3' as any,
            },
            source: 'moscow',
            destination: 'moscow',
            route_without_jams: true,
        },
        {
            price: {
                time_price_intervals: [{step: '1', mode: 'prepay', begin: '2', price: '5', end: '10'}],
                distance_price_intervals: [{step: '3', mode: 'prepay', begin: '4', price: '6', end: '10'}],
                time_price_intervals_meter_id: 12,
                distance_price_intervals_meter_id: 13,
                once: '2' as any,
                minimal: '3' as any,
            },
            source: MULTIZONE,
            destination: MULTIZONE,
            // route_without_jams: false, // чтобы проверить что эначение подсавляется маппером
        } as any
    ],
    add_minimal_to_paid_cancel: false,
    summable_requirements: [
        {
            multiplier: 1,
            type: 'req1',
            max_price: 2,
            included: true,
            req_type: REQ_TYPES.multiplier,
            price: {
                distance_multiplier: '1' as any,
                included_distance: '2' as any,
                included_time: '2' as any,
                time_multiplier: '3' as any,
            }
        },
        {
            type: 'req2',
            max_price: '4' as any,
            price: {
                distance_multiplier: '1' as any,
                included_distance: '2' as any,
                included_time: '2' as any,
                time_multiplier: '3' as any,
            }
        },
    ]
};
