import moment from 'moment';

import {DEFAULT_TIMEZONE} from '../../consts';
import {HierarchyDescriptionName, ZoneType} from '../../enums';
import {
    convertFiltersToQueryConditions,
    makeServerFormatDate,
    makeWeekdaysInterval,
    prepareBrandingKeys,
    prepareBrandingToModel,
    prepareDateToTimeDate,
    prepareDraftData,
    prepareSchedule,
} from '../common';

describe('prepareDraftData', () => {
    it('Содержит active_period и date_expired', () => {
        const {request_id, ...result} = prepareDraftData({api_path: 'api_path', data: 'data'}, [
            {
                condition_name: HierarchyDescriptionName.ActivePeriod,
                values: [{start: '2021-09-03T00:00:00+00:00', end: '2023-01-01T00:00:00+00:00'}],
            },
        ]);
        expect(result).toEqual({
            mode: 'push' as const,
            service_name: 'ride-discounts',
            run_manually: false,
            date_expired: '2021-09-03T12:00:00+00:00',
            api_path: 'api_path',
            data: 'data',
        });
    });

    it('Не содержит active_period и date_expired', () => {
        const {request_id, ...result} = prepareDraftData({api_path: 'api_path', data: 'data'}, [
            {
                condition_name: HierarchyDescriptionName.ActivePeriod,
                values: [],
            },
        ]);
        expect(result).toEqual({
            mode: 'push' as const,
            service_name: 'ride-discounts',
            run_manually: false,
            api_path: 'api_path',
            data: 'data',
        });
    });
});

describe('prepareSchedule', () => {
    it('Заполнены все поля', () => {
        const result = prepareSchedule({weekdays: [1], timeStart: '01:01', timeEnd: '21:20'});
        expect(result).toEqual({
            timezone: DEFAULT_TIMEZONE,
            intervals: [
                {
                    exclude: false,
                    day: [1],
                },
                {
                    exclude: false,
                    daytime: [
                        {
                            from: '01:01:00',
                            to: '21:20:59',
                        },
                    ],
                },
            ],
        });
    });
    it('Поля не заполнены', () => {
        const result = prepareSchedule({});
        expect(result).toEqual({
            timezone: DEFAULT_TIMEZONE,
            intervals: [
                {
                    exclude: false,
                    day: [],
                },
                {
                    exclude: false,
                    daytime: [
                        {
                            from: '00:00:00',
                            to: '23:59:59',
                        },
                    ],
                },
            ],
        });
    });
});

describe('prepareDateToTimeDate', () => {
    it('Moment дата', () => {
        const result = prepareDateToTimeDate(moment('2019-01-01T12:00+00:00').tz('UTC'), 'UTC');
        expect(result.time).toBe('12:00');
        expect(result.date.isSame(moment('2019-01-01'))).toBeTruthy();
    });
    it('String дата', () => {
        const result = prepareDateToTimeDate('2019-01-01T12:00+00:00', 'UTC');
        expect(result.time).toBe('12:00');
        expect(result.date.isSame(moment('2019-01-01'))).toBeTruthy();
    });
    it('Moscow дата', () => {
        const result = prepareDateToTimeDate('2019-01-01T12:00+00:00', 'Europe/Moscow');
        expect(result.time).toBe('15:00');
        expect(result.date.isSame(moment('2019-01-01'))).toBeTruthy();
    });
});

describe('makeServerFormatDate', () => {
    it('Корректное преобразование UTC даты', () => {
        const result = makeServerFormatDate({time: '14:00', date: moment('2019-01-01T12:00')});
        expect(result).toBe('2019-01-01T14:00:00+00:00');
    });

    it('Корректное преобразование даты с таймзоной', () => {
        const result = makeServerFormatDate({time: '14:00', date: moment('2019-01-01T12:00')}, 'Europe/Moscow');
        expect(result).toBe('2019-01-01T14:00:00+03:00');
    });
});

describe('makeWeekdaysInterval', () => {
    it('Корректное преобразование расписания', () => {
        const result = makeWeekdaysInterval({
            timezone: DEFAULT_TIMEZONE,
            intervals: [
                {
                    exclude: false,
                    day: [1],
                },
                {
                    exclude: false,
                    daytime: [
                        {
                            from: '01:01:00',
                            to: '21:20:59',
                        },
                    ],
                },
            ],
        });
        expect(result).toEqual({
            weekdays: [1],
            timeStart: '01:01',
            timeEnd: '21:20',
        });
    });
});

describe('prepareBrandingKeys', () => {
    it('Заполнены все поля', () => {
        const result = prepareBrandingKeys({
            defaultBranding: {
                cardTitle: 'qwe',
                cardSubtitle: 'rty',
                paymentMethodSubtitle: 'uio',
            },
            combinedBranding: {
                cardTitle: 'asd',
                cardSubtitle: 'fgh',
                paymentMethodSubtitle: 'jkl',
            },
        });
        expect(result).toEqual({
            default_branding_keys: {
                card_title: 'qwe',
                card_subtitle: 'rty',
                payment_method_subtitle: 'uio',
            },
            combined_branding_keys: {
                card_title: 'asd',
                card_subtitle: 'fgh',
                payment_method_subtitle: 'jkl',
            },
        });
    });
    it('Поля не заполнены', () => {
        const result = prepareBrandingKeys({
            defaultBranding: {
                cardTitle: '',
                cardSubtitle: '',
                paymentMethodSubtitle: '',
            },
            combinedBranding: {
                cardTitle: '',
                cardSubtitle: '',
                paymentMethodSubtitle: '',
            },
        });
        expect(result).toEqual({
            default_branding_keys: {},
            combined_branding_keys: {},
        });
    });
});

describe('prepareBrandingToModel', () => {
    it('Заполнены все поля', () => {
        const result = prepareBrandingToModel({
            default_branding_keys: {
                card_title: 'qwe',
                card_subtitle: 'rty',
                payment_method_subtitle: 'uio',
            },
            combined_branding_keys: {
                card_title: 'asd',
                card_subtitle: 'fgh',
                payment_method_subtitle: 'jkl',
            },
        });
        expect(result).toEqual({
            defaultBranding: {
                cardTitle: 'qwe',
                cardSubtitle: 'rty',
                paymentMethodSubtitle: 'uio',
            },
            combinedBranding: {
                cardTitle: 'asd',
                cardSubtitle: 'fgh',
                paymentMethodSubtitle: 'jkl',
            },
        });
    });
    it('Поля не заполнены', () => {
        const result = prepareBrandingToModel();
        expect(result).toEqual({
            defaultBranding: {
                cardTitle: '',
                cardSubtitle: '',
                paymentMethodSubtitle: '',
            },
            combinedBranding: {
                cardTitle: '',
                cardSubtitle: '',
                paymentMethodSubtitle: '',
            },
        });
    });
});

describe('convertFiltersToQueryConditions', () => {
    it('Все фильтры заполнены', () => {
        const result = convertFiltersToQueryConditions(
            {
                discountClass: ['class'],
                labelExperiment: ['exp'],
                tariffZone: ['br_moscow'],
                orderType: ['order'],
                tags: ['tag'],
                paymentMethod: ['pay'],
                binSets: ['bin'],
                applications: ['app'],
                yaplus: ['0'],
                tariff: ['tar'],
                isSetPointB: ['1'],
                geoareaSetA: ['setA'],
                geoareaSetB: ['setB'],
                startDate: moment('2019-01-01T12:00'),
                endDate: moment('2022-02-02T13:00'),
                surgeRangeStart: '1',
                surgeRangeEnd: '3',
            },
            [
                {
                    name: 'br_moscow',
                    hierarchy_type: 'BR',
                    node_type: 'node',
                    name_ru: '',
                    name_en: '',
                },
            ],
        );
        expect(result).toEqual([
            {condition_name: HierarchyDescriptionName.DiscountClass, values: ['class']},
            {condition_name: HierarchyDescriptionName.LabelExperiment, values: ['exp']},
            {
                condition_name: HierarchyDescriptionName.Zone,
                values: [
                    {
                        name: 'br_moscow',
                        type: ZoneType.Geonode,
                        is_prioritized: false,
                    },
                    {
                        name: 'br_moscow',
                        type: ZoneType.Geonode,
                        is_prioritized: true,
                    },
                ],
            },
            {condition_name: HierarchyDescriptionName.OrderType, values: ['order']},
            {condition_name: HierarchyDescriptionName.Tag, values: ['tag']},
            {condition_name: HierarchyDescriptionName.PaymentMethod, values: ['pay']},
            {condition_name: HierarchyDescriptionName.Bins, values: ['bin']},
            {condition_name: HierarchyDescriptionName.ApplicationType, values: ['app']},
            {condition_name: HierarchyDescriptionName.YaPlus, values: [0]},
            {condition_name: HierarchyDescriptionName.Tariff, values: ['tar']},
            {condition_name: HierarchyDescriptionName.IsSetPointB, values: [1]},
            {condition_name: HierarchyDescriptionName.GeoareaSetA, values: [['setA']]},
            {condition_name: HierarchyDescriptionName.GeoareaSetB, values: [['setB']]},
            {
                condition_name: HierarchyDescriptionName.ActivePeriod,
                values: [
                    {
                        start: '2019-01-01T12:00:00+00:00',
                        end: '2022-02-02T12:59:59+00:00',
                        is_start_utc: true,
                        is_end_utc: true,
                    },
                    {
                        start: '2019-01-01T12:00:00+00:00',
                        end: '2022-02-02T12:59:59+00:00',
                        is_start_utc: false,
                        is_end_utc: false,
                    },
                ],
            },
            {
                condition_name: HierarchyDescriptionName.SurgeRange,
                values: [
                    {
                        start: '1.0',
                        end: '3.0',
                    },
                ],
            },
        ]);
    });
    it('Фильтры содержат ANY OTHER', () => {
        const result = convertFiltersToQueryConditions(
            {
                discountClass: ['Any'],
                labelExperiment: ['Other'],
                yaplus: ['Any'],
            },
            [],
        );
        expect(result).toEqual([
            {condition_name: HierarchyDescriptionName.DiscountClass, values: 'Any'},
            {condition_name: HierarchyDescriptionName.LabelExperiment, values: 'Other'},
            {condition_name: HierarchyDescriptionName.YaPlus, values: 'Any'},
        ]);
    });
});
