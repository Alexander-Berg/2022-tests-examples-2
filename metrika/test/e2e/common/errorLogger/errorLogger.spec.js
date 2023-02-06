const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('errorLogger e2e test', function () {
    const url = `${e2eUtils.baseUrl}/test/errorLogger/errorLogger.hbs`;

    beforeEach(function () {
        return this.browser.deleteCookie().timeoutsAsyncScript(10000);
    });

    it('should send error request', function () {
        return this.browser
            .url(url)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        serverHelpers.onRequest(function (request) {
                            done(request);
                        });

                        try {
                            new Ya.Metrika2({
                                id: {
                                    toString() {
                                        throw Error('Invalid id');
                                    },
                                },
                            });
                        } catch (e) {}
                    },
                }),
            )
            .then(({ value: request }) => {
                const { siteInfo, counterId } =
                    e2eUtils.getRequestParams(request);
                let key = Object.keys(siteInfo)[0];
                let val = siteInfo[key];
                chai.expect(counterId).to.eq('26302566');
                chai.expect(key).to.equal('jserrs');
                [key] = Object.keys(val);
                val = val[key];
                chai.expect(!!key).to.be.true;
                [key] = Object.keys(val);
                val = val[key];
                chai.expect(key).to.equal('Invalid id');
                [key] = Object.keys(val);
                val = val[key];
                chai.expect(key).to.equal('c.i');
                [key] = Object.keys(val);
                chai.expect(key).to.equal(url);
            });
    });
});
