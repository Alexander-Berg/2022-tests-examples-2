const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Not turbo flags', function () {
    const baseUrl = 'test/notTurboFlags/notTurboFlags.hbs';
    const counterId = 12342;

    const testUid = 12345;

    beforeEach(function () {
        return this.browser.timeoutsAsyncScript(10000).deleteCookie();
    });

    const createFlagTest = (title, checkRequest, path, data) =>
        it(title, function () {
            return this.browser
                .url(baseUrl)
                .then(
                    e2eUtils.provideServerHelpers(this.browser, {
                        cb(serverHelpers, options, done) {
                            if (options.path) {
                                window[options.path] = options.data;
                            }
                            serverHelpers.onRequest(function (request) {
                                done(request);
                            }, options.regexp.defaultRequestRegEx);
                            new Ya.Metrika2({
                                id: options.counterId,
                            });
                        },
                        counterId,
                        path,
                        data,
                    }),
                )
                .then(e2eUtils.handleRequest(this.browser))
                .then(({ value: request }) => {
                    checkRequest(request);
                });
        });

    createFlagTest(
        'Should detect selenium',
        (request) => {
            const { brInfo } = e2eUtils.getRequestParams(request);
            chai.expect(brInfo.iss).to.equal('1');
        },
        '_selenium',
        true,
    );
    createFlagTest(
        'Should detect headless',
        (request) => {
            const { brInfo } = e2eUtils.getRequestParams(request);
            chai.expect(brInfo.hdl).to.equal('1');
        },
        '_phantom',
        true,
    );
    createFlagTest(
        'Should detect facebook instant articles',
        (request) => {
            const { brInfo } = e2eUtils.getRequestParams(request);
            chai.expect(brInfo.iia).to.equal('1');
        },
        'ia_document',
        { shareURL: true, referrer: true },
    );
    createFlagTest('Should send navigation start', (request) => {
        const { brInfo } = e2eUtils.getRequestParams(request);
        chai.expect(parseInt(brInfo.ns, 10)).to.not.be.NaN;
    });

    it('Should send re', function () {
        return this.browser
            .url(baseUrl)
            .deleteCookie('_ym_uid')
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        window.localStorage.setItem('_ym_uid', options.testUid);
                        serverHelpers.onRequest(function (request) {
                            done(request);
                        }, options.regexp.defaultRequestRegEx);
                        new Ya.Metrika2({
                            id: options.counterId,
                        });
                    },
                    counterId,
                    testUid,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: request }) => {
                const { telemetry } = e2eUtils.getRequestParams(request);
                chai.expect(telemetry.re).to.equal('1');
            });
    });

    it('Should not send re', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        document.cookie = `_ym_uid=${options.testUid}`;
                        window.localStorage.setItem('_ym_uid', options.testUid);
                        serverHelpers.onRequest(function (request) {
                            done(request);
                        }, options.regexp.defaultRequestRegEx);
                        new Ya.Metrika2({
                            id: options.counterId,
                        });
                    },
                    counterId,
                    testUid,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: request }) => {
                const { brInfo } = e2eUtils.getRequestParams(request);
                chai.expect(brInfo.re).to.equal(undefined);
            });
    });
});
