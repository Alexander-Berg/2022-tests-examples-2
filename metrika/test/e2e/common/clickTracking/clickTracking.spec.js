const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Click tracking test', function () {
    const baseUrl = 'test/clickTracking/clickTracking.hbs';

    const firstCounterId = 26302566;
    const secondCounterId = 123;
    const thirdCounterId = 26302567;

    beforeEach(function () {
        return this.browser.timeoutsAsyncScript(6000).deleteCookie();
    });

    const check = (requests, data, counter = firstCounterId) => {
        const btn = e2eUtils.querystring(data);
        chai.assert(
            e2eUtils.findHit(
                requests,
                counter,
                `${e2eUtils.buttonUrl}/?${btn}`,
            ),
            `no button: ${btn}`,
        );
    };
    const checkNo = (requests, data, counter = firstCounterId) => {
        const btn = e2eUtils.querystring(data);
        chai.assert(
            !e2eUtils.findHit(requests, counter, btn, false),
            `has button: ${btn}`,
        );
    };

    it('should send simple button click', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        serverHelpers.addRule(
                            [
                                {
                                    regex: `/watch/(${options.firstCounterId}|${options.thirdCounterId})`,
                                    count: 2,
                                    body: {
                                        settings: {
                                            button_goals: 1,
                                        },
                                    },
                                },
                                {
                                    regex: `/watch/${options.secondCounterId}`,
                                    count: 2,
                                    body: {
                                        settings: {
                                            button_goals: 0,
                                        },
                                    },
                                },
                            ],
                            function () {
                                window.requests = [];
                                serverHelpers.onRequest(function (request) {
                                    window.requests.push(request);
                                }, options.regexp.defaultRequestRegEx);
                                new Ya.Metrika2({
                                    id: options.firstCounterId,
                                });
                                new Ya.Metrika2({
                                    id: options.secondCounterId,
                                });
                                new Ya.Metrika2({
                                    id: options.thirdCounterId,
                                });
                                done(true);
                            },
                        );
                    },
                    firstCounterId,
                    secondCounterId,
                    thirdCounterId,
                }),
            )
            .click('#button_id')
            .click('#input_button_id')
            .click('#input_submit_id')
            .click('#input_reset_id')
            .click('#input_file_id')
            .click('#a_id')
            .click('#div_id')
            .pause(1000)
            .execute(function () {
                return window.requests;
            })
            .then(({ value: requests }) => {
                check(requests, { p: '?WA', i: 'button_id', c: 950681575 });
                checkNo(requests, { i: 'button_id' }, secondCounterId);
                check(
                    requests,
                    { p: '?WA', i: 'button_id', c: 950681575 },
                    thirdCounterId,
                );

                check(requests, { p: 'P', ty: 'button', c: 1294518684 });
                check(requests, { p: 'P1', ty: 'submit', c: 1310515648 });
                check(requests, { p: 'P2', ty: 'reset', c: 3395317463 });
                check(requests, { p: 'P3', ty: 'file', c: 2202730430 });
                check(requests, { p: ';', h: 2119416003, c: 843117986 });
                check(requests, { p: 'A1', i: 'div_id', c: 2875119458 });
            });
    });

    it('should send complex button click', function () {
        return this.browser
            .url(baseUrl)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        serverHelpers.addRule(
                            [
                                {
                                    regex: `/watch/(${options.firstCounterId}|${options.thirdCounterId})`,
                                    count: 2,
                                    body: {
                                        settings: {
                                            button_goals: 1,
                                        },
                                    },
                                },
                            ],
                            function () {
                                window.requests = [];
                                serverHelpers.onRequest(function (request) {
                                    window.requests.push(request);
                                }, options.regexp.defaultRequestRegEx);
                                new Ya.Metrika2({
                                    id: options.firstCounterId,
                                });
                                done(true);
                            },
                        );
                    },
                    firstCounterId,
                }),
            )
            .click('#button_inner_id')
            .click('#a_id_outer_2_div')
            .click('#a_id_outer_3_span')
            .click('#div_id_outer')
            .pause(1000)
            .execute(function () {
                return window.requests;
            })
            .then(({ value: requests }) => {
                check(requests, {
                    p: '?;1',
                    i: 'button_inner_id',
                    c: 3245688980,
                });
                checkNo(requests, { i: 'a_id_outer' });
                check(requests, { p: ';2' });
                check(requests, { p: ';3', c: 1282046021 });
                check(requests, { p: 'AA2', i: 'div_id_inner', c: 2875119458 });
                checkNo(requests, { i: 'div_id_outer' });
            });
    });
});
