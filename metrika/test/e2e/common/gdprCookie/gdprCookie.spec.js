const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Gdpr cookie e2e test', function () {
    const baseUrl = 'test/gdprCookie/gdprCookie.hbs';
    const counterId = 26302566;

    beforeEach(function () {
        return this.browser.timeoutsAsyncScript(10000);
    });
    it('should not set cookie before gdpr resolve', function () {
        return this.browser
            .url(`${baseUrl}`)
            .deleteCookie()
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        new Ya.Metrika2({
                            id: options.counterId,
                        });
                        done();
                    },
                    counterId,
                }),
            )
            .pause(100)
            .then(() => {
                return this.browser.getCookie('_ym_test_gdpr');
            })
            .then((testCookie) => {
                chai.expect(testCookie).to.be.equal(null);
            })
            .then(() => {
                return this.browser.getCookie('_ym_test_gdpr_after');
            })
            .then((testCookie) => {
                chai.expect(testCookie.value).to.be.equal('1');
            });
    });
});
