import moment from 'moment-timezone';

import {
    getTodayStartUTCFormatted,
    convertLocalDateToServer,
    convertDatetimeToServer,
    makeMomentFromDuration,
    checkPeriodStrict,
    makeFullPeriodWithTimes,
    createTimeFromMinutes,
    HOURS_RANGE,
} from '../format';

test('getTodayStartUTCFormatted return today day start in UTC', () => {
    const now = moment('2021-12-23T15:30:20');

    expect(getTodayStartUTCFormatted(now)).toEqual('2021-12-23T00:00:00Z');
});

test('convertLocalDateToServer convert date to server format with Msk TZ', () => {
    const now = moment('2021-12-23');

    expect(convertLocalDateToServer(now)).toEqual('2021-12-23T00:00:00 +0300');
});

test('convertLocalDateToServer return undefined if no date', () => {
    expect(convertLocalDateToServer(undefined)).toBeUndefined();
});

test('convertDatetimeToServer convert datetime to server format', () => {
    const now = moment('2021-12-23T15:30:20');

    expect(convertDatetimeToServer(now)).toEqual('2021-12-23T15:30:20+03:00');
});

test('convertDatetimeToServer return undefined if no datetime', () => {
    expect(convertDatetimeToServer(undefined)).toBeUndefined();
});

test('makeMomentFromDuration return moment from duration in minutes', () => {
    const durationMinutes = 5;
    const now = moment().startOf('day').add(durationMinutes, 'minute');

    expect(makeMomentFromDuration(durationMinutes, 'minutes').format()).toEqual(now.format());
});

test('makeMomentFromDuration can`t work with hours', () => {
    try {
        makeMomentFromDuration(5, 'hours').format();
    } catch (e) {
        expect(e.message).toEqual('common.error_duration_formatter');
    }
});

test('checkPeriodStrict return true if start of period is before end', () => {
    const start = moment('2021-12-23T00:00:00');
    const end = moment('2021-12-23T00:05:00');

    expect(checkPeriodStrict(start, end)).toEqual(true);
});

test('checkPeriodStrict throw error if start of period is before end', () => {
    try {
        const start = moment('2021-12-23T00:05:00');
        const end = moment('2021-12-23T00:00:00');

        checkPeriodStrict(start, end);
    } catch (e) {
        expect(e.message).toEqual('components.shifts.the_dates_are_mixed_up.');
    }
});

test('makeFullPeriodWithTimes convert period to UTC start/end day period', () => {
    const start = moment('2021-12-23T12:00:00');
    const end = moment('2021-12-23T15:00:00');

    expect(makeFullPeriodWithTimes([start, end])?.map(item => item?.utc().format()))
        .toStrictEqual(['2021-12-22T21:00:00Z', '2021-12-23T20:59:00Z']);
});

test('makeFullPeriodWithTimes don`t touch nulls', () => {
    expect(makeFullPeriodWithTimes([null, null]))
        .toStrictEqual([null, null]);
});

describe('createTimeFromMinutes tests', () => {
    test('it must convert minutes before 1 hour to time string', () => {
        expect(createTimeFromMinutes(40))
            .toEqual('00:40');
    });

    test('it must convert minutes with integer hour to time string', () => {
        expect(createTimeFromMinutes(150))
            .toEqual('02:30');
    });

    test('it must convert minutes with 23 hour to time string', () => {
        expect(createTimeFromMinutes(1380)) // 23 * 60
            .toEqual('23:00');
    });

    test('it must convert minutes with 24 hour to time string', () => {
        expect(createTimeFromMinutes(1440)) // 24 * 60
            .toEqual('00:00');
    });

    test('it must convert minutes with 23:59 hour to time string', () => {
        expect(createTimeFromMinutes(1439)) // 23 * 60 + 59
            .toEqual('23:59');
    });

    test('it must convert minutes with 24:01 hour to time string', () => {
        expect(createTimeFromMinutes(1441)) // 24 * 60 + 1
            .toEqual('00:01');
    });

    test('it must convert 0 minutes to time string', () => {
        expect(createTimeFromMinutes(0))
            .toEqual('00:00');
    });

    test('it must convert minus minutes to time string', () => {
        expect(createTimeFromMinutes(-150))
            .toEqual('21:30');
    });

    test('it must not convert not digit to time string', () => {
        const notDigitError = 'minutes must have type number';

        try {
            createTimeFromMinutes(+'1,.124399');
        } catch (e) {
            expect(e.message).toEqual(notDigitError);
        }

        try {
            createTimeFromMinutes('~~~' as any as number);
        } catch (e) {
            expect(e.message).toEqual(notDigitError);
        }
    });
});

describe('HOURS_RANGE tests', () => {
    test('it must return list 0..23', () => {
        const expected = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23];

        expect(HOURS_RANGE).toStrictEqual(expected);
    });
});
