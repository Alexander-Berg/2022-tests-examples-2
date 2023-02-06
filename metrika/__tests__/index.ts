import { remap } from '../normalize';

describe('remap', () => {
    it('works', () => {
        const result = remap(
            { yandexEmployeeLogin: '13' },
            { 13: 'loginFromStaff' },
        );

        expect(result).toEqual({ yandexEmployeeLogin: 'loginFromStaff' });
    });

    it('skips keys if they not presented in raw object', () => {
        const result = remap({ yandexEmployeeLogin: '13' }, {});

        expect(result).toEqual({});
    });

    it('skips keys if they not presented in mapping object', () => {
        const result = remap({}, { 13: 'loginFromStaff' });

        expect(result).toEqual({});
    });

    it('mixed case', () => {
        const result = remap(
            { someOtherField: '42' },
            { 13: 'loginFromStaff' },
        );

        expect(result).toEqual({});
    });
});
