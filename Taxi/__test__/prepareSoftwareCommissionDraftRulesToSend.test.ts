import {prepareSoftwareCommissionDraftRulesToSend} from '../converters';
import {SoftwareCommissionModel} from '../types';

describe('prepareSoftwareCommissionDraftRulesToSend', function () {
    test('$view not exits', () => {
        const data: SoftwareCommissionModel = {
            matcher: {
                zones: ['zone'],
                starts_at: '2021-11-02T20:00:00',
            },
            kind: 'kind',
            fees: {
                percent: '10',
            },
        };
        expect(() => prepareSoftwareCommissionDraftRulesToSend(data)).toThrowError();
    });
    test('required fields only', () => {
        const data: SoftwareCommissionModel = {
            matcher: {
                zones: ['zone'],
                starts_at: '2021-11-02T20:00:00',
            },
            kind: 'kind',
            fees: {
                percent: '10',
            },
            $view: {},
        };
        const expected = [
            {
                kind: 'kind',
                fees: {
                    percent: '0.1000',
                },
                matcher: {
                    starts_at: '2021-11-02T17:00:00+00:00',
                    zones: ['zone'],
                },
                settings: {},
            },
        ];
        const res = prepareSoftwareCommissionDraftRulesToSend(data);
        expect(res).toEqual(expected);
    });

    test('all fields', () => {
        const data: SoftwareCommissionModel = {
            matcher: {
                zones: ['zone'],
                tariffs: ['tariff'],
                starts_at: '2021-11-02T20:00:00',
                ends_at: '2021-11-22T20:00:00',
                tags: ['tags'],
                payment_types: ['payment_type'],
                hiring_type: 'commercial',
            },
            kind: 'kind',
            fees: [
                {
                    subscription_level: '0',
                    fee: '5',
                },
            ],
            settings: {
                withdraw_from_driver_account: false,
                cost_bounds: {
                    cost_min: '5',
                    cost_max: '10',
                },
                hiring: {
                    hiring_age: 20,
                },
            },
            $view: {
                startsAtTime: '10:00',
                endsAtTime: '15:00',
                description: 'description',
                ticket: 'ticket',
                ticketDescription: 'ticketDescription',
                ticketSummary: 'ticketSummary',
                timezone: 180,
            },
        };
        const expected = [
            {
                kind: 'kind',
                fees: [
                    {
                        subscription_level: 'Level0',
                        fee: '5',
                    },
                ],
                matcher: {
                    ends_at: '2021-11-22T15:00:00+03:00',
                    starts_at: '2021-11-02T10:00:00+03:00',
                    tags: ['tags'],
                    zones: ['zone'],
                    hiring_type: 'commercial',
                    payment_types: ['payment_type'],
                    tariffs: ['tariff'],
                },
                settings: {
                    cost_bounds: {
                        cost_min: '5',
                        cost_max: '10',
                    },
                    hiring: {
                        hiring_age: 20,
                    },
                    withdraw_from_driver_account: false,
                },
            },
        ];
        const res = prepareSoftwareCommissionDraftRulesToSend(data);
        expect(res).toEqual(expected);
    });

    it('Для каждого выбранного payment_type в модели в драфт попадает скопированное правило', () => {
        const data: SoftwareCommissionModel = {
            matcher: {
                zones: ['zone'],
                starts_at: '2021-11-02T20:00:00',
                payment_types: ['card', 'corp'],
            },
            kind: 'kind',
            fees: {
                percent: '10',
            },
            $view: {},
        };
        const getExpectedDraftRule = (paymentType: string) => ({
            kind: 'kind',
            fees: {
                percent: '0.1000',
            },
            matcher: {
                starts_at: '2021-11-02T17:00:00+00:00',
                zones: ['zone'],
                payment_types: [paymentType]
            },
            settings: {},
        });

        const res = prepareSoftwareCommissionDraftRulesToSend(data);

        expect(res).toEqual([getExpectedDraftRule('card'), getExpectedDraftRule('corp')]);
    });
});
