const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Hid e2e test', function () {
    const baseUrl = 'test/hid/hid.hbs';
    const counterId1 = 26302566;
    const counterId2 = 51903872;

    beforeEach(function () {
        return this.browser.deleteCookie().timeoutsAsyncScript(10000);
    });

    it('should send equal hids', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const counters = {};

                        new Ya.Metrika2({
                            id: options.counterId1,
                        });

                        new Ya.Metrika2({
                            id: options.counterId2,
                        });

                        serverHelpers.onRequest(function (request) {
                            const url = request.url.split('?')[0];
                            const counter = url.split('/').pop();

                            if (!counters[counter]) {
                                counters[counter] = request;
                            }

                            if (Object.keys(counters).length === 2) {
                                done(counters);
                            }
                        }, options.regexp.defaultRequestRegEx);
                    },
                    counterId1,
                    counterId2,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: counters }) => {
                const requestHid = {};

                Object.values(counters).forEach((request) => {
                    const { brInfo, counterId } =
                        e2eUtils.getRequestParams(request);

                    chai.expect(request.url).to.include('hid');
                    chai.expect(brInfo).to.include.any.keys('hid');
                    chai.expect(requestHid).to.not.have.any.keys(counterId);

                    requestHid[counterId] = brInfo.hid;
                });

                chai.expect(requestHid).to.have.any.keys(
                    String(counterId1),
                    String(counterId2),
                );

                chai.expect(requestHid[counterId1]).to.be.equal(
                    requestHid[counterId2],
                );
            });
    });
});
