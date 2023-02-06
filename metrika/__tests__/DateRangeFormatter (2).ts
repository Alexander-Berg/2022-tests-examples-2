import SpyInstance = jest.SpyInstance;

import moment = require('moment');

import { DateRangeFormatter as DRF } from '../index';

let dateNowSpy: SpyInstance<() => number>;

describe('DateRangeFormatter', () => {
    beforeAll(() => {
        // Set up a fixed current date

        const fixedDateTimestamp = new Date(Date.UTC(2019, 11, 31)).valueOf();

        dateNowSpy = jest.spyOn(Date, 'now');
        dateNowSpy.mockImplementation(() => fixedDateTimestamp);
    });

    afterAll(() => {
        dateNowSpy.mockRestore();
    });

    describe('correctly handles incorrect input', () => {
        it('of start date as a string', () => {
            const fromInput = '2019-!!-02-21';
            const toInput = '2019-02-22';

            const toExpected = moment(toInput).format(DRF.formats.full);

            const expected = `${fromInput} — ${toExpected}`;

            expect(DRF.format(fromInput, toInput)).toBe(expected);
        });

        it('of end date as a string', () => {
            const fromInput = '2019-02-21';
            const toInput = '2019-!!-02-22';

            const fromExpected = moment(fromInput).format(DRF.formats.full);

            const expected = `${fromExpected} — ${toInput}`;

            expect(DRF.format(fromInput, toInput)).toBe(expected);
        });

        it('of both dates as strings', () => {
            const fromInput = '2019-!!-02-21';
            const toInput = '2019-!!-02-22';

            const expected = `${fromInput} — ${toInput}`;

            expect(DRF.format(fromInput, toInput)).toBe(expected);
        });

        it('of both dates as Moment objects', () => {
            const invalidInput = moment.invalid();

            const invalidDateExpected = DRF.invalidDateObjectOutput;
            const expected = `${invalidDateExpected} — ${invalidDateExpected}`;

            expect(DRF.format(invalidInput, invalidInput)).toBe(expected);
        });
    });

    describe('correctly handles ending date being less than starting date', () => {
        it('in the current year', () => {
            const expected = moment('2019-02-21').format(DRF.formats.month);

            expect(DRF.format('2019-02-21', '2019-02-20')).toBe(expected);
        });

        it('in the previous year', () => {
            const expected = moment('2018-02-21').format(DRF.formats.full);

            expect(DRF.format('2018-02-21', '2018-02-20')).toBe(expected);
        });
    });

    describe('correctly formats range of less than a day', () => {
        it('in the current year', () => {
            const expected = moment('2019-02-21').format(DRF.formats.month);

            expect(DRF.format('2019-02-21', '2019-02-21')).toBe(expected);
        });

        it('in the previous year', () => {
            const expected = moment('2018-02-21').format(DRF.formats.full);

            expect(DRF.format('2018-02-21', '2018-02-21')).toBe(expected);
        });
    });

    describe('correctly formats range of a few days ', () => {
        it('in the current year', () => {
            const fromExpected = moment('2019-02-21').format(DRF.formats.day);
            const toExpected = moment('2019-02-25').format(DRF.formats.month);

            const expected = `${fromExpected} — ${toExpected}`;

            expect(DRF.format('2019-02-21', '2019-02-25')).toBe(expected);
        });

        it('in the previous year', () => {
            const fromExpected = moment('2018-02-21').format(DRF.formats.day);
            const toExpected = moment('2018-02-25').format(DRF.formats.full);

            const expected = `${fromExpected} — ${toExpected}`;

            expect(DRF.format('2018-02-21', '2018-02-25')).toBe(expected);
        });
    });

    describe('correctly formats range of a few days', () => {
        it('of different months in the current year', () => {
            const fromExpected = moment('2019-02-15').format(DRF.formats.month);
            const toExpected = moment('2019-04-09').format(DRF.formats.month);

            const expected = `${fromExpected} — ${toExpected}`;

            expect(DRF.format('2019-02-15', '2019-04-09')).toBe(expected);
        });

        it('of different months in the previous year', () => {
            const fromExpected = moment('2018-02-15').format(DRF.formats.month);
            const toExpected = moment('2018-04-09').format(DRF.formats.full);

            const expected = `${fromExpected} — ${toExpected}`;

            expect(DRF.format('2018-02-15', '2018-04-09')).toBe(expected);
        });
    });

    describe('correctly formats range of a few days between different years', () => {
        it('ending on previous year', () => {
            const fromExpected = moment('2017-12-15').format(DRF.formats.full);
            const toExpected = moment('2018-01-15').format(DRF.formats.full);

            const expected = `${fromExpected} — ${toExpected}`;

            expect(DRF.format('2017-12-15', '2018-01-15')).toBe(expected);
        });

        it('ending on current year', () => {
            const fromExpected = moment('2018-12-15').format(DRF.formats.full);
            const toExpected = moment('2019-01-15').format(DRF.formats.full);

            const expected = `${fromExpected} — ${toExpected}`;

            expect(DRF.format('2018-12-15', '2019-01-15')).toBe(expected);
        });
    });
});
