import {
    convertToRateWithIndexes,
    fillRangeIndexes,
    getIndex,
    getIntervalCounters,
    getIntervals,
    isRangeOverlap,
    joinRates,
    splitNotOrderedRate
} from '../rateCommonUtils';
import {createRate, durInMins} from './utils';

describe('getIndex', () => {
    it('mon 00:00', () => {
        expect(getIndex('mon', '00:00')).toBe(0);
    });

    it('mon 01:02', () => {
        expect(getIndex('mon', '01:02')).toBe(durInMins(0, 1, 2));
    });

    it('tue 02:03', () => {
        expect(getIndex('tue', '02:03')).toBe(durInMins(1, 2, 3));
    });

    it('sun 23:59', () => {
        expect(getIndex('sun', '23:59')).toBe(durInMins(6, 23, 59));
    });
});

describe('getIntervals', () => {
    it('один интервал', () => {
        const rates = convertToRateWithIndexes([
            {
                weekDayStart: 'tue',
                start: '10:30',
                weekDayEnd: 'tue',
                end: '18:30',
                bonus_amount: 'A',
            },
        ]);
        expect(getIntervals(rates)).toEqual([durInMins(1, 10, 30), durInMins(1, 18, 30)]);
    });

    it('два интервала', () => {
        const rates = convertToRateWithIndexes([
            {
                weekDayStart: 'mon',
                start: '00:00',
                weekDayEnd: 'mon',
                end: '16:00',
            },
            {
                weekDayStart: 'tue',
                start: '00:00',
                weekDayEnd: 'wed',
                end: '00:00',
            },
        ]);
        expect(getIntervals(rates)).toEqual([0, durInMins(0, 16), durInMins(1), durInMins(2)]);
    });

    it('два пересекающихся интервала', () => {
        const rates = convertToRateWithIndexes([
            {
                weekDayStart: 'mon',
                start: '00:00',
                weekDayEnd: 'mon',
                end: '02:00',
            },
            {
                weekDayStart: 'mon',
                start: '01:00',
                weekDayEnd: 'mon',
                end: '03:00',
            },
        ]);
        expect(getIntervals(rates)).toEqual([0, durInMins(0, 1), durInMins(0, 2), durInMins(0, 3)]);
    });

    it('интервал во всю неделю', () => {
        const rates = convertToRateWithIndexes([
            {
                weekDayStart: 'tue',
                start: '00:00',
                weekDayEnd: 'tue',
                end: '00:00',
            },
        ]);
        expect(getIntervals(rates)).toEqual([durInMins(0), durInMins(7)]);
    });
});

describe('getIntervalCounters', () => {
    it('интервал вне индекса', () => {
        const rates = convertToRateWithIndexes([
            createRate('mon', '01:00', 'mon', '02:00', 'A'),
        ]);
        expect(getIntervalCounters(rates, 0)).toBe('0');
    });

    it('1 интервал', () => {
        const rates = convertToRateWithIndexes([
            createRate('mon', '00:00', 'mon', '02:00', 'A'),
        ]);
        expect(getIntervalCounters(rates, durInMins(0, 1))).toBe('A');
    });

    it('2 пересекающихся интервала', () => {
        const rates = convertToRateWithIndexes([
            createRate('mon', '00:00', 'mon', '02:00', 'A'),
            createRate('mon', '00:00', 'mon', '02:00', 'B'),
        ]);
        expect(getIntervalCounters(rates, durInMins(0, 1))).toBe('A,B');
    });
});

describe('splitNotOrderedRate', () => {
    it('должен разделить вс-вт на пн-вт + вс-пн', () => {
        const rate = fillRangeIndexes(createRate('sun', '11:11', 'tue', '22:22', 'A'));

        expect(splitNotOrderedRate(rate)).toEqual([
            {
                bonus_amount: 'A',
                start: '00:00',
                weekDayStart: 'mon',
                indexStart: 0,
                weekDayEnd: 'tue',
                end: '22:22',
                indexEnd: 2782,
                isWholeWeek: false,
            },
            {
                bonus_amount: 'A',
                weekDayStart: 'sun',
                start: '11:11',
                indexStart: 9311,
                weekDayEnd: 'mon',
                end: '00:00',
                indexEnd: 10080,
                isWholeWeek: false,
            },
        ]);
    });
});

describe('joinRates', () => {
    it('должен объединить пересекающиеся интервалы', () => {
        const rates = convertToRateWithIndexes([
            createRate('mon', '10:00', 'mon', '20:00', 'A'),
            createRate('mon', '05:00', 'mon', '10:00', 'A'),
            createRate('mon', '04:00', 'mon', '05:00', 'A'),
            createRate('mon', '02:00', 'mon', '03:59', 'A'),
        ]);
        const expected = convertToRateWithIndexes([
            createRate('mon', '02:00', 'mon', '03:59', 'A'),
            createRate('mon', '04:00', 'mon', '20:00', 'A'),
        ]);
        expect(joinRates(rates)).toEqual(expected);
    });
});

describe('isRangeOverlap', () => {
    it('должен работать с пустым массивом', () => {
        expect(isRangeOverlap([])).toBe(false);
    });

    it('пересечение, 2х одинаковых отрезка', () => {
        const rates = [
            createRate('fri', '10:00', 'mon', '20:00', 'A'),
            createRate('fri', '10:00', 'mon', '20:00', 'A'),
        ];
        expect(isRangeOverlap(rates)).toBe(true);
    });

    it('пересечение', () => {
        const rates = [
            createRate('mon', '10:00', 'mon', '20:01', 'A'),
            createRate('mon', '20:00', 'mon', '23:00', 'A'),
        ];
        expect(isRangeOverlap(rates)).toBe(true);
    });

    it('пересечение, где 1 rate пересекает воскресенье', () => {
        const rates = [
            createRate('sun', '10:00', 'mon', '20:00', 'A'),
            createRate('mon', '19:00', 'mon', '23:00', 'A'),
        ];
        expect(isRangeOverlap(rates)).toBe(true);
    });

    it('пересечение, есть rate во всю неделю', () => {
        const rates = [
            createRate('mon', '19:00', 'mon', '23:00', 'A'),
            createRate('mon', '20:00', 'mon', '20:00', 'A'),
        ];
        expect(isRangeOverlap(rates)).toBe(true);
    });

    it('нет пересечений', () => {
        const rates = [
            createRate('mon', '19:00', 'mon', '23:00', 'A'),
            createRate('mon', '23:00', 'thu', '00:00', 'A'),
        ];
        expect(isRangeOverlap(rates)).toBe(false);
    });

    it('нет пересечений, 1 rate во всю неделю', () => {
        const rates = [
            createRate('mon', '19:00', 'mon', '19:00', 'A'),
        ];
        expect(isRangeOverlap(rates)).toBe(false);
    });

    it('нет пересечений, 1 rate пересекает конец недели', () => {
        const rates = [
            createRate('mon', '19:00', 'tue', '19:00', 'A'),
            createRate('fri', '19:00', 'mon', '19:00', 'A'),
        ];
        expect(isRangeOverlap(rates)).toBe(false);
    });
});
