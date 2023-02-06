const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe.skip('antifrod', function () {
    const url = 'test/antifrod/antifrod.hbs';
    const counterId = 123;

    beforeEach(function () {
        return this.browser.deleteCookie();
    });

    it('sets antifrod ls flags', function () {
        return this.browser
            .timeoutsAsyncScript(5000)
            .url(url)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        localStorage.clear();
                        new Ya.Metrika2({
                            id: options.counterId,
                            webvisor: true,
                            childIframe: true,
                        });
                        setTimeout(done, 1000);
                    },
                    counterId,
                }),
            )
            .refresh()
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
                const { brInfo } = e2eUtils.getRequestParams(request);
                chai.expect(brInfo.afr).to.be.ok;
            });
    });
});
