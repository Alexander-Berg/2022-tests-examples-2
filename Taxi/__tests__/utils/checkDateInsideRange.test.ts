import moment, {Moment} from 'moment-timezone';

import {DATE_DDMMYYYYHHMM} from '../../format';
import {checkDateInsideRange} from '../../utils';

describe('checkDateInsideRange tests', () => {
    const range: [Moment, Moment] = [
        moment('01.08.1997 12:42', DATE_DDMMYYYYHHMM),
        moment('04.08.1997 12:42', DATE_DDMMYYYYHHMM),
    ];

    test('it must return true, ([1, 4], 2)', () => {
        const date = moment('02.08.1997 12:42', DATE_DDMMYYYYHHMM);

        expect(checkDateInsideRange(date, range))
            .toEqual(true);
    });

    test('it must return true, ([1, 4], 1)', () => {
        const date = moment('01.08.1997 12:42', DATE_DDMMYYYYHHMM);

        expect(checkDateInsideRange(date, range))
            .toEqual(true);
    });

    test('it must return true, ([1, 4], 4)', () => {
        const date = moment('04.08.1997 12:42', DATE_DDMMYYYYHHMM);

        expect(checkDateInsideRange(date, range))
            .toEqual(true);
    });

    test('it must return false, ([1, 4], -1)', () => {
        const date = moment('30.07.1997 12:42', DATE_DDMMYYYYHHMM);

        expect(checkDateInsideRange(date, range))
            .toEqual(false);
    });

    test('it must return false, ([1, 4], 6)', () => {
        const date = moment('06.08.1997 12:42', DATE_DDMMYYYYHHMM);

        expect(checkDateInsideRange(date, range))
            .toEqual(false);
    });

    test('it must return false, ((1, 4], 1)', () => {
        const date = moment('01.08.1997 12:42', DATE_DDMMYYYYHHMM);

        expect(checkDateInsideRange(date, range, {isLeftIncludes: false}))
            .toEqual(false);
    });

    test('it must return true, ((1, 4], 2)', () => {
        const date = moment('02.08.1997 12:42', DATE_DDMMYYYYHHMM);

        expect(checkDateInsideRange(date, range, {isLeftIncludes: false}))
            .toEqual(true);
    });

    test('it must return false, ((1, 4), 4)', () => {
        const date = moment('04.08.1997 12:42', DATE_DDMMYYYYHHMM);

        expect(checkDateInsideRange(date, range, {
            isLeftIncludes: false,
            isRightIncludes: false,
        }))
            .toEqual(false);
    });

    test('it must return false, ((1, 4), 6)', () => {
        const date = moment('06.08.1997 12:42', DATE_DDMMYYYYHHMM);

        expect(checkDateInsideRange(date, range, {
            isLeftIncludes: false,
            isRightIncludes: false,
        }))
            .toEqual(false);
    });
});
