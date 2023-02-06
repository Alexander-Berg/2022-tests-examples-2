const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Set User ID e2e test', function () {
    const baseUrl = 'test/setUserID/setUserID.hbs';
    const counterId = 26302566;
    const userID = 1234;
    const expectedData = { __ym: { user_id: userID } };

    beforeEach(function () {
        return this.browser
            .deleteCookie()
            .timeoutsAsyncScript(10000)
            .url(baseUrl);
    });

    it('Should send user params correctly', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb: function onExec(serverHelpers, options, done) {
                        const counter = new Ya.Metrika2(options.counterId);
                        const requests = [];
                        counter.setUserID(options.userID);
                        serverHelpers.onRequest(function (request) {
                            requests.push(request);
                            if (requests.length === 2) {
                                done(requests);
                            }
                        }, options.regexp.defaultRequestRegEx);
                    },
                    counterId,
                    userID,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const paramsRequest = requests
                    .map(e2eUtils.getRequestParams)
                    .find(({ brInfo }) => brInfo.pa);
                chai.expect(paramsRequest).to.be.ok;
                chai.expect(paramsRequest.siteInfo).to.deep.equal(expectedData);
            });
    });
});
