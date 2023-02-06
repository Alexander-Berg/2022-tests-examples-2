const {getLanguageFactory} = require('../patch-langdetect');

describe('patch-langdetect', () => {
    describe('getLanguageFactory', () => {
        it('Should not be found language', () => {
            const getLanguage1 = getLanguageFactory();
            const getLanguage2 = getLanguageFactory({languageFromQuery: 'ru', languageFromAL: 'en'});
            const availableLanguages = ['he', 'fr', 'fi'];

            expect(getLanguage1(availableLanguages)).toBeUndefined();
            expect(getLanguage2(availableLanguages)).toBeUndefined();
            expect(getLanguage2([])).toBeUndefined();
        });

        it('Should be found language', () => {
            const getLanguage = getLanguageFactory({languageFromAL: 'en', languageFromQuery: 'ru'});

            expect(getLanguage(['ru'])).toBe('ru');
            expect(getLanguage(['en'])).toBe('en');
            expect(getLanguage(['en', 'ru'])).toBe('ru');
            expect(getLanguage(['ru', 'en'])).toBe('ru');
        });
    });
});
