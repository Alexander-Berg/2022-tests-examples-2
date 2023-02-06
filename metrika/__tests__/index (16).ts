import { formatInteger, formatFloat } from '../utils';

describe('formatInteger', () => {
    it('should leave provided string untouched if it contains only numeric symbols', () => {
        const integer = formatInteger('123');
        expect(integer).toBe('123');
    });

    it('should remove all non numeric symbols from provided string', () => {
        const integer = formatInteger('123abc456*;.,789');
        expect(integer).toBe('123456789');
    });

    it("should leave empty string if provided string doesn't contain any numeric symbol", () => {
        const integer = formatInteger('*;.,');
        expect(integer).toBe('');
    });
});

describe('formatFloat', () => {
    it('should leave provided string untouched if it contains only numeric symbols', () => {
        const float = formatFloat('123');
        expect(float).toBe('123');
    });

    it('should leave provided string untouched if it contains only numeric symbols and delimiter (dot)', () => {
        const float = formatFloat('123.456');
        expect(float).toBe('123.456');
    });

    it('should replace comma delimiter with dot and leave other symbols untouched', () => {
        const float = formatFloat('123,456');
        expect(float).toBe('123.456');
    });

    it('should remove all symbols starting by the second delimiter (dot)', () => {
        const float = formatFloat('123.456.789');
        expect(float).toBe('123.456');
    });

    it('should remove all symbols starting by the second delimiter (comma)', () => {
        const float = formatFloat('123,456,789.0');
        expect(float).toBe('123.456');
    });

    it('should remove all non numeric symbols from provided string', () => {
        const float = formatFloat('123.abc456*;789');
        expect(float).toBe('123.456789');
    });

    it("should leave empty string if provided string doesn't contain any numeric symbol", () => {
        const float = formatFloat('*;');
        expect(float).toBe('');
    });
});
