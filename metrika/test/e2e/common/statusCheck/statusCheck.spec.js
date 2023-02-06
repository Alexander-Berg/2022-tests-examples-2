const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Status Check', function () {
    const baseUrl = 'test/statusCheck/status.hbs';
    const CHECK_URL_PARAM = '_ym_status-check';
    const LANG_URL_PARAM = '_ym_lang';
    const counterId = '20320';
    const langEn = 'en';
    const resourceRegexp = {
        ru: /form-selector\/status_ru.js$/,
        en: /form-selector\/status_en.js$/,
    };

    function urlWithSearchParams(counter, lang) {
        return `${baseUrl}?${CHECK_URL_PARAM}=${counter}&${LANG_URL_PARAM}=${lang}`;
    }

    function testCheckStatusProvider({
        ctx,
        counterIdForInit,
        counterIdForCheck,
        urlLangParam = '',
    }) {
        return (
            ctx.browser
                .url(urlWithSearchParams(counterIdForCheck, urlLangParam))
                .getText('.content')
                .then((innerText) => {
                    chai.expect('Status Check page').to.be.equal(innerText);
                })
                .then(
                    e2eUtils.provideServerHelpers(ctx.browser, {
                        cb(serverHelpers, options, done) {
                            new Ya.Metrika2({
                                id: options.counterIdForInit,
                            });

                            setTimeout(done, 1000);
                        },
                        counterIdForInit,
                    }),
                )
                // check for script tag
                .execute(function () {
                    return Array.prototype.slice
                        .call(document.getElementsByTagName('script'))
                        .map((item) => item.src);
                })
                .then(({ value: scripts }) => {
                    const lang = urlLangParam || 'ru';

                    chai.expect(
                        scripts.filter((src) => resourceRegexp[lang].test(src))
                            .length,
                    ).to.eq(
                        counterIdForInit === counterIdForCheck ? 1 : 0,
                        `can not find script "status_${lang}.js"`,
                    );
                })
        );
    }

    beforeEach(function () {
        return this.browser.deleteCookie().timeoutsAsyncScript(10000);
    });

    it('returns positive status for existing counter', function () {
        return (
            testCheckStatusProvider({
                ctx: this,
                counterIdForInit: counterId,
                counterIdForCheck: counterId,
            })
                // test checkStatus function
                .execute(function () {
                    return window.Ya._metrika._u.status.checkStatus();
                })
                .then(({ value }) => {
                    chai.expect(value).to.deep.eq(
                        {
                            id: parseInt(counterId, 10),
                            counterFound: true,
                        },
                        'can not check status',
                    );
                })
        );
    });

    it('loads proper script when language is provided', function () {
        return testCheckStatusProvider({
            ctx: this,
            counterIdForInit: counterId,
            counterIdForCheck: counterId,
            lang: langEn,
        });
    });

    it('returns negative status for missing counter', function () {
        return (
            testCheckStatusProvider({
                ctx: this,
                counterIdForInit: counterId,
                counterIdForCheck: `${counterId}1`,
            })
                // test checkStatus function
                .execute(function () {
                    return window.Ya._metrika._u;
                })
                .then(({ value }) => {
                    chai.expect(value).to.be.null;
                })
        );
    });
});
