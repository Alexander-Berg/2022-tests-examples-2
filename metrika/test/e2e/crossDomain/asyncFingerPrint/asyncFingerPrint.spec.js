const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

// Можно расскипать после выкакти в прод
describe.skip('AsyncFingerPrint', function () {
    const baseUrl = `https://yandex.ru/test/asyncFingerPrint/asyncFingerPrint.hbs`;
    const counterId = 26302566;
    beforeEach(function () {
        return this.browser
            .timeoutsAsyncScript(10000)
            .url(baseUrl)
            .localStorage('DELETE')
            .execute(function () {
                [
                    'gdpr=0',
                    `forceIO=${window.cookieVal}; domain=.yandex.ru; path=/`,
                ].forEach((val) => {
                    document.cookie = val;
                });
                localStorage.setItem('_ym_synced', '{"SYNCED_ADM":9999999999}');
            });
    });
    it('should find fingerPrint page', function () {
        return this.browser.getText('body').then((innerText) => {
            chai.expect(
                innerText,
                'check if page contains required text',
            ).to.be.equal('AsyncFingerPrint page');
        });
    });
    it('should set aip from localstrorage', function () {
        const testVal = '123123';
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        localStorage.setItem('_ym_aip', options.testVal);
                        serverHelpers.collectRequests(
                            500,
                            null,
                            options.regexp.defaultRequestRegEx,
                        );
                        new Ya.Metrika2({
                            id: options.counterId,
                        });
                    },
                    counterId,
                    testVal,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                chai.expect(requests).to.be.lengthOf(1);
                const parsedRequests = requests.map(e2eUtils.getRequestParams);
                const { brInfo } = parsedRequests[0];
                chai.expect(brInfo.j0).to.be.eq(testVal);
            });
    });
    it('should exists aip browserInfo flag', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.collectRequests(
                            3000,
                            null,
                            options.regexp.defaultRequestRegEx,
                        );
                        const instance = new Ya.Metrika2({
                            id: options.counterId,
                        });
                        setTimeout(() => {
                            instance.params({ __ym: 1 });
                        }, 1500);
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                chai.expect(requests).to.be.ok;
                const parsedRequests = requests.map(e2eUtils.getRequestParams);
                const params = parsedRequests.filter(({ brInfo }) => brInfo.pa);
                chai.expect(params).lengthOf(1);
                const { brInfo } = params[0];
                chai.expect(brInfo).to.have.property('j0');
            });
    });
});
