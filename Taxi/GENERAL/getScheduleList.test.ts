import { Offer, SchedulePiecework, ScheduleRental } from 'sections/offers/types';

import { getScheduleList } from './getScheduleList';

describe('getScheduleList', () => {
  /* eslint-disable @typescript-eslint/camelcase */
  const scheduleRental: Array<ScheduleRental> = [{
    min_rental_period: 1,
    cost_per_day: 1000,
    schedule_kind: 'six_days_per_week',
    deposit_amount: 10000,
    commission: 20
  }];

  const schedulePiecework: Array<SchedulePiecework> = [{
    schedule_kind: 'one_day_in_two',
    salary: 'seventy_thirty',
    min_order_amount: 1000
  }];
  /* eslint-enable @typescript-eslint/camelcase */

  it('returns concatenation of `scheduleRental` and `schedulePiecework` when available', () => {
    expect(
      getScheduleList({ schedulePiecework, scheduleRental } as Offer)
    ).toStrictEqual([...scheduleRental, ...schedulePiecework]);

    expect(getScheduleList({ schedulePiecework } as Offer)).toStrictEqual(schedulePiecework);
    expect(getScheduleList({ scheduleRental } as Offer)).toStrictEqual(scheduleRental);
  });

  it('returns default when neither `scheduleRental` nor `schedulePiecework` available', () => {
    const offer = {
      minRentalPeriod: 1,
      dailyRent: 1000,
      depositCost: 10000,
      commission: 20,
      schedulePiecework: null,
      scheduleRental: null
    } as Offer;

    expect(getScheduleList(offer)).toStrictEqual(scheduleRental);
  });
});
