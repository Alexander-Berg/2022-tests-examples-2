const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Uid', function () {
    const baseUrl = 'test/commonUidCookie/commonUidCookie.hbs';
    const firstCounterId = 26302566;
    const secondCounterId = 24226447;
    const mockUidValue = 'aksodsakp';
    const mockUidKey = 'test';
    const extractUid = (request) => {
        const {
            brInfo: { u },
        } = e2eUtils.getRequestParams(request);

        return u;
    };

    beforeEach(function () {
        return this.browser.deleteCookie().timeoutsAsyncScript(10000);
    });

    it('Should send the value of Uid in case the Uid cookie is set', function () {
        return this.browser
            .url(baseUrl)
            .getText('body')
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        document.cookie = `_ym_uid=${options.mockUidValue}`;

                        new Ya.Metrika2({
                            id: options.firstCounterId,
                        });
                        new Ya.Metrika2({
                            id: options.secondCounterId,
                        });

                        serverHelpers.onRequest(
                            // eslint-disable-next-line no-undef
                            createHanldeRequestFunction(done),
                            options.regexp.defaultRequestRegEx,
                        );
                    },
                    firstCounterId,
                    secondCounterId,
                    mockUidValue,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requestsToCheck }) => {
                const uids = requestsToCheck.map(extractUid);

                chai.expect(uids[0]).to.equal(mockUidValue);
                chai.expect(uids[0]).to.equal(uids[1]);
            });
    });

    it("Should generate the value of Uid in case the cookie wasn't set", function () {
        return this.browser
            .url(baseUrl)
            .getText('body')
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        new Ya.Metrika2({
                            id: options.firstCounterId,
                        });
                        new Ya.Metrika2({
                            id: options.secondCounterId,
                        });

                        serverHelpers.onRequest(
                            // eslint-disable-next-line no-undef
                            createHanldeRequestFunction(done),
                            options.regexp.defaultRequestRegEx,
                        );
                    },
                    firstCounterId,
                    secondCounterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requestsToCheck }) => {
                const uids = requestsToCheck.map(extractUid);

                chai.expect(uids[0]).to.be.a('string');
                chai.expect(uids[0]).to.not.be.oneOf(['null', 'undefined']);
                chai.expect(uids[0]).to.equal(uids[1]);
            });
    });

    it('Should return the correct value of Uid if the ldc parameter is set', function () {
        return this.browser
            .url(baseUrl)
            .getText('body')
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        document.cookie = `_ym_${options.mockUidKey}=${options.mockUidValue}`;

                        new Ya.Metrika2({
                            id: options.firstCounterId,
                            ldc: options.mockUidKey,
                        });
                        new Ya.Metrika2({
                            id: options.secondCounterId,
                            ldc: options.mockUidKey,
                        });

                        serverHelpers.onRequest(
                            // eslint-disable-next-line no-undef
                            createHanldeRequestFunction(done),
                            options.regexp.defaultRequestRegEx,
                        );
                    },
                    firstCounterId,
                    secondCounterId,
                    mockUidValue,
                    mockUidKey,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requestsToCheck }) => {
                const uids = requestsToCheck.map(extractUid);

                chai.expect(uids[0]).to.equal(mockUidValue);
                chai.expect(uids[0]).to.equal(uids[1]);
            });
    });
});
