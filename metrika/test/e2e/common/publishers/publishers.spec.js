const chai = require('chai');
const e2eUtils = require('../../utils');

describe('publishers test', () => {
    const baseUrl = 'test/publishers/';
    const jsonldUrl = `${baseUrl}jsonld.hbs`;
    const opengraphUrl = `${baseUrl}opengraph.hbs`;
    const microdataUrl = `${baseUrl}microdata.hbs`;
    const counterId = 26302567;

    beforeEach(function () {
        return this.browser.timeoutsAsyncScript(10000);
    });

    it('resend send article data after remove and add', function () {
        return this.browser
            .url(microdataUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        window.Uint8Array.prototype.slice = null;
                        serverHelpers.addRule(
                            {
                                regex: `/watch/(${options.counterId})`,
                                count: 1,
                                body: {
                                    settings: {
                                        publisher: {
                                            schema: options.schemaName,
                                        },
                                    },
                                },
                            },
                            function () {
                                window.r = [];
                                serverHelpers.onRequest((rq) => {
                                    window.r.push(rq);
                                    if (rq.url.match(/webvisor/)) {
                                        done(window.r);
                                    }
                                });
                                new Ya.Metrika2(options.counterId);
                            },
                        );
                    },
                    schemaName: 'microdata',
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .execute(() => {
                window.a = document.getElementById('article');
                window.a.parentNode.removeChild(window.a);
            })
            .pause(1000)
            .then(e2eUtils.handleRequest(this.browser))
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, opt, done) {
                        document.getElementById('parent').appendChild(window.a);
                        serverHelpers.onRequest((rq) => {
                            if (rq.url.match(/webvisor/)) {
                                done(window.r);
                            }
                        });
                    },
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const parsedRequests = requests
                    .map(e2eUtils.getRequestParams)
                    .filter((requestData) => requestData.url.match(/webvisor/));
                chai.expect(parsedRequests).to.be.lengthOf(2);
            });
    });

    it('send protobuf data', function () {
        return this.browser
            .url(microdataUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.addRule(
                            {
                                regex: `/watch/(${options.counterId})`,
                                count: 1,
                                body: {
                                    settings: {
                                        publisher: {
                                            schema: options.schemaName,
                                        },
                                    },
                                },
                            },
                            function () {
                                serverHelpers.collectRequests(
                                    3000,
                                    null,
                                    options.regexp.webvisorRequestRegEx,
                                );

                                new Ya.Metrika2({
                                    id: options.counterId,
                                });
                            },
                        );
                    },
                    schemaName: 'microdata',
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const parsedRequests = requests.map(e2eUtils.getRequestParams);

                chai.expect(parsedRequests.length).to.be.equal(1);
                const [{ articleInfo }, { publishersHeader }] =
                    parsedRequests[0].body;
                chai.expect(articleInfo.authors.length).to.be.equal(2);
                chai.expect(articleInfo.pageTitle).to.be.equal('How to drive');
                chai.expect(publishersHeader.involvedTime).to.be.gt(1);
                chai.expect(publishersHeader.articleMeta.length).to.be.equal(1);
                const [meta] = publishersHeader.articleMeta;
                chai.expect(meta.chars).to.be.equal(501);
            });
    });

    it('send json data', function () {
        return this.browser
            .url(microdataUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.addRule(
                            {
                                regex: `/watch/(${options.counterId})`,
                                count: 1,
                                body: {
                                    settings: {
                                        publisher: {
                                            schema: options.schemaName,
                                        },
                                    },
                                },
                            },
                            function () {
                                window.Blob = undefined;

                                serverHelpers.collectRequests(
                                    3000,
                                    null,
                                    options.regexp.webvisorRequestRegEx,
                                );

                                new Ya.Metrika2({
                                    id: options.counterId,
                                });
                            },
                        );
                    },
                    schemaName: 'microdata',
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const parsedRequests = requests.map(e2eUtils.getRequestParams);
                chai.expect(parsedRequests.length).to.equal(1);

                const [
                    { data: articleInfoData, type: articleInfoType },
                    { data: publishersHeaderData, type: publishersHeaderType },
                ] = parsedRequests[0].body;
                chai.expect(articleInfoType).to.equal('articleInfo');
                chai.expect(articleInfoData.authors.length).to.be.equal(2);
                chai.expect(articleInfoData.pageTitle).to.be.equal(
                    'How to drive',
                );
                chai.expect(publishersHeaderType).to.equal('publishersHeader');
                chai.expect(publishersHeaderData.involvedTime).to.be.gt(1);
                chai.expect(
                    publishersHeaderData.articleMeta.length,
                ).to.be.equal(1);
                const [meta] = publishersHeaderData.articleMeta;
                chai.expect(meta.chars).to.be.equal(501);
            });
    });

    it('send data with two counters', function () {
        return this.browser
            .url(microdataUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        window.Uint8Array.prototype.slice = null;
                        serverHelpers.addRule(
                            {
                                regex: `/watch/(${options.counterId + 1}|${
                                    options.counterId
                                })`,
                                count: 2,
                                body: {
                                    settings: {
                                        publisher: {
                                            schema: options.schemaName,
                                        },
                                        pcs: '0',
                                        webvisor: {
                                            arch_type: 'html',
                                            date: '2017-05-18 13:54:43',
                                            recp: '1.00000',
                                        },
                                    },
                                },
                            },
                            function () {
                                serverHelpers.collectRequests(
                                    3000,
                                    null,
                                    options.regexp.webvisorRequestRegEx,
                                );
                                new Ya.Metrika2({
                                    id: options.counterId,
                                });
                                new Ya.Metrika2({
                                    id: options.counterId + 1,
                                });
                            },
                        );
                    },
                    schemaName: 'microdata',
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const parsedRequests = requests.map(e2eUtils.getRequestParams);
                const message = 'должно быть два запроса от разных счётчиков';

                chai.expect(parsedRequests.length, message).to.be.equal(2);
                chai.expect(
                    parsedRequests.map((e) => e.counterId),
                    message,
                ).to.have.all.members([`${counterId}`, `${counterId + 1}`]);
            });
    });

    it('send article id from previous page', function () {
        return this.browser
            .url(jsonldUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.addRule(
                            {
                                regex: `/watch/(${options.counterId})`,
                                count: 1,
                                body: {
                                    settings: {
                                        publisher: {
                                            schema: 'json_ld',
                                        },
                                        pcs: '0',
                                        webvisor: {
                                            arch_type: 'html',
                                            date: '2017-05-18 13:54:43',
                                            recp: '1.00000',
                                        },
                                    },
                                },
                            },
                            function () {
                                serverHelpers.collectRequests(200);

                                new Ya.Metrika2({
                                    id: options.counterId,
                                    trackLinks: true,
                                });
                            },
                        );
                    },
                    counterId,
                }),
            )
            .click('.go')
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.addRule(
                            {
                                regex: `/watch/(${options.counterId})`,
                                count: 1,
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
                            },
                            function () {
                                serverHelpers.collectRequests(
                                    3000,
                                    null,
                                    options.regexp.webvisorRequestRegEx,
                                );

                                new Ya.Metrika2({
                                    id: options.counterId,
                                    trackLinks: true,
                                });
                            },
                        );
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const requestsCount = requests.length;

                chai.expect(
                    requestsCount,
                    'должны быть запросы паблишеров',
                ).to.greaterThan(0);

                let paiCounter = 0;
                requests.forEach((request) => {
                    const { brInfo } = e2eUtils.getRequestParams(request);
                    if (brInfo.pai) {
                        paiCounter += 1;
                    }
                });

                chai.expect(
                    paiCounter,
                    'pai должен быть в каждом запросе паблишеров',
                ).to.equal(requestsCount);
            });
    });

    // сохраняется в ls на счётчик
    it('article id from previous page is specific to counter', function () {
        return this.browser
            .url(jsonldUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.addRule(
                            {
                                regex: `/watch/(${options.counterId})`,
                                count: 1,
                                body: {
                                    settings: {
                                        publisher: {
                                            schema: 'json_ld',
                                        },
                                        pcs: '0',
                                        webvisor: {
                                            arch_type: 'html',
                                            date: '2017-05-18 13:54:43',
                                            recp: '1.00000',
                                        },
                                    },
                                },
                            },
                            function () {
                                serverHelpers.collectRequests(200);

                                new Ya.Metrika2({
                                    id: options.counterId,
                                    trackLinks: true,
                                });
                            },
                        );
                    },
                    counterId,
                }),
            )
            .click('.go')
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.addRule(
                            {
                                regex: `/watch/(${options.counterId})`,
                                count: 1,
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
                            },
                            function () {
                                serverHelpers.collectRequests(
                                    3000,
                                    null,
                                    options.regexp.webvisorRequestRegEx,
                                );

                                new Ya.Metrika2({
                                    id: options.counterId,
                                    trackLinks: true,
                                });
                            },
                        );
                    },
                    counterId: counterId + 1,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const hasPai = requests.some(
                    (request) => e2eUtils.getRequestParams(request).brInfo.pai,
                );

                chai.expect(
                    requests.length,
                    'должны быть запросы паблишеров',
                ).to.greaterThan(0);
                chai.expect(
                    hasPai,
                    // потому что другой счётчик
                    'в запросах паблишеров не должно быть параметра pai',
                ).to.be.false;
            });
    });

    const testSchema = (browser, url, schemaName) => {
        return browser
            .url(url)
            .then(
                e2eUtils.provideServerHelpers(browser, {
                    cb(serverHelpers, options, done) {
                        window.Uint8Array.prototype.slice = null;
                        serverHelpers.addRule(
                            {
                                regex: `/watch/${options.counterId}`,
                                body: {
                                    settings: {
                                        publisher: {
                                            schema: options.schemaName,
                                        },
                                        pcs: '0',
                                        webvisor: {
                                            arch_type: 'html',
                                            date: '2017-05-18 13:54:43',
                                            recp: '1.00000',
                                        },
                                    },
                                },
                            },
                            function () {
                                const urlParser = document.createElement('a');
                                serverHelpers.onRequest(function (request) {
                                    urlParser.href = request.url;
                                    if (
                                        urlParser.pathname ===
                                        `/webvisor/${options.counterId}`
                                    ) {
                                        done(request);
                                    }
                                });

                                new Ya.Metrika2({
                                    id: options.counterId,
                                });
                            },
                        );
                    },
                    schemaName,
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(browser))
            .then((request) => {
                let duplicates = false;
                let publisherHeader = null;
                let articleInfo = null;
                const { params, body } = e2eUtils.getRequestParams(
                    request.value,
                );
                body.forEach((value) => {
                    const record = value;
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
    };

    it('Parses and sends jsonld schema', function () {
        return testSchema(this.browser, jsonldUrl, 'json_ld');
    });

    it('Parses and sends microdata schema', function () {
        return testSchema(this.browser, microdataUrl, 'microdata');
    });

    it('Parses and sends opengraph schema', function () {
        return testSchema(this.browser, opengraphUrl, 'opengraph');
    });
});
