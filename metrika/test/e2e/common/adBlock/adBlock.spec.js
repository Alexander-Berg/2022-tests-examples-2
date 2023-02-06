const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('AdBlock', function () {
    const baseDir = 'test/adBlock';
    const baseUrl = `${baseDir}/adBlock.hbs`;
    const adBlockKey = '_ym_isad';
    const adBlockIsDisabled = '2';
    const adBlockIsEnabled = '1';
    const firstCounterId = 26302566;
    const secondCounterId = 24226447;

    beforeEach(function () {
        return this.browser
            .deleteCookie()
            .timeoutsAsyncScript(3000)
            .url(baseUrl);
    });
    it('detects adBlok', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.addRule(
                            {
                                regex: 'advert.gif',
                                status: '500',
                            },
                            function () {
                                serverHelpers.collectRequests(200);
                                new Ya.Metrika2({
                                    id: options.firstCounterId,
                                });
                            },
                        );
                    },
                    firstCounterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const gifRequests = requests.filter((req) =>
                    /advert\.gif/.test(req.url),
                );
                chai.expect(gifRequests.length).to.be.equal(1);
                return this.browser.getCookie(adBlockKey);
            })
            .then((isAdblock) => {
                chai.expect(isAdblock.value).to.be.equal(adBlockIsEnabled);
            });
    });
    it('Should send image request and set the cookie value, if it is not set', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.collectRequests(200);
                        new Ya.Metrika2({
                            id: options.firstCounterId,
                        });
                        new Ya.Metrika2({
                            id: options.secondCounterId,
                        });
                    },
                    firstCounterId,
                    secondCounterId,
                    adBlockKey,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const gifRequests = requests.filter((req) =>
                    /advert\.gif/.test(req.url),
                );
                chai.expect(gifRequests.length).to.be.equal(1);
                return this.browser.getCookie(adBlockKey);
            })
            .then((isAdblock) => {
                chai.expect(isAdblock.value).to.be.equal(adBlockIsDisabled);
            });
    });

    it('Should not send image request if cookie set', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        document.cookie = `${options.adBlockKey}=${options.adBlockIsDisabled}`;
                        serverHelpers.collectRequests(200);
                        new Ya.Metrika2({
                            id: options.firstCounterId,
                        });
                        new Ya.Metrika2({
                            id: options.secondCounterId,
                        });

                        serverHelpers.onRequest(
                            // eslint-disable-next-line no-undef
                            createHandleRequestFunction(done),
                        );
                    },
                    firstCounterId,
                    secondCounterId,
                    adBlockKey,
                    adBlockIsDisabled,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                requests.forEach((request) => {
                    const { brInfo } = e2eUtils.getRequestParams(request);
                    chai.expect(brInfo.adb).to.be.eq(adBlockIsDisabled);
                });
            });
    });
});
