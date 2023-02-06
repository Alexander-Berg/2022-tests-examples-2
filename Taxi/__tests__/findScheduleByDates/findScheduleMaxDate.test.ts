import moment from 'moment-timezone';

import {findScheduleMaxDate} from 'utils/findScheduleByDates';

import {
    EMPLOYEE_NO_SCHEDULES,
    EMPLOYEE_RIGHT_DATE_EXISTS_1,
    EMPLOYEE_RIGHT_DATE_EXISTS_2,
    EMPLOYEE_INFINITY_SCHEDULE_EXPIRES_DATE,
} from './mock';

describe('findScheduleMaxDate tests', () => {
    test('it must return undefined without schedules', () => {
        expect(findScheduleMaxDate([]))
            .toStrictEqual(undefined);
    });

    describe('testing field expires_at on single employee', () => {
        test('it must return undefined with infinite expires date', () => {
            expect(findScheduleMaxDate(
                EMPLOYEE_INFINITY_SCHEDULE_EXPIRES_DATE.schedules,
                'expires_at',
            ))
                .toStrictEqual(undefined);
        });

        test('it must return undefined with empty schedules', () => {
            expect(findScheduleMaxDate(
                EMPLOYEE_NO_SCHEDULES.schedules,
                'expires_at',
            ))
                .toStrictEqual(undefined);
        });

        test('it must return date with exists expires date May', () => {
            const expectedDate = moment('2022-05-01T00:00:00+03:00');

            expect(findScheduleMaxDate(
                EMPLOYEE_RIGHT_DATE_EXISTS_1.schedules,
                'expires_at',
            ))
                .toStrictEqual(expectedDate);
        });

        test('it must return undefined with exists expires date April', () => {
            const expectedDate = moment('2022-04-10T00:00:00+03:00');

            expect(findScheduleMaxDate(
                EMPLOYEE_RIGHT_DATE_EXISTS_2.schedules,
                'expires_at',
            ))
                .toStrictEqual(expectedDate);
        });
    });

    describe('testing field starts_at on single employee', () => {
        test('it must return max left date with infinite expires date', () => {
            const expectedDate = moment('2022-04-11T00:00:00+03:00');

            expect(findScheduleMaxDate(EMPLOYEE_INFINITY_SCHEDULE_EXPIRES_DATE.schedules))
                .toStrictEqual(expectedDate);
        });

        test('it must return undefined with empty schedules', () => {
            expect(findScheduleMaxDate(EMPLOYEE_NO_SCHEDULES.schedules))
                .toStrictEqual(undefined);
        });

        test('it must return max left date with all expires schedules', () => {
            const expectedDate = moment('2022-04-01T00:00:00+03:00');

            expect(findScheduleMaxDate(EMPLOYEE_RIGHT_DATE_EXISTS_1.schedules))
                .toStrictEqual(expectedDate);
        });
    });
});
