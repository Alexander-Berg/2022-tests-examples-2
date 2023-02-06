const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Yandex search tld', function () {
    const baseUrl = 'https://yandex.com.tr/test/searchTld/searchPage.hbs';
    const counterId = 20302;
    beforeEach(function () {
        return this.browser.timeoutsAsyncScript(10000).deleteCookie();
    });
    it('should find yandex search page', function () {
        return this.browser
            .url(baseUrl)
            .getText('.content')
            .then((innerText) => {
                chai.expect('yandex search test').to.be.equal(innerText);
            })
            .click('#next')
            .getText('.content')
            .then((innerText) => {
                chai.expect('yandex search test').to.be.equal(innerText);
            })
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.collectRequests(
                            1000,
                            null,
                            options.regexp.defaultRequestRegEx,
                        );
                        new Ya.Metrika2({
                            id: options.counterId,
                        });
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                let hasPVRequest = false;
                requests.forEach((request) => {
                    const { brInfo } = e2eUtils.getRequestParams(request);
                    hasPVRequest =
                        hasPVRequest ||
                        (request.headers['x-host'] === 'mc.yandex.com.tr' &&
                            brInfo.pv === '1');
                });
                chai.assert(hasPVRequest);
            });
    });
});
