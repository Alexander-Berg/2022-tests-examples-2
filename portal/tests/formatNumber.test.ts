import { formatNumber } from '../formatNumber';

describe('formatNumber', function() {
    test('should format', function() {
        expect(formatNumber(1)).toEqual('1');
        expect(formatNumber(1.23)).toEqual('1,23');
        expect(formatNumber(1.23456789)).toEqual('1,23456789');
        expect(formatNumber(1000)).toEqual('1&nbsp;000');
        expect(formatNumber(10000)).toEqual('10&nbsp;000');
        expect(formatNumber(123456)).toEqual('123&nbsp;456');
        expect(formatNumber(1234567)).toEqual('1&nbsp;234&nbsp;567');
        expect(formatNumber(12345678)).toEqual('12&nbsp;345&nbsp;678');
        expect(formatNumber(12345678.12345678)).toEqual('12&nbsp;345&nbsp;678,12345678');
    });

    test('should format with delimiter', function() {
        expect(formatNumber(18, ':')).toEqual('18');
        expect(formatNumber(18.30, ':')).toEqual('18:3');
    });

    test('should format with thousands delimiter', function() {
        expect(formatNumber(123456, undefined, '_')).toEqual('123_456');
    });
});
