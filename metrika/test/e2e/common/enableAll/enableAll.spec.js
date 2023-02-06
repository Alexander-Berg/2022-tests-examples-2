const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('enableAll e2e test', function () {
    const baseUrl = `${e2eUtils.baseUrl}/test/enableAll/enableAll.hbs`;
    const counterId = 26302566;

    const getTrackLinksReqs = (requests) =>
        requests.filter((request) => {
            const { params } = e2eUtils.getRequestParams(request);
            return (
                new RegExp(e2eUtils.REGEXPS.defaultRequestRegEx).test(
                    request.url,
                ) &&
                params['page-url'] === 'https://myrandomsitehost.ru/some-url'
            );
        });

    const getNotBounceReqs = (requests) =>
        requests.filter((request) => {
            const { params, brInfo } = e2eUtils.getRequestParams(request);

            console.log(
                'TEST',
                brInfo.nb,
                +brInfo.cl,
                brInfo.ar,
                baseUrl,
                params['page-url'],
            );

            return (
                brInfo.nb === '1' &&
                !Number.isNaN(+brInfo.cl) &&
                brInfo.ar === '1' &&
                baseUrl === params['page-url']
            );
        });

    const getClickmapReqs = (requests) =>
        requests.filter((request) => {
            return new RegExp(e2eUtils.REGEXPS.clickmapRequestRegEx).test(
                request.url,
            );
        });

    beforeEach(function () {
        return this.browser.timeoutsAsyncScript(25000);
    });

    it('should enable trackLinks, clickmap, notBounce', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        serverHelpers.collectRequests(200, done);
                        new Ya.Metrika2({
                            id: options.counterId,
                            clickmap: false,
                            trackLinks: false,
                        });
                        document.querySelector('#button').click();
                        document.querySelector('#link').click();
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const clickmapReqs = getClickmapReqs(requests);
                const linksReqs = getTrackLinksReqs(requests);
                const notBounceReqs = getNotBounceReqs(requests);

                chai.expect(clickmapReqs.length).to.be.equal(0);
                chai.expect(linksReqs.length).to.be.equal(0);
                chai.expect(notBounceReqs.length).to.be.equal(0);
            })
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const requests = [];
                        setTimeout(function () {
                            done(requests);
                        }, 17000);
                        serverHelpers.onRequest(function (request) {
                            requests.push(request);
                        });
                        Ya._metrika.counter.enableAll();
                        document.querySelector('#button').click();
                        document.querySelector('#link').click();
                    },
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const clickmapReqs = getClickmapReqs(requests);
                const linksReqs = getTrackLinksReqs(requests);
                const notBounceReqs = getNotBounceReqs(requests);

                chai.expect(clickmapReqs.length).to.be.equal(1);
                chai.expect(linksReqs.length).to.be.equal(1);
                chai.expect(notBounceReqs.length).to.be.equal(1);
            });
    });

    it('should enable trackLinks, clickmap, notBounce if the enableAll parameter is set', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        new Ya.Metrika2({
                            id: options.counterId,
                            enableAll: true,
                        });
                        done();
                    },
                    counterId,
                }),
            )
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const requests = [];
                        setTimeout(function () {
                            done(requests);
                        }, 17000);
                        serverHelpers.onRequest(function (request) {
                            requests.push(request);
                        });
                        document.querySelector('#button').click();
                        document.querySelector('#link').click();
                    },
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const clickmapReqs = getClickmapReqs(requests);
                const linksReqs = getTrackLinksReqs(requests);
                const notBounceReqs = getNotBounceReqs(requests);

                chai.expect(clickmapReqs.length).to.be.equal(1);
                chai.expect(linksReqs.length).to.be.equal(1);
                chai.expect(notBounceReqs.length).to.be.equal(1);
            });
    });
});
