const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Incognito test', function () {
    const baseUrl = 'test/isPrivate/isPrivate.hbs';
    const counterId = 26302566;

    it('Incognito run', function () {
        const timeout = 4000;

        // ff
        this.browser.timeouts({
            script: timeout,
            implicit: timeout,
            pageLoad: timeout,
        });
        // chrome
        this.browser.timeoutsAsyncScript(timeout);

        return this.browser
            .url(`${e2eUtils.baseUrl}/${baseUrl}`)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const testUrl = 'testUrl';
                        serverHelpers.collectRequests(
                            1000,
                            done,
                            options.regexp.defaultRequestRegEx,
                        );
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                        });
                        setTimeout(() => {
                            counter.hit(testUrl);
                        }, 500);
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                chai.expect(requests).to.lengthOf(2);
                const hasPriFlag = requests.some((request) => {
                    const { brInfo } = e2eUtils.getRequestParams(request);
                    return brInfo.pri === '1';
                });
                chai.expect(hasPriFlag).to.eq(true);
            });
    });
});
