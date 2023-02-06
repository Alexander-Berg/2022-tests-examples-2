import {Rate, WeekDay} from '../types';

/**
 * DurationInMinutes
 */
export const durInMins = (days: number = 0, hours: number = 0, mins: number = 0) => days * 24 * 60 + hours * 60 + mins;

export const createRate = (
    wdStart: WeekDay,
    start: string,
    wdEnd: WeekDay,
    end: string,
    bonus_amount: string,
): Rate => ({
    weekDayStart: wdStart,
    start,
    weekDayEnd: wdEnd,
    end,
    bonus_amount,
});
