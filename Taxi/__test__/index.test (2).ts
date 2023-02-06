import {calcPromocodesInOrdersPercentage} from '..';

test('calcPromocodesInOrdersPercentage', () => {
    expect(calcPromocodesInOrdersPercentage()).toEqual(0);
    expect(calcPromocodesInOrdersPercentage(0, 100)).toEqual(0);
    expect(calcPromocodesInOrdersPercentage(1, 0)).toEqual(0);

    expect(calcPromocodesInOrdersPercentage(1, 99)).toEqual(1.01);
    expect(calcPromocodesInOrdersPercentage(100, 99)).toEqual(101.01);

    expect(calcPromocodesInOrdersPercentage(1, 101)).toEqual(0.99);
    expect(calcPromocodesInOrdersPercentage(101, 100)).toEqual(101);

    expect(calcPromocodesInOrdersPercentage(1, 200)).toEqual(0.5);
    expect(calcPromocodesInOrdersPercentage(1, 2000)).toEqual(0.05);
    expect(calcPromocodesInOrdersPercentage(1, 20000)).toEqual(0.01);
});
