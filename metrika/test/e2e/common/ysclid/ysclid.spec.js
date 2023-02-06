const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe.skip('yscid', function () {
    const testParams = 'test=1';
    const ysclidParams = 'ysclid=1111';
    const baseUrl = `test/ysclid/ysclid.hbs?${testParams}&${ysclidParams}`;
    const counterId = 26302566;

    beforeEach(function () {
        return this.browser.deleteCookie().timeoutsAsyncScript(10000);
    });

    it('replace yscid param', function () {
        return this.browser
            .url(`${e2eUtils.baseUrl}/${baseUrl}`)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                        });

                        setTimeout(() => {
                            serverHelpers.onRequest(
                                done,
                                options.regexp.defaultRequestRegEx,
                            );
                            counter.hit(`/${window.location.search}`);
                        }, 500);
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: request }) => {
                chai.expect(request.url).to.be.ok;
                const { params } = e2eUtils.getRequestParams(request);
                chai.expect(params['page-url']).to.not.includes(ysclidParams);
                chai.expect(params['page-url']).to.includes(testParams);
            });
    });
});
