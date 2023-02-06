const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('notBounce', function () {
    const testUrl = `${e2eUtils.baseUrl}/test/notBounce/notBounce.hbs`;
    const counterId = 26302566;

    const requestIsNotBounce = (request) => {
        const { params, brInfo } = e2eUtils.getRequestParams(request);

        return (
            brInfo.nb === '1' &&
            !Number.isNaN(+brInfo.cl) &&
            brInfo.ar === '1' &&
            testUrl === params['page-url']
        );
    };

    beforeEach(function () {
        return this.browser.timeoutsAsyncScript(10000).url(testUrl);
    });

    it('Sends not bounce request if configured to do so and sends clicks info', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        new Ya.Metrika2({
                            id: options.counterId,
                            accurateTrackBounce: 200,
                            clickmap: true,
                        });
                        serverHelpers.collectRequests(
                            400,
                            null,
                            options.regexp.defaultRequestRegEx,
                        );
                        const button = document.querySelector('button');
                        setTimeout(() => {
                            button.click();
                        }, 100);
                        setTimeout(() => {
                            button.click();
                        }, 150);
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const notBounceRequest = requests.find(requestIsNotBounce);
                chai.expect(!!notBounceRequest).to.be.true;

                const { telemetry } =
                    e2eUtils.getRequestParams(notBounceRequest);
                const clicks = parseInt(telemetry.clc || '0', 10);
                chai.expect(clicks).to.equal(2);
            });
    });

    it('Sends not bounce request if method is called', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                        });
                        counter.notBounce();
                        serverHelpers.collectRequests(
                            200,
                            null,
                            options.regexp.defaultRequestRegEx,
                        );
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const hasNotBounceRequest = requests.some(requestIsNotBounce);

                chai.expect(hasNotBounceRequest).to.be.true;
            });
    });

    it('Sends not bounce request for each method call', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.collectRequests(
                            500,
                            null,
                            options.regexp.defaultRequestRegEx,
                        );

                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                        });
                        counter.notBounce();
                        counter.notBounce();
                        counter.notBounce();
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const notBounceRequests = requests.filter(requestIsNotBounce);
                chai.expect(notBounceRequests).to.have.lengthOf(3);
            });
    });

    it(`doesn't log callback's error`, function () {
        return this.browser
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

                        counter.notBounce({
                            callback() {
                                throw new Error('user error');
                            },
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

    it('Sends not bounce request if accurateTrackBounce method called', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                        });
                        counter.accurateTrackBounce(100);
                        counter.accurateTrackBounce(100);
                        serverHelpers.collectRequests(
                            400,
                            null,
                            options.regexp.defaultRequestRegEx,
                        );
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const notBounceRequests = requests.filter(requestIsNotBounce);
                chai.expect(notBounceRequests.length).to.eq(1);
            });
    });
});
