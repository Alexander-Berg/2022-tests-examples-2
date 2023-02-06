const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Metrika uid test', function () {
    const path = 'test/subdomainUid/uid.hbs';
    const rootDomain = `https://yandex.ru/${path}`;
    const subDomain = `https://mc.yandex.ru/${path}`;
    const counterId = 20302;
    beforeEach(function () {
        return this.browser.timeoutsAsyncScript(10000).deleteCookie();
    });
    it('should find yandex.ru page', function () {
        return this.browser
            .url(rootDomain)
            .getText('body')
            .then((innerText) => {
                chai.expect('yandex.ru page').to.be.equal(innerText);
            });
    });
    it('sould find mc.yandex.ru', function () {
        return this.browser
            .url(subDomain)
            .getText('body')
            .then((innerText) => {
                chai.expect('yandex.ru page').to.be.equal(innerText);
            });
    });
    it('have same uid on diffrent subdomains', function () {
        let requests = [];
        return this.browser
            .url(rootDomain)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.collectRequests(1000);
                        new Ya.Metrika2({
                            id: options.counterId,
                        });
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: [request] }) => {
                const requestInfo = e2eUtils.getRequestParams(request);
                chai.expect(requestInfo.params['page-url']).to.be.equal(
                    rootDomain,
                );
                requests = requests.concat(requestInfo);
            })
            .url(subDomain)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.collectRequests(1000);
                        new Ya.Metrika2({
                            id: options.counterId,
                        });
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: [request] }) => {
                const requestInfo = e2eUtils.getRequestParams(request);
                chai.expect(requestInfo.params['page-url']).to.be.equal(
                    subDomain,
                );
                requests = requests.concat(requestInfo);
                chai.expect(requests).to.be.lengthOf(2);
                const [rootDomainRequest, subDomainRequest] = requests;
                chai.expect(rootDomainRequest.brInfo.u).to.be.eq(
                    subDomainRequest.brInfo.u,
                );
            });
    });
});
