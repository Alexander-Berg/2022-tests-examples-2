import moment from 'moment-timezone';

import {
    EMPLOYEE_INFINITY_SCHEDULE_EXPIRES_DATE,
    EMPLOYEES_ALL_SIMPLE_CASES,
} from 'utils/__tests__/findScheduleByDates/mock';
import dates from 'utils/dates';

import {filterEmployees} from '../utils';

describe('employee.bulk.filterEmployees tests', () => {
    test('it must return undefined without schedules', () => {
        expect(filterEmployees([], moment()))
            .toStrictEqual([]);
    });

    test('it must return three employees except one with infinite right date', () => {
        const dateStart = moment('18.04.2022', dates.format.DATE_DDMMYYYY);

        expect(filterEmployees(EMPLOYEES_ALL_SIMPLE_CASES, dateStart))
            .toStrictEqual(EMPLOYEES_ALL_SIMPLE_CASES.filter(
                ({yandex_uid}) => EMPLOYEE_INFINITY_SCHEDULE_EXPIRES_DATE.yandex_uid !== yandex_uid,
            ));
    });
});
