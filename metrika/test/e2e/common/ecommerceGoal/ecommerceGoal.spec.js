const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Ecommerce auto goals', function () {
    const baseUrl = `${e2eUtils.baseUrl}/test/ecommerceGoal/ecommerceGoal.hbs`;
    const counterId = 12092382;
    this.beforeEach(function () {
        return this.browser
            .url(baseUrl)
            .timeoutsAsyncScript(3000)
            .getText('body')
            .then((innerText) => {
                chai.expect(innerText).to.be.equal('Ecommerce goal');
            });
    });
    it('handles fb track only once if ecommerce enabled', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.addRule(
                            {
                                regex: `/watch/${options.counterId}`,
                                body: {
                                    settings: {
                                        auto_goals: 1,
                                    },
                                },
                                count: 1,
                            },
                            function () {
                                window.fbq = function () {};
                                new Ya.Metrika2({
                                    id: options.counterId,
                                    ecommerce: 'dataLayer',
                                });
                                setTimeout(() => {
                                    window.fbq('track', 'AddToCart');
                                    window.fbq('track', 'Lead');
                                }, 500);
                                window.fbq.callMethod = function () {};
                            },
                        );
                        serverHelpers.collectRequests(
                            1000,
                            null,
                            options.regexp.defaultRequestRegEx,
                        );
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: request }) => {
                chai.expect(request).to.be.lengthOf(2);
                const [, goal] = request.map(e2eUtils.getRequestParams);
                const parsedUrl = new URL(`${e2eUtils.baseUrl}`);
                chai.expect(goal.params['page-url']).to.be.eq(
                    `autogoal://${parsedUrl.hostname}/ym-submit-lead-0`,
                );
            });
    });
    it('handles dataLayer changes', function () {
        this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.addRule(
                            {
                                regex: `/watch/${options.counterId}`,
                                body: {
                                    settings: {
                                        auto_goals: 1,
                                    },
                                },
                                count: 1,
                            },
                            function () {
                                new Ya.Metrika2({
                                    id: options.counterId,
                                });
                                window.dataLayer = [];
                                function pushEvent() {
                                    // eslint-disable-next-line prefer-rest-params
                                    window.dataLayer.push(arguments);
                                }
                                pushEvent('event', 'begin_checkout');
                            },
                        );
                        serverHelpers.collectRequests(
                            1000,
                            null,
                            options.regexp.defaultRequestRegEx,
                        );
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: request }) => {
                chai.expect(request).to.be.lengthOf(2);
                const [, goal] = request.map(e2eUtils.getRequestParams);
                const parsedUrl = new URL(`${e2eUtils.baseUrl}`);
                chai.expect(goal.params['page-url']).to.be.eq(
                    `autogoal://${parsedUrl.hostname}/ym-begin-checkout-2`,
                );
            });
    });
});
