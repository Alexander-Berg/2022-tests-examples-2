import {parseRegion, getLanguageFromAL} from '../langdetect';

describe('langdetect utils', () => {
    describe('parseRegion', () => {
        it('Возвращает страну и язык', () => {
            expect(parseRegion()).toEqual({lang: '', country: '', origin: ''});
            expect(parseRegion('ru_KZ')).toEqual({lang: 'ru', country: 'kz', origin: 'ru_kz'});
        });

        it('Возвращает страну и язык из replacers, если не передано ничего', () => {
            expect(parseRegion('', {replacers: {country: 'ru', lang: 'en'}})).toEqual({
                lang: 'en',
                country: 'ru',
                origin: ''
            });
            expect(parseRegion('', {replacers: {country: 'ru', lang: 'en'}, fixOrigin: true})).toEqual({
                lang: 'en',
                country: 'ru',
                origin: 'en_ru'
            });
        });

        it('Для андройдов фиксим иврит (обещали сделать замену на андройде в последствии)', () => {
            expect(parseRegion('iw_il')).toEqual({lang: 'he', country: 'il', origin: 'iw_il'});
            expect(parseRegion('iw_il', {fixOrigin: true})).toEqual({lang: 'he', country: 'il', origin: 'he_il'});
        });
    });

    describe('getLanguageFromAL', () => {
        it('Возвращает язык и язык', () => {
            expect(getLanguageFromAL({'accept-language': 'ru,en-US;q=0.9,en;q=0.8,lt;q=0.7,he;q=0.6'})).toBe('ru');
        });
    });
});
