const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('noCookie', function () {
    const testUrl = `${e2eUtils.baseUrl}/test/noCookie/noCookie.hbs`;
    const counterId = 26302566;
    beforeEach(function () {
        return this.browser
            .deleteCookie()
            .timeoutsAsyncScript(10000)
            .url(testUrl);
    });
    it('doesnot set any _ym_ cookies ', function () {
        return this.browser
            .getText('body')
            .then((innerText) => {
                chai.expect(innerText).to.be.eq('no cookie page');
            })
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        new Ya.Metrika2({
                            id: options.counterId,
                            nck: true,
                        });
                        setTimeout(function () {
                            done(document.cookie);
                        }, 500);
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: cookie }) => {
                cookie.split(';').forEach((str) => {
                    const [key] = str.replace(' ', '').split('=');
                    chai.expect(key.substr(0, 3)).to.be.not.eq('_ym');
                }, {});
            });
    });
});
