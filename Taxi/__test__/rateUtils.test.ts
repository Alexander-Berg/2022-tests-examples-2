/* tslint:disable:max-file-line-count no-trailing-whitespace*/
import moment from 'moment';

import {DraftApiPath} from '../enums';

import {convertToRateWithIndexes, getNumberEquivalentForWeekDay} from '../rateCommonUtils';
import {
    getIntervalRates,
    getRatesByExcel,
    getRatesByRules,
    mergeGoalRates,
    sortRates,
    splitRates,
} from '../rateUtils';
import {Rate, TableSmartRule} from '../types';
import {createRate} from './utils';

const DEFAULT_SUBVENTION_SETTINGS = {
    geoarea_disabled: false,
    intervals: {
        night: 0,
        morning: 6,
        daytime: 12,
        evening: 18,
    },
};

describe('getNumberEquivalentForWeekDay', () => {
    it('Возвращает ожидаемое число минут от начала недели для указанного дня', () => {
        expect(getNumberEquivalentForWeekDay('00:10', 'mon')).toBe(10);
        expect(getNumberEquivalentForWeekDay('00:10', 'wed')).toBe(2890);
        expect(getNumberEquivalentForWeekDay('12:15', 'fri')).toBe(6495);
    });
});

describe('getRatesByRules', () => {
    it('должна правильно выводить границы дней', () => {
        const rules: Array<TableSmartRule> = [
            {
                id: '515f3b6c-3426-4de9-a64b-6ed65b813986',
                start: '2021-04-14 00:00',
                end: moment('2021-04-24T21:00:00.000Z'),
                rates: [
                    {week_day: 'mon', start: '00:00', bonus_amount: '1'},
                    {week_day: 'mon', start: '06:00', bonus_amount: '0'},
                    {week_day: 'tue', start: '06:00', bonus_amount: '2'},
                    {week_day: 'tue', start: '12:00', bonus_amount: '0'},
                    {week_day: 'wed', start: '12:00', bonus_amount: '3'},
                    {week_day: 'wed', start: '18:00', bonus_amount: '0'},
                    {week_day: 'thu', start: '18:00', bonus_amount: '4'},
                    {week_day: 'fri', start: '00:00', bonus_amount: '0'},
                ],
                budget_id: '0db18574-acee-42de-a8d8-06ece8e196bf',
                draft_id: '154441',
                zone: 'zvenigorod',
                tariff_class: 'Комфорт',
                rule_type: 'single_ride',
                isScheduleRef: false,
                apiPath: DraftApiPath.Unknown,
                ticket: undefined,
                draftZones: [],
            },
        ];
        const expected = [
            'smart_subventions.mon — smart_subventions.night',
            'smart_subventions.tue — smart_subventions.morning',
            'smart_subventions.wed — smart_subventions.day',
            'smart_subventions.thu — smart_subventions.evening',
        ];

        expect(getRatesByRules(rules, DEFAULT_SUBVENTION_SETTINGS)).toEqual(expected);
    });

    it('должна склеивать в периоды несколько рейтов от правил', () => {
        const rules: Array<TableSmartRule> = [
            {
                id: '291543ba-019b-4755-8164-be10170711e7',
                start: '2021-04-12 21:00',
                end: moment('2021-04-14T18:00:00.000Z'),
                tag: 'kek',
                branding_type: 'without_sticker',
                activity_points: 0,
                rates: [
                    {week_day: 'sat', start: '00:00', bonus_amount: '80'},
                    {week_day: 'sun', start: '00:00', bonus_amount: '0'},
                ],
                budget_id: 'c2147c2f-ed3c-4430-8e46-bf696d8ad05c',
                draft_id: '153847',
                zone: 'almaty',
                tariff_class: 'Эконом',
                geoarea: 'dasha',
                rule_type: 'single_ride',
                isScheduleRef: false,
                apiPath: DraftApiPath.Unknown,
                ticket: undefined,
                draftZones: [],
            },
            {
                id: 'a1a65a80-fa3e-4cf8-9342-d8e4300491cb',
                start: '2021-04-14 21:00',
                end: moment('2021-04-23T18:00:00.000Z'),
                rates: [
                    {week_day: 'wed', start: '11:11', bonus_amount: '2222'},
                    {week_day: 'sat', start: '22:22', bonus_amount: '0'},
                ],
                budget_id: '24333408-7418-4565-b2d7-39916a039ff9',
                draft_id: '148511',
                zone: 'almaty',
                tariff_class: 'Комфорт 2.0',
                rule_type: 'single_ride',
                isScheduleRef: false,
                apiPath: DraftApiPath.Unknown,
                ticket: undefined,
                draftZones: [],
            },
        ];

        expect(getRatesByRules(rules, DEFAULT_SUBVENTION_SETTINGS)).toEqual([
            'smart_subventions.wed — smart_subventions.morning, smart_subventions.day, smart_subventions.evening',
            'smart_subventions.thu - smart_subventions.sat — smart_subventions.night, smart_subventions.morning, smart_subventions.day, smart_subventions.evening',
        ]);
    });

    it('должна обрабатывать случай с полным расписанием, например Пн 00:00 - Пн 00:00', () => {
        const rules: Array<TableSmartRule> = [
            {
                id: '3224828b-fb7f-4e26-9b37-368d06264c9a',
                tariff_class: 'Эконом',
                window: 1,
                currency: 'RUB',
                start: '2021-04-07 00:00',
                end: moment('2021-04-29T21:00:00.000Z'),
                budget_id: 'bbf1be88-2681-4ad5-8cab-363fef2e90f1',
                draft_id: '151012',
                branding_type: 'sticker',
                rule_type: 'goal',
                steps: [{id: 'A', steps: [{nrides: 1, amount: '439.31'}]}],
                rates: [{week_day: 'mon', start: '00:00', bonus_amount: 'A'}],
                zone: 'zheleznodorozhny',
                geonode: 'zheleznodorozhny',
                apiPath: DraftApiPath.Unknown,
                ticket: undefined,
                draftZones: [],
            },
        ];

        expect(getRatesByRules(rules, DEFAULT_SUBVENTION_SETTINGS)).toEqual([
            'smart_subventions.mon - smart_subventions.sun — smart_subventions.night, smart_subventions.morning, smart_subventions.day, smart_subventions.evening',
        ]);
    });

    it('должна обрабатывать случай с измененным конфигом для расписания', () => {
        jest.mock('../utils', () => ({
            getSmartSubventionsConfig: {
                geoarea_disabled: false,
                intervals: {
                    night: 0,
                    morning: 6,
                    daytime: 12,
                    evening: 18,
                },
            },
        }));
        const rules: Array<TableSmartRule> = [
            {
                id: '4645469b-4718-4386-8300-716875e23892',
                start: '2021-04-21 00:00',
                end: moment('2021-04-23T21:00:00.000Z'),
                tag: 'run123',
                branding_type: 'sticker_and_lightbox',
                rates: [
                    {week_day: 'mon', start: '00:34', bonus_amount: '3'},
                    {week_day: 'mon', start: '00:45', bonus_amount: '0'},
                ],
                budget_id: 'ed6ba0a6-9ae1-4d03-a7e5-31550fc8d952',
                draft_id: '157811',
                zone: 'zvenigorod',
                tariff_class: 'Select+',
                geoarea: 'a_pol10',
                rule_type: 'single_ride',
                isScheduleRef: false,
                apiPath: DraftApiPath.Unknown,
                ticket: undefined,
                draftZones: [],
            },
        ];
        expect(getRatesByRules(rules, DEFAULT_SUBVENTION_SETTINGS)).toEqual([
            'smart_subventions.mon — smart_subventions.night',
        ]);
    });

    it('должна сортировать дни недели от Понедельника до Воскресенья и сортировать интервалы от ночи до вечера', () => {
        jest.mock('../utils', () => ({
            getSmartSubventionsConfig: {
                geoarea_disabled: false,
                intervals: {
                    night: 1,
                    morning: 5,
                    daytime: 10,
                    evening: 18,
                },
            },
        }));
        const rules: Array<TableSmartRule> = [
            {
                id: '498a8483-3dcd-45dc-bfeb-e37e6618bee7',
                tariff_class: 'Эконом',
                geonode:
                    'br_root/br_russia/br_sibirskij_fo/br_krasnojarskij_kraj/br_krasnoyarsk/br_krasnoyarsk_adm/krasnoyarsk',
                window: 1,
                currency: 'RUB',
                start: '2022-01-22 00:00',
                end: moment('2022-01-24T17:00:00.000Z'),
                budget_id: '2005d543-1e6d-4c95-b898-0cd87d2b42c5',
                draft_id: '525177',
                rule_type: 'goal',
                steps: [{id: 'A', steps: [{nrides: 1, amount: '10'}]}],
                rates: [
                    {week_day: 'mon', start: '00:00', bonus_amount: '0'},
                    {week_day: 'mon', start: '07:00', bonus_amount: 'A'},
                    {week_day: 'tue', start: '00:00', bonus_amount: '0'},
                    {week_day: 'tue', start: '07:00', bonus_amount: 'A'},
                    {week_day: 'wed', start: '00:00', bonus_amount: '0'},
                    {week_day: 'wed', start: '07:00', bonus_amount: 'A'},
                    {week_day: 'thu', start: '00:00', bonus_amount: '0'},
                    {week_day: 'thu', start: '07:00', bonus_amount: 'A'},
                    {week_day: 'fri', start: '00:00', bonus_amount: '0'},
                    {week_day: 'fri', start: '07:00', bonus_amount: 'A'},
                    {week_day: 'sat', start: '00:00', bonus_amount: '0'},
                    {week_day: 'sat', start: '07:00', bonus_amount: 'A'},
                    {week_day: 'sun', start: '00:00', bonus_amount: '0'},
                    {week_day: 'sun', start: '07:00', bonus_amount: 'A'},
                ],
                zone: 'krasnoyarsk',
                apiPath: DraftApiPath.Create,
                ticket: 'TAXIRATE-106',
                draftZones: [],
            },
        ];
        expect(
            getRatesByRules(rules, {
                geoarea_disabled: false,
                intervals: {
                    night: 1,
                    morning: 5,
                    daytime: 10,
                    evening: 18,
                },
            }),
        ).toEqual([
            'smart_subventions.mon - smart_subventions.sun — smart_subventions.morning, smart_subventions.day, smart_subventions.evening',
        ]);
    });
});

describe('getIntervalRates', () => {
    it('должна отрабатывать корректно, если расписание оканчивается на 23:59 воскресенья', () => {
        expect(
            getIntervalRates([
                createRate('mon', '00:00', 'sun', '23:59', '4'),
            ]),
        ).toEqual([
            {
                bonus_amount: '4',
                week_day: 'mon',
                start: '00:00',
            },
            {
                bonus_amount: '0',
                week_day: 'sun',
                start: '23:59',
            },
        ]);
    });

    it('должна отрабатывать корректно, когда есть пересечения интервалов', () => {
        expect(
            getIntervalRates([
                createRate('mon', '00:00', 'tue', '10:00', 'A'),
                createRate('tue', '10:00', 'tue', '20:00', 'A,B'),
                createRate('tue', '20:00', 'wed', '20:00', 'B'),
            ]),
        ).toEqual([
            {
                bonus_amount: 'A',
                start: '00:00',
                week_day: 'mon',
            },
            {
                bonus_amount: 'A,B',
                start: '10:00',
                week_day: 'tue',
            },
            {
                bonus_amount: 'B',
                start: '20:00',
                week_day: 'tue',
            },
            {
                bonus_amount: '0',
                start: '20:00',
                week_day: 'wed',
            },
        ]);
    });

    it('должна отрабатывать корректно, когда интервал длится всю неделю + пересечение', () => {
        const rates: Rate[] = [
            createRate('mon', '00:00', 'tue', '10:00', 'A'),
            createRate('tue', '10:00', 'wed', '00:00', 'A,B'),
            createRate('wed', '00:00', 'mon', '00:00', 'A'),
        ];
        expect(getIntervalRates(rates)).toEqual([
            {
                bonus_amount: 'A',
                start: '00:00',
                week_day: 'mon',
            },
            {
                bonus_amount: 'A,B',
                start: '10:00',
                week_day: 'tue',
            },
            {
                bonus_amount: 'A',
                start: '00:00',
                week_day: 'wed',
            },
        ]);
    });

    it('должна отрабатывать корректно, когда интервал длится всю неделю', () => {
        expect(
            getIntervalRates([
                createRate('mon', '00:00', 'mon', '00:00', 'A')
            ])
        ).toEqual([
            {
                bonus_amount: 'A',
                start: '00:00',
                week_day: 'mon',
            },
        ]);
    });

    it('должна корректно отображать конец расписания (https://st.yandex-team.ru/TEFADMIN-763)', () => {
        expect(
            getIntervalRates([
                createRate('mon', '06:00', 'mon', '23:00', '1'),
                createRate('tue', '06:00', 'tue', '23:00', '1'),
                createRate('wed', '06:00', 'wed', '23:00', '1'),
                createRate('thu', '06:00', 'thu', '23:00', '1'),
                createRate('fri', '06:00', 'fri', '23:00', '1'),
                createRate('sat', '06:00', 'sat', '23:00', '1'),
                createRate('sun', '06:00', 'sun', '23:00', '1'),
            ]),
        ).toEqual([
            {bonus_amount: '1', week_day: 'mon', start: '06:00'},
            {bonus_amount: '0', week_day: 'mon', start: '23:00'},
            {bonus_amount: '1', week_day: 'tue', start: '06:00'},
            {bonus_amount: '0', week_day: 'tue', start: '23:00'},
            {bonus_amount: '1', week_day: 'wed', start: '06:00'},
            {bonus_amount: '0', week_day: 'wed', start: '23:00'},
            {bonus_amount: '1', week_day: 'thu', start: '06:00'},
            {bonus_amount: '0', week_day: 'thu', start: '23:00'},
            {bonus_amount: '1', week_day: 'fri', start: '06:00'},
            {bonus_amount: '0', week_day: 'fri', start: '23:00'},
            {bonus_amount: '1', week_day: 'sat', start: '06:00'},
            {bonus_amount: '0', week_day: 'sat', start: '23:00'},
            {bonus_amount: '1', week_day: 'sun', start: '06:00'},
            {bonus_amount: '0', week_day: 'sun', start: '23:00'},
        ]);

        expect(
            getIntervalRates([
                createRate('mon', '06:00', 'mon', '22:00', '3'),
                createRate('tue', '06:00', 'tue', '22:00', '3'),
                createRate('wed', '06:00', 'wed', '22:00', '3'),
                createRate('thu', '06:00', 'thu', '22:00', '3'),
                createRate('fri', '06:00', 'fri', '22:00', '3'),
                createRate('sat', '06:00', 'sat', '22:00', '3'),
                createRate('sun', '06:00', 'sun', '22:00', '13'),
            ]),
        ).toEqual([
            {bonus_amount: '3', week_day: 'mon', start: '06:00'},
            {bonus_amount: '0', week_day: 'mon', start: '22:00'},
            {bonus_amount: '3', week_day: 'tue', start: '06:00'},
            {bonus_amount: '0', week_day: 'tue', start: '22:00'},
            {bonus_amount: '3', week_day: 'wed', start: '06:00'},
            {bonus_amount: '0', week_day: 'wed', start: '22:00'},
            {bonus_amount: '3', week_day: 'thu', start: '06:00'},
            {bonus_amount: '0', week_day: 'thu', start: '22:00'},
            {bonus_amount: '3', week_day: 'fri', start: '06:00'},
            {bonus_amount: '0', week_day: 'fri', start: '22:00'},
            {bonus_amount: '3', week_day: 'sat', start: '06:00'},
            {bonus_amount: '0', week_day: 'sat', start: '22:00'},
            {bonus_amount: '13', week_day: 'sun', start: '06:00'},
            {bonus_amount: '0', week_day: 'sun', start: '22:00'},
        ]);
    });

    it('должна корректно отображать перевод расписания с воскресенья на новую неделю (https://st.yandex-team.ru/TEFADMIN-755)', () => {
        expect(
            getIntervalRates([
                createRate('mon', '06:00', 'tue', '00:00', '4'),
                createRate('tue', '06:00', 'wed', '00:00', '4'),
                createRate('wed', '06:00', 'thu', '00:00', '4'),
                createRate('thu', '06:00', 'fri', '00:00', '4'),
                createRate('fri', '06:00', 'sat', '00:00', '4'),
                createRate('sat', '06:00', 'sun', '00:00', '4'),
                createRate('sun', '06:00', 'mon', '00:00', '4'),
            ]),
        ).toEqual([
            {bonus_amount: '0', week_day: 'mon', start: '00:00'},
            {bonus_amount: '4', week_day: 'mon', start: '06:00'},
            {bonus_amount: '0', week_day: 'tue', start: '00:00'},
            {bonus_amount: '4', week_day: 'tue', start: '06:00'},
            {bonus_amount: '0', week_day: 'wed', start: '00:00'},
            {bonus_amount: '4', week_day: 'wed', start: '06:00'},
            {bonus_amount: '0', week_day: 'thu', start: '00:00'},
            {bonus_amount: '4', week_day: 'thu', start: '06:00'},
            {bonus_amount: '0', week_day: 'fri', start: '00:00'},
            {bonus_amount: '4', week_day: 'fri', start: '06:00'},
            {bonus_amount: '0', week_day: 'sat', start: '00:00'},
            {bonus_amount: '4', week_day: 'sat', start: '06:00'},
            {bonus_amount: '0', week_day: 'sun', start: '00:00'},
            {bonus_amount: '4', week_day: 'sun', start: '06:00'},
        ]);
    });
});

describe('sortRates', () => {
    it('Cортировка дат, интервалы которых не пересекаются', () => {
        const rates: Rate[] = [
            {
                weekDayStart: 'fri',
                weekDayEnd: 'fri',
                bonus_amount: '100',
                start: '16:40',
                end: '19:40',
            },
            {
                weekDayStart: 'wed',
                weekDayEnd: 'wed',
                bonus_amount: '100',
                start: '16:40',
                end: '19:40',
            },
            {
                weekDayStart: 'mon',
                weekDayEnd: 'mon',
                bonus_amount: '100',
                start: '16:40',
                end: '19:40',
            },
        ];

        const result: Rate[] = [
            {
                weekDayStart: 'mon',
                weekDayEnd: 'mon',
                bonus_amount: '100',
                start: '16:40',
                end: '19:40',
            },
            {
                weekDayStart: 'wed',
                weekDayEnd: 'wed',
                bonus_amount: '100',
                start: '16:40',
                end: '19:40',
            },
            {
                weekDayStart: 'fri',
                weekDayEnd: 'fri',
                bonus_amount: '100',
                start: '16:40',
                end: '19:40',
            },
        ];

        expect(sortRates(rates)).toEqual(result);
    });

    it('Сортировка дат, интервалы которых пересекаются', () => {
        const rates: Rate[] = [
            {
                weekDayStart: 'wed',
                weekDayEnd: 'fri',
                bonus_amount: '100',
                start: '16:40',
                end: '19:40',
            },
            {
                weekDayStart: 'tue',
                weekDayEnd: 'thu',
                bonus_amount: '100',
                start: '16:40',
                end: '19:40',
            },
            {
                weekDayStart: 'mon',
                weekDayEnd: 'wed',
                bonus_amount: '100',
                start: '16:40',
                end: '19:40',
            },
        ];

        const result: Rate[] = [
            {
                weekDayStart: 'mon',
                weekDayEnd: 'wed',
                bonus_amount: '100',
                start: '16:40',
                end: '19:40',
            },
            {
                weekDayStart: 'tue',
                weekDayEnd: 'thu',
                bonus_amount: '100',
                start: '16:40',
                end: '19:40',
            },
            {
                weekDayStart: 'wed',
                weekDayEnd: 'fri',
                bonus_amount: '100',
                start: '16:40',
                end: '19:40',
            },
        ];

        expect(sortRates(rates)).toEqual(result);
    });

    it('Сортировка дат, у которых дата старта совпадает', () => {
        const rates: Rate[] = [
            {
                weekDayStart: 'mon',
                weekDayEnd: 'fri',
                bonus_amount: '100',
                start: '16:40',
                end: '19:40',
            },
            {
                weekDayStart: 'mon',
                weekDayEnd: 'thu',
                bonus_amount: '100',
                start: '16:40',
                end: '19:40',
            },
            {
                weekDayStart: 'mon',
                weekDayEnd: 'wed',
                bonus_amount: '100',
                start: '16:40',
                end: '19:40',
            },
        ];

        const result: Rate[] = [
            {
                weekDayStart: 'mon',
                weekDayEnd: 'wed',
                bonus_amount: '100',
                start: '16:40',
                end: '19:40',
            },
            {
                weekDayStart: 'mon',
                weekDayEnd: 'thu',
                bonus_amount: '100',
                start: '16:40',
                end: '19:40',
            },
            {
                weekDayStart: 'mon',
                weekDayEnd: 'fri',
                bonus_amount: '100',
                start: '16:40',
                end: '19:40',
            },
        ];

        expect(sortRates(rates)).toEqual(result);
    });
});

describe('getRatesByExcel', () => {
    it('Должна парсить значения правильно', () => {
        expect(
            getRatesByExcel(`hour/weekday	1	2	3	4	5	6	7
        0	1
        1		2
        2			3
        3				4
        4					5
        5						6
        6							7
        7						8
        8					9
        9				8
        10			7
        11		6
        12	5
        13		4
        14			3
        15				2
        16					1
        17						2
        18							3
        19						4
        20					5
        21				6
        22			7
        23		8					`),
        ).toEqual([
            {start: '00:00', weekDayStart: 'mon', bonus_amount: '1', end: '01:00', weekDayEnd: 'mon'},
            {start: '12:00', weekDayStart: 'mon', bonus_amount: '5', end: '13:00', weekDayEnd: 'mon'},
            {start: '01:00', weekDayStart: 'tue', bonus_amount: '2', end: '02:00', weekDayEnd: 'tue'},
            {start: '11:00', weekDayStart: 'tue', bonus_amount: '6', end: '12:00', weekDayEnd: 'tue'},
            {start: '13:00', weekDayStart: 'tue', bonus_amount: '4', end: '14:00', weekDayEnd: 'tue'},
            {start: '23:00', weekDayStart: 'tue', bonus_amount: '8', end: '00:00', weekDayEnd: 'wed'},
            {start: '02:00', weekDayStart: 'wed', bonus_amount: '3', end: '03:00', weekDayEnd: 'wed'},
            {start: '10:00', weekDayStart: 'wed', bonus_amount: '7', end: '11:00', weekDayEnd: 'wed'},
            {start: '14:00', weekDayStart: 'wed', bonus_amount: '3', end: '15:00', weekDayEnd: 'wed'},
            {start: '22:00', weekDayStart: 'wed', bonus_amount: '7', end: '23:00', weekDayEnd: 'wed'},
            {start: '03:00', weekDayStart: 'thu', bonus_amount: '4', end: '04:00', weekDayEnd: 'thu'},
            {start: '09:00', weekDayStart: 'thu', bonus_amount: '8', end: '10:00', weekDayEnd: 'thu'},
            {start: '15:00', weekDayStart: 'thu', bonus_amount: '2', end: '16:00', weekDayEnd: 'thu'},
            {start: '21:00', weekDayStart: 'thu', bonus_amount: '6', end: '22:00', weekDayEnd: 'thu'},
            {start: '04:00', weekDayStart: 'fri', bonus_amount: '5', end: '05:00', weekDayEnd: 'fri'},
            {start: '08:00', weekDayStart: 'fri', bonus_amount: '9', end: '09:00', weekDayEnd: 'fri'},
            {start: '16:00', weekDayStart: 'fri', bonus_amount: '1', end: '17:00', weekDayEnd: 'fri'},
            {start: '20:00', weekDayStart: 'fri', bonus_amount: '5', end: '21:00', weekDayEnd: 'fri'},
            {start: '05:00', weekDayStart: 'sat', bonus_amount: '6', end: '06:00', weekDayEnd: 'sat'},
            {start: '07:00', weekDayStart: 'sat', bonus_amount: '8', end: '08:00', weekDayEnd: 'sat'},
            {start: '17:00', weekDayStart: 'sat', bonus_amount: '2', end: '18:00', weekDayEnd: 'sat'},
            {start: '19:00', weekDayStart: 'sat', bonus_amount: '4', end: '20:00', weekDayEnd: 'sat'},
            {start: '06:00', weekDayStart: 'sun', bonus_amount: '7', end: '07:00', weekDayEnd: 'sun'},
            {start: '18:00', weekDayStart: 'sun', bonus_amount: '3', end: '19:00', weekDayEnd: 'sun'},
        ]);

        expect(
            getRatesByExcel(`hour/weekday	1	2	3	4	5	6	7
        0	1
        1	1	2
        2	1	2	3
        3	2		3	4
        4	2			4	5
        5	3				5	6
        6						6	7
        7						8	7
        8					9	8
        9				8	9
        10			7	8
        11	5	6	7
        12	5
        13	6	4
        14	6		3	2
        15	7		3	2
        16					1	2
        17					1	2	3
        18							3
        19					4	4
        20					5	3
        21			7	6
        22		8	7	6
        23		8					`),
        ).toEqual([
            {start: '00:00', weekDayStart: 'mon', bonus_amount: '1', end: '03:00', weekDayEnd: 'mon'},
            {start: '03:00', weekDayStart: 'mon', bonus_amount: '2', end: '05:00', weekDayEnd: 'mon'},
            {start: '05:00', weekDayStart: 'mon', bonus_amount: '3', end: '06:00', weekDayEnd: 'mon'},
            {start: '11:00', weekDayStart: 'mon', bonus_amount: '5', end: '13:00', weekDayEnd: 'mon'},
            {start: '13:00', weekDayStart: 'mon', bonus_amount: '6', end: '15:00', weekDayEnd: 'mon'},
            {start: '15:00', weekDayStart: 'mon', bonus_amount: '7', end: '16:00', weekDayEnd: 'mon'},
            {start: '01:00', weekDayStart: 'tue', bonus_amount: '2', end: '03:00', weekDayEnd: 'tue'},
            {start: '11:00', weekDayStart: 'tue', bonus_amount: '6', end: '12:00', weekDayEnd: 'tue'},
            {start: '13:00', weekDayStart: 'tue', bonus_amount: '4', end: '14:00', weekDayEnd: 'tue'},
            {start: '22:00', weekDayStart: 'tue', bonus_amount: '8', end: '00:00', weekDayEnd: 'wed'},
            {start: '02:00', weekDayStart: 'wed', bonus_amount: '3', end: '04:00', weekDayEnd: 'wed'},
            {start: '10:00', weekDayStart: 'wed', bonus_amount: '7', end: '12:00', weekDayEnd: 'wed'},
            {start: '14:00', weekDayStart: 'wed', bonus_amount: '3', end: '16:00', weekDayEnd: 'wed'},
            {start: '21:00', weekDayStart: 'wed', bonus_amount: '7', end: '23:00', weekDayEnd: 'wed'},
            {start: '03:00', weekDayStart: 'thu', bonus_amount: '4', end: '05:00', weekDayEnd: 'thu'},
            {start: '09:00', weekDayStart: 'thu', bonus_amount: '8', end: '11:00', weekDayEnd: 'thu'},
            {start: '14:00', weekDayStart: 'thu', bonus_amount: '2', end: '16:00', weekDayEnd: 'thu'},
            {start: '21:00', weekDayStart: 'thu', bonus_amount: '6', end: '23:00', weekDayEnd: 'thu'},
            {start: '04:00', weekDayStart: 'fri', bonus_amount: '5', end: '06:00', weekDayEnd: 'fri'},
            {start: '08:00', weekDayStart: 'fri', bonus_amount: '9', end: '10:00', weekDayEnd: 'fri'},
            {start: '16:00', weekDayStart: 'fri', bonus_amount: '1', end: '18:00', weekDayEnd: 'fri'},
            {start: '19:00', weekDayStart: 'fri', bonus_amount: '4', end: '20:00', weekDayEnd: 'fri'},
            {start: '20:00', weekDayStart: 'fri', bonus_amount: '5', end: '21:00', weekDayEnd: 'fri'},
            {start: '05:00', weekDayStart: 'sat', bonus_amount: '6', end: '07:00', weekDayEnd: 'sat'},
            {start: '07:00', weekDayStart: 'sat', bonus_amount: '8', end: '09:00', weekDayEnd: 'sat'},
            {start: '16:00', weekDayStart: 'sat', bonus_amount: '2', end: '18:00', weekDayEnd: 'sat'},
            {start: '19:00', weekDayStart: 'sat', bonus_amount: '4', end: '20:00', weekDayEnd: 'sat'},
            {start: '20:00', weekDayStart: 'sat', bonus_amount: '3', end: '21:00', weekDayEnd: 'sat'},
            {start: '06:00', weekDayStart: 'sun', bonus_amount: '7', end: '08:00', weekDayEnd: 'sun'},
            {start: '17:00', weekDayStart: 'sun', bonus_amount: '3', end: '19:00', weekDayEnd: 'sun'},
        ]);
    });

    it('Должна выбрасывать ошибку при невалидных значениях в таблице', () => {
        try {
            getRatesByExcel(`hour/weekday	1	2	3	4	5	6	7
        0	1
        1		2
        2			3
        3				4
        4					5
        5						-6
        6							7
        7						8
        8					9
        9				8
        10			7
        11		6
        12	5
        13		4
        14			3
        15				2
        16					1
        17						2
        18							3
        19						4
        20					5
        21				6
        22			7
        23		8					`);
        } catch (e) {
            expect(e instanceof Error).toEqual(true);
        }
    });
});

describe('mergeGoalRates', () => {
    it('один интервал', () => {
        const rates: Rate[] = [
            createRate('mon', '00:00', 'mon', '02:00', 'A'),
        ];
        expect(mergeGoalRates(rates)).toEqual(rates);
    });

    it('два интервала', () => {
        const rates: Rate[] = [
            createRate('mon', '10:00', 'mon', '20:00', 'A'),
            createRate('tue', '10:00', 'tue', '20:00', 'B'),
        ];
        const expected: Rate[] = [
            createRate('mon', '10:00', 'mon', '20:00', 'A'),
            // добавляется заполнение промежутка
            createRate('mon', '20:00', 'tue', '10:00', '0'),
            createRate('tue', '10:00', 'tue', '20:00', 'B'),
        ];
        expect(mergeGoalRates(rates)).toEqual(expected);
    });

    it('два пересекающихся интервала (один внутри другого)', () => {
        const rates: Rate[] = [
            createRate('mon', '09:00', 'mon', '20:00', 'A'),
            createRate('mon', '10:00', 'mon', '12:00', 'B'),
        ];
        const expected: Rate[] = [
            createRate('mon', '09:00', 'mon', '10:00', 'A'),
            createRate('mon', '10:00', 'mon', '12:00', 'A,B'),
            createRate('mon', '12:00', 'mon', '20:00', 'A'),
        ];
        expect(mergeGoalRates(rates)).toEqual(expected);
    });

    it('два пересекающихся интервала', () => {
        const rates: Rate[] = [
            createRate('mon', '08:00', 'mon', '10:00', 'A'),
            createRate('mon', '09:00', 'mon', '12:00', 'B'),
        ];
        const expected: Rate[] = [
            createRate('mon', '08:00', 'mon', '09:00', 'A'),
            createRate('mon', '09:00', 'mon', '10:00', 'A,B'),
            createRate('mon', '10:00', 'mon', '12:00', 'B'),
        ];
        expect(mergeGoalRates(rates)).toEqual(expected);
    });

    it('два пересекающихся интервала (разные дни)', () => {
        const rates: Rate[] = [
            createRate('mon', '00:00', 'tue', '20:00', 'A'),
            createRate('tue', '10:00', 'wed', '20:00', 'B'),
        ];
        const expected: Rate[] = [
            createRate('mon', '00:00', 'tue', '10:00', 'A'),
            createRate('tue', '10:00', 'tue', '20:00', 'A,B'),
            createRate('tue', '20:00', 'wed', '20:00', 'B'),
        ];
        expect(mergeGoalRates(rates)).toEqual(expected);
    });

    it('недельный интервал mon и пересечение', () => {
        const rates: Rate[] = [
            // выбрана вся неделя пн 10:00-пн 10:00
            createRate('mon', '10:00', 'mon', '10:00', 'A'),
            createRate('tue', '10:00', 'wed', '00:00', 'B'),
        ];
        const expected: Rate[] = [
            createRate('mon', '00:00', 'tue', '10:00', 'A'),
            createRate('tue', '10:00', 'wed', '00:00', 'A,B'),
            createRate('wed', '00:00', 'mon', '00:00', 'A'),
        ];
        expect(mergeGoalRates(rates)).toEqual(expected);
    });

    it('интервал, где конец следует перед началом (вс-вт)', () => {
        const rates: Rate[] = [
            createRate('sun', '10:00', 'tue', '10:00', 'A'),
        ];
        const expected: Rate[] = [
            // разбиваем интервал на две части
            createRate('mon', '00:00', 'tue', '10:00', 'A'),
            // заполняем промежуток пустым интервалом
            createRate('tue', '10:00', 'sun', '10:00', '0'),
            // вторая часть
            createRate('sun', '10:00', 'mon', '00:00', 'A'),
        ];
        expect(mergeGoalRates(rates)).toEqual(expected);
    });
});

describe('splitRates', () => {
    it('должен отработать на двух интервалах с пересечением', () => {
        const rates = ([
            createRate('mon', '09:00', 'mon', '10:00', 'A'),
            createRate('mon', '10:00', 'mon', '12:00', 'A,B'),
            createRate('mon', '12:00', 'mon', '20:00', 'A'),
        ]);
        const expected = convertToRateWithIndexes([
            createRate('mon', '09:00', 'mon', '20:00', 'A'),
            createRate('mon', '10:00', 'mon', '12:00', 'B'),
        ]);
        expect(splitRates(rates)).toEqual(expected);
    });

    it('больше интервалов', () => {
        const rates = [
            createRate('mon', '09:00', 'mon', '10:00', 'A'),
            createRate('mon', '10:00', 'mon', '12:00', 'A,B'),
            createRate('mon', '12:00', 'mon', '20:00', 'A'),
            createRate('mon', '20:00', 'mon', '21:00', 'B'),
            createRate('tue', '09:00', 'tue', '20:00', 'A'),
        ];
        const expected = convertToRateWithIndexes([
            createRate('mon', '09:00', 'mon', '20:00', 'A'),
            createRate('tue', '09:00', 'tue', '20:00', 'A'),
            createRate('mon', '10:00', 'mon', '12:00', 'B'),
            createRate('mon', '20:00', 'mon', '21:00', 'B'),
        ]);
        expect(splitRates(rates)).toEqual(expected);
    });
});
