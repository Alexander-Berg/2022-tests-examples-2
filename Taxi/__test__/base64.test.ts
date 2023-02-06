import {decode, encode} from '_pkg/utils/base64';

describe('utils/base64', () => {
    describe('encode', () => {
        test('корректно кодирует строки', () => {
            const encoded = encode('foo');
            expect(encoded).toBe('Zm9v');
        });

        test('корректно кодирует числа', () => {
            const encoded = encode(1);
            expect(encoded).toBe('MQ==');
        });

        test('корректно кодирует unicode строки', () => {
            const encoded = encode('строка');
            expect(encoded).toBe('0YHRgtGA0L7QutCw');
        });
    });

    describe('decode', () => {
        test('корректно декодирует строки', () => {
            const encoded = decode('Zm9v');
            expect(encoded).toBe('foo');
        });

        test('корректно декодирует unicode строки', () => {
            const encoded = decode('0YHRgtGA0L7QutCw');
            expect(encoded).toBe('строка');
        });

        test('корректно декодирует не b64 строки', () => {
            const encoded = decode('foo');
            expect(encoded).toBeUndefined();
        });
    });
});
