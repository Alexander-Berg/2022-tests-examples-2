const chai = require('chai');
const e2eUtils = require('../../utils');

describe('phone changer test', () => {
    const baseUrl = `${e2eUtils.baseUrl}/test/phoneChanger/phoneChanger.hbs`;
    const counterId = 2630256622;

    beforeEach(function () {
        return this.browser.timeoutsAsyncScript(10000);
    });
    afterEach(function () {
        return this.browser.deleteCookie();
    });
    it('check the page', function () {
        return this.browser
            .url(baseUrl)
            .getText('body')
            .then((innerText) => {
                chai.expect(
                    innerText.includes('phoneChanger'),
                    'check if page contains required text',
                ).to.be.true;
            });
    });

    it('do not change phones w/o settings', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        serverHelpers.addRule({
                            regex: `/watch/${options.counterId}`,
                            body: {
                                settings: {
                                    eu: 0,
                                },
                            },
                        });
                        new Ya.Metrika2({
                            id: options.counterId,
                        });
                        setTimeout(function () {
                            done();
                        }, 500);
                    },
                    counterId,
                }),
            )
            .getText('.phone1')
            .then((text) => {
                chai.expect(text).to.be.equal('+7 (222) 333-44-55');
            });
    });

    it('changes phones when settings are provided', function () {
        const url = baseUrl;
        return this.browser
            .url(url)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb: function onExec(serverHelpers, options, done) {
                        serverHelpers.addRule(
                            {
                                regex: `/watch/${options.counterId}`,
                                body: {
                                    settings: {
                                        phchange: {
                                            clientId: '1111',
                                            orderId: '2222',
                                            service_id: 1,
                                            phones: [
                                                [
                                                    '+72223334455',
                                                    '+01112223344',
                                                ],
                                            ],
                                        },
                                    },
                                },
                            },
                            function () {
                                const firstPhone =
                                    document.querySelector('.phone1');
                                new Ya.Metrika2({
                                    id: options.counterId,
                                });

                                setTimeout(function () {
                                    const phones = [firstPhone.textContent];
                                    done(phones);
                                }, 500);
                            },
                        );
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then((request) => {
                chai.expect(request.value).to.deep.equal([
                    '+0 (111) 222-33-44',
                ]);
            });
    });

    it('check if logging works', function () {
        const url = baseUrl;
        return this.browser
            .url(url)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb: function onExec(serverHelpers, options) {
                        serverHelpers.addRule(
                            {
                                regex: `/watch/${options.counterId}`,
                                body: {
                                    settings: {
                                        phchange: {
                                            clientId: '1111',
                                            orderId: '2222',
                                            service_id: 1,
                                            phones: [
                                                [
                                                    '+72223334455',
                                                    '+01112223344',
                                                ],
                                            ],
                                        },
                                    },
                                },
                            },
                            function () {
                                serverHelpers.collectRequests(2000);
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
                const logRequest = requests
                    .map(e2eUtils.getRequestParams)
                    .find(
                        (request) =>
                            request.url.includes(`/watch/${counterId}/1`) &&
                            request.siteInfo,
                    );
                chai.expect(logRequest).not.null;
                const phoneChangeData = logRequest.siteInfo.__ym.phc;
                chai.expect(phoneChangeData.clientId).to.equal('1111');
                chai.expect(phoneChangeData.orderId).to.equal('2222');
                chai.expect(phoneChangeData.service_id).to.equal(1);
                chai.expect(phoneChangeData.phones).to.deep.equal({
                    '+72223334455': { '+01112223344': 1 },
                });
            });
    });

    it('check if we change phones while DOM changes', function () {
        const url = baseUrl;
        return this.browser
            .url(url)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb: function onExec(serverHelpers, options, done) {
                        serverHelpers.addRule(
                            {
                                regex: `/watch/${options.counterId}`,
                                body: {
                                    settings: {
                                        phchange: {
                                            clientId: '1111',
                                            orderId: '2222',
                                            service_id: 1,
                                            phones: [
                                                [
                                                    '+72223334455',
                                                    '+01112223344',
                                                ],
                                                [
                                                    '+81113334455',
                                                    '+11112223344',
                                                ],
                                            ],
                                        },
                                    },
                                },
                            },
                            function () {
                                new Ya.Metrika2({
                                    id: options.counterId,
                                });
                                setTimeout(() => {
                                    const node = document.createElement('div');
                                    node.innerHTML = '+8 (111) 333-44-55';
                                    const firstPhone =
                                        document.querySelector('.phone1');
                                    firstPhone.parentNode.appendChild(node);
                                    setTimeout(function () {
                                        const phones = [
                                            firstPhone.textContent,
                                            node.textContent,
                                        ];
                                        done(phones);
                                    }, 1000);
                                }, 100);
                            },
                        );
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then((request) => {
                chai.expect(request.value).to.deep.equal([
                    '+0 (111) 222-33-44',
                    '+1 (111) 222-33-44',
                ]);
            });
    });

    it.skip('check if we log phone changed on DOM changes', function () {
        const url = baseUrl;
        return this.browser
            .url(url)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb: function onExec(serverHelpers, options) {
                        serverHelpers.addRule(
                            {
                                regex: `/watch/${options.counterId}`,
                                body: {
                                    settings: {
                                        phchange: {
                                            clientId: '1111',
                                            orderId: '2222',
                                            service_id: 1,
                                            phones: [
                                                ['72223334455', '01112223344'],
                                                ['72223334400', '11112223344'],
                                            ],
                                        },
                                    },
                                },
                            },
                            function () {
                                serverHelpers.collectRequests(2000);
                                new Ya.Metrika2({
                                    id: options.counterId,
                                });
                                setTimeout(() => {
                                    const node = document.createElement('div');
                                    node.innerHTML = '8-222-333-44-55';
                                    const bro =
                                        document.querySelector('.phone1');
                                    bro.parentNode.appendChild(node);
                                }, 500);
                            },
                        );
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const logRequests = requests
                    .map(e2eUtils.getRequestParams)
                    .filter(
                        (request) =>
                            request.url.includes(`/watch/${counterId}/1`) &&
                            request.siteInfo,
                    );
                chai.expect(logRequests.length).to.be.above(1);
                logRequests.forEach((request) => {
                    const phoneChangeData = request.siteInfo.__ym.phc;
                    chai.expect(phoneChangeData.clientId).to.equal('1111');
                    chai.expect(phoneChangeData.orderId).to.equal('2222');
                    chai.expect(phoneChangeData.service_id).to.equal(1);
                    chai.expect(phoneChangeData.phones).to.deep.equal({
                        72223334455: { '01112223344': 1 },
                        72223334400: { 11112223344: 0 },
                    });
                });
            });
    });
});
