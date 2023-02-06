const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Encoding e2e test', function () {
    const url = `${e2eUtils.baseUrl}/test/encoding/encoding.hbs`;
    const counterId = 26302566;
    const encoding = 'windows-1251';

    beforeEach(function () {
        return this.browser.deleteCookie().timeoutsAsyncScript(10000);
    });

    it('Checks encoding', function () {
        return this.browser
            .url(`${url}?encoding=${encoding}`)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        new Ya.Metrika2({
                            id: options.counterId,
                        });
                        serverHelpers.onRequest(function (request) {
                            done(request);
                        }, options.regexp.defaultRequestRegEx);
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: request }) => {
                const { brInfo } = e2eUtils.getRequestParams(request);
                chai.expect(brInfo.en).to.equal(encoding);
            });
    });
});
