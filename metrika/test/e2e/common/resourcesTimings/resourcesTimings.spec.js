const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('ResourcesTimings e2e test', function () {
    const baseUrl = 'test/resourcesTimings/resourcesTimings.hbs';
    const counterId = 24226447;
    const resourcesTimingsCounterId = 51533966;
    const resourcesTimingsRequestRegex = `\\/watch\\/${resourcesTimingsCounterId}`;

    beforeEach(function () {
        return this.browser
            .deleteCookie()
            .timeoutsAsyncScript(10000)
            .url(baseUrl);
    });

    it('should send request with timings8 params after counter initialization', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        new Ya.Metrika2({
                            id: options.counterId,
                            accurateTrackBounce: 1,
                        });
                        serverHelpers.onRequest((request) => {
                            done(request);
                        }, options.resourcesTimingsRequestRegex);
                    },
                    counterId,
                    resourcesTimingsRequestRegex,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: request }) => {
                chai.expect(request, 'request didnt arrive somehow').to.exist;
                const { siteInfo, brInfo } = e2eUtils.getRequestParams(request);
                chai.expect(siteInfo, 'no site-info field').to.exist;
                chai.expect(brInfo.v).to.be.ok;
                chai.expect(brInfo.vf).to.be.ok;
                chai.expect(
                    Object.keys(siteInfo),
                    'no timings8 found',
                ).to.include('timings8');
            });
    });

    it('should not send request when notBounce is called', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                        });
                        counter.notBounce();
                        serverHelpers.collectRequests(
                            700,
                            null,
                            options.regexp.defaultRequestRegEx,
                        );
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const parsedRequests = requests.map(e2eUtils.getRequestParams);
                const isResourcesTimingsRequest = parsedRequests.some(
                    ({ counterId: id }) => id === resourcesTimingsCounterId,
                );
                chai.expect(
                    isResourcesTimingsRequest,
                    "resourcesTimings request shouldn't have been made",
                ).to.be.false;
            });
    });

    it("should hide client errors in case transport doesn't work", function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        serverHelpers.addRule(
                            {
                                regex: options.resourcesTimingsRequestRegex,
                                count: 1,
                                status: '500',
                            },
                            function () {
                                const logError = (e) => {
                                    done(e.type);
                                };
                                window.addEventListener('error', logError);
                                window.addEventListener(
                                    'unhandledrejection',
                                    logError,
                                );
                                new Ya.Metrika2({
                                    id: options.counterId,
                                    accurateTrackBounce: 1,
                                });
                                serverHelpers.onRequest(() => {
                                    setTimeout(done, 2000);
                                }, options.resourcesTimingsRequestRegex);
                            },
                        );
                    },
                    counterId,
                    resourcesTimingsRequestRegex,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value }) => {
                chai.expect(value).to.be.null;
            });
    });
});
