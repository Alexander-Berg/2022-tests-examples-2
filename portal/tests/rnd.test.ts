import { randomInteger, rnd } from '../rnd';

describe('rnd', () => {
    describe('rnd', function() {
        let orig: typeof Math.random;

        beforeEach(function() {
            orig = Math.random;

            let i = 0;
            let arr = [
                0.1,
                0.123456789,
                0.23456789,
                0.3456789
            ];

            Math.random = function() {
                let res = arr[i++];
                i = i % arr.length;
                return res;
            };
        });

        afterEach(function() {
            Math.random = orig;
        });

        test('should return rnd id', function() {
            expect(rnd()).toEqual('1');
            expect(rnd()).toEqual('123456789');
            expect(rnd()).toEqual('23456789');
            expect(rnd()).toEqual('3456789');
            expect(rnd()).toEqual('1');
        });
    });

    describe('randomInteger', function() {
        let orig: typeof Math.random;

        beforeEach(function() {
            orig = Math.random;

            let i = 0;
            let arr = [
                0.1,
                0.123456789,
                0.23456789,
                0.3456789,
                0,
                0.9999999999999
            ];

            Math.random = function() {
                let res = arr[i++];
                i = i % arr.length;
                return res;
            };
        });

        afterEach(function() {
            Math.random = orig;
        });

        test('should return random int', function() {
            expect(randomInteger(0, 1)).toEqual(0);
            expect(randomInteger(0, 2)).toEqual(0);
            expect(randomInteger(0, 10)).toEqual(2);
            expect(randomInteger(0, 10)).toEqual(3);
            expect(randomInteger(0, 100)).toEqual(0);
            expect(randomInteger(0, 100)).toEqual(100);
        });
    });
});
