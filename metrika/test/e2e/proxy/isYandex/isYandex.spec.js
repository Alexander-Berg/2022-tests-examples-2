const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Yandex e2e proxy test', function () {
    const baseUrl = 'https://yandex.ru/test/isYandex/isYandex.hbs';
    const counterId = 20302;
    beforeEach(function () {
        return this.browser.timeoutsAsyncScript(10000).deleteCookie();
    });
    it('should find yandex page', function () {
        return this.browser
            .url(baseUrl)
            .getText('body')
            .then((innerText) => {
                chai.expect('yandex page').to.be.equal(innerText);
            });
    });
    it('should send gdpr request on yndex domain', function () {
        return this.browser
            .url(baseUrl)
            .getText('body')
            .then((innerText) => {
                chai.expect('yandex page').to.be.equal(innerText);
            })
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.collectRequests(1000);
                        new Ya.Metrika2({
                            id: options.counterId,
                        });
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: [request] }) => {
                if (!(request && request.url)) {
                    chai.assert(false, 'No hit');
                } else {
                    const { params } = e2eUtils.getRequestParams(request);
                    chai.expect(params['page-url']).to.be.equal(baseUrl);
                }
            });
    });
});
