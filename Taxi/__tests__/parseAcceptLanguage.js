import parseAcceptLanguage from '../parseAcceptLanguage';

describe('parseAcceptLanguage', () => {
    it('Should be return undefined if call with empty arguments', () => {
        expect(parseAcceptLanguage()).toBeUndefined();
    });

    it('Should be parse accept language', () => {
        expect(parseAcceptLanguage('ru,en;q=0.9')).toEqual(['ru', 'en']);
        expect(parseAcceptLanguage('he,en;q=0.9')).toEqual(['he', 'en']);
        expect(parseAcceptLanguage('ru-RU,en;q=0.9')).toEqual(['ru', 'en']);
        expect(parseAcceptLanguage('He,En;q=0.9')).toEqual(['he', 'en']);
    });
});
