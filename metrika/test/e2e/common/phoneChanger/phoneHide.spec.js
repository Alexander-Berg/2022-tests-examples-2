const chai = require('chai');
const e2eUtils = require('../../utils');

describe('phone hide test', () => {
    const baseUrl = `${e2eUtils.baseUrl}/test/phoneChanger/phoneHide.hbs`;
    const counterId = 2630256622;

    beforeEach(function () {
        return this.browser.timeoutsAsyncScript(10000);
    });
    afterEach(function () {
        return this.browser.deleteCookie();
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
            .getHTML('.phone1')
            .then((text) => {
                chai.expect(text).to.be.equal(
                    '<a class="phone1" href="tel:+7 (222) 333-44-55">+7 (222) 333-44-55</a>',
                );
            });
    });

    it('hide phones when settings are provided', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb: function onExec(serverHelpers, options, done) {
                        serverHelpers.addRule(
                            {
                                regex: `/watch/${options.counterId}`,
                                body: {
                                    settings: {
                                        phhide: ['+72223334455'],
                                    },
                                },
                            },
                            function () {
                                window.req = [];
                                serverHelpers.collectRequests(
                                    1000,
                                    (requests) => {
                                        window.req =
                                            window.req.concat(requests);
                                    },
                                    options.regexp.defaultRequestRegEx,
                                );

                                new Ya.Metrika2({
                                    id: options.counterId,
                                });
                                done();
                            },
                        );
                    },
                    counterId,
                }),
            )
            .pause(500)
            .moveToObject('.phone1', 0, 0)
            .pause(2000)
            .execute(function () {
                return {
                    reqs: window.req,
                };
            })
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: { reqs: requests } }) => {
                chai.expect(
                    requests.some((req) =>
                        req.url.includes('tel%3A72223334455'),
                    ),
                ).to.equal(true);
            });
    });

    it('check if we hide phones while DOM changes', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb: function onExec(serverHelpers, options, done) {
                        serverHelpers.addRule(
                            {
                                regex: `/watch/${options.counterId}`,
                                body: {
                                    settings: {
                                        phhide: ['81113334456'],
                                    },
                                },
                            },
                            function () {
                                window.req = [];
                                serverHelpers.collectRequests(
                                    1000,
                                    (requests) => {
                                        window.req =
                                            window.req.concat(requests);
                                    },
                                    options.regexp.defaultRequestRegEx,
                                );

                                new Ya.Metrika2({
                                    id: options.counterId,
                                });
                                setTimeout(() => {
                                    const node = document.createElement('a');
                                    node.href = 'tel:+8 (111) 333-44-56';
                                    node.innerHTML = '+8 (111) 333-44-56';
                                    node.className = 'phone2';

                                    const firstPhone =
                                        document.querySelector('.phone1');
                                    firstPhone.parentNode.appendChild(node);
                                }, 100);
                                done();
                            },
                        );
                    },
                    counterId,
                }),
            )
            .pause(500)
            .moveToObject('.phone2', 0, 0)
            .pause(2000)
            .execute(function () {
                return {
                    reqs: window.req,
                };
            })
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: { reqs: requests } }) => {
                chai.expect(
                    requests.some((req) =>
                        req.url.includes('tel%3A81113334456'),
                    ),
                ).to.equal(true);
            });
    });
});
