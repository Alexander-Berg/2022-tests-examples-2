const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('jsonp transport', function () {
    const baseUrl = 'test/jsonp/jsonp.hbs';
    const counterId = 26302566;
    beforeEach(function () {
        return this.browser.deleteCookie().timeoutsAsyncScript(10000);
    });

    it('sends requests', function () {
        return (
            this.browser
                .url(baseUrl)
                .getText('body')
                .then((innerText) => {
                    chai.expect(innerText).to.be.equal('Jsonp page');
                })
                .then(
                    e2eUtils.provideServerHelpers(this.browser, {
                        cb(serverHelpers, options) {
                            localStorage.clear();
                            serverHelpers.addRule(
                                {
                                    regex: `wmode=7`,
                                    count: 3,
                                    status: '500',
                                },
                                function () {
                                    serverHelpers.collectRequests(
                                        500,
                                        null,
                                        options.regexp.defaultRequestRegEx,
                                    );
                                    new Ya.Metrika2(options.counterId);
                                },
                            );
                        },
                        counterId,
                    }),
                )
                .then(e2eUtils.handleRequest(this.browser))
                .then(({ value: rawRequests }) => {
                    const requests = rawRequests.reduce((accum, req) => {
                        const request = e2eUtils.getRequestParams(req);
                        if (request.params.wmode === '5') {
                            chai.expect(request.brInfo.pv).to.be.equal('1');
                            accum.push(request);
                        }
                        return accum;
                    }, []);
                    chai.expect(requests).to.lengthOf(1);
                })
                /* eslint-disable */
                .executeAsync((done) => {
                    var info;
                    // window['_ymjsp1'] = 1;
                    for (key in window)
                        if (window.hasOwnProperty(key)) {
                            info = key.match(/^_ymjsp/);
                            if (info) break;
                        }
                    done(info);
                })
                /* eslint-enable */
                .then(({ value: result }) => {
                    chai.expect(result).to.be.null;
                })
        );
    });
});
