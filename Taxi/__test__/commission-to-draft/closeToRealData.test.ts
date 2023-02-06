import moment from 'moment';

import {COMMISSION_SERVICE_NAME, DRAFT_API_PATHS} from '../../../consts';
import {CommissionType} from '../../../enums';
import {CommissionView} from '../../../types';
import {commissionToDraft} from '../../matchers';

describe('commissionToDraft matcher', () => {
    test('close to real commission data', () => {
        const commission: CommissionView = {
            end: null!,
            tag: 'reposition_district_extracoms_8',
            vat: '1.18',
            type: CommissionType.AsymptoticFormula,
            zones: ['moscow'],
            asymp: '16.275',
            begin: moment('2019-12-16T00:00:00'),
            ticket: 'taxirate-20',
            cost_norm: -39.399,
            numerator: 853.8,
            expired_cost: '800',
            payment_types: ['cash'],
            agent_percent: '0.0001',
            cancel_percent: '0.11',
            max_order_cost: '6000',
            min_order_cost: '0',
            expired_percent: '0.11',
            acquiring_percent: '0',
            taximeter_payment: '5.5',
            branding_discounts: [
                {value: '0.03', marketing_level: ['lightbox']},
                {value: '0.05', marketing_level: ['co_branding', 'lightbox']},
                {value: '0.06', marketing_level: ['sticker']},
                {value: '0.05', marketing_level: ['co_branding']},
                {value: '0.06', marketing_level: ['sticker', 'lightbox']},
            ],
            park_cancel_max_td: 600,
            park_cancel_min_td: 420,
            user_cancel_max_td: 600,
            user_cancel_min_td: 120,
            max_commission_percent: '0.237',
            billable_cancel_distance: 300,
            has_fixed_cancel_percent: false,
            callcenter_commission_percent: '0',
        };

        const expected = {
            request_id: 'request_id',
            run_manually: false,
            mode: 'push',
            service_name: COMMISSION_SERVICE_NAME,
            api_path: DRAFT_API_PATHS.COMMISSIONS_CREATE,
            data: {
                commissions: [
                    {
                        agreements: [
                            {
                                cancel_rate: undefined,
                                expired_rate: '0.0011',
                                kind: 'asymptotic',
                                rate: {
                                    asymp: '16.275',
                                    cost_norm: '-39.399',
                                    max_commission_percent: '0.0024',
                                    numerator: '853.8',
                                },
                            },
                            {
                                kind: 'agent',
                                rate: '0',
                            },
                            {
                                kind: 'call_center',
                                rate: '0',
                            },
                        ],
                        id: '0',
                        matcher: {
                            begin_at: '2019-12-16T00:00:00',
                            end_at: undefined,
                            tariff_class: undefined,
                            payment_type: 'cash',
                            tag: 'reposition_district_extracoms_8',
                            zone: 'moscow',
                        },
                        settings: {
                            cancel_settings: {
                                park_billable_cancel_interval: ['25200', '36000'],
                                pickup_location_radius: 300,
                                user_billable_cancel_interval: ['7200', '36000'],
                            },
                            discounts: [
                                {
                                    marketing_level: ['lightbox'],
                                    value: '0.0003',
                                },
                                {
                                    marketing_level: ['co_branding', 'lightbox'],
                                    value: '0.0005',
                                },
                                {
                                    marketing_level: ['sticker'],
                                    value: '0.0006',
                                },
                                {
                                    marketing_level: ['co_branding'],
                                    value: '0.0005',
                                },
                                {
                                    marketing_level: ['sticker', 'lightbox'],
                                    value: '0.0006',
                                },
                            ],
                            expired_cost: '800',
                            max_cost: '6000',
                            min_cost: '0',
                            vat: '0.0118',
                        },
                    },
                ],
            },
        };
        const preparedData = {
            ...commissionToDraft(commission),
            request_id: 'request_id',
            data: {
                commissions: commissionToDraft(commission).data?.commissions.map((item, index) => ({
                    ...item,
                    id: String(index),
                })),
            },
        };
        expect(preparedData).toEqual(expected);
    });
});
