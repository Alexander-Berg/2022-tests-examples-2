import moment from 'moment';
import {expectSaga} from 'redux-saga-test-plan';

import {CreateRequest} from '_libs/drafts/types';

import {LABELS, SUBVENTION_MODEL} from '../../../consts';
import {goalModelPath, goalRuleValidationPath} from '../../../modelUtils';
import {CreateRulesRequest, GoalRuleVM, SingleRideRuleVM} from '../../../types';
import SingleRideService, {createSubventionRuleDraft} from '../SingleRideService';
import {TIMEZONE_OPERATION_MOCK_DATA} from './mocks';

type ExpectedResultType = Pick<CreateRequest, 'description' | 'tickets'> & {
    data: CreateRulesRequest;
};

describe('createSubventionRuleDraft', () => {
    it('должна формировать single ride модель для ручки', () => {
        const model: Partial<SingleRideRuleVM> = {
            start: {time: '12:31', date: moment('2021-03-17T09:31:00.000Z')},
            end: {time: '12:41', date: moment('2021-03-18T09:41:00.000Z')},
            offset: 0,
            rates: [{start: '12:41', weekDayStart: 'tue', weekDayEnd: 'sat', end: '12:42', bonus_amount: '1'}],
            rule_type: 'single_ride',
            zone: ['accra'],
            tariff_class: ['business'],
            geoarea: ['11111'],
            tag: 'waaaaat',
            branding_type: 'no_full_branding',
            activity_points: ('1' as unknown) as number,
            budget: {weekly: '1', threshold: ('2' as unknown) as number, rolling: true, daily: '3'},
            ticketData: {ticket: 'taxirate-53'},
        };
        const expectedResult: ExpectedResultType = {
            data: {
                rule_spec: {
                    zones: ['accra'],
                    rule: {
                        rule_type: 'single_ride',
                        rates: [
                            {bonus_amount: '1', week_day: 'tue', start: '12:41'},
                            {bonus_amount: '0', week_day: 'sat', start: '12:42'},
                        ],
                        start: '2021-03-17T12:31:00+0000',
                        end: '2021-03-18T12:41:00+0000',
                        branding_type: 'no_full_branding',
                        activity_points: 1,
                        tag: 'waaaaat',
                    },
                    budget: {weekly: '1', threshold: 2, rolling: true, daily: '3'},
                    tariff_classes: ['business'],
                    geoareas: ['11111'],
                },
                old_rule_ids: [],
            },
            tickets: {existed: ['TAXIRATE-53']},
        };
        return expectSaga(createSubventionRuleDraft, model)
            .withState({
                asyncOperations: TIMEZONE_OPERATION_MOCK_DATA,
            })
            .run()
            .then(res => {
                expect(res.returnValue).toEqual(expectedResult);
            });
    });

    it('должна формировать goal модель для ручки', () => {
        const model: Partial<GoalRuleVM> = {
            start: {time: '12:31', date: moment('2021-03-17T09:31:00.000Z')},
            end: {time: '12:31', date: moment('2021-03-20T09:31:00.000Z')},
            offset: 2,
            rates: [{start: '14:12', weekDayStart: 'wed', end: '12:41', weekDayEnd: 'fri', bonus_amount: 'A'}],
            counters: {
                steps: [{id: 'A', steps: [{nrides: 1, amount: '2'}]}],
            },
            currency: 'XOF',
            rule_type: 'goal',
            unique_driver_id: '1',
            zone: ['/br_israel/br_ashkelon'],
            tariff_class: ['comfortplus'],
            geoarea: ['111'],
            tag: 'dasha',
            branding_type: 'no_full_branding',
            window: ('1' as unknown) as number,
            activity_points: ('1' as unknown) as number,
            budget: {weekly: '2', threshold: ('3' as unknown) as number, rolling: true, daily: '4'},
            ticketData: {ticket: 'taxirate-53'},
        };
        const expectedResult: ExpectedResultType = {
            data: {
                rule_spec: {
                    zones: ['/br_israel/br_ashkelon'],
                    rule: {
                        unique_driver_id: '1',
                        window: 1,
                        currency: 'XOF',
                        rule_type: 'goal',
                        counters: {
                            steps: [{id: 'A', steps: [{nrides: 1, amount: '2'}]}],
                            schedule: [
                                {week_day: 'wed', start: '14:12', counter: 'A'},
                                {week_day: 'fri', start: '12:41', counter: '0'},
                            ],
                        },
                        start: '2021-03-17T12:31:00+0200',
                        end: '2021-03-20T12:31:00+0200',
                        branding_type: 'no_full_branding',
                        activity_points: 1,
                        tag: 'dasha',
                    },
                    budget: {weekly: '2', threshold: 3, rolling: true, daily: '4'},
                    tariff_classes: ['comfortplus'],
                },
                old_rule_ids: [],
            },
            tickets: {existed: ['TAXIRATE-53']},
        };

        return expectSaga(createSubventionRuleDraft, model)
            .withState({
                asyncOperations: TIMEZONE_OPERATION_MOCK_DATA,
                [SUBVENTION_MODEL]: model,
            })
            .run()
            .then(res => {
                expect(res.returnValue).toEqual(expectedResult);
            });
    });

    it('должна прокидывать RUB валюту в форму, если в геоноде нет валюты', () => {
        const model: Partial<GoalRuleVM> = {
            start: {time: '12:31', date: moment('2021-03-17T09:31:00.000Z')},
            end: {time: '12:31', date: moment('2021-03-20T09:31:00.000Z')},
            offset: 2,
            rates: [{start: '14:12', weekDayStart: 'wed', end: '12:41', weekDayEnd: 'fri', bonus_amount: 'A'}],
            counters: {
                steps: [{id: 'A', steps: [{nrides: 1, amount: '2'}]}],
            },
            rule_type: 'goal',
            unique_driver_id: '1',
            zone: ['/br_israel/br_ashkelon'],
            tariff_class: ['comfortplus'],
            geoarea: ['111'],
            tag: 'dasha',
            branding_type: 'no_full_branding',
            window: ('1' as unknown) as number,
            activity_points: ('1' as unknown) as number,
            budget: {weekly: '2', threshold: ('3' as unknown) as number, rolling: true, daily: '4'},
            ticketData: {ticket: 'taxirate-53'},
        };
        const expectedResult: ExpectedResultType = {
            data: {
                rule_spec: {
                    zones: ['/br_israel/br_ashkelon'],
                    rule: {
                        unique_driver_id: '1',
                        window: 1,
                        currency: 'RUB',
                        rule_type: 'goal',
                        counters: {
                            steps: [{id: 'A', steps: [{nrides: 1, amount: '2'}]}],
                            schedule: [
                                {week_day: 'wed', start: '14:12', counter: 'A'},
                                {week_day: 'fri', start: '12:41', counter: '0'},
                            ],
                        },
                        start: '2021-03-17T12:31:00+0200',
                        end: '2021-03-20T12:31:00+0200',
                        branding_type: 'no_full_branding',
                        activity_points: 1,
                        tag: 'dasha',
                    },
                    budget: {weekly: '2', threshold: 3, rolling: true, daily: '4'},
                    tariff_classes: ['comfortplus'],
                },
                old_rule_ids: [],
            },
            tickets: {existed: ['TAXIRATE-53']},
        };

        return expectSaga(createSubventionRuleDraft, model)
            .withState({
                asyncOperations: TIMEZONE_OPERATION_MOCK_DATA,
                [SUBVENTION_MODEL]: model,
            })
            .run()
            .then(res => {
                expect(res.returnValue).toEqual(expectedResult);
            });
    });

    it('Функция должна проставлять значение для недельной суммы, если пользователь не ввел значение недельной суммы и ввел значение для дневной суммы (https://st.yandex-team.ru/TEFADMIN-935)', () => {
        const model: Partial<GoalRuleVM> = {
            start: {time: '12:31', date: moment('2021-03-17T09:31:00.000Z')},
            end: {time: '12:31', date: moment('2021-03-20T09:31:00.000Z')},
            offset: 2,
            rates: [{start: '14:12', weekDayStart: 'wed', end: '12:41', weekDayEnd: 'fri', bonus_amount: 'A'}],
            counters: {
                steps: [{id: 'A', steps: [{nrides: 1, amount: '2'}]}],
            },
            rule_type: 'goal',
            unique_driver_id: '1',
            zone: ['/br_israel/br_ashkelon'],
            tariff_class: ['comfortplus'],
            geoarea: ['111'],
            tag: 'dasha',
            branding_type: 'no_full_branding',
            window: ('1' as unknown) as number,
            activity_points: ('1' as unknown) as number,
            budget: {threshold: ('3' as unknown) as number, rolling: true, daily: '4'},
            ticketData: {ticket: 'taxirate-53'},
        };
        const expectedResult: ExpectedResultType = {
            data: {
                rule_spec: {
                    zones: ['/br_israel/br_ashkelon'],
                    rule: {
                        unique_driver_id: '1',
                        window: 1,
                        currency: 'RUB',
                        rule_type: 'goal',
                        counters: {
                            steps: [{id: 'A', steps: [{nrides: 1, amount: '2'}]}],
                            schedule: [
                                {week_day: 'wed', start: '14:12', counter: 'A'},
                                {week_day: 'fri', start: '12:41', counter: '0'},
                            ],
                        },
                        start: '2021-03-17T12:31:00+0200',
                        end: '2021-03-20T12:31:00+0200',
                        branding_type: 'no_full_branding',
                        activity_points: 1,
                        tag: 'dasha',
                    },
                    budget: {weekly: '28', threshold: 3, rolling: true, daily: '4'},
                    tariff_classes: ['comfortplus'],
                },
                old_rule_ids: [],
            },
            tickets: {existed: ['TAXIRATE-53']},
        };

        return expectSaga(createSubventionRuleDraft, model)
            .withState({
                asyncOperations: TIMEZONE_OPERATION_MOCK_DATA,
                [SUBVENTION_MODEL]: model,
            })
            .run()
            .then(res => {
                expect(res.returnValue).toEqual(expectedResult);
            });
    });
});

describe('sortGoalSteps', () => {
    it('должно сортировать шаги', () => {
        const goalModel: Partial<GoalRuleVM> = {
            counters: {
                steps: [
                    {
                        steps: [
                            {
                                nrides: 2,
                                amount: '2',
                            },
                            {
                                nrides: 1,
                                amount: '1',
                            },
                        ],
                    },
                    {
                        steps: [
                            {
                                nrides: 3,
                                amount: '3',
                            },
                            {
                                nrides: 4,
                                amount: '4',
                            },
                        ],
                    },
                ],
            },
        };

        return expectSaga(SingleRideService.sortGoalSteps)
            .withState({
                [SUBVENTION_MODEL]: goalModel,
            })
            .run()
            .then(({effects: {put}}) => {
                const expectedPutEffect = {
                    '@@redux-saga/IO': true,
                    'combinator': false,
                    'type': 'PUT',
                    'payload': {
                        action: {
                            type: 'rrf/change',
                            model: goalModelPath(m => m.counters.steps),
                            value: [
                                {
                                    steps: [
                                        {nrides: 1, amount: '1'},
                                        {nrides: 2, amount: '2'},
                                    ],
                                },
                                {
                                    steps: [
                                        {nrides: 3, amount: '3'},
                                        {nrides: 4, amount: '4'},
                                    ],
                                },
                            ],
                            silent: false,
                            multi: false,
                            external: true,
                        },
                    },
                };
                // Проверяем, что вызвали change у rrf, с отсортированными данными
                expect(put[1]).toEqual(expectedPutEffect);

                const expectedValidationResult = {
                    '@@redux-saga/IO': true,
                    'combinator': false,
                    'type': 'PUT',
                    'payload': {
                        action: {
                            type: 'rrf/setFieldsValidity',
                            model: SUBVENTION_MODEL,
                            fieldsValidity: {
                                [goalRuleValidationPath(m => m.counters.steps[0].steps[1].amount)]: LABELS.AMOUNT_ERROR,
                            },
                            options: {errors: true},
                        },
                    },
                };
                // Проверяем, что вызвали валидатор для ступеней, и что валидатор дал нужный результат
                expect(put[4]).toEqual(expectedValidationResult);
            });
    });
});
