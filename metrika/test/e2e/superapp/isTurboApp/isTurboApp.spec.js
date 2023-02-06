const chai = require('chai');
const e2eUtils = require('../../utils');

// METR-38254
describe.skip('isTurboApp brInfo flag', function () {
    const baseUrl = 'test/isTurboApp/isTurboApp.hbs';
    const counterId = 3;
    const validateRequest = (exists, { counterId: id, brInfo }) => {
        chai.expect(id, 'wrong counter id').to.eq(String(counterId));
        chai.expect(brInfo.ta, 'wrong brInfo').to.eq(exists ? '1' : undefined);
    };
    const turboAppPresent = validateRequest.bind(null, true);
    const turboAppMissing = validateRequest.bind(null, false);

    beforeEach(function () {
        return this.browser
            .deleteCookie()
            .timeoutsAsyncScript(3000)
            .url(baseUrl);
    });

    it('should set brInfo flag if window.yandex.app', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        window.yandex = {};
                        window.yandex.app = {};
                        serverHelpers.onRequest(
                            done,
                            options.regexp.defaultRequestRegEx,
                        );
                        new Ya.Metrika2(options.counterId);
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: rawRequest }) => {
                turboAppPresent(e2eUtils.getRequestParams(rawRequest));
            });
    });

    it('should not set brInfo flag if window.yandex.app is empty', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        window.yandex = null;
                        serverHelpers.onRequest(
                            done,
                            options.regexp.defaultRequestRegEx,
                        );
                        new Ya.Metrika2(options.counterId);
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: rawRequest }) => {
                turboAppMissing(e2eUtils.getRequestParams(rawRequest));
            });
    });
});
