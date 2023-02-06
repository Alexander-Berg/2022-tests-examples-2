const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('fingerPrint', function () {
    const baseUrl = `https://yandex.ru/test/fingerPrint/fingerPrint.hbs`;
    const counterId = 26302566;
    beforeEach(function () {
        return this.browser
            .timeoutsAsyncScript(10000)
            .url(baseUrl)
            .deleteCookie()
            .localStorage('DELETE')
            .execute(function () {
                document.cookie = 'gdpr=0';
                localStorage.setItem('_ym_synced', '{"SYNCED_ADM":9999999999}');
            });
    });
    it('should find fingerPrint page', function () {
        return this.browser.getText('body').then((innerText) => {
            chai.expect(
                innerText,
                'check if page contains required text',
            ).to.be.equal('FingerPrint page');
        });
    });
    it('should exists fip browserInfo flag', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        serverHelpers.onRequest(function (req) {
                            done(req);
                        });
                        new Ya.Metrika2({
                            id: options.counterId,
                        });
                        setTimeout(done, 1000);
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: result }) => {
                chai.expect(result).to.be.ok;
                const { brInfo } = e2eUtils.getRequestParams(result);
                chai.expect(brInfo.fip).to.be.ok;
            });
    });
});
