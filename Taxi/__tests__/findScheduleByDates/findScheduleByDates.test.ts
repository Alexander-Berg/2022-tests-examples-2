import moment from 'moment-timezone';

import {
    findScheduleByDates,
    findEdgeDateOfAllOperatorSchedules,
} from 'utils/findScheduleByDates';

import {
    EMPLOYEE_INFINITY_SCHEDULE_EXPIRES_DATE,
    EMPLOYEES_ALL_SIMPLE_CASES,
    EMPLOYEE_NO_SCHEDULES,
    EMPLOYEE_RIGHT_DATE_EXISTS_2,
    EMPLOYEE_RIGHT_DATE_EXISTS_1,
} from './mock';

describe('findScheduleByDates tests', () => {
    test('it must return undefined without schedules', () => {
        expect(findScheduleByDates([], '18.04.2022'))
            .toStrictEqual(undefined);
    });

    test('it must return current schedule with infinite expires date (11.04.22 — ∞, 18.04.2022)', () => {
        expect(findScheduleByDates(
            EMPLOYEE_INFINITY_SCHEDULE_EXPIRES_DATE.schedules,
            '18.04.2022',
        ))
            .toStrictEqual(EMPLOYEE_INFINITY_SCHEDULE_EXPIRES_DATE.schedules[2]);
    });

    test('it must return past schedule with expires date (01.04.22 — 07.04.22, 04.04.2022)', () => {
        expect(findScheduleByDates(
            EMPLOYEE_INFINITY_SCHEDULE_EXPIRES_DATE.schedules,
            '04.04.2022',
        ))
            .toStrictEqual(EMPLOYEE_INFINITY_SCHEDULE_EXPIRES_DATE.schedules[0]);
    });

    test('it must return past schedule with expires date and left range (07.04.22 — 11.04.22, 07.04.2022)', () => {
        expect(findScheduleByDates(
            EMPLOYEE_INFINITY_SCHEDULE_EXPIRES_DATE.schedules,
            '07.04.2022',
        ))
            .toStrictEqual(EMPLOYEE_INFINITY_SCHEDULE_EXPIRES_DATE.schedules[1]);
    });

    test('it must return past schedule with expires date and right range minus 1 (07.04.22 — 11.04.22, 10.04.2022)', () => {
        /*
        * крайняя дата у нас номинально, она не входит в график
        * правая дата всегда не учитывается
        * */
        expect(findScheduleByDates(
            EMPLOYEE_INFINITY_SCHEDULE_EXPIRES_DATE.schedules,
            '10.04.2022',
        ))
            .toStrictEqual(EMPLOYEE_INFINITY_SCHEDULE_EXPIRES_DATE.schedules[1]);
    });

    test('it must return past schedule with expires date and right range (07.04.22 — 11.04.22, 11.04.2022)', () => {
        expect(findScheduleByDates(
            EMPLOYEE_INFINITY_SCHEDULE_EXPIRES_DATE.schedules,
            '11.04.2022',
        ))
            .toStrictEqual(EMPLOYEE_INFINITY_SCHEDULE_EXPIRES_DATE.schedules[2]);
    });
});

/*
* нам нужно тестировать последовательно сначала findScheduleByDates, потому findEdgeDateOfAllOperatorSchedules
* потому что findEdgeDateOfAllOperatorSchedules зависит от findScheduleByDates
* */
describe('findEdgeDateOfAllOperatorSchedules tests', () => {
    describe('testing without default date', () => {
        // тут дефолт проверить
        test('it must return undefined without schedules', () => {
            expect(findEdgeDateOfAllOperatorSchedules([]))
                .toStrictEqual(undefined);
        });

        test('it must return max left start date', () => {
            const expectedDate = moment('2022-04-11T00:00:00+03:00');

            expect(findEdgeDateOfAllOperatorSchedules(EMPLOYEES_ALL_SIMPLE_CASES))
                .toStrictEqual(expectedDate);
        });

        test('it must return undefined as max start date with employee without any schedule', () => {
            expect(findEdgeDateOfAllOperatorSchedules([EMPLOYEE_NO_SCHEDULES]))
                .toStrictEqual(undefined);
        });

        test('it must return max right date of expires schedules', () => {
            /*
            * самый поздний здесь у EMPLOYEE_RIGHT_DATE_EXISTS_1 01.05.2022
            * */
            const expectedDate = moment('2022-05-01T00:00:00+03:00');

            expect(findEdgeDateOfAllOperatorSchedules(
                [EMPLOYEE_RIGHT_DATE_EXISTS_1, EMPLOYEE_RIGHT_DATE_EXISTS_2],
                {type: 'expires_at'},
            ))
                .toStrictEqual(expectedDate);
        });

        test('it must return max right date (isExpiresInfinite is on)', () => {
            /*
            * undefined, потому что стоит флаг по умолчанию, что если есть график без конца — undefined
            * */
            expect(findEdgeDateOfAllOperatorSchedules(
                EMPLOYEES_ALL_SIMPLE_CASES,
                {type: 'expires_at'},
            ))
                .toStrictEqual(undefined);
        });

        test('it must return max right date (isExpiresInfinite is off)', () => {
            /*
            * самый поздний здесь у EMPLOYEE_RIGHT_DATE_EXISTS_1 01.05.2022
            * */
            const expectedDate = moment('2022-05-01T00:00:00+03:00');

            expect(findEdgeDateOfAllOperatorSchedules(
                EMPLOYEES_ALL_SIMPLE_CASES,
                {type: 'expires_at', isExpiresInfinite: false},
            ))
                .toStrictEqual(expectedDate);
        });
    });

    describe('testing with default date', () => {
        const defaultDate = moment();

        // тут дефолт проверить
        test('it must return default date without schedules', () => {
            expect(findEdgeDateOfAllOperatorSchedules([], {defaultDate}))
                .toStrictEqual(defaultDate);
        });
    });
});
