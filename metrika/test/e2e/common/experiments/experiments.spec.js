const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Experiments e2e test', function () {
    const baseUrl = 'test/experiments/experiments.hbs';
    const experimentUrlParam = 'exp';
    const testExperiment = 'TEST_EXPERIMENT';
    const counterId = 26302566;

    beforeEach(function () {
        return this.browser.timeoutsAsyncScript(10000).deleteCookie();
    });

    it('should exists experiment method', function () {
        return this.browser
            .url(baseUrl)
            .getText('body')
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                        });
                        done(counter);
                    },
                    counterId,
                }),
            )
            .then(({ value: counter }) => {
                chai.expect(counter).to.include.any.keys('experiments');
            });
    });
    it('should send http request', function () {
        return this.browser
            .url(baseUrl)
            .getText('body')
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        new Ya.Metrika2({
                            id: options.counterId,
                        });
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                        });
                        counter.experiments('TEST_EXPERIMENT');

                        serverHelpers.onRequest(function (request) {
                            if (
                                request.url.indexOf('exp=TEST_EXPERIMENT') !==
                                -1
                            ) {
                                done(request);
                            }
                        });
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: request }) => {
                if (!request.url) {
                    chai.assert(false, 'No experiments');
                } else {
                    const { url, params, brInfo } =
                        e2eUtils.getRequestParams(request);

                    chai.assert(url.match(`watch/${counterId}`));
                    chai.expect(request.url).to.include(
                        `${experimentUrlParam}=${testExperiment}`,
                    );
                    chai.expect(brInfo.ar).to.be.equal('1');
                    chai.expect(brInfo.ex).to.be.equal('1');
                    chai.expect(params[experimentUrlParam]).to.be.equal(
                        testExperiment,
                    );
                    chai.expect(params.charset).to.be.equal('utf-8');
                    chai.expect(params['page-url']).to.be.equal(
                        `${e2eUtils.baseUrl}/${baseUrl}`,
                    );
                }
            });
    });
    it(`doesn't log callback's error`, function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.collectRequests(
                            500,
                            (requests, done) => {
                                done({
                                    requests,
                                    errors: getPageErrors(),
                                });
                            },
                            options.regexp.defaultRequestRegEx,
                        );

                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                        });

                        counter.experiments('TEST EXPERIMENT', () => {
                            throw new Error('user error');
                        });
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value }) => {
                chai.expect(value.requests.length).to.be.equal(2);
                chai.expect(value.errors.usual.length).to.be.equal(1);
                chai.expect(value.errors.unhandledrejection.length).to.be.equal(
                    0,
                );
                chai.expect(value.errors.usual[0]).to.include('user error');
            });
    });
});
