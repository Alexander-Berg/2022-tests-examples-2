const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Optout e2e test', function () {
    const baseUrl = 'test/optout/optout.hbs';
    const testUrl = 'contacts';
    const counterId = 26302566;

    const testOptions = {
        counterId,
        testUrl,
    };

    beforeEach(function () {
        return this.browser.timeoutsAsyncScript(10000).url(baseUrl);
    });

    it("shouldn't initalize if window.disableYaCounter{counterID} is true", function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        window[`disableYaCounter${options.counterId}`] = true;
                        new Ya.Metrika2(options.counterId);

                        serverHelpers.collectRequests(200, null);
                    },
                    ...testOptions,
                }),
            )
            .then(({ value: requests }) => {
                chai.expect(requests).to.be.empty;
            });
    });

    it('should send http request with disabled optout', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        Ya._metrika.oo = false;
                        new Ya.Metrika2(options.counterId);

                        serverHelpers.collectRequests(200, null);
                    },
                    ...testOptions,
                }),
            )
            .then(({ value: requests }) => {
                chai.expect(requests).is.not.empty;
            });
    });

    it('should not send http request with enabled optout', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        Ya._metrika.oo = true;
                        new Ya.Metrika2(options.counterId);
                        serverHelpers.collectRequests(200, null);
                    },
                    ...testOptions,
                }),
            )
            .then(({ value: requests }) => {
                chai.expect(requests).is.empty;
            });
    });
});
