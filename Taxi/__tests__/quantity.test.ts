import {
    absoluteRefundQuantityStrategy,
    availableRefundQuantityStrategy,
    baseOnCountTakedQuantityStrategy,
    boundedCheckFormated,
    calcSumCountQuantity,
    calcTakedQuantityCounted,
    calcTakedQuantitySafely,
    calcTakedQuantityToMinRemove,
    calcTakedQuantityWithLimit,
    moveToMaxTakedQuantityStrategy,
    moveToMinRemoveTakedQuantityStrategy,
    removeTakedQuantityStrategy,
    stayCurrentTakedQuantityStrategy,
    strictFormatter
} from '../quantity';

describe('takedQuantity', () => {
    test('stayCurrentTakedQuantityStrategy', () => {
        expect(stayCurrentTakedQuantityStrategy(0, 0, 0)).toBe(0);
        expect(stayCurrentTakedQuantityStrategy(0, 0, 100)).toBe(0);
        expect(stayCurrentTakedQuantityStrategy(0, 10, 100)).toBe(10);
        expect(stayCurrentTakedQuantityStrategy(0, 100, 10)).toBe(10);
        expect(stayCurrentTakedQuantityStrategy(9, 0, 100)).toBe(9);
        expect(stayCurrentTakedQuantityStrategy(9, 10, 100)).toBe(19);
        expect(stayCurrentTakedQuantityStrategy(900, 10, 100)).toBe(10);
        expect(stayCurrentTakedQuantityStrategy(90, 9, 100)).toBe(99);
        expect(stayCurrentTakedQuantityStrategy(90, 10, 100)).toBe(100);
        expect(moveToMaxTakedQuantityStrategy(100, 100, 100)).toBe(100);
    });

    test('moveToMaxTakedQuantityStrategy', () => {
        expect(moveToMaxTakedQuantityStrategy(0, 0, 0)).toBe(0);
        expect(moveToMaxTakedQuantityStrategy(0, 0, 100)).toBe(0);
        expect(moveToMaxTakedQuantityStrategy(0, 10, 100)).toBe(10);
        expect(moveToMaxTakedQuantityStrategy(0, 100, 10)).toBe(10);
        expect(moveToMaxTakedQuantityStrategy(9, 0, 100)).toBe(9);
        expect(moveToMaxTakedQuantityStrategy(9, 10, 100)).toBe(19);
        expect(moveToMaxTakedQuantityStrategy(900, 10, 100)).toBe(100);
        expect(moveToMaxTakedQuantityStrategy(90, 9, 100)).toBe(99);
        expect(moveToMaxTakedQuantityStrategy(90, 10, 100)).toBe(100);
        expect(moveToMaxTakedQuantityStrategy(100, 100, 100)).toBe(100);
    });

    test('strictFormatter', () => {
        expect(() => strictFormatter(null)).toThrow();
        expect(() => strictFormatter(undefined)).toThrow();
        expect(() => strictFormatter('')).toThrow();
        expect(() => strictFormatter(' ')).toThrow();
        expect(() => strictFormatter('test')).toThrow();
        expect(() => strictFormatter('0 test')).toThrow();
        expect(() => strictFormatter('10 test')).toThrow();
        expect(() => strictFormatter('0.99 test')).toThrow();
        expect(() => strictFormatter(NaN)).toThrow();
        expect(() => strictFormatter(-10)).toThrow();
        expect(() => strictFormatter(-0)).not.toThrow();
        expect(() => strictFormatter(0.99)).not.toThrow();
        expect(() => strictFormatter(10)).not.toThrow();
        expect(() => strictFormatter('-10')).toThrow();
        expect(() => strictFormatter('-0')).not.toThrow();
        expect(() => strictFormatter('0.99')).not.toThrow();
        expect(() => strictFormatter('10')).not.toThrow();

        expect(strictFormatter(-0)).toBe(0);
        expect(strictFormatter(0.99)).toBe(0.99);
        expect(strictFormatter(10)).toBe(10);
        expect(strictFormatter('-0')).toBe(0);
        expect(strictFormatter('0.99')).toBe(0.99);
        expect(strictFormatter('10')).toBe(10);
    });

    test('calcTakedQuantitySafely', () => {
        expect(() => calcTakedQuantitySafely(0, 0, 0)).not.toThrow();
        expect(() => calcTakedQuantitySafely(null, null, null)).toThrow();
        expect(() => calcTakedQuantitySafely(0, null, null)).toThrow();
        expect(() => calcTakedQuantitySafely(0, 0, null)).toThrow();
        expect(() => calcTakedQuantitySafely(undefined, undefined, undefined)).toThrow();
        expect(() => calcTakedQuantitySafely(undefined, undefined, 0)).toThrow();
        expect(() => calcTakedQuantitySafely(0, undefined, 0)).toThrow();
        expect(() => calcTakedQuantitySafely('', 0, 0)).toThrow();
        expect(() => calcTakedQuantitySafely(0, '', 0)).toThrow();
        expect(() => calcTakedQuantitySafely(0, 0, '')).toThrow();
        expect(() => calcTakedQuantitySafely(' ', 0, 0)).toThrow();
        expect(() => calcTakedQuantitySafely(0, ' ', 0)).toThrow();
        expect(() => calcTakedQuantitySafely(0, 0, ' ')).toThrow();
        expect(() => calcTakedQuantitySafely('test', 0, 0)).toThrow();
        expect(() => calcTakedQuantitySafely(0, 'test', 0)).toThrow();
        expect(() => calcTakedQuantitySafely(0, 0, 'test')).toThrow();
        expect(() => calcTakedQuantitySafely(-10, 0, 0)).toThrow();
        expect(() => calcTakedQuantitySafely(0, -10, 0)).toThrow();
        expect(() => calcTakedQuantitySafely(0, 0, -10)).toThrow();
        expect(() => calcTakedQuantitySafely(NaN, 0, 0)).toThrow();
        expect(() => calcTakedQuantitySafely(0, NaN, 0)).toThrow();
        expect(() => calcTakedQuantitySafely(0, 0, NaN)).toThrow();
        expect(() => calcTakedQuantitySafely('-10', 0, 0)).toThrow();
        expect(() => calcTakedQuantitySafely(0, '-10', 0)).toThrow();
        expect(() => calcTakedQuantitySafely(0, 0, '-10')).toThrow();
        expect(() => calcTakedQuantitySafely(10, 10, 10)).not.toThrow();
        expect(() => calcTakedQuantitySafely(100, 100, 10)).not.toThrow();

        expect(calcTakedQuantitySafely(0, 0, 100)).toBe(0);
        expect(calcTakedQuantitySafely(0, 10, 100)).toBe(10);
        expect(calcTakedQuantitySafely(0, 100, 10)).toBe(10);
        expect(calcTakedQuantitySafely(9, 0, 100)).toBe(9);
        expect(calcTakedQuantitySafely(9, 10, 100)).toBe(19);
        expect(calcTakedQuantitySafely(900, 10, 100)).toBe(10);
        expect(calcTakedQuantitySafely(90, 9, 100)).toBe(99);
        expect(calcTakedQuantitySafely(90, 10, 100)).toBe(100);
        expect(calcTakedQuantitySafely(100, 100, 100)).toBe(100);
        expect(calcTakedQuantitySafely('0', '0', '100')).toBe(0);
        expect(calcTakedQuantitySafely('0', '10', '100')).toBe(10);
        expect(calcTakedQuantitySafely('0', '100', '10')).toBe(10);
        expect(calcTakedQuantitySafely('9', '0', '100')).toBe(9);
        expect(calcTakedQuantitySafely('9', '10', '100')).toBe(19);
        expect(calcTakedQuantitySafely('900', '10', '100')).toBe(10);
        expect(calcTakedQuantitySafely('90', '9', '100')).toBe(99);
        expect(calcTakedQuantitySafely('90', '10', '100')).toBe(100);
        expect(calcTakedQuantitySafely('100', '100', '100')).toBe(100);
    });

    test('calcTakedQuantityWithLimit', () => {
        expect(() => calcTakedQuantityWithLimit(0, 0, 0)).not.toThrow();
        expect(() => calcTakedQuantityWithLimit(null, null, null)).toThrow();
        expect(() => calcTakedQuantityWithLimit(0, null, null)).toThrow();
        expect(() => calcTakedQuantityWithLimit(0, 0, null)).toThrow();
        expect(() => calcTakedQuantityWithLimit(undefined, undefined, undefined)).toThrow();
        expect(() => calcTakedQuantityWithLimit(undefined, undefined, 0)).toThrow();
        expect(() => calcTakedQuantityWithLimit(0, undefined, 0)).toThrow();
        expect(() => calcTakedQuantityWithLimit('', 0, 0)).toThrow();
        expect(() => calcTakedQuantityWithLimit(0, '', 0)).toThrow();
        expect(() => calcTakedQuantityWithLimit(0, 0, '')).toThrow();
        expect(() => calcTakedQuantityWithLimit(' ', 0, 0)).toThrow();
        expect(() => calcTakedQuantityWithLimit(0, ' ', 0)).toThrow();
        expect(() => calcTakedQuantityWithLimit(0, 0, ' ')).toThrow();
        expect(() => calcTakedQuantityWithLimit('test', 0, 0)).toThrow();
        expect(() => calcTakedQuantityWithLimit(0, 'test', 0)).toThrow();
        expect(() => calcTakedQuantityWithLimit(0, 0, 'test')).toThrow();
        expect(() => calcTakedQuantityWithLimit(-10, 0, 0)).toThrow();
        expect(() => calcTakedQuantityWithLimit(0, -10, 0)).toThrow();
        expect(() => calcTakedQuantityWithLimit(0, 0, -10)).toThrow();
        expect(() => calcTakedQuantityWithLimit(NaN, 0, 0)).toThrow();
        expect(() => calcTakedQuantityWithLimit(0, NaN, 0)).toThrow();
        expect(() => calcTakedQuantityWithLimit(0, 0, NaN)).toThrow();
        expect(() => calcTakedQuantityWithLimit('-10', 0, 0)).toThrow();
        expect(() => calcTakedQuantityWithLimit(0, '-10', 0)).toThrow();
        expect(() => calcTakedQuantityWithLimit(0, 0, '-10')).toThrow();
        expect(() => calcTakedQuantityWithLimit(10, 10, 10)).not.toThrow();
        expect(() => calcTakedQuantityWithLimit(100, 100, 10)).not.toThrow();

        expect(calcTakedQuantityWithLimit(0, 0, 100)).toBe(0);
        expect(calcTakedQuantityWithLimit(0, 10, 100)).toBe(10);
        expect(calcTakedQuantityWithLimit(0, 100, 10)).toBe(10);
        expect(calcTakedQuantityWithLimit(9, 0, 100)).toBe(9);
        expect(calcTakedQuantityWithLimit(9, 10, 100)).toBe(19);
        expect(calcTakedQuantityWithLimit(900, 10, 100)).toBe(100);
        expect(calcTakedQuantityWithLimit(90, 9, 100)).toBe(99);
        expect(calcTakedQuantityWithLimit(90, 10, 100)).toBe(100);
        expect(calcTakedQuantityWithLimit(100, 100, 100)).toBe(100);
        expect(calcTakedQuantityWithLimit('0', '0', '100')).toBe(0);
        expect(calcTakedQuantityWithLimit('0', '10', '100')).toBe(10);
        expect(calcTakedQuantityWithLimit('0', '100', '10')).toBe(10);
        expect(calcTakedQuantityWithLimit('9', '0', '100')).toBe(9);
        expect(calcTakedQuantityWithLimit('9', '10', '100')).toBe(19);
        expect(calcTakedQuantityWithLimit('900', '10', '100')).toBe(100);
        expect(calcTakedQuantityWithLimit('90', '9', '100')).toBe(99);
        expect(calcTakedQuantityWithLimit('90', '10', '100')).toBe(100);
        expect(calcTakedQuantityWithLimit('100', '100', '100')).toBe(100);
    });

    test('baseOnCountTakedQuantityStrategy', () => {
        expect(baseOnCountTakedQuantityStrategy(0, 0, 0)).toBe(0);
        expect(baseOnCountTakedQuantityStrategy(0, 0, 100)).toBe(0);
        expect(baseOnCountTakedQuantityStrategy(10, 0, 100)).toBe(10);
        expect(baseOnCountTakedQuantityStrategy(99, 0, 100)).toBe(99);
        expect(baseOnCountTakedQuantityStrategy(100, 0, 100)).toBe(100);
        expect(baseOnCountTakedQuantityStrategy(0, 50, 100)).toBe(0);
        expect(baseOnCountTakedQuantityStrategy(10, 50, 100)).toBe(10);
        expect(baseOnCountTakedQuantityStrategy(99, 50, 100)).toBe(50);
        expect(baseOnCountTakedQuantityStrategy(100, 50, 100)).toBe(50);
    });

    test('boundedCheckFormated', () => {
        expect(() => boundedCheckFormated(0, 0, 0)).not.toThrow();
        expect(() => boundedCheckFormated(0, 0, 100)).not.toThrow();
        expect(() => boundedCheckFormated(0, 10, 100)).not.toThrow();
        expect(() => boundedCheckFormated(0, 99, 100)).not.toThrow();
        expect(() => boundedCheckFormated(0, 1000, 100)).toThrow();
        expect(() => boundedCheckFormated(1000, 0, 0)).not.toThrow();
        expect(() => boundedCheckFormated(1000, 0, 100)).not.toThrow();
        expect(() => boundedCheckFormated(1000, 10, 100)).not.toThrow();
        expect(() => boundedCheckFormated(1000, 99, 100)).not.toThrow();
        expect(() => boundedCheckFormated(1000, 1000, 100)).toThrow();
    });

    test('calcTakedQuantityCounted', () => {
        expect(() => calcTakedQuantityCounted(0, 0, 0)).not.toThrow();
        expect(() => calcTakedQuantityCounted(null, null, null)).toThrow();
        expect(() => calcTakedQuantityCounted(0, null, null)).toThrow();
        expect(() => calcTakedQuantityCounted(0, 0, null)).toThrow();
        expect(() => calcTakedQuantityCounted(undefined, undefined, undefined)).toThrow();
        expect(() => calcTakedQuantityCounted(undefined, undefined, 0)).toThrow();
        expect(() => calcTakedQuantityCounted(0, undefined, 0)).toThrow();
        expect(() => calcTakedQuantityCounted('', 0, 0)).toThrow();
        expect(() => calcTakedQuantityCounted(0, '', 0)).toThrow();
        expect(() => calcTakedQuantityCounted(0, 0, '')).toThrow();
        expect(() => calcTakedQuantityCounted(' ', 0, 0)).toThrow();
        expect(() => calcTakedQuantityCounted(0, ' ', 0)).toThrow();
        expect(() => calcTakedQuantityCounted(0, 0, ' ')).toThrow();
        expect(() => calcTakedQuantityCounted('test', 0, 0)).toThrow();
        expect(() => calcTakedQuantityCounted(0, 'test', 0)).toThrow();
        expect(() => calcTakedQuantityCounted(0, 0, 'test')).toThrow();
        expect(() => calcTakedQuantityCounted(-10, 0, 0)).toThrow();
        expect(() => calcTakedQuantityCounted(0, -10, 0)).toThrow();
        expect(() => calcTakedQuantityCounted(0, 0, -10)).toThrow();
        expect(() => calcTakedQuantityCounted(NaN, 0, 0)).toThrow();
        expect(() => calcTakedQuantityCounted(0, NaN, 0)).toThrow();
        expect(() => calcTakedQuantityCounted(0, 0, NaN)).toThrow();
        expect(() => calcTakedQuantityCounted('-10', 0, 0)).toThrow();
        expect(() => calcTakedQuantityCounted(0, '-10', 0)).toThrow();
        expect(() => calcTakedQuantityCounted(0, 0, '-10')).toThrow();
        expect(() => calcTakedQuantityCounted(10, 10, 10)).not.toThrow();
        expect(() => calcTakedQuantityCounted(100, 100, 10)).toThrow();
        expect(() => calcTakedQuantityCounted(1000, 99, 100)).not.toThrow();

        expect(calcTakedQuantityCounted(0, 0, 0)).toBe(0);
        expect(calcTakedQuantityCounted(0, 0, 100)).toBe(0);
        expect(calcTakedQuantityCounted(10, 0, 100)).toBe(10);
        expect(calcTakedQuantityCounted(99, 0, 100)).toBe(99);
        expect(calcTakedQuantityCounted(100, 0, 100)).toBe(100);
        expect(calcTakedQuantityCounted(0, 50, 100)).toBe(0);
        expect(calcTakedQuantityCounted(10, 50, 100)).toBe(10);
        expect(calcTakedQuantityCounted(99, 50, 100)).toBe(50);
        expect(calcTakedQuantityCounted(100, 50, 100)).toBe(50);
        expect(calcTakedQuantityCounted('0', '0', '0')).toBe(0);
        expect(calcTakedQuantityCounted('0', '0', '100')).toBe(0);
        expect(calcTakedQuantityCounted('10', '0', '100')).toBe(10);
        expect(calcTakedQuantityCounted('99', '0', '100')).toBe(99);
        expect(calcTakedQuantityCounted('100', '0', '100')).toBe(100);
        expect(calcTakedQuantityCounted('0', '50', '100')).toBe(0);
        expect(calcTakedQuantityCounted('10', '50', '100')).toBe(10);
        expect(calcTakedQuantityCounted('99', '50', '100')).toBe(50);
        expect(calcTakedQuantityCounted('100', '50', '100')).toBe(50);
    });

    test('removeTakedQuantityStrategy', () => {
        expect(removeTakedQuantityStrategy(0, 0, 0)).toBe(0);
        expect(removeTakedQuantityStrategy(0, 0, 100)).toBe(100);
        expect(removeTakedQuantityStrategy(10, 0, 100)).toBe(90);
        expect(removeTakedQuantityStrategy(99, 0, 100)).toBe(1);
        expect(removeTakedQuantityStrategy(100, 0, 100)).toBe(0);
        expect(removeTakedQuantityStrategy(0, 50, 100)).toBe(100);
        expect(removeTakedQuantityStrategy(10, 50, 100)).toBe(90);
        expect(removeTakedQuantityStrategy(99, 50, 100)).toBe(100);
        expect(removeTakedQuantityStrategy(100, 50, 100)).toBe(100);
    });

    test('moveToMinRemoveTakedQuantityStrategy', () => {
        expect(moveToMinRemoveTakedQuantityStrategy(0, 0, 0)).toBe(0);
        expect(moveToMinRemoveTakedQuantityStrategy(0, 0, 100)).toBe(100);
        expect(moveToMinRemoveTakedQuantityStrategy(10, 0, 100)).toBe(90);
        expect(moveToMinRemoveTakedQuantityStrategy(99, 0, 100)).toBe(1);
        expect(moveToMinRemoveTakedQuantityStrategy(100, 0, 100)).toBe(0);
        expect(moveToMinRemoveTakedQuantityStrategy(0, 50, 100)).toBe(100);
        expect(moveToMinRemoveTakedQuantityStrategy(10, 50, 100)).toBe(90);
        expect(moveToMinRemoveTakedQuantityStrategy(99, 50, 100)).toBe(50);
        expect(moveToMinRemoveTakedQuantityStrategy(100, 50, 100)).toBe(50);
    });

    test('calcTakedQuantityToMinRemove', () => {
        expect(() => calcTakedQuantityToMinRemove(0, 0, 0)).not.toThrow();
        expect(() => calcTakedQuantityToMinRemove(null, null, null)).toThrow();
        expect(() => calcTakedQuantityToMinRemove(0, null, null)).toThrow();
        expect(() => calcTakedQuantityToMinRemove(0, 0, null)).toThrow();
        expect(() => calcTakedQuantityToMinRemove(undefined, undefined, undefined)).toThrow();
        expect(() => calcTakedQuantityToMinRemove(undefined, undefined, 0)).toThrow();
        expect(() => calcTakedQuantityToMinRemove(0, undefined, 0)).toThrow();
        expect(() => calcTakedQuantityToMinRemove('', 0, 0)).toThrow();
        expect(() => calcTakedQuantityToMinRemove(0, '', 0)).toThrow();
        expect(() => calcTakedQuantityToMinRemove(0, 0, '')).toThrow();
        expect(() => calcTakedQuantityToMinRemove(' ', 0, 0)).toThrow();
        expect(() => calcTakedQuantityToMinRemove(0, ' ', 0)).toThrow();
        expect(() => calcTakedQuantityToMinRemove(0, 0, ' ')).toThrow();
        expect(() => calcTakedQuantityToMinRemove('test', 0, 0)).toThrow();
        expect(() => calcTakedQuantityToMinRemove(0, 'test', 0)).toThrow();
        expect(() => calcTakedQuantityToMinRemove(0, 0, 'test')).toThrow();
        expect(() => calcTakedQuantityToMinRemove(-10, 0, 0)).toThrow();
        expect(() => calcTakedQuantityToMinRemove(0, -10, 0)).toThrow();
        expect(() => calcTakedQuantityToMinRemove(0, 0, -10)).toThrow();
        expect(() => calcTakedQuantityToMinRemove(NaN, 0, 0)).toThrow();
        expect(() => calcTakedQuantityToMinRemove(0, NaN, 0)).toThrow();
        expect(() => calcTakedQuantityToMinRemove(0, 0, NaN)).toThrow();
        expect(() => calcTakedQuantityToMinRemove('-10', 0, 0)).toThrow();
        expect(() => calcTakedQuantityToMinRemove(0, '-10', 0)).toThrow();
        expect(() => calcTakedQuantityToMinRemove(0, 0, '-10')).toThrow();
        expect(() => calcTakedQuantityToMinRemove(10, 10, 10)).not.toThrow();
        expect(() => calcTakedQuantityToMinRemove(100, 100, 10)).toThrow();
        expect(() => calcTakedQuantityToMinRemove(1000, 99, 100)).not.toThrow();

        expect(calcTakedQuantityToMinRemove(0, 0, 0)).toBe(0);
        expect(calcTakedQuantityToMinRemove(0, 0, 100)).toBe(100);
        expect(calcTakedQuantityToMinRemove(10, 0, 100)).toBe(90);
        expect(calcTakedQuantityToMinRemove(99, 0, 100)).toBe(1);
        expect(calcTakedQuantityToMinRemove(100, 0, 100)).toBe(0);
        expect(calcTakedQuantityToMinRemove(0, 50, 100)).toBe(100);
        expect(calcTakedQuantityToMinRemove(10, 50, 100)).toBe(90);
        expect(calcTakedQuantityToMinRemove(99, 50, 100)).toBe(50);
        expect(calcTakedQuantityToMinRemove(100, 50, 100)).toBe(50);
        expect(calcTakedQuantityToMinRemove('0', '0', '0')).toBe(0);
        expect(calcTakedQuantityToMinRemove('0', '0', '100')).toBe(100);
        expect(calcTakedQuantityToMinRemove('10', '0', '100')).toBe(90);
        expect(calcTakedQuantityToMinRemove('99', '0', '100')).toBe(1);
        expect(calcTakedQuantityToMinRemove('100', '0', '100')).toBe(0);
        expect(calcTakedQuantityToMinRemove('0', '50', '100')).toBe(100);
        expect(calcTakedQuantityToMinRemove('10', '50', '100')).toBe(90);
        expect(calcTakedQuantityToMinRemove('99', '50', '100')).toBe(50);
        expect(calcTakedQuantityToMinRemove('100', '50', '100')).toBe(50);
    });

    test('calcSumCountQuantity', () => {
        expect(() => calcSumCountQuantity(0, 0, 0)).not.toThrow();
        expect(() => calcSumCountQuantity(null, null, null)).toThrow();
        expect(() => calcSumCountQuantity(0, null, null)).toThrow();
        expect(() => calcSumCountQuantity(0, 0, null)).toThrow();
        expect(() => calcSumCountQuantity(undefined, undefined, undefined)).toThrow();
        expect(() => calcSumCountQuantity(undefined, undefined, 0)).toThrow();
        expect(() => calcSumCountQuantity(0, undefined, 0)).not.toThrow();
        expect(() => calcSumCountQuantity('', 0, 0)).toThrow();
        expect(() => calcSumCountQuantity(0, '', 0)).not.toThrow();
        expect(() => calcSumCountQuantity(0, 0, '')).toThrow();
        expect(() => calcSumCountQuantity(' ', 0, 0)).toThrow();
        expect(() => calcSumCountQuantity(0, ' ', 0)).not.toThrow();
        expect(() => calcSumCountQuantity(0, 0, ' ')).toThrow();
        expect(() => calcSumCountQuantity('test', 0, 0)).toThrow();
        expect(() => calcSumCountQuantity(0, 'test', 0)).not.toThrow();
        expect(() => calcSumCountQuantity(0, 0, 'test')).toThrow();
        expect(() => calcSumCountQuantity(-10, 0, 0)).toThrow();
        expect(() => calcSumCountQuantity(0, -10, 0)).not.toThrow();
        expect(() => calcSumCountQuantity(0, 0, -10)).toThrow();
        expect(() => calcSumCountQuantity(NaN, 0, 0)).toThrow();
        expect(() => calcSumCountQuantity(0, NaN, 0)).not.toThrow();
        expect(() => calcSumCountQuantity(0, 0, NaN)).toThrow();
        expect(() => calcSumCountQuantity('-10', 0, 0)).toThrow();
        expect(() => calcSumCountQuantity(0, '-10', 0)).not.toThrow();
        expect(() => calcSumCountQuantity(0, 0, '-10')).toThrow();
        expect(() => calcSumCountQuantity(10, 10, 10)).not.toThrow();
        expect(() => calcSumCountQuantity(100, 100, 10)).not.toThrow();
        expect(() => calcSumCountQuantity(1000, 99, 100)).not.toThrow();

        expect(calcSumCountQuantity(0, 0, 0)).toBe(0);
        expect(calcSumCountQuantity(0, 0, 100)).toBe(100);
        expect(calcSumCountQuantity(10, 0, 100)).toBe(110);
        expect(calcSumCountQuantity(99, 0, 100)).toBe(199);
        expect(calcSumCountQuantity(100, 0, 100)).toBe(200);
        expect(calcSumCountQuantity(0, 50, 100)).toBe(100);
        expect(calcSumCountQuantity(10, 50, 100)).toBe(110);
        expect(calcSumCountQuantity(99, 50, 100)).toBe(199);
        expect(calcSumCountQuantity(100, 50, 100)).toBe(200);
        expect(calcSumCountQuantity('0', '0', '0')).toBe(0);
        expect(calcSumCountQuantity('0', '0', '100')).toBe(100);
        expect(calcSumCountQuantity('10', '0', '100')).toBe(110);
        expect(calcSumCountQuantity('99', '0', '100')).toBe(199);
        expect(calcSumCountQuantity('100', '0', '100')).toBe(200);
        expect(calcSumCountQuantity('0', '50', '100')).toBe(100);
        expect(calcSumCountQuantity('10', '50', '100')).toBe(110);
        expect(calcSumCountQuantity('99', '50', '100')).toBe(199);
        expect(calcSumCountQuantity('100', '50', '100')).toBe(200);
    });
});

describe('refundQuantity', () => {
    test('absoluteRefundQuantityStrategy', () => {
        expect(absoluteRefundQuantityStrategy(null)).toBe(0);
        expect(absoluteRefundQuantityStrategy(undefined)).toBe(0);
        expect(absoluteRefundQuantityStrategy(NaN)).toBe(0);
        expect(absoluteRefundQuantityStrategy('')).toBe(0);
        expect(absoluteRefundQuantityStrategy(' ')).toBe(0);
        expect(absoluteRefundQuantityStrategy('test')).toBe(0);
        expect(absoluteRefundQuantityStrategy('0 test')).toBe(0);
        expect(absoluteRefundQuantityStrategy('-10 test')).toBe(0);
        expect(absoluteRefundQuantityStrategy('-10')).toBe(0);
        expect(absoluteRefundQuantityStrategy('-0.99')).toBe(0);
        expect(absoluteRefundQuantityStrategy('0.99')).toBe(0.99);
        expect(absoluteRefundQuantityStrategy('0')).toBe(0);
        expect(absoluteRefundQuantityStrategy('10')).toBe(10);
        expect(absoluteRefundQuantityStrategy(-10)).toBe(0);
        expect(absoluteRefundQuantityStrategy(0.99)).toBe(0.99);
        expect(absoluteRefundQuantityStrategy(10)).toBe(10);
    });

    test('availableRefundQuantityStrategy', () => {
        expect(availableRefundQuantityStrategy(0, 0)).toBe(0);
        expect(availableRefundQuantityStrategy(null, null)).toBe(0);
        expect(availableRefundQuantityStrategy(0, null)).toBe(0);
        expect(availableRefundQuantityStrategy(null, 0)).toBe(0);
        expect(availableRefundQuantityStrategy(undefined, undefined)).toBe(0);
        expect(availableRefundQuantityStrategy(0, undefined)).toBe(0);
        expect(availableRefundQuantityStrategy(undefined, 0)).toBe(0);
        expect(availableRefundQuantityStrategy(NaN, NaN)).toBe(0);
        expect(availableRefundQuantityStrategy(0, NaN)).toBe(0);
        expect(availableRefundQuantityStrategy(NaN, 0)).toBe(0);
        expect(availableRefundQuantityStrategy('', '')).toBe(0);
        expect(availableRefundQuantityStrategy(0, '')).toBe(0);
        expect(availableRefundQuantityStrategy('', 0)).toBe(0);
        expect(availableRefundQuantityStrategy(' ', ' ')).toBe(0);
        expect(availableRefundQuantityStrategy(0, ' ')).toBe(0);
        expect(availableRefundQuantityStrategy(' ', 0)).toBe(0);
        expect(availableRefundQuantityStrategy('test', 'test')).toBe(0);
        expect(availableRefundQuantityStrategy(0, 'test')).toBe(0);
        expect(availableRefundQuantityStrategy('test', 0)).toBe(0);
        expect(availableRefundQuantityStrategy('0 test', '0 test')).toBe(0);
        expect(availableRefundQuantityStrategy(0, '0 test')).toBe(0);
        expect(availableRefundQuantityStrategy('0 test', 0)).toBe(0);
        expect(availableRefundQuantityStrategy('-10 test', '-10 test')).toBe(0);
        expect(availableRefundQuantityStrategy(0, '-10 test')).toBe(0);
        expect(availableRefundQuantityStrategy('-10 test', 0)).toBe(0);
        expect(availableRefundQuantityStrategy('-10', '-10')).toBe(0);
        expect(availableRefundQuantityStrategy(0, '-10')).toBe(0);
        expect(availableRefundQuantityStrategy('-10', 0)).toBe(0);
        expect(availableRefundQuantityStrategy('-0.99', '-0.99')).toBe(0);
        expect(availableRefundQuantityStrategy(0, '-0.99')).toBe(0);
        expect(availableRefundQuantityStrategy('-0.99', 0)).toBe(0);
        expect(availableRefundQuantityStrategy('0', '0')).toBe(0);
        expect(availableRefundQuantityStrategy(0, '0')).toBe(0);
        expect(availableRefundQuantityStrategy('0', 0)).toBe(0);
        expect(availableRefundQuantityStrategy('10', '10')).toBe(0);
        expect(availableRefundQuantityStrategy(0, '10')).toBe(10);
        expect(availableRefundQuantityStrategy('10', 0)).toBe(0);
        expect(availableRefundQuantityStrategy(0, 10)).toBe(10);
        expect(availableRefundQuantityStrategy(10, 10)).toBe(0);
        expect(availableRefundQuantityStrategy(100, 10)).toBe(0);
        expect(availableRefundQuantityStrategy(100, 100)).toBe(0);
        expect(availableRefundQuantityStrategy(99, 100)).toBe(1);
    });
});
