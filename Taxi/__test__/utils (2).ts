import isNumber from 'lodash/isNumber';

import {SpecialTaximeter} from '../../../../types';
import {INTERVAL} from './const';

type TariffInterval = SpecialTaximeter['price']['distance_price_intervals'][number];

export const checkPriceItem = (item: TariffInterval) => {
    expect(isNumber(item.begin)).toBe(true);
    expect(isNumber(item.end)).toBe(true);
    expect(isNumber(item.price)).toBe(true);
    expect(item.step).toBe(INTERVAL.round_time_step);
    expect(item.mode).toBe(INTERVAL.round_time_mode);
};
