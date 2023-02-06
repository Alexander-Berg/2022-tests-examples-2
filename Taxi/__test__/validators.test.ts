import moment from 'moment';

import {
    buildInRangeValidator,
    consistsOfASCIIOnly,
    isEmpty,
    isInteger,
    isNotEmpty,
    isNotNegativeInteger,
    isNotNegativeNumber,
    isNotNullable,
    isNullable,
    isNumber,
    isObject,
    isPositiveInt,
    isTime
} from '../validators';

function testEmptyFunction() {
    return 1;
}

describe('utils/strict/validators', function () {
    test('isNumber', () => {
        expect(isNumber(1)).toBeTruthy();
        expect(isNumber(0.1)).toBeTruthy();
        expect(isNumber(0)).toBeTruthy();
        expect(isNumber(-1)).toBeTruthy();
        expect(isNumber('1')).toBeTruthy();
        expect(isNumber('0.1')).toBeTruthy();
        expect(isNumber('0')).toBeTruthy();
        expect(isNumber('-1')).toBeTruthy();

        expect(isNumber('')).toBeFalsy();
        expect(isNumber('a')).toBeFalsy();
        expect(isNumber(null)).toBeFalsy();
        expect(isNumber(undefined)).toBeFalsy();
    });

    test('isNotNegativeNumber', () => {
        expect(isNotNegativeNumber(1)).toBeTruthy();
        expect(isNotNegativeNumber(0.1)).toBeTruthy();
        expect(isNotNegativeNumber(0)).toBeTruthy();
        expect(isNotNegativeNumber('1')).toBeTruthy();
        expect(isNotNegativeNumber('0.1')).toBeTruthy();
        expect(isNotNegativeNumber('0')).toBeTruthy();

        expect(isNotNegativeNumber('')).toBeFalsy();
        expect(isNotNegativeNumber('-1')).toBeFalsy();
        expect(isNotNegativeNumber(-1)).toBeFalsy();
        expect(isNotNegativeNumber('a')).toBeFalsy();
        expect(isNotNegativeNumber(null)).toBeFalsy();
        expect(isNotNegativeNumber(undefined)).toBeFalsy();
    });

    test('isInteger', () => {
        expect(isInteger(1)).toBeTruthy();
        expect(isInteger(0)).toBeTruthy();
        expect(isInteger(-1)).toBeTruthy();
        expect(isInteger('1')).toBeTruthy();
        expect(isInteger('0')).toBeTruthy();
        expect(isInteger('-1')).toBeTruthy();

        expect(isInteger('')).toBeFalsy();
        expect(isInteger(0.1)).toBeFalsy();
        expect(isInteger('0.1')).toBeFalsy();
        expect(isInteger('a')).toBeFalsy();
        expect(isInteger(null)).toBeFalsy();
        expect(isInteger(undefined)).toBeFalsy();
    });

    test('isNotNegativeInteger', () => {
        expect(isNotNegativeInteger(1)).toBeTruthy();
        expect(isNotNegativeInteger(0)).toBeTruthy();
        expect(isNotNegativeInteger('1')).toBeTruthy();
        expect(isNotNegativeInteger('0')).toBeTruthy();

        expect(isNotNegativeInteger('')).toBeFalsy();
        expect(isNotNegativeInteger('-1')).toBeFalsy();
        expect(isNotNegativeInteger(-1)).toBeFalsy();
        expect(isNotNegativeInteger(0.1)).toBeFalsy();
        expect(isNotNegativeInteger('0.1')).toBeFalsy();
        expect(isNotNegativeInteger('a')).toBeFalsy();
        expect(isNotNegativeInteger(null)).toBeFalsy();
        expect(isNotNegativeInteger(undefined)).toBeFalsy();
    });

    test('isPositiveInt', () => {
        expect(isPositiveInt(1)).toBeTruthy();
        expect(isPositiveInt('1')).toBeTruthy();

        expect(isPositiveInt('')).toBeFalsy();
        expect(isPositiveInt(0)).toBeFalsy();
        expect(isPositiveInt('0')).toBeFalsy();
        expect(isPositiveInt('-1')).toBeFalsy();
        expect(isPositiveInt(-1)).toBeFalsy();
        expect(isPositiveInt(0.1)).toBeFalsy();
        expect(isPositiveInt('0.1')).toBeFalsy();
        expect(isPositiveInt('a')).toBeFalsy();
        expect(isPositiveInt(null)).toBeFalsy();
        expect(isPositiveInt(undefined)).toBeFalsy();
    });

    test('isNullable', () => {
        expect(isNullable(null)).toBeTruthy();
        expect(isNullable(undefined)).toBeTruthy();

        expect(isNullable(1)).toBeFalsy();
        expect(isNullable(0)).toBeFalsy();
        expect(isNullable('1')).toBeFalsy();
        expect(isNullable('a')).toBeFalsy();
        expect(isNullable({})).toBeFalsy();
        expect(isNullable([])).toBeFalsy();
        expect(isNullable(testEmptyFunction)).toBeFalsy();
    });

    test('isNotNullable', () => {
        expect(isNotNullable(1)).toBeTruthy();
        expect(isNotNullable(0)).toBeTruthy();
        expect(isNotNullable('1')).toBeTruthy();
        expect(isNotNullable('0')).toBeTruthy();
        expect(isNotNullable('a')).toBeTruthy();
        expect(isNotNullable({})).toBeTruthy();
        expect(isNotNullable([])).toBeTruthy();
        expect(isNotNullable(testEmptyFunction)).toBeTruthy();
        expect(isNotNullable(true)).toBeTruthy();
        expect(isNotNullable(false)).toBeTruthy();

        expect(isNotNullable(null)).toBeFalsy();
        expect(isNotNullable(undefined)).toBeFalsy();
    });

    test('isObject', () => {
        expect(isObject({})).toBeTruthy();
        expect(isObject({foo: 'bar'})).toBeTruthy();

        expect(isObject(testEmptyFunction)).toBeFalsy();
        expect(isObject(null)).toBeFalsy();
        expect(isObject(undefined)).toBeFalsy();
        expect(isObject(NaN)).toBeFalsy();
        expect(isObject(0)).toBeFalsy();
        expect(isObject(1)).toBeFalsy();
        expect(isObject('a')).toBeFalsy();
        expect(isObject([])).toBeFalsy();
    });

    test('isNotEmpty', () => {
        expect(isNotEmpty('f')).toBeTruthy();
        expect(isNotEmpty({foo: 'bar'})).toBeTruthy();
        expect(isNotEmpty(['foo'])).toBeTruthy();
        expect(isNotEmpty(1)).toBeTruthy();
        expect(isNotEmpty(0)).toBeTruthy();
        expect(isNotEmpty(true)).toBeTruthy();
        expect(isNotEmpty(false)).toBeTruthy();
        expect(isNotEmpty(testEmptyFunction)).toBeTruthy();
        expect(isNotEmpty('0')).toBeTruthy();

        expect(isNotEmpty({})).toBeFalsy();
        expect(isNotEmpty([])).toBeFalsy();
        expect(isNotEmpty('')).toBeFalsy();
        expect(isNotEmpty(null)).toBeFalsy();
        expect(isNotEmpty(undefined)).toBeFalsy();
        expect(isNotEmpty(NaN)).toBeFalsy();
    });

    test('isEmpty', () => {
        expect(isEmpty({})).toBeTruthy();
        expect(isEmpty([])).toBeTruthy();
        expect(isEmpty('')).toBeTruthy();
        expect(isEmpty(null)).toBeTruthy();
        expect(isEmpty(undefined)).toBeTruthy();
        expect(isEmpty(NaN)).toBeTruthy();

        expect(isEmpty('f')).toBeFalsy();
        expect(isEmpty({foo: 'bar'})).toBeFalsy();
        expect(isEmpty(['foo'])).toBeFalsy();
        expect(isEmpty(1)).toBeFalsy();
        expect(isEmpty(0)).toBeFalsy();
        expect(isEmpty(true)).toBeFalsy();
        expect(isEmpty(false)).toBeFalsy();
        expect(isEmpty(testEmptyFunction)).toBeFalsy();
        expect(isEmpty('0')).toBeFalsy();
    });

    test('isTime', () => {
        expect(isTime(undefined)).toBeFalsy();
        expect(isTime(null)).toBeFalsy();
        expect(isTime('')).toBeFalsy();
        expect(isTime('23:59:60')).toBeFalsy();
        expect(isTime('23:60')).toBeFalsy();
        expect(isTime('23:60:59')).toBeFalsy();
        expect(isTime('24:59:59')).toBeFalsy();
        expect(isTime('23')).toBeFalsy();
        expect(isTime('23:5')).toBeFalsy();
        expect(isTime(moment().format())).toBeFalsy();

        expect(isTime('00:00')).toBeTruthy();
        expect(isTime('00:00:00')).toBeTruthy();
        expect(isTime('23:59')).toBeTruthy();
        expect(isTime('23:59:59')).toBeTruthy();
        expect(isTime(moment().format('hh:MM'))).toBeTruthy();
        expect(isTime(moment().format('hh:MM:ss'))).toBeTruthy();
    });

    test('buildInRangeValidator', () => {
        const isInInterval = buildInRangeValidator(0, 1, 'interval');
        expect(isInInterval(0.5)).toBeTruthy();
        expect(isInInterval('0.5')).toBeTruthy();
        expect(isInInterval(0)).toBeFalsy();
        expect(isInInterval(1)).toBeFalsy();
        expect(isInInterval(undefined)).toBeFalsy();
        expect(isInInterval(null)).toBeFalsy();

        const isInHalfIntervalLeft = buildInRangeValidator(0, 1, 'half_interval_left');
        expect(isInHalfIntervalLeft(0.5)).toBeTruthy();
        expect(isInHalfIntervalLeft('0.5')).toBeTruthy();
        expect(isInHalfIntervalLeft(0)).toBeTruthy();
        expect(isInHalfIntervalLeft(1)).toBeFalsy();
        expect(isInHalfIntervalLeft(undefined)).toBeFalsy();
        expect(isInHalfIntervalLeft(null)).toBeFalsy();

        const isInHalfIntervalRight = buildInRangeValidator(0, 1, 'half_interval_right');
        expect(isInHalfIntervalRight(0.5)).toBeTruthy();
        expect(isInHalfIntervalRight('0.5')).toBeTruthy();
        expect(isInHalfIntervalRight(0)).toBeFalsy();
        expect(isInHalfIntervalRight(1)).toBeTruthy();
        expect(isInHalfIntervalRight(undefined)).toBeFalsy();
        expect(isInHalfIntervalRight(null)).toBeFalsy();

        const isInSegment = buildInRangeValidator(0, 1, 'segment');
        expect(isInSegment(0.5)).toBeTruthy();
        expect(isInSegment('0.5')).toBeTruthy();
        expect(isInSegment(0)).toBeTruthy();
        expect(isInSegment(1)).toBeTruthy();
        expect(isInSegment(1.0001)).toBeFalsy();
        expect(isInSegment(-0.0001)).toBeFalsy();
        expect(isInSegment(undefined)).toBeFalsy();
        expect(isInSegment(null)).toBeFalsy();
    });

    test('consistsOfASCIIOnly', () => {
        expect(consistsOfASCIIOnly('п')).toBeFalsy();
        expect(consistsOfASCIIOnly('Привет, сосед')).toBeFalsy();
        expect(consistsOfASCIIOnly(null)).toBeFalsy();
        expect(consistsOfASCIIOnly(undefined)).toBeFalsy();

        expect(consistsOfASCIIOnly('asdfg')).toBeTruthy();
        expect(consistsOfASCIIOnly('123565')).toBeTruthy();
        expect(consistsOfASCIIOnly('0-9test')).toBeTruthy();
        expect(consistsOfASCIIOnly('!hello!')).toBeTruthy();
        expect(consistsOfASCIIOnly('\x00')).toBeTruthy();
        expect(consistsOfASCIIOnly('\xFF')).toBeTruthy();
        expect(consistsOfASCIIOnly('\xFF\xFF')).toBeTruthy();
        expect(consistsOfASCIIOnly(';,.:\'\"?!')).toBeTruthy();
        expect(consistsOfASCIIOnly('')).toBeTruthy();
    });
});
