import { detectLang } from '../detect';
import { Lang } from '@shared/i18n/lang';

describe('lang-detect', () => {
    const availableLanguages = [Lang.Ru, Lang.En];
    const defaultLanguage = Lang.Ru;

    describe('XLang header', () => {
        it('should detect lang from XLang header', () => {
            expect(
                detectLang({
                    availableLangs: availableLanguages,
                    defaultLang: defaultLanguage,
                    xLangHeader: Lang.En,
                    myCookie: 'YycCAAEA',
                    acceptLanguageHeader: 'ru,en;q=0.9',
                })
            ).toBe(Lang.En);
        });
    });

    describe('getLangFromCookie ', () => {
        it('should detect lang from cookie', () => {
            expect(
                detectLang({ availableLangs: availableLanguages, defaultLang: defaultLanguage, myCookie: 'YycCAAEA' })
            ).toBe(Lang.Ru);
            expect(
                detectLang({ availableLangs: availableLanguages, defaultLang: defaultLanguage, myCookie: 'YycCAAMA' })
            ).toBe(Lang.En);
            expect(
                detectLang({ availableLangs: availableLanguages, defaultLang: defaultLanguage, myCookie: 'YycCAAgA' })
            ).toBe(defaultLanguage);
        });
    });

    describe('getLangFromHeader ', () => {
        it('should detect lang from header', () => {
            expect(
                detectLang({
                    availableLangs: availableLanguages,
                    defaultLang: defaultLanguage,
                    acceptLanguageHeader: 'ru,en;q=0.9',
                })
            ).toBe(Lang.Ru);
            expect(
                detectLang({
                    availableLangs: availableLanguages,
                    defaultLang: defaultLanguage,
                    acceptLanguageHeader: 'en-US,en;q=0.5',
                })
            ).toBe(Lang.En);
            expect(
                detectLang({
                    availableLangs: availableLanguages,
                    defaultLang: defaultLanguage,
                    acceptLanguageHeader: 'fr-CH,fr;q=0.9',
                })
            ).toBe(defaultLanguage);
        });
    });
});
