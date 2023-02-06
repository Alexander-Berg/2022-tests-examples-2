const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Retansmit test', function () {
    const baseUrl = 'test/retransmit/retransmit.hbs';
    const counterId = 26302566;

    beforeEach(function () {
        return this.browser
            .deleteCookie()
            .timeoutsAsyncScript(10000)
            .url(baseUrl)
            .executeAsync(function (done) {
                localStorage.clear();
                done();
            });
    });

    it('retransmits first webvisor', function () {
        return this.browser
            .url(`${e2eUtils.baseUrl}/test/retransmit/retransmit_webvisor1.hbs`)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        serverHelpers.addRule(
                            [
                                {
                                    regex: `/webvisor/${options.counterId}`,
                                    status: '500',
                                    count: 2,
                                },
                            ],
                            function () {
                                setTimeout(() => {
                                    done();
                                }, 2100);

                                new Ya.Metrika({
                                    webvisor: true,
                                    id: options.counterId,
                                });
                            },
                        );
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .refresh(true)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        new Ya.Metrika({
                            webvisor: true,
                            id: options.counterId + 1,
                        });

                        serverHelpers.collectRequestsForTime(1000, 'webvisor');
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value }) => {
                value.forEach((request) => {
                    const { params, url, brInfo } =
                        e2eUtils.getRequestParams(request);
                    chai.assert(url.endsWith(`/webvisor/${counterId}`));
                    chai.expect(params['wv-hit']).to.not.be.NaN;
                    chai.expect(brInfo.rqnl).to.equal('1');

                    // Чтобы отсечь первый запрос
                    if (params.wmode === '0') {
                        chai.expect(params['wv-type']).to.equal('0');
                    }
                });
            });
    });

    it.skip('retransmits publishers', function () {
        const url = `${e2eUtils.baseUrl}/test/publishers/microdata.hbs`;

        return this.browser
            .url(url)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        window.Uint8Array.prototype.slice = null;
                        serverHelpers.addRule(
                            [
                                {
                                    regex: `/watch/${options.counterId}`,
                                    body: {
                                        settings: {
                                            publisher: {
                                                schema: 'microdata',
                                            },
                                            pcs: '0',
                                            webvisor: {
                                                arch_type: 'html',
                                                date: '2017-05-18 13:54:43',
                                                recp: '1.00000',
                                            },
                                        },
                                    },
                                    count: 1,
                                },
                                {
                                    regex: `/webvisor/${options.counterId}`,
                                    status: '500',
                                    count: 2,
                                },
                            ],
                            function () {
                                setTimeout(() => {
                                    done();
                                }, 2100);

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
            .refresh(true)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        window.Uint8Array.prototype.slice = null;
                        serverHelpers.addRule(
                            {
                                regex: `/watch/${options.counterId}`,
                                body: {
                                    settings: {},
                                },
                                count: 1,
                            },
                            () => {
                                const urlParser = document.createElement('a');
                                serverHelpers.onRequest(function (request) {
                                    urlParser.href = request.url;
                                    if (/webvisor/.test(urlParser.pathname)) {
                                        done({
                                            requestInfo: request,
                                            lsInfo: localStorage.getItem(
                                                '_ym_retryReqs',
                                            ),
                                        });
                                    }
                                });

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
            .then(({ value: { requestInfo: request, lsInfo } }) => {
                let duplicates = false;
                let publisherHeader = null;
                let articleInfo = null;
                const { params, body, brInfo } =
                    e2eUtils.getRequestParams(request);
                chai.expect(JSON.parse(lsInfo)).to.be.an('object').that.is
                    .empty;

                body.forEach((value) => {
                    const record = value;
                    record.data = JSON.parse(record.data);
                    if (record.type === 'articleInfo') {
                        if (articleInfo) {
                            duplicates = true;
                        }
                        articleInfo = record;
                    } else if (record.type === 'publishersHeader') {
                        if (publisherHeader) {
                            duplicates = true;
                        }
                        publisherHeader = record;
                    }
                });

                chai.expect(brInfo.rqnl).to.equal('2');

                chai.expect(params['wv-hit']).to.not.be.NaN;
                chai.expect(params['wv-part']).to.not.be.NaN;
                chai.expect(params['wv-type']).to.not.be.NaN;
                chai.expect(duplicates).to.be.false;
                chai.expect(articleInfo.data.pageTitle).to.be.string;
                chai.expect(articleInfo.data.pageUrlCanonical).to.be.string;
                chai.expect(articleInfo.data.id > 0).to.be.true;
                chai.expect(publisherHeader.data.articleMeta.length).to.equal(
                    1,
                );
                chai.expect(publisherHeader.data.articleMeta[0].id).to.equal(
                    articleInfo.data.id,
                );
            });
    });

    it('retransmit page', function () {
        return this.browser.getText('.info').then((innerText) => {
            chai.expect('Bad retransmit page').to.be.equal(innerText);
        });
    });

    it('retransmit fail request', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.addRule(
                            {
                                regex: 'wmode=(7|5)',
                                count: 3,
                                status: '500',
                            },
                            function () {
                                serverHelpers.collectRequests(
                                    300,
                                    (_, done) => {
                                        const result = JSON.parse(
                                            localStorage.getItem(
                                                '_ym_retryReqs',
                                            ),
                                        );
                                        done(result);
                                    },
                                    options.regexp.defaultRequestRegEx,
                                );

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
            .then(({ value: result }) => {
                chai.expect(Object.keys(result).length).to.be.eq(1);
                return this.browser.pause(200).click('.nextPage');
            })
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        new Ya.Metrika2({
                            id: options.counterId,
                        });

                        new Ya.MetrikaDebug({
                            id: options.counterId + 1,
                        });

                        serverHelpers.collectRequests(
                            1000,
                            (requests) => {
                                done({
                                    requests,
                                    ls: localStorage.getItem('_ym_retryReqs'),
                                });
                            },
                            options.regexp.defaultRequestRegEx,
                        );
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: result }) => {
                chai.expect(JSON.parse(result.ls)).to.be.deep.equal({});
                chai.expect(result.requests.length).to.be.equal(3);
                const titles = result.requests.map((req) => {
                    const { brInfo } = e2eUtils.getRequestParams(req);
                    if (brInfo.t === 'Bad retransmit page title') {
                        chai.expect(brInfo.rqnl).to.be.equal('2');
                    }
                    return brInfo.t;
                });
                chai.expect(titles).includes('Bad retransmit page title');
                chai.expect(titles).includes('Good retransmit page title');
            });
    });
});
