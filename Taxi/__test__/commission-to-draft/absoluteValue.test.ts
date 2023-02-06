import moment from 'moment';

import {COMMISSION_SERVICE_NAME, DRAFT_API_PATHS} from '../../../consts';
import {CommissionType} from '../../../enums';
import {commissionToDraft} from '../../matchers';

describe('commissionToDraft matcher', () => {
    test('AbsoluteValue with $view', () => {
        const commission = {
            type: CommissionType.AbsoluteValue,
            commission: '30',
            cancel_commission: '10',
            expired_commission: '15',
            zones: ['moscow'],
            tariff_classes: ['econom'],
            payment_types: ['cash'],
            begin: moment('2020-12-12T09:00:00+00:00'),
            begin_time: '10:00',
            min_order_cost: '10',
            max_order_cost: '15',
            expired_cost: '20',
            vat: '15',
            billable_cancel_distance: 10,
            user_cancel_min_td: 0.02,
            user_cancel_max_td: 0.1,
            park_cancel_min_td: 1,
            park_cancel_max_td: 2,
            $view: {
                ticket: 'TICKET',
                ticketDescription: 'ticketDescription',
                ticketSummary: 'ticketSummary',
                description: 'description',
            },
        };

        const expected = {
            request_id: 'request_id',
            run_manually: false,
            mode: 'push',
            service_name: COMMISSION_SERVICE_NAME,
            api_path: DRAFT_API_PATHS.COMMISSIONS_CREATE,
            description: 'description',
            tickets: {
                create_data: {
                    description: 'ticketDescription',
                    summary: 'ticketSummary',
                },
                existed: ['TICKET'],
            },
            data: {
                $ticket: 'TICKET',
                commissions: [
                    {
                        id: '0',
                        matcher: {
                            tag: undefined,
                            zone: 'moscow',
                            tariff_class: 'econom',
                            payment_type: 'cash',
                            begin_at: '2020-12-12T10:00:00',
                            end_at: undefined,
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
                            discounts: undefined,
                        },
                        agreements: [
                            {
                                cancel_commission: '10',
                                commission: '30',
                                expired_commission: '15',
                                kind: 'absolute_value',
                            },
                            {
                                kind: 'agent',
                                rate: undefined,
                            },
                            {
                                kind: 'call_center',
                                rate: '0',
                            },
                        ],
                    },
                ],
            },
        };
        const preparedDraft = commissionToDraft(commission);
        const preparedData = {
            ...preparedDraft,
            request_id: 'request_id',
            data: {
                ...preparedDraft.data,
                commissions: preparedDraft.data?.commissions.map((item, index) => ({
                    ...item,
                    id: String(index),
                })),
            },
        };
        expect(preparedData).toEqual(expected);
    });
});
