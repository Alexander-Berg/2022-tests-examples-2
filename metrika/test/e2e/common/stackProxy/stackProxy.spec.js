const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Stack proxy test', function () {
    const baseUrl = 'test/stackProxy/stackProxy.hbs';
    const counterId = 26302566;

    beforeEach(function () {
        return this.browser
            .timeoutsAsyncScript(10000)
            .url(baseUrl)
            .getText('body')
            .then((text) => {
                chai.expect(text).to.be.equal('Stack proxy page');
            });
    });
    it('init counter after script load', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.collectRequests(
                            400,
                            null,
                            options.regexp.defaultRequestRegEx,
                        );
                        setTimeout(function () {
                            window.ym(options.counterId, 'init');
                            window.ym(options.counterId + 1, 'init');
                            window.ym(options.counterId, 'hit', '/');
                            window.ym(options.counterId + 1, 'hit', '/');
                        }, 10);
                        // eslint-disable-next-line no-undef
                        initCounterFromLocalJs();
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: results }) => {
                const requestsInfo = results.map(e2eUtils.getRequestParams);
                chai.expect(requestsInfo.length).to.be.equal(4);
                chai.expect(
                    requestsInfo.filter(({ brInfo }) => brInfo.ar).length,
                ).to.be.equal(2);
            });
    });
    it('init counter', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        window.ym = function (...args) {
                            window.ym.a.push(args);
                        };
                        window.ym.a = [];
                        serverHelpers.collectRequests(
                            500,
                            null,
                            options.regexp.defaultRequestRegEx,
                        );
                        setTimeout(function () {
                            // eslint-disable-next-line no-undef
                            initCounterFromLocalJs();
                        }, 10);
                        window.ym(options.counterId, 'init');
                        window.ym(options.counterId + 1, 'init');
                        window.ym(options.counterId, 'hit', '/');
                        window.ym(options.counterId + 1, 'hit', '/');
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: results }) => {
                const requestsInfo = results.map(e2eUtils.getRequestParams);
                chai.expect(requestsInfo.length).to.be.equal(4);
                chai.expect(
                    requestsInfo.filter(({ brInfo }) => brInfo.ar).length,
                ).to.be.equal(2);
            });
    });
});
