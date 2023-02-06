import {normalizeFloat, toFloat} from '../toFloat';

describe('toFloat', () => {
    it('Возвращает undefined для данных, которые нельзя интерпретировать как число', () => {
        expect(toFloat(undefined)).toBeUndefined();
        expect(toFloat('')).toBeUndefined();
        expect(toFloat(undefined, -5)).toBeUndefined();
        expect(toFloat('', 3)).toBeUndefined();
        expect(toFloat(undefined, 2)).toBeUndefined();
    });

    it('Возвращает float число с указанным количеством чисел после точки, отбрасывая лишние нули', () => {
        expect(toFloat(0)).toBe('0');
        expect(toFloat('0')).toBe('0');
        expect(toFloat(0, -1)).toBe('0');
        expect(toFloat(0, 1)).toBe('0');
        expect(toFloat('0', 4)).toBe('0');

        expect(toFloat('1.234', 0)).toBe('1');
        expect(toFloat('1.234')).toBe('1.234');
        expect(toFloat('1.234', 1)).toBe('1.2');
        expect(toFloat('1.237', 2)).toBe('1.24');
        expect(toFloat('1.237', 4)).toBe('1.237');
        expect(toFloat('1.237000', 4)).toBe('1.237');
        expect(toFloat(56, 2)).toBe('56');
        expect(toFloat('56', 3)).toBe('56');
    });
});

describe('normalizeFloat', () => {
    it('Всегда возвращает строку с указанным количеством чисел после точки дополняя их нулями', () => {
        expect(normalizeFloat(0)).toBe('0');
        expect(normalizeFloat(undefined)).toBe('0');
        expect(normalizeFloat('')).toBe('0');
        expect(normalizeFloat('0')).toBe('0');
        expect(normalizeFloat(0, -1)).toBe('0');
        expect(normalizeFloat(undefined, -5)).toBe('0');

        expect(normalizeFloat(0, 1)).toBe('0.0');
        expect(normalizeFloat('', 3)).toBe('0.000');
        expect(normalizeFloat(undefined, 2)).toBe('0.00');
        expect(normalizeFloat('0', 4)).toBe('0.0000');

        expect(normalizeFloat('1.234', 0)).toBe('1');
        expect(normalizeFloat('1.234', 1)).toBe('1.2');
        expect(normalizeFloat('1.237', 2)).toBe('1.24');
        expect(normalizeFloat('1.237', 4)).toBe('1.2370');
        expect(normalizeFloat(56, 2)).toBe('56.00');
        expect(normalizeFloat('56', 3)).toBe('56.000');
    });
});
