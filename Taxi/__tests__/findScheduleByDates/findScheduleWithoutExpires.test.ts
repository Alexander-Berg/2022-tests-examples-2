import {findScheduleWithoutExpires} from 'utils/findScheduleByDates';

import {
    EMPLOYEE_NO_SCHEDULES,
    EMPLOYEE_RIGHT_DATE_EXISTS_2,
    EMPLOYEE_INFINITY_SCHEDULE_EXPIRES_DATE,
} from './mock';

describe('findScheduleWithoutExpires tests', () => {
    test('it must return undefined without schedules', () => {
        expect(findScheduleWithoutExpires([]))
            .toStrictEqual(undefined);
    });

    test('it must return undefined with empty schedules', () => {
        expect(findScheduleWithoutExpires(EMPLOYEE_NO_SCHEDULES.schedules))
            .toStrictEqual(undefined);
    });

    test('it must return schedules without expires date', () => {
        expect(findScheduleWithoutExpires(EMPLOYEE_INFINITY_SCHEDULE_EXPIRES_DATE.schedules))
            .toStrictEqual(EMPLOYEE_INFINITY_SCHEDULE_EXPIRES_DATE.schedules[2]);
    });

    test('it must return undefined, because all schedules are having expires date', () => {
        expect(findScheduleWithoutExpires(EMPLOYEE_RIGHT_DATE_EXISTS_2.schedules))
            .toStrictEqual(undefined);
    });
});
