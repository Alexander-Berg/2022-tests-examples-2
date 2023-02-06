const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Not Incognito test', function () {
    const baseUrl = 'test/isNotPrivate/isNotPrivate.hbs';
    const counterId = 26302566;

    it('Not Incognito run', function () {
        const timeout = 4000;

        // chrome
        this.browser.timeoutsAsyncScript(timeout);

        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        const testUrl = 'testUrl';
                        serverHelpers.collectRequests(
                            1000,
                            null,
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
                    return brInfo.pri === '0';
                });
                chai.expect(hasPriFlag).to.eq(false);
            });
    });
});
