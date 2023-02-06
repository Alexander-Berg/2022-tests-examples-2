const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Function e2e test', function () {
    const baseDir = 'test/function';
    const baseUrl = `${baseDir}/function.hbs`;
    const counterId = 26302566;
    const testUrl = 'contacts';

    beforeEach(function () {
        return this.browser.timeoutsAsyncScript(10000).deleteCookie();
    });

    it('should use cached functions', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        serverHelpers.onRequest(function (request) {
                            if (request.url.indexOf(options.testUrl) !== -1) {
                                done(request);
                            }
                        });
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                        });
                        // eslint-disable-next-line no-extend-native
                        Array.prototype.map = undefined;
                        counter.hit(options.testUrl);
                    },
                    counterId,
                    testUrl,
                    defaultRequestRegEx: e2eUtils.defaultRequestRegEx,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: request }) => {
                chai.expect(request.url).to.be.ok;
                const { params } = e2eUtils.getRequestParams(request);
                chai.expect(params['page-url']).to.be.equal(
                    `${e2eUtils.baseUrl}/${baseDir}/${testUrl}`,
                );
            });
    });
});
