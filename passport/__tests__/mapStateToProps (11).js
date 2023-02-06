import mapStateToProps from '../mapStateToProps';

describe('Components: Footer.mapStateToProps', () => {
    it('should return valid props', () => {
        const state = {
            settings: {
                tld: 'ru',
                env: {
                    name: 'production'
                },
                help: {
                    passport: 'yandex.%tld%'
                },
                language: 'ru',
                langlist: [
                    {id: 'ru', name: 'rus', link: '/ru'},
                    {id: 'en', name: 'eng', link: '/com'}
                ]
            },
            common: {
                isWebView: false
            }
        };

        const result = mapStateToProps(state);

        expect(result).toEqual({
            tld: 'ru',
            lang: 'ru',
            options: [{text: 'eng', url: '/com'}],
            helpLink: 'yandex.ru',
            currentYear: new Date().getFullYear(),
            hasSwitcher: true,
            isWebView: false
        });
    });

    it('should fallback props', () => {
        const state = {
            settings: {
                tld: 'az',
                env: {
                    name: 'production'
                },
                help: {
                    passport: 'yandex.%tld%'
                },
                language: 'ru',
                langlist: [
                    {id: 'ru', name: 'rus', link: '/ru'},
                    {id: 'en', name: 'eng', link: '/com'}
                ]
            },
            common: {
                isWebView: false
            }
        };

        let result = mapStateToProps(state);

        expect(result).toEqual({
            tld: 'az',
            lang: 'ru',
            options: [{text: 'eng', url: '/com'}],
            helpLink: 'yandex.ru',
            currentYear: new Date().getFullYear(),
            hasSwitcher: true,
            isWebView: false
        });

        state.settings.tld = 'fr';
        result = mapStateToProps(state);

        expect(result).toEqual({
            tld: 'fr',
            lang: 'ru',
            options: [{text: 'eng', url: '/com'}],
            helpLink: 'yandex.com',
            currentYear: new Date().getFullYear(),
            hasSwitcher: true,
            isWebView: false
        });

        state.settings.langlist = [];
        result = mapStateToProps(state);

        expect(result).toEqual({
            tld: 'fr',
            lang: 'ru',
            options: [],
            helpLink: 'yandex.com',
            currentYear: new Date().getFullYear(),
            hasSwitcher: false,
            isWebView: false
        });

        state.settings.langlist = [
            {id: 'ru', name: 'rus', link: '/ru'},
            {id: 'en', name: 'eng', link: '/com'}
        ];
        state.settings.env.name = 'intranet';
        result = mapStateToProps(state);

        expect(result).toEqual({
            tld: 'fr',
            lang: 'ru',
            options: [],
            helpLink: 'yandex.com',
            currentYear: new Date().getFullYear(),
            hasSwitcher: false,
            isWebView: false
        });

        state.settings.help = null;
        result = mapStateToProps(state);

        expect(result).toEqual({
            tld: 'fr',
            lang: 'ru',
            options: [],
            helpLink: '#',
            currentYear: new Date().getFullYear(),
            hasSwitcher: false,
            isWebView: false
        });
    });
});
