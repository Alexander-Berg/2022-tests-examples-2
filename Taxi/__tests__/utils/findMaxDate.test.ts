import moment, {Moment} from 'moment-timezone';

import {DATE_DDMMYYYYHHMM} from '../../format';
import {findMinMaxRangeDate} from '../../utils';

describe('findMaxDate tests', () => {
    test('it must return target date ([0, 4], 6 -> 6)', () => {
        const date = moment('06.08.1997 12:42', DATE_DDMMYYYYHHMM);
        const range: [Moment, Moment] = [
            moment('01.08.1997 12:42', DATE_DDMMYYYYHHMM),
            moment('04.08.1997 12:42', DATE_DDMMYYYYHHMM),
        ];

        expect(findMinMaxRangeDate({range, targetDate: date}))
            .toEqual(date);
    });

    test('it must return target date ([0, 4], 4 -> 4)', () => {
        const date = moment('04.08.1997 12:42', DATE_DDMMYYYYHHMM);
        const range: [Moment, Moment] = [
            moment('01.08.1997 12:42', DATE_DDMMYYYYHHMM),
            moment('04.08.1997 12:42', DATE_DDMMYYYYHHMM),
        ];

        expect(findMinMaxRangeDate({range, targetDate: date}))
            .toEqual(date);
    });

    test('it must return target date ([0, 4], 0 -> 0)', () => {
        const date = moment('01.08.1997 12:42', DATE_DDMMYYYYHHMM);
        const range: [Moment, Moment] = [
            moment('01.08.1997 12:42', DATE_DDMMYYYYHHMM),
            moment('04.08.1997 12:42', DATE_DDMMYYYYHHMM),
        ];

        expect(findMinMaxRangeDate({range, targetDate: date}))
            .toEqual(date);
    });

    test('it must return target date ([0, 4], 2 -> 2)', () => {
        const date = moment('02.08.1997 12:42', DATE_DDMMYYYYHHMM);
        const range: [Moment, Moment] = [
            moment('01.08.1997 12:42', DATE_DDMMYYYYHHMM),
            moment('04.08.1997 12:42', DATE_DDMMYYYYHHMM),
        ];

        expect(findMinMaxRangeDate({range, targetDate: date}))
            .toEqual(date);
    });

    test('it must return target date ([0, 4], -1 -> -1)', () => {
        const date = moment('30.07.1997 12:42', DATE_DDMMYYYYHHMM);
        const range: [Moment, Moment] = [
            moment('01.08.1997 12:42', DATE_DDMMYYYYHHMM),
            moment('04.08.1997 12:42', DATE_DDMMYYYYHHMM),
        ];

        expect(findMinMaxRangeDate({range, targetDate: date}))
            .toEqual(date);

        expect(findMinMaxRangeDate({
            range,
            targetDate: date,
            firstIsTarget: false,
        }))
            .toEqual(range[0]);
    });

    test('it must return target date ([undefined, undefined], -1 -> -1)', () => {
        const date = moment('30.07.1997 12:42', DATE_DDMMYYYYHHMM);
        const range: Undefinable<[Moment, Moment]> = undefined;

        expect(findMinMaxRangeDate({range, targetDate: date}))
            .toEqual(date);
    });
});
