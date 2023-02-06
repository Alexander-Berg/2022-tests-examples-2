import moment from 'moment';

import {Draft, DraftStatusEnum} from '_libs/drafts/types';

import {CommissionType} from '../../enums';
import {V1RulesCreateBody} from '../../types';
import {draftToModel} from '../matchers';

describe('draftToModel matcher', () => {
    test('asymptotic', () => {
        const draft: Draft<V1RulesCreateBody> = {
            id: 123,
            status: DraftStatusEnum.NeedApproval,
            data: {
                commissions: [
                    {
                        id: '1',
                        settings: {
                            min_cost: '10',
                            max_cost: '15',
                            expired_cost: '20',
                            vat: '0.15',
                            discounts: [
                                {
                                    value: '0.1',
                                    marketing_level: ['test']
                                },
                                {
                                    value: '0.2',
                                    marketing_level: ['test2']
                                }
                            ],
                            cancel_settings: {
                                user_billable_cancel_interval: ['1', '6'],
                                park_billable_cancel_interval: ['60', '120'],
                                pickup_location_radius: 10
                            }
                        },
                        matcher: {
                            zone: 'moscow',
                            payment_type: 'cash',
                            tariff_class: 'econom',
                            begin_at: '2020-12-12T09:00:00+00:00',
                            end_at: '2100-12-12T08:00:00+00:00',
                            tag: 'tag'
                        },
                        agreements: [
                            {
                                kind: 'asymptotic',
                                rate: {
                                    cost_norm: '42',
                                    numerator: '42',
                                    asymp: '42',
                                    max_commission_percent: '0.1'
                                },
                                cancel_rate: '0.03',
                                expired_rate: '0.05'
                            },
                            {
                                kind: 'hiring',
                                rate: '0.12',
                                hiring_age: 20
                            },
                            {
                                kind: 'hiring_commercial',
                                rate: '0.22',
                                hiring_age: 20
                            },
                            {
                                kind: 'taximeter',
                                commission: '10'
                            },
                            {
                                kind: 'voucher',
                                rate: '0.25'
                            },
                            {
                                kind: 'acquiring',
                                rate: '0.2'
                            },
                            {
                                kind: 'agent',
                                rate: '0.15'
                            },
                            {
                                kind: 'call_center',
                                rate: '0.3'
                            }
                        ]
                    },
                    {
                        id: '2',
                        matcher: {
                            zone: 'rostov-on-don',
                            tariff_class: 'comfort',
                            payment_type: 'online',
                            begin_at: '2020-12-12T09:00:00+00:00',
                        },
                        settings: {
                            min_cost: '10',
                            max_cost: '15',
                            expired_cost: '20',
                            vat: '0.15',
                            cancel_settings: {
                                user_billable_cancel_interval: ['1', '6'],
                                park_billable_cancel_interval: ['60', '120'],
                                pickup_location_radius: 10
                            }
                        },
                        agreements: []
                    },
                    {
                        id: '3',
                        matcher: {
                            zone: 'rostov-on-don',
                            tariff_class: 'comfort',
                            payment_type: 'cash',
                            begin_at: '2020-12-12T09:00:00+00:00',
                        },
                        settings: {
                            min_cost: '10',
                            max_cost: '15',
                            expired_cost: '20',
                            vat: '0.15',
                            cancel_settings: {
                                user_billable_cancel_interval: ['1', '6'],
                                park_billable_cancel_interval: ['60', '120'],
                                pickup_location_radius: 10
                            }
                        },
                        agreements: []
                    }
                ]
            }
        };

        const expected = {
            type: CommissionType.AsymptoticFormula,
            cost_norm: 42,
            numerator: 42,
            asymp: '42',
            max_commission_percent: '10',
            expired_percent: '5',
            cancel_percent: '3',
            has_fixed_cancel_percent: true,
            billable_cancel_distance: 10,
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
            begin_time: moment('2020-12-12T09:00:00+00:00').format('HH:mm'),
            end_time: moment('2100-12-12T08:00:00+00:00').format('HH:mm'),
            min_order_cost: '10',
            max_order_cost: '15',
            expired_cost: '20',
            vat: '15',
            branding_discounts: [
                {
                    value: '10',
                    marketing_level: ['test']
                },
                {
                    value: '20',
                    marketing_level: ['test2']
                }
            ],
            user_cancel_min_td: 0.02,
            user_cancel_max_td: 0.1,
            park_cancel_min_td: 1,
            park_cancel_max_td: 2,
            draft: draft
        };
        expect(draftToModel(draft)).toEqual(expected);
    });

    test('fixed_rate', () => {
        const draft: Draft<V1RulesCreateBody> = {
            id: 123,
            status: DraftStatusEnum.NeedApproval,
            data: {
                commissions: [
                    {
                        id: '1',
                        settings: {
                            min_cost: '10',
                            max_cost: '15',
                            expired_cost: '20',
                            vat: '0.15',
                            cancel_settings: {
                                user_billable_cancel_interval: ['1', '6'],
                                park_billable_cancel_interval: ['60', '120'],
                                pickup_location_radius: 10
                            }
                        },
                        matcher: {
                            zone: 'moscow',
                            payment_type: 'cash',
                            tariff_class: 'econom',
                            begin_at: '2020-12-12T09:00:00+00:00',
                            end_at: '2100-12-12T08:00:00+00:00',
                            tag: 'tag'
                        },
                        agreements: [
                            {
                                kind: 'fixed_rate',
                                rate: '0.3',
                                cancel_rate: '0.1',
                                expired_rate: '0.15'
                            }
                        ]
                    }
                ]
            }
        };

        const expected = {
            type: CommissionType.FixedPercent,
            percent: '30',
            expired_percent: '15',
            cancel_percent: '10',
            has_fixed_cancel_percent: true,
            zones: ['moscow'],
            tariff_classes: ['econom'],
            payment_types: ['cash'],
            tag: 'tag',
            billable_cancel_distance: 10,
            begin: moment('2020-12-12T09:00:00+00:00'),
            begin_time: moment('2020-12-12T09:00:00+00:00').format('HH:mm'),
            end: moment('2100-12-12T08:00:00+00:00'),
            end_time: moment('2100-12-12T08:00:00+00:00').format('HH:mm'),
            min_order_cost: '10',
            max_order_cost: '15',
            expired_cost: '20',
            vat: '15',
            user_cancel_min_td: 0.02,
            user_cancel_max_td: 0.1,
            park_cancel_min_td: 1,
            park_cancel_max_td: 2,
            draft: draft
        };
        expect(draftToModel(draft)).toEqual(expected);
    });

    test('absolute_value', () => {
        const draft: Draft<V1RulesCreateBody> = {
            id: 123,
            status: DraftStatusEnum.NeedApproval,
            data: {
                commissions: [
                    {
                        id: '1',
                        settings: {
                            min_cost: '10',
                            max_cost: '15',
                            expired_cost: '20',
                            vat: '0.15',
                            cancel_settings: {
                                user_billable_cancel_interval: ['1', '6'],
                                park_billable_cancel_interval: ['60', '120'],
                                pickup_location_radius: 10
                            }
                        },
                        matcher: {
                            zone: 'moscow',
                            payment_type: 'cash',
                            tariff_class: 'econom',
                            begin_at: '2020-12-12T09:00:00+00:00',
                            tag: 'tag'
                        },
                        agreements: [
                            {
                                kind: 'absolute_value',
                                commission: '30',
                                cancel_commission: '10',
                                expired_commission: '15'
                            }
                        ]
                    }
                ]
            }
        };

        const expected = {
            type: CommissionType.AbsoluteValue,
            commission: '30',
            cancel_commission: '10',
            expired_commission: '15',
            zones: ['moscow'],
            tariff_classes: ['econom'],
            payment_types: ['cash'],
            billable_cancel_distance: 10,
            begin: moment('2020-12-12T09:00:00+00:00'),
            begin_time: moment('2020-12-12T09:00:00+00:00').format('HH:mm'),
            tag: 'tag',
            min_order_cost: '10',
            max_order_cost: '15',
            expired_cost: '20',
            vat: '15',
            user_cancel_min_td: 0.02,
            user_cancel_max_td: 0.1,
            park_cancel_min_td: 1,
            park_cancel_max_td: 2,
            draft: draft
        };
        expect(draftToModel(draft)).toEqual(expected);
    });

    test('empty agreements', () => {
        const draft: Draft<V1RulesCreateBody> = {
            id: 123,
            status: DraftStatusEnum.NeedApproval,
            data: {
                commissions: [
                    {
                        id: '1',
                        settings: {
                            min_cost: '10',
                            max_cost: '15',
                            expired_cost: '20',
                            vat: '0.15',
                            cancel_settings: {
                                user_billable_cancel_interval: ['1', '6'],
                                park_billable_cancel_interval: ['60', '120'],
                                pickup_location_radius: 10
                            }
                        },
                        matcher: {
                            zone: 'moscow',
                            payment_type: 'cash',
                            tariff_class: 'econom',
                            begin_at: '2020-12-12T09:00:00+00:00',
                        },
                        agreements: []
                    }
                ]
            }
        };

        const expected = {
            type: CommissionType.FixedPercent,
            zones: ['moscow'],
            tariff_classes: ['econom'],
            payment_types: ['cash'],
            begin: moment('2020-12-12T09:00:00+00:00'),
            begin_time: moment('2020-12-12T09:00:00+00:00').format('HH:mm'),
            billable_cancel_distance: 10,
            min_order_cost: '10',
            max_order_cost: '15',
            expired_cost: '20',
            vat: '15',
            user_cancel_min_td: 0.02,
            user_cancel_max_td: 0.1,
            park_cancel_min_td: 1,
            park_cancel_max_td: 2,
            draft: draft
        };
        expect(draftToModel(draft)).toEqual(expected);
    });
});
