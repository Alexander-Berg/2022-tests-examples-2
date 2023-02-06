import {Rate as RateView} from '_pkg/blocks/intervals/types';

import {Rate} from '../types';
import {getIntervalRates} from '../utils';

describe('getIntervalRates', () => {
    it('Последовательные интервалы от начала недели до конца', () => {
        const rates: Rate[] = [
            {
                weekDayStart: 'mon',
                weekDayEnd: 'wed',
                bonus_amount: '100',
                start: '00:00',
                end: '15:00',
            },
            {
                weekDayStart: 'wed',
                weekDayEnd: 'mon',
                bonus_amount: '200',
                start: '15:00',
                end: '00:00',
            },
        ];

        const result: RateView[] = [
            {
                week_day: 'mon',
                start: '00:00',
                bonus_amount: '100'
            },
            {
                week_day: 'wed',
                start: '15:00',
                bonus_amount: '200'
            },
        ];

        expect(getIntervalRates(rates)).toEqual(result);
    });

    it('Последовательные интервалы внутри одного дня', () => {
        const rates: Rate[] = [
            {
                weekDayStart: 'mon',
                weekDayEnd: 'mon',
                bonus_amount: '100',
                start: '00:00',
                end: '03:00',
            },
            {
                weekDayStart: 'mon',
                weekDayEnd: 'mon',
                bonus_amount: '200',
                start: '03:00',
                end: '18:00',
            },
        ];

        const result: RateView[] = [
            {
                week_day: 'mon',
                start: '00:00',
                bonus_amount: '100'
            },
            {
                week_day: 'mon',
                start: '03:00',
                bonus_amount: '200'
            },
            {
                week_day: 'mon',
                start: '18:00',
                bonus_amount: '0'
            },
        ];

        expect(getIntervalRates(rates)).toEqual(result);
    });

    it('Интервалы в середине недели не связанные друг с другом', () => {
        const rates: Rate[] = [
            {
                weekDayStart: 'tue',
                weekDayEnd: 'wed',
                bonus_amount: '100',
                start: '00:00',
                end: '15:00',
            },
            {
                weekDayStart: 'fri',
                weekDayEnd: 'sat',
                bonus_amount: '200',
                start: '15:00',
                end: '00:00',
            },
        ];

        const result: RateView[] = [
            {
                week_day: 'tue',
                start: '00:00',
                bonus_amount: '100'
            },
            {
                week_day: 'wed',
                start: '15:00',
                bonus_amount: '0'
            },
            {
                week_day: 'fri',
                start: '15:00',
                bonus_amount: '200'
            },
            {
                week_day: 'sat',
                start: '00:00',
                bonus_amount: '0'
            },
        ];

        expect(getIntervalRates(rates)).toEqual(result);
    });

    it('Пересекающиеся интервалы. Более позднее пересечение отменяет дату окончания предыдущего', () => {
        const rates: Rate[] = [
            {
                weekDayStart: 'mon',
                weekDayEnd: 'fri',
                bonus_amount: '100',
                start: '00:00',
                end: '15:00',
            },
            {
                weekDayStart: 'wed',
                weekDayEnd: 'thu',
                bonus_amount: '200',
                start: '15:00',
                end: '00:00',
            },
        ];

        const result: RateView[] = [
            {
                week_day: 'mon',
                start: '00:00',
                bonus_amount: '100'
            },
            {
                week_day: 'wed',
                start: '15:00',
                bonus_amount: '200'
            },
            {
                week_day: 'thu',
                start: '00:00',
                bonus_amount: '0'
            },
        ];

        expect(getIntervalRates(rates)).toEqual(result);
    });

    it('Должна вставлять отсечку, если последний интервал заканчивается на следующей неделе и не стыкуется с началом первого интервала', () => {
        const rates: Rate[] = [
            {weekDayStart: 'mon', weekDayEnd: 'sun', start: '07:00', end: '00:00', bonus_amount: '1'},
            {weekDayStart: 'sun', weekDayEnd: 'mon', start: '07:00', end: '00:00', bonus_amount: '1'},
        ];

        const result: RateView[] = [
            {bonus_amount: '0', week_day: 'mon', start: '00:00'},
            {bonus_amount: '1', week_day: 'mon', start: '07:00'},
            {bonus_amount: '0', week_day: 'sun', start: '00:00'},
            {bonus_amount: '1', week_day: 'sun', start: '07:00'},
        ];
        expect(getIntervalRates(rates)).toEqual(result);
    });
});
