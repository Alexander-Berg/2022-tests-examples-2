import {describe, expect, it} from 'tests/jest.globals';

import {combineName, joinWithDirection} from './combine-name';

describe('joinWithDirection', () => {
    it('lrt', async () => {
        expect(joinWithDirection(['a', 'b', 'c'], 'ltr')).toBe('abc');
    });

    it('rtl', async () => {
        expect(joinWithDirection(['a', 'b', 'c'], 'rtl')).toBe('cba');
    });
});

describe('combineName', () => {
    it('en', async () => {
        const dataLang = 'en';

        expect(combineName({dataLang})).toBe('');

        expect(
            combineName({
                code: '123',
                name: undefined,
                dataLang
            })
        ).toBe('123');

        expect(
            combineName({
                code: '123',
                name: 'name',
                dataLang
            })
        ).toBe('name');

        expect(
            combineName({
                code: '123',
                name: 'name',
                count: 300,
                dataLang
            })
        ).toBe('name 300');

        expect(
            combineName({
                code: '123',
                name: 'name',
                count: 300,
                countUnit: 'ml',
                dataLang
            })
        ).toBe('name 300 ml');

        expect(
            combineName({
                code: '123',
                name: 'name',
                count: 300,
                countUnit: 'ml',
                countPack: 6,
                dataLang
            })
        ).toBe('name 6x300 ml');
    });

    it('ru', async () => {
        const dataLang = 'ru';

        expect(combineName({dataLang})).toBe('');

        expect(
            combineName({
                code: '123',
                name: undefined,
                dataLang
            })
        ).toBe('123');

        expect(
            combineName({
                code: '123',
                name: 'name',
                dataLang
            })
        ).toBe('name');

        expect(
            combineName({
                code: '123',
                name: 'name',
                count: 300,
                dataLang
            })
        ).toBe('name, 300');

        expect(
            combineName({
                code: '123',
                name: 'name',
                count: 300,
                countUnit: 'ml',
                dataLang
            })
        ).toBe('name, 300 ml');

        expect(
            combineName({
                code: '123',
                name: 'name',
                count: 300,
                countUnit: 'ml',
                countPack: 6,
                dataLang
            })
        ).toBe('name, 6x300 ml');
    });

    it('he', async () => {
        const dataLang = 'he';

        expect(combineName({dataLang})).toBe('');

        expect(
            combineName({
                code: '123',
                name: undefined,
                dataLang
            })
        ).toBe('123');

        expect(
            combineName({
                code: '123',
                name: 'name',
                dataLang
            })
        ).toBe('name');

        expect(
            combineName({
                code: '123',
                name: 'name',
                count: 300,
                dataLang
            })
        ).toBe('300 name');

        expect(
            combineName({
                code: '123',
                name: 'name',
                count: 300,
                countUnit: 'ml',
                dataLang
            })
        ).toBe('ml 300 name');

        expect(
            combineName({
                code: '123',
                name: 'name',
                count: 300,
                countUnit: 'ml',
                countPack: 6,
                dataLang
            })
        ).toBe('ml 6x300 name');
    });
});
