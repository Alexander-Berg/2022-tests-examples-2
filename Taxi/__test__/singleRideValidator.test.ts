import moment from 'moment';
import {expectSaga} from 'redux-saga-test-plan';

import {TIMEZONE_RECORD_OPERATION} from '_pkg/sagas/services/TimezoneService';
import {DraftModes} from '_types/common/drafts';

import {SingleRideRuleVM} from '../../../types';
import {subventionValidationPath} from '../../../utils';
import singleRideValidator from '../singleRideValidator';

const ASYNC_OPERATIONS = {
    GEONODES_OPERATION: {
        result: [],
    },
    [TIMEZONE_RECORD_OPERATION]: {
        result: {
            accra: {
                zone: 'accra',
                tariff_settings: {
                    tariff_settings_id: '5caf05328f8d18512aeb00c5',
                    home_zone: 'accra',
                    is_disabled: false,
                    timezone: 'Africa/Accra',
                    city_id: 'Аккра',
                    country: 'gha',
                },
            },
        },
    },
};

describe('singleRideValidator', () => {
    it('должна отключать проверку недельной суммы, если введена дневная сумма (https://st.yandex-team.ru/TEFADMIN-935)', () => {
        const model: Partial<SingleRideRuleVM> = {
            start: {date: moment('2021-05-13T21:00:00.000Z')},
            end: {date: moment('2021-05-22T21:00:00.000Z')},
            offset: 0,
            rule_type: 'single_ride',
            rates: [{start: '12:31', weekDayStart: 'thu', end: '12:31', weekDayEnd: 'sun', bonus_amount: '1'}],
            budget: {threshold: ('4' as unknown) as number, rolling: true, daily: '4'},
            zone: ['accra'],
            tariff_class: ['uberx'],
        };
        return expectSaga(singleRideValidator)
            .withState({
                SUBVENTION_MODEL: model,
                asyncOperations: ASYNC_OPERATIONS,
                router: {
                    currentRoute: {},
                },
            })
            .run()
            .then(resp => {
                expect(resp.effects.put[4].payload.action.fieldsValidity['data.budget.weekly']).toEqual(undefined);
            });
    });

    it('недельняя сумма обязательное поле, если не введена дневная сумма', () => {
        const model: Partial<SingleRideRuleVM> = {
            start: {date: moment('2021-05-13T21:00:00.000Z')},
            end: {date: moment('2021-05-22T21:00:00.000Z')},
            offset: 0,
            rule_type: 'single_ride',
            rates: [{start: '12:31', weekDayStart: 'thu', end: '12:31', weekDayEnd: 'sun', bonus_amount: '1'}],
            budget: {threshold: ('4' as unknown) as number, rolling: true},
            zone: ['accra'],
            tariff_class: ['uberx'],
        };
        return expectSaga(singleRideValidator)
            .withState({
                SUBVENTION_MODEL: model,
                asyncOperations: ASYNC_OPERATIONS,
                router: {
                    currentRoute: {},
                },
            })
            .run()
            .then(resp => {
                expect(
                    resp.effects.put[3].payload.action.fieldsValidity[subventionValidationPath(m => m.budget.weekly)],
                ).toEqual(true);
            });
    });

    // https://st.yandex-team.ru/TEFADMIN-867
    it('не должна валидировать порог исчерпания, если введено число больше нуля', () => {
        const model: Partial<SingleRideRuleVM> = {
            start: {date: moment('2021-05-13T21:00:00.000Z')},
            end: {date: moment('2021-05-22T21:00:00.000Z')},
            offset: 0,
            rule_type: 'single_ride',
            rates: [{start: '12:31', weekDayStart: 'thu', end: '12:31', weekDayEnd: 'sun', bonus_amount: '1'}],
            budget: {threshold: ('123123' as unknown) as number, rolling: true},
            zone: ['accra'],
            tariff_class: ['uberx'],
        };
        return expectSaga(singleRideValidator)
            .withState({
                SUBVENTION_MODEL: model,
                asyncOperations: ASYNC_OPERATIONS,
                router: {
                    currentRoute: {},
                },
            })
            .run()
            .then(resp => {
                expect(
                    resp.effects.put[4].payload.action.fieldsValidity[
                        subventionValidationPath(m => m.budget.threshold)
                        ],
                ).toEqual(undefined);
            });
    });

    // https://st.yandex-team.ru/TEFADMIN-867
    it('не должна валидировать порог исчерпания, если не введены данные', () => {
        const model: Partial<SingleRideRuleVM> = {
            start: {date: moment('2021-05-13T21:00:00.000Z')},
            end: {date: moment('2021-05-22T21:00:00.000Z')},
            offset: 0,
            rule_type: 'single_ride',
            rates: [{start: '12:31', weekDayStart: 'thu', end: '12:31', weekDayEnd: 'sun', bonus_amount: '1'}],
            budget: {threshold: undefined, rolling: true},
            zone: ['accra'],
            tariff_class: ['uberx'],
        };
        return expectSaga(singleRideValidator)
            .withState({
                SUBVENTION_MODEL: model,
                asyncOperations: ASYNC_OPERATIONS,
                router: {
                    currentRoute: {},
                },
            })
            .run()
            .then(resp => {
                expect(
                    resp.effects.put[4].payload.action.fieldsValidity[
                        subventionValidationPath(m => m.budget.threshold)
                        ],
                ).toEqual(undefined);
            });
    });

    // https://st.yandex-team.ru/TEFADMIN-867
    it('должна валидировать порог исчерпания, если введено число меньше единицы', () => {
        const model: Partial<SingleRideRuleVM> = {
            start: {date: moment('2021-05-13T21:00:00.000Z')},
            end: {date: moment('2021-05-22T21:00:00.000Z')},
            offset: 0,
            rule_type: 'single_ride',
            rates: [{start: '12:31', weekDayStart: 'thu', end: '12:31', weekDayEnd: 'sun', bonus_amount: '1'}],
            budget: {threshold: ('0' as unknown) as number, rolling: true},
            zone: ['accra'],
            tariff_class: ['uberx'],
        };
        return expectSaga(singleRideValidator)
            .withState({
                SUBVENTION_MODEL: model,
                asyncOperations: ASYNC_OPERATIONS,
                router: {
                    currentRoute: {},
                },
            })
            .run()
            .then(resp => {
                expect(
                    resp.effects.put[4].payload.action.fieldsValidity[
                        subventionValidationPath(m => m.budget.threshold)
                        ],
                ).toEqual('smart_subventions.must_be_greater_than_0');
            });
    });

    it('Должна выдавать ошибку, если выбранные зоны находятся не в одной таймзоне', () => {
        const model: Partial<SingleRideRuleVM> = {
            start: {date: moment('2021-05-13T21:00:00.000Z')},
            end: {date: moment('2021-05-22T21:00:00.000Z')},
            offset: 0,
            rule_type: 'single_ride',
            rates: [{start: '12:31', weekDayStart: 'thu', end: '12:31', weekDayEnd: 'sun', bonus_amount: '1'}],
            budget: {threshold: ('0' as unknown) as number, rolling: true},
            zone: ['moscow', 'samara'],
            tariff_class: ['uberx'],
        };
        return expectSaga(singleRideValidator)
            .withState({
                SUBVENTION_MODEL: model,
                asyncOperations: {
                    GEONODES_OPERATION: {
                        result: [],
                    },
                    [TIMEZONE_RECORD_OPERATION]: {
                        result: {
                            moscow: {
                                zone: 'moscow',
                                tariff_settings: {
                                    tariff_settings_id: '56f968f07c0aa65c44998e4b',
                                    home_zone: 'moscow',
                                    is_disabled: false,
                                    timezone: 'Europe/Moscow',
                                    city_id: 'Москва',
                                    country: 'rus',
                                },
                            },
                            samara: {
                                zone: 'samara',
                                tariff_settings: {
                                    tariff_settings_id: '56f968f07c0aa65c44998e47',
                                    home_zone: 'samara',
                                    is_disabled: false,
                                    timezone: 'Europe/Samara',
                                    city_id: 'Самара',
                                    country: 'rus',
                                },
                            },
                        },
                    },
                },
                router: {
                    currentRoute: {},
                },
            })
            .run()
            .then(resp => {
                expect(
                    resp.effects.put[4].payload.action.fieldsValidity[subventionValidationPath(m => m.zone)],
                ).toEqual('smart_subventions.single_ride_offset_error');
            });
    });

    it('Не должна проверять ticket в форме для edit-draft мода', () => {
        const model: Partial<SingleRideRuleVM> = {
            start: {date: moment('2021-05-13T21:00:00.000Z')},
            end: {date: moment('2021-05-22T21:00:00.000Z')},
            offset: 0,
            rule_type: 'single_ride',
            rates: [{start: '12:31', weekDayStart: 'thu', end: '12:31', weekDayEnd: 'sun', bonus_amount: '1'}],
            budget: {threshold: ('0' as unknown) as number, rolling: true},
            zone: ['accra', 'perm'],
            tariff_class: ['uberx'],
        };

        return expectSaga(singleRideValidator)
            .withState({
                SUBVENTION_MODEL: model,
                asyncOperations: {
                    GEONODES_OPERATION: {
                        result: [],
                    },
                    [TIMEZONE_RECORD_OPERATION]: {
                        result: {
                            accra: {
                                zone: 'accra',
                                tariff_settings: {
                                    tariff_settings_id: '5caf05328f8d18512aeb00c5',
                                    home_zone: 'accra',
                                    is_disabled: false,
                                    timezone: 'Africa/Accra',
                                    city_id: 'Аккра',
                                    country: 'gha',
                                },
                            },
                            perm: {
                                zone: 'perm',
                                tariff_settings: {
                                    tariff_settings_id: '56f968f07c0aa65c44998e4c',
                                    home_zone: 'perm',
                                    is_disabled: false,
                                    timezone: 'Asia/Yekaterinburg',
                                    city_id: 'Пермь',
                                    classifier_name: 'Пермь',
                                    country: 'rus',
                                },
                            },
                        },
                    },
                },
                router: {
                    currentRoute: {
                        mode: DraftModes.CreateDraft,
                    },
                },
            })
            .run()
            .then(resp => {
                expect(
                    resp.effects.put[4].payload.action.fieldsValidity[
                        subventionValidationPath(m => m.ticketData.ticket)
                        ],
                ).toEqual(undefined);
            });
    });
});
