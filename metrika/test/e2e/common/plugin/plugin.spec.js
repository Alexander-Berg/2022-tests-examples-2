const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Plugin', function () {
    const baseUrl = 'test/plugin/main.hbs';
    const errorMessage =
        "didn't receive a response, perhaps counter didn't answer to the plugin's postMessage()?";
    const counterId = 123; // счетчик создается в plugin.hbs

    beforeEach(function () {
        return this.browser
            .deleteCookie()
            .timeoutsAsyncScript(10000)
            .url(baseUrl);
    });

    it('Should answer the request of the plugin', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        let id;

                        window.addEventListener('message', function (event) {
                            clearTimeout(id);
                            done(event.data);
                        });

                        document
                            .getElementById('iframe')
                            .contentWindow.postMessage(
                                '{"__yminfo": "__yminfo:1575966909600:1:0", "data": {"type": "pluginInfo", "hid": 1, "counterId": 1}}',
                                '*',
                            );

                        id = setTimeout(function () {
                            throw new Error(options.errorMessage);
                        }, 1500);
                    },
                    errorMessage,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value }) => {
                const parsedValue = JSON.parse(value);
                const { data } = parsedValue;
                const ymInfo = parsedValue.__yminfo;

                chai.expect(ymInfo).to.equal('__yminfo:1575966909600:1:1');
                chai.expect(data).to.be.an('array');

                data.sort((first, second) => {
                    return (
                        Object.keys(first).length - Object.keys(second).length
                    );
                });
                const defaultResponse = data[0];
                const featureResponse = data[1];

                chai.expect(
                    featureResponse,
                    'no counterId found, make sure the plugin feature is implemented',
                ).to.exist;
                chai.expect(defaultResponse.counterId).to.equal(
                    featureResponse.counterId,
                );
                chai.expect(defaultResponse.counterId).to.equal(counterId);

                const expectedData = {
                    counterId,
                    ldc: 'ok',
                    id: counterId,
                    defer: true,
                    type: '0',
                    nck: true,
                };
                chai.expect(featureResponse.counterId).to.equal(
                    expectedData.counterId,
                );
                chai.expect(featureResponse.ldc).to.equal(expectedData.ldc);
                chai.expect(featureResponse.id).to.equal(expectedData.id);
                chai.expect(featureResponse.defer).to.equal(expectedData.defer);
                chai.expect(featureResponse.type).to.equal(expectedData.type);
                chai.expect(featureResponse.nck).to.equal(expectedData.nck);
            });
    });
});
