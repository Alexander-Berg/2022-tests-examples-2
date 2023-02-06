/**
 * @jest-environment node
 */
import {isAfter, isNotUnstable, normalizeVersion, parse} from './version';

describe('Version', () => {
    describe('parse', () => {
        test('0.1.1234', () => expect(parse('0.1.1234')).toEqual([0, 1, 1234, 0]));
        test('0.1.1234.1', () => expect(parse('0.1.1234.1')).toEqual([0, 1, 1234, 1]));
        test('0.1.1234-12345', () => expect(parse('0.1.1234-12345')).toEqual([0, 1, 1234, 0]));
    });

    describe('normalizeVersion', () => {
        test('0.1.1234-12345', () => expect(normalizeVersion('0.1.1234-12345')).toBe('0.1.1234.0'));
        test('0.1.1234', () => expect(normalizeVersion('0.1.1234')).toBe('0.1.1234.0'));
        test('0.1.1234.1', () => expect(normalizeVersion('0.1.1234.1')).toBe('0.1.1234.1'));
    });

    describe('isAfter', () => {
        test('null < 0.100', () => expect(isAfter(null, '0.100')).toBe(false));
        test('0.100 > null', () => expect(isAfter('0.100', null)).toBe(true));
        test('0.200 > 0.100', () => expect(isAfter('0.200', '0.100')).toBe(true));
        test('1.3 > 0.100', () => expect(isAfter('1.3', '0.100')).toBe(true));
        test('1.100 > 0.200', () => expect(isAfter('0.200', '1.100')).toBe(false));
        test('0.200 < 1.100', () => expect(isAfter('1.100', '0.200')).toBe(true));
        test('1.3.5 > 1.3.4-100', () => expect(isAfter('1.3.5', '1.3.4-100')).toBe(true));
        test('1.3.4-200 = 1.3.4-100', () => expect(isAfter('1.3.4-200', '1.3.4-100')).toBe(false));
    });

    describe('isNotUnstable', () => {
        test('0.1.1234', () => expect(isNotUnstable('0.1.1234')).toBe(true));
        test('0.1.1234.1', () => expect(isNotUnstable('0.1.1234.1')).toBe(true));
        test('0.1.1234-12345', () => expect(isNotUnstable('0.1.1234-12345')).toBe(false));
    });
});
