import { SchedulePiecework, ScheduleRental } from 'sections/offers/types';

import { isSchedulePiecework, isScheduleRental } from './getScheduleKind';

/* eslint-disable @typescript-eslint/camelcase */
const scheduleRental: ScheduleRental = {
  schedule_kind: 'six_days_per_week',
  cost_per_day: 1000,
  deposit_amount: 1000,
  min_rental_period: 1,
  commission: 100
};

const schedulePiecework: SchedulePiecework = {
  schedule_kind: 'two_days_in_two',
  salary: 'fifty_fifty',
  min_order_amount: 100
};
/* eslint-enable @typescript-eslint/camelcase */

describe('isSchedulePiecework', () => {
  it('returns `false` for `scheduleRental`', () => {
    expect(isSchedulePiecework(scheduleRental)).toBe(false);
  });

  it('returns `true` for `schedulePiecework`', () => {
    expect(isSchedulePiecework(schedulePiecework)).toBe(true);
  });
});

describe('isScheduleRental', () => {
  it('returns `false` for `schedulePiecework`', () => {
    expect(isScheduleRental(schedulePiecework)).toBe(false);
  });

  it('returns `true` for `scheduleRental`', () => {
    expect(isScheduleRental(scheduleRental)).toBe(true);
  });
});
