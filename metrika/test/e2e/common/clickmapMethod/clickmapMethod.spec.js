const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Clickmap Method e2e test', function () {
    const baseUrl = `${e2eUtils.baseUrl}/test/clickmapMethod/clickmapMethod.hbs`;
    const counterId = 26302566;

    beforeEach(function () {
        return this.browser.timeoutsAsyncScript(10000);
    });

    it('should track ?', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        serverHelpers.collectRequests(
                            200,
                            done,
                            options.regexp.clickmapRequestRegEx,
                        );
                        new Ya.Metrika2({
                            id: options.counterId,
                        });
                        document.querySelector('#button').click();
                    },
                    clickmapRequestRegEx: e2eUtils.clickmapRequestRegEx,
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                chai.expect(requests.length).to.be.equal(0);
            })
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        serverHelpers.collectRequests(
                            200,
                            done,
                            options.regexp.clickmapRequestRegEx,
                        );
                        Ya._metrika.counter.clickmap(true);
                        document.querySelector('#button').click();
                    },
                    clickmapRequestRegEx: e2eUtils.clickmapRequestRegEx,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                chai.expect(requests.length).to.be.equal(1);
            })
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        serverHelpers.collectRequests(
                            200,
                            done,
                            options.regexp.clickmapRequestRegEx,
                        );
                        Ya._metrika.counter.clickmap(false);
                        document.querySelector('#button').click();
                    },
                    clickmapRequestRegEx: e2eUtils.clickmapRequestRegEx,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                chai.expect(requests.length).to.be.equal(0);
            });
    });
});
