import range from 'lodash/range';
import moment from 'moment-timezone';

import {
    DATE_DDMMYYYYHHMM,
    getHoursListFromNow,
} from '../../format';

describe('getHoursListFromNow tests', () => {
    test('it must return correct not empty hours of middle day', () => {
        const date = moment('06.08.1997 12:42', DATE_DDMMYYYYHHMM);

        expect(getHoursListFromNow(date))
            .toEqual({
                past: range(0, 13),
                last: range(13, 23),
            });
    });

    test('it must return past [0] and 1..23 last hours of 00:00', () => {
        const date = moment('06.08.1997 00:00', DATE_DDMMYYYYHHMM);

        expect(getHoursListFromNow(date))
            .toEqual({
                past: [0],
                last: range(1, 23),
            });
    });

    test('it must return full past and empty last hours of end of the day', () => {
        const date = moment('06.08.1997 23:59', DATE_DDMMYYYYHHMM);

        expect(getHoursListFromNow(date))
            .toEqual({
                past: range(0, 23),
                last: [],
            });
    });

    test('it must return empty past and full last hours of start of the day', () => {
        const date = moment('06.08.1997 00:01', DATE_DDMMYYYYHHMM);

        expect(getHoursListFromNow(date))
            .toEqual({
                past: [0],
                last: range(1, 23),
            });
    });
});
