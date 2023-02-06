import moment from 'moment-timezone';

import {checkIntersect, DATE_YYYYMMDD} from '../../format';

type RangeType = Parameters<typeof checkIntersect>[0];

describe('checkIntersect tests', () => {
    describe('true tests', () => {
        test('it must return true [0; 3] and [1; 2]', () => {
            const lhs: RangeType = [
                moment('2022-01-18', DATE_YYYYMMDD),
                moment('2022-01-21', DATE_YYYYMMDD),
            ];
            const rhs: RangeType = [
                moment('2022-01-19', DATE_YYYYMMDD),
                moment('2022-01-20', DATE_YYYYMMDD),
            ];

            expect(checkIntersect(lhs, rhs))
                .toEqual(true);
        });

        test('it must return true [0; 3] and [0; 2]', () => {
            const firstDate = moment('2022-01-18', DATE_YYYYMMDD);

            const lhs: RangeType = [
                firstDate,
                moment('2022-01-21', DATE_YYYYMMDD),
            ];
            const rhs: RangeType = [
                firstDate,
                moment('2022-01-20', DATE_YYYYMMDD),
            ];

            expect(checkIntersect(lhs, rhs))
                .toEqual(true);
        });

        test('it must return true [0; 3] and [1; 3]', () => {
            const secondDate = moment('2022-01-21', DATE_YYYYMMDD);

            const lhs: RangeType = [
                moment('2022-01-18', DATE_YYYYMMDD),
                secondDate,
            ];
            const rhs: RangeType = [
                moment('2022-01-19', DATE_YYYYMMDD),
                secondDate,
            ];

            expect(checkIntersect(lhs, rhs))
                .toEqual(true);
        });

        test('it must return true [3; 5] and [1; 4]', () => {
            const lhs: RangeType = [
                moment('2022-01-18', DATE_YYYYMMDD),
                moment('2022-01-21', DATE_YYYYMMDD),
            ];
            const rhs: RangeType = [
                moment('2022-01-16', DATE_YYYYMMDD),
                moment('2022-01-20', DATE_YYYYMMDD),
            ];

            expect(checkIntersect(lhs, rhs))
                .toEqual(true);
        });

        test('it must return true [3; 5] and [4; 7]', () => {
            const lhs: RangeType = [
                moment('2022-01-18', DATE_YYYYMMDD),
                moment('2022-01-21', DATE_YYYYMMDD),
            ];
            const rhs: RangeType = [
                moment('2022-01-20', DATE_YYYYMMDD),
                moment('2022-01-23', DATE_YYYYMMDD),
            ];

            expect(checkIntersect(lhs, rhs))
                .toEqual(true);
        });

        test('it must return true [3; 5] and [1; 3]', () => {
            const lhs: RangeType = [
                moment('2022-01-18', DATE_YYYYMMDD),
                moment('2022-01-21', DATE_YYYYMMDD),
            ];
            const rhs: RangeType = [
                moment('2022-01-16', DATE_YYYYMMDD),
                moment('2022-01-18', DATE_YYYYMMDD),
            ];

            expect(checkIntersect(lhs, rhs))
                .toEqual(true);
        });

        test('it must return true [3; 5] and [5; 7]', () => {
            const lhs: RangeType = [
                moment('2022-01-18', DATE_YYYYMMDD),
                moment('2022-01-21', DATE_YYYYMMDD),
            ];
            const rhs: RangeType = [
                moment('2022-01-21', DATE_YYYYMMDD),
                moment('2022-01-23', DATE_YYYYMMDD),
            ];

            expect(checkIntersect(lhs, rhs))
                .toEqual(true);
        });

        test('it must return true [3; 5] and [1; 7]', () => {
            const lhs: RangeType = [
                moment('2022-01-18', DATE_YYYYMMDD),
                moment('2022-01-21', DATE_YYYYMMDD),
            ];
            const rhs: RangeType = [
                moment('2022-01-16', DATE_YYYYMMDD),
                moment('2022-01-23', DATE_YYYYMMDD),
            ];

            expect(checkIntersect(lhs, rhs))
                .toEqual(true);
        });
    });

    /// ///////////////////////////////////

    describe('false tests', () => {
        test('it must return false [4; 7] and [1; 2]', () => {
            const lhs: RangeType = [
                moment('2022-01-18', DATE_YYYYMMDD),
                moment('2022-01-21', DATE_YYYYMMDD),
            ];
            const rhs: RangeType = [
                moment('2022-01-15', DATE_YYYYMMDD),
                moment('2022-01-16', DATE_YYYYMMDD),
            ];

            expect(checkIntersect(lhs, rhs))
                .toEqual(false);
        });

        test('it must return false [4; 7] and [9; 10]', () => {
            const lhs: RangeType = [
                moment('2022-01-18', DATE_YYYYMMDD),
                moment('2022-01-21', DATE_YYYYMMDD),
            ];
            const rhs: RangeType = [
                moment('2022-01-23', DATE_YYYYMMDD),
                moment('2022-01-24', DATE_YYYYMMDD),
            ];

            expect(checkIntersect(lhs, rhs))
                .toEqual(false);
        });
    });
});
