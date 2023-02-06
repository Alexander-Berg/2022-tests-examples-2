import { isEqual, differenceInDays } from 'date-fns';

import { RelativePeriod } from 'application/modules/Time/modules/Period/typings';

import { defaultPeriod } from '../duck';
import { parsePeriodFromSources, parseGroupingFromSources } from '../parse';
import { getDates } from '../serialize';

describe('Period', () => {
    describe('parse', () => {
        describe('parsePeriodFromSources', () => {
            it('works with invalid items', () => {
                const result = parsePeriodFromSources([
                    'week',
                    '',
                    null,
                    undefined,
                ]);
                expect(result.type).toBe('relative');
            });
            it('returns default if all items are invalid', () => {
                const result = parsePeriodFromSources(['eee', null, undefined]);
                expect(result).toEqual(defaultPeriod);
            });
        });
        describe('parseGroupingFromSources', () => {
            it('works with invalid items', () => {
                const result = parseGroupingFromSources(
                    ['day', '', null, undefined],
                    { type: 'relative', period: { type: 'week' } },
                );

                expect(result).toBe('day');
            });
            it('returns default if all items are invalid', () => {
                const result = parseGroupingFromSources(
                    ['hey', '', null, undefined],
                    { type: 'relative', period: { type: 'week' } },
                );

                expect(result).toBe('day');
            });
            it('works', () => {
                const result = parseGroupingFromSources(
                    ['hour', null, undefined],
                    { type: 'relative', period: { type: 'yesterday' } },
                );

                expect(result).toBe('hour');
            });
        });
    });

    describe('getDates', () => {
        describe('relative', () => {
            it('retrieves current date', () => {
                const yesterday = getDates({
                    type: 'relative',
                    period: {
                        type: 'yesterday',
                    },
                });

                const today = getDates({
                    type: 'relative',
                    period: {
                        type: 'today',
                    },
                });

                const week = getDates({
                    type: 'relative',
                    period: {
                        type: 'week',
                    },
                });

                expect(
                    isEqual(new Date(yesterday.from), new Date(yesterday.to)),
                ).toBe(true);

                expect(isEqual(new Date(today.from), new Date(today.to))).toBe(
                    true,
                );

                expect(
                    differenceInDays(
                        new Date(today.from),
                        new Date(yesterday.from),
                    ),
                ).toEqual(1);

                expect(
                    differenceInDays(new Date(week.to), new Date(week.from)),
                ).toEqual(6);

                expect(
                    differenceInDays(new Date(week.to), new Date(today.to)),
                ).toEqual(0);

                expect(
                    differenceInDays(new Date(today.to), new Date(week.from)),
                ).toEqual(6);
            });

            it('retrieves previous date', () => {
                const getCurrentAndPrevPeriods = (period: RelativePeriod) => {
                    return [false, true].map((previous) =>
                        getDates(
                            {
                                type: 'relative',
                                period: {
                                    type: period,
                                },
                            },
                            previous,
                        ),
                    );
                };

                const [yesterday, prevYesterday] = getCurrentAndPrevPeriods(
                    'yesterday',
                );
                const [today, prevToday] = getCurrentAndPrevPeriods('today');
                const [week, prevWeek] = getCurrentAndPrevPeriods('week');

                expect(
                    differenceInDays(
                        new Date(yesterday.from),
                        new Date(prevYesterday.from),
                    ),
                ).toEqual(1);

                expect(
                    differenceInDays(
                        new Date(yesterday.to),
                        new Date(prevYesterday.to),
                    ),
                ).toEqual(1);

                expect(
                    differenceInDays(
                        new Date(today.from),
                        new Date(prevToday.from),
                    ),
                ).toEqual(1);

                expect(
                    differenceInDays(
                        new Date(today.to),
                        new Date(prevToday.to),
                    ),
                ).toEqual(1);

                expect(
                    differenceInDays(
                        new Date(week.from),
                        new Date(prevWeek.from),
                    ),
                ).toEqual(7);

                expect(
                    differenceInDays(new Date(week.to), new Date(prevWeek.to)),
                ).toEqual(7);
            });
        });

        describe('absolute', () => {
            it('retrieves date', () => {
                const from = new Date().toString();
                const to = new Date().toString();
                const period = getDates({
                    type: 'absolute',
                    period: {
                        from,
                        to,
                    },
                });

                expect(period.from).toEqual(from);
                expect(period.to).toEqual(to);
            });

            it('retrieves previous date', () => {
                const getCurrentAndPrevPeriods = (period: RelativePeriod) => {
                    const current = getDates({
                        type: 'relative',
                        period: {
                            type: period,
                        },
                    });

                    const prev = getDates(
                        {
                            type: 'absolute',
                            period: {
                                from: current.from,
                                to: current.to,
                            },
                        },
                        true,
                    );

                    return [current, prev] as const;
                };

                const [today, prevToday] = getCurrentAndPrevPeriods('today');
                const [yesterday, prevYesterday] = getCurrentAndPrevPeriods(
                    'yesterday',
                );
                const [week, prevWeek] = getCurrentAndPrevPeriods('week');

                expect(
                    differenceInDays(
                        new Date(today.from),
                        new Date(prevToday.from),
                    ),
                ).toEqual(1);

                expect(
                    differenceInDays(
                        new Date(today.to),
                        new Date(prevToday.to),
                    ),
                ).toEqual(1);

                expect(
                    differenceInDays(
                        new Date(yesterday.from),
                        new Date(prevYesterday.from),
                    ),
                ).toEqual(1);

                expect(
                    differenceInDays(
                        new Date(yesterday.to),
                        new Date(prevYesterday.to),
                    ),
                ).toEqual(1);

                expect(
                    differenceInDays(
                        new Date(week.from),
                        new Date(prevWeek.from),
                    ),
                ).toEqual(7);

                expect(
                    differenceInDays(new Date(week.to), new Date(prevWeek.to)),
                ).toEqual(7);
            });
        });
    });
});
