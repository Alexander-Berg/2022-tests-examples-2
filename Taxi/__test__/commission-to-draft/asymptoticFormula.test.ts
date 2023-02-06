import moment from 'moment';

import {COMMISSION_SERVICE_NAME, DRAFT_API_PATHS} from '../../../consts';
import {CommissionType} from '../../../enums';
import {CommissionView} from '../../../types';
import {commissionToDraft} from '../../matchers';

describe('commissionToDraft matcher', () => {
    test('AsymptoticFormula', () => {
        const commission: CommissionView = {
            type: CommissionType.AsymptoticFormula,
            cost_norm: 42,
            numerator: 42,
            asymp: '42',
            max_commission_percent: '10',
            expired_percent: '5',
            cancel_percent: '3',
            has_fixed_cancel_percent: true,
            zones: ['moscow', 'rostov-on-don'],
            tariff_classes: ['econom', 'comfort'],
            payment_types: ['cash', 'online'],
            acquiring_percent: '20',
            agent_percent: '15',
            taximeter_payment: '10',
            callcenter_commission_percent: '30',
            hiring: '12',
            hiring_commercial: '22',
            hiring_age: 20,
            tag: 'tag',
            begin: moment('2020-12-12T09:00:00+00:00'),
            end: moment('2100-12-12T08:00:00+00:00'),
            begin_time: '10:00',
            end_time: '12:00',
            min_order_cost: '10',
            max_order_cost: '15',
            expired_cost: '20',
            vat: '15',
            billable_cancel_distance: 10,
            branding_discounts: [
                {
                    value: '10',
                    marketing_level: ['test'],
                },
                {
                    value: '20',
                    marketing_level: ['test2'],
                },
            ],
            user_cancel_min_td: 0.02,
            user_cancel_max_td: 0.1,
            park_cancel_min_td: 1,
            park_cancel_max_td: 2,
        };

        const expectedBody = {
            matcher: {
                begin_at: '2020-12-12T10:00:00',
                end_at: '2100-12-12T12:00:00',
                tag: 'tag',
            },
            settings: {
                min_cost: '10',
                max_cost: '15',
                expired_cost: '20',
                vat: '0.15',
                cancel_settings: {
                    user_billable_cancel_interval: ['1.2', '6'],
                    park_billable_cancel_interval: ['60', '120'],
                    pickup_location_radius: 10,
                },
                discounts: [
                    {
                        value: '0.1',
                        marketing_level: ['test'],
                    },
                    {
                        value: '0.2',
                        marketing_level: ['test2'],
                    },
                ],
            },
            agreements: [
                {
                    cancel_rate: '0.03',
                    expired_rate: '0.05',
                    kind: 'asymptotic',
                    rate: {
                        asymp: '42',
                        cost_norm: '42',
                        max_commission_percent: '0.1',
                        numerator: '42',
                    },
                },
                {
                    kind: 'agent',
                    rate: '0.15',
                },
                {
                    kind: 'call_center',
                    rate: '0',
                },
            ],
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
                        id: '0',
                        ...expectedBody,
                        matcher: {
                            ...expectedBody.matcher,
                            zone: 'moscow',
                            tariff_class: 'econom',
                            payment_type: 'cash',
                        },
                    },
                    {
                        id: '1',
                        ...expectedBody,
                        matcher: {
                            ...expectedBody.matcher,
                            zone: 'moscow',
                            tariff_class: 'comfort',
                            payment_type: 'cash',
                        },
                    },
                    {
                        id: '2',
                        ...expectedBody,
                        matcher: {
                            ...expectedBody.matcher,
                            zone: 'moscow',
                            tariff_class: 'econom',
                            payment_type: 'online',
                        },
                    },
                    {
                        id: '3',
                        ...expectedBody,
                        matcher: {
                            ...expectedBody.matcher,
                            zone: 'moscow',
                            tariff_class: 'comfort',
                            payment_type: 'online',
                        },
                    },
                    {
                        id: '4',
                        ...expectedBody,
                        matcher: {
                            ...expectedBody.matcher,
                            zone: 'rostov-on-don',
                            tariff_class: 'econom',
                            payment_type: 'cash',
                        },
                    },
                    {
                        id: '5',
                        ...expectedBody,
                        matcher: {
                            ...expectedBody.matcher,
                            zone: 'rostov-on-don',
                            tariff_class: 'comfort',
                            payment_type: 'cash',
                        },
                    },
                    {
                        id: '6',
                        ...expectedBody,
                        matcher: {
                            ...expectedBody.matcher,
                            zone: 'rostov-on-don',
                            tariff_class: 'econom',
                            payment_type: 'online',
                        },
                    },
                    {
                        id: '7',
                        ...expectedBody,
                        matcher: {
                            ...expectedBody.matcher,
                            zone: 'rostov-on-don',
                            tariff_class: 'comfort',
                            payment_type: 'online',
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
