const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('User Params e2e test', function () {
    const baseUrl = 'test/userParams/userParams.hbs';
    const counterId = 26302566;
    const dataToSend = { a: { b: 'c' } };
    const expectedData = { __ymu: { a: { b: 'c' } } };

    beforeEach(function () {
        return this.browser.deleteCookie().timeoutsAsyncScript(10000);
    });

    it('Should send user params correctly via constructor', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const parsedDataToSend = JSON.parse(
                            options.dataToSendStr,
                        );

                        new Ya.Metrika2({
                            id: options.counterId,
                            userParams: parsedDataToSend,
                        });

                        serverHelpers.collectRequests(
                            500,
                            done,
                            options.regexp.defaultRequestRegEx,
                        );
                    },
                    counterId,
                    dataToSendStr: JSON.stringify(dataToSend),
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const paramsRequests = requests
                    .map(e2eUtils.getRequestParams)
                    .filter(({ brInfo }) => brInfo.pa);

                chai.expect(paramsRequests.length).to.be.equal(1);

                const paramsRequest = paramsRequests[0];
                chai.expect(paramsRequest).to.be.ok;

                chai.expect(paramsRequest.siteInfo).to.deep.equal(expectedData);
            });
    });

    it('Should send user params correctly via method', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const counter = new Ya.Metrika2(options.counterId);
                        const parsedDataToSend = JSON.parse(
                            options.dataToSendStr,
                        );

                        counter.userParams(parsedDataToSend);

                        serverHelpers.collectRequests(
                            500,
                            done,
                            options.regexp.defaultRequestRegEx,
                        );
                    },
                    counterId,
                    dataToSendStr: JSON.stringify(dataToSend),
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
