const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Destruct test', function () {
    const baseUrl = 'test/destruct/destruct.hbs';
    const counterId = '1';
    const secondCounterId = '2';
    const testGoal = 'TEST_GOAL';
    const testExperements = 'TEST_EXPERIMENT';
    const testHitUrl = 'contacts';
    const testAddFileExtension = 'fileExtension';
    const testParams = {
        someParam: 'someVal',
        someNumber: 12323,
        someObj: {
            someList: [1, 23, '', null],
        },
    };

    beforeEach(function () {
        return this.browser.timeoutsAsyncScript(10000).deleteCookie();
    });

    it('shouldnt send requests or call methods after counter destruction', function () {
        return this.browser
            .url(baseUrl)
            .getText('body')
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                        });

                        counter.destruct();

                        counter.reachGoal(options.testGoal);
                        counter.params(options.testParams);
                        counter.experiments(options.testExperements);
                        counter.notBounce();
                        counter.extLink('http://randomdomain.com', {
                            title: 'Random link click',
                        });
                        counter.addFileExtension(options.testAddFileExtension);
                        counter.file();
                        counter.hit(options.testHitUrl);

                        document
                            .querySelector('#file-with-user-extension-link')
                            .click();
                        counter.addFileExtension('zhopeg');
                        document.querySelector('#file-link').click();
                        document.querySelector('#file-ext-link').click();
                        document
                            .querySelector('#file-with-user-extension-link')
                            .click();
                        document.querySelector('#ext-link').click();

                        serverHelpers.collectRequests(
                            200,
                            null,
                            options.regexp.defaultRequestRegEx,
                        );
                    },
                    counterId,
                    testGoal,
                    testParams,
                    testAddFileExtension,
                    testExperements,
                    testHitUrl,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                chai.expect(requests.length).to.be.equal(1);
            });
    });
    it('shouldnt send hit request after counter destruction', function () {
        return this.browser
            .url(baseUrl)
            .getText('body')
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                            accurateTrackBounce: 500,
                        });

                        counter.destruct();

                        serverHelpers.collectRequests(
                            200,
                            null,
                            options.regexp.defaultRequestRegEx,
                        );
                    },
                    counterId,
                }),
            )
            .then(({ value: requests }) => {
                chai.expect(requests.length).to.be.deep.equal(1);
            });
    });
    it("shouldn't send formvisor/webvisor2 events after destruct", function () {
        return this.browser
            .url(baseUrl)
            .getText('body')
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                            webvisor: true,
                        });
                        setTimeout(function () {
                            counter.destruct();
                        }, 500);
                        setTimeout(function () {
                            setTimeout(function () {
                                document.querySelector('#myButton').click();
                            }, 100);
                            serverHelpers.collectRequests(
                                1000,
                                null,
                                options.regexp.webvisorRequestRegEx,
                            );
                        }, 8000);
                    },
                    counterId,
                }),
            )
            .then(({ value: requests }) => {
                chai.expect(requests.length).to.be.equal(0);
            });
    });
    it('should remove counter from the metrika namespace', function () {
        return this.browser
            .url(baseUrl)
            .getText('body')
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                        });

                        counter.destruct();

                        setTimeout(function () {
                            done(window.Ya._metrika.counters);
                        }, 1000);
                    },
                    counterId,
                }),
            )
            .then(({ value: counters }) => {
                chai.expect(counters).to.be.deep.equal({});
            });
    });
    it('should not send request after destruct and extLink, file click', function () {
        return this.browser
            .url(baseUrl)
            .getText('body')
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                        });

                        counter.destruct();
                        serverHelpers.collectRequests(
                            200,
                            null,
                            options.regexp.defaultRequestRegEx,
                        );
                    },
                    counterId,
                }),
            )
            .then(({ value: requests }) => {
                chai.expect(requests.length).to.be.equal(1);
            });
    });
    it('shouldnt send requests for dataLayer pushes after counter destruction', function () {
        return this.browser
            .url(baseUrl)
            .getText('body')
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        window.dataLayer = [];

                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                            ecommerce: 'dataLayer',
                        });

                        counter.destruct();

                        window.dataLayer.push({ ecommerce: { remove: 1 } });
                        serverHelpers.collectRequests(
                            200,
                            null,
                            options.regexp.defaultRequestRegEx,
                        );
                    },
                    counterId,
                }),
            )
            .then(({ value: requests }) => {
                chai.expect(requests.length).to.be.deep.equal(1);
            });
    });
    it('should send request only second counter', function () {
        return this.browser
            .url(baseUrl)
            .getText('body')
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                        });
                        const counter2 = new Ya.Metrika2({
                            id: options.secondCounterId,
                        });

                        counter.destruct();

                        counter.params(options.testParams);
                        counter2.params(options.testParams);

                        serverHelpers.collectRequests(
                            200,
                            null,
                            options.regexp.defaultRequestRegEx,
                        );
                    },
                    counterId,
                    secondCounterId,
                    testParams,
                }),
            )
            .then(({ value: requests }) => {
                chai.expect(requests.length).to.be.deep.equal(3);
            });
    });
    it(`shouldn't send request first counter after first counter destruction and initialized counter with same id and other type`, function () {
        return this.browser
            .url(baseUrl)
            .getText('body')
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                        });
                        const counter2 = new Ya.Metrika2({
                            id: options.counterId,
                            type: options.counterId,
                        });

                        counter.destruct();

                        counter.params(options.testParams);
                        counter2.params(options.testParams);

                        serverHelpers.collectRequests(
                            200,
                            null,
                            options.regexp.defaultRequestRegEx,
                        );
                    },
                    counterId,
                    testParams,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const request = requests[2];
                const { params } = e2eUtils.getRequestParams(request);

                chai.expect(params['cnt-class']).to.be.equal(counterId);
                chai.expect(requests.length).to.be.deep.equal(3);
            });
    });
});
