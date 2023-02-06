const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Alt domain for metrika requests', function () {
    const resource = 'test/altDomain/altDomain.hbs';
    const baseUrl = `https://mc.webvisor.org/${resource}`;
    const counterId = 20302;
    beforeEach(function () {
        return this.browser.timeoutsAsyncScript(10000).deleteCookie();
    });
    it('should find ua page', function () {
        return (
            this.browser
                .url(baseUrl)
                .getText('.content')
                .then((innerText) => {
                    chai.expect('ua page').to.be.equal(innerText);
                })
                .click('#next')
                .getText('.content')
                .then((innerText) => {
                    chai.expect('ua page').to.be.equal(innerText);
                })
                // первый заход ломаем все запросы на mc.yandex.ru
                .then(
                    e2eUtils.provideServerHelpers(this.browser, {
                        cb(serverHelpers, options) {
                            serverHelpers.addRule(
                                {
                                    regex: `/watch/${options.counterId}`,
                                    count: 2,
                                    status: '500',
                                },
                                function () {
                                    serverHelpers.collectRequests(1000);
                                    new Ya.Metrika2({
                                        id: options.counterId,
                                    });
                                },
                            );
                        },
                        counterId,
                    }),
                )
                .then(e2eUtils.handleRequest(this.browser))
                .then(({ value: requests }) => {
                    const altDomainRequests = requests.filter((req) => {
                        return req.headers['x-host'] === 'mc.webvisor.org';
                    });
                    chai.expect(altDomainRequests).to.have.lengthOf(2);
                    const [syncRequest, hitRequest] = altDomainRequests;
                    chai.expect(syncRequest.url).to.include(
                        'sync_cookie_image_check',
                    );
                    chai.expect(hitRequest.url).to.include(
                        `watch/${counterId}`,
                    );
                })
                // убеждаемся что стейт сохранен
                .execute(function () {
                    return document.cookie;
                })
                .then(({ value: cookie }) => {
                    const { _ym_hostIndex: hostIndex } =
                        e2eUtils.parseCookie(cookie);
                    chai.expect(hostIndex).to.be.eq('0-1,1-0');
                })
                .refresh(true)
                // снова ломаем запросы на mc.yandex.ru
                .then(
                    e2eUtils.provideServerHelpers(this.browser, {
                        cb(serverHelpers, options) {
                            serverHelpers.addRule(
                                {
                                    regex: `/watch/${options.counterId}`,
                                    count: 2,
                                    status: '500',
                                },
                                function () {
                                    serverHelpers.collectRequests(1000);
                                    new Ya.Metrika2({
                                        id: options.counterId,
                                    });
                                },
                            );
                        },
                        counterId,
                    }),
                )
                .then(e2eUtils.handleRequest(this.browser))
                .then(({ value: requests }) => {
                    const altDomainRequests = requests.filter((req) => {
                        return req.headers['x-host'] === 'mc.webvisor.org';
                    });
                    chai.expect(altDomainRequests).to.have.lengthOf(1);
                })
                // стейт догнался
                .execute(function () {
                    return document.cookie;
                })
                .then(({ value: cookie }) => {
                    const { _ym_hostIndex: hostIndex } =
                        e2eUtils.parseCookie(cookie);
                    chai.expect(hostIndex).to.be.eq('0-2,1-0');
                })
                .refresh(true)
                // теперь запросы должны сразу идти на mc.webvisor.org
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
                .then(({ value: requests }) => {
                    const altDomainRequests = requests.filter((req) => {
                        return req.headers['x-host'] === 'mc.webvisor.org';
                    });
                    chai.expect(altDomainRequests).to.have.lengthOf(1);
                })
                .execute(function () {
                    return document.cookie;
                })
                .then(({ value: cookie }) => {
                    const { _ym_hostIndex: hostIndex } =
                        e2eUtils.parseCookie(cookie);
                    chai.expect(hostIndex).to.be.eq('0-2,1-0');
                })
        );
    });
});
