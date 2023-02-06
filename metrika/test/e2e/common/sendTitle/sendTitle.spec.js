const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('noTitle', function () {
    const baseUrl = 'test/sendTitle/sendTitle.hbs';
    const counterId = 26302566;

    beforeEach(function () {
        return this.browser.timeoutsAsyncScript(10000).url(baseUrl);
    });

    it('should send title', function () {
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
                const { brInfo } = e2eUtils.getRequestParams(request);
                chai.expect(brInfo.t).to.eq('SendTitle page title');
            });
    });

    it('should not send title with noTitle param', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        serverHelpers.onRequest(function (request) {
                            done(request);
                        }, options.regexp.defaultRequestRegEx);
                        new Ya.Metrika2({
                            id: options.counterId,
                            sendTitle: false,
                        });
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: request }) => {
                const { brInfo } = e2eUtils.getRequestParams(request);
                chai.expect(brInfo.t).to.be.undefined;
            });
    });
});
