import { Offer } from 'sections/offers/types';
import { offerToBonusesArray } from './offerToBonusesArray';

describe('bonusesObjectToArray', () => {
  it('returns array with available bonuses', () => {
    const offer = {
      yellowNumbers: true,
      providesPhone: true,
      licensed: false,
      babyChair: true,
      branded: false,
      carRepair: false,
      carFuel: false,
      carWash: true,
      carService: true,
      canBuyCar: false,
      insuranceCasco: false,
      techSupport: false,
      seasonalTireReplacement: false
    };
    const expected = [
      'yellowNumbers',
      'providesPhone',
      'babyChair',
      'carWash',
      'carService'
    ];
    expect(offerToBonusesArray(offer as Offer).sort()).toStrictEqual(expected.sort());
  });

  it('returns empty array if there are no available bonuses', () => {
    const bonuses = {
      licensed: false,
      carFuel: false
    };
    expect(offerToBonusesArray(bonuses as Offer)).toStrictEqual([]);
  });
});
