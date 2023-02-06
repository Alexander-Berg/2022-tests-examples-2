const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Yandex e2e smoke test', function () {
    const baseUrl = 'https://yandex.ru/test/isYandexSmoke/isYandexSmoke.hbs';
    const counterId = 20302;
    const timeout = 10000;

    beforeEach(function () {
        // ff
        this.browser.timeouts({
            script: timeout,
            implicit: timeout,
            pageLoad: timeout,
        });
        // chrome
        this.browser.timeoutsAsyncScript(timeout);

        return this.browser.deleteCookie().url(baseUrl).pause(3000);
    });
    it('should find yandex page', function () {
        return this.browser.getText('body').then((innerText) => {
            chai.expect('yandex page').to.be.equal(innerText);
        });
    });
    it('should send gdpr request on yndex domain', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        serverHelpers.onRequest(function (request) {
                            done(request);
                        }, options.regexp.defaultRequestRegEx);
                        new Ya.Metrika2({
                            id: options.counterId,
                        });
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: request }) => {
                if (!(request && request.url)) {
                    chai.assert(false, 'No hit');
                } else {
                    const { params } = e2eUtils.getRequestParams(request);
                    chai.expect(params['page-url']).to.be.equal(baseUrl);
                }
            });
    });
});
