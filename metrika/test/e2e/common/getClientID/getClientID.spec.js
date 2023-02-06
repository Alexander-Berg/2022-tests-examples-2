const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Get Client ID e2e test', function () {
    const baseUrl = 'test/getClientID/getClientID.hbs';
    const counterId = 26302566;
    const prefix = '_ym_';
    const firstUserID = '125364247324';
    const secondUserID = '2394324421122';

    beforeEach(function () {
        return this.browser
            .deleteCookie()
            .timeoutsAsyncScript(10000)
            .url(baseUrl);
    });

    it('Should return user id correctly', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb: function onExec(serverHelpers, options, done) {
                        document.cookie = `${options.prefix}uid=${options.firstUserID}`;

                        const counter = new Ya.Metrika2(options.counterId);
                        done(counter.getClientID());
                    },
                    counterId,
                    firstUserID,
                    prefix,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: uid }) => {
                chai.expect(uid).to.equal(firstUserID);
            });
    });

    it('Should return user id correctly if ldc is not "uid"', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb: function onExec(serverHelpers, options, done) {
                        const nonUidLdc = 'smth';
                        document.cookie = `${options.prefix}${nonUidLdc}=${options.secondUserID}`;

                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                            ldc: nonUidLdc,
                        });
                        done(counter.getClientID());
                    },
                    counterId,
                    secondUserID,
                    prefix,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: uid }) => {
                chai.expect(uid).to.equal(secondUserID);
            });
    });

    it('Should create user id if none was found in the cookies', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb: function onExec(serverHelpers, options, done) {
                        const counter = new Ya.Metrika2(options.counterId);
                        done(counter.getClientID());
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: uid }) => {
                chai.expect(uid).to.be.a('string');
            });
    });

    it(`doesn't log callback's error`, function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        serverHelpers.collectRequests(
                            500,
                            (requests) => {
                                done({
                                    requests,
                                    errors: getPageErrors(),
                                });
                            },
                            options.regexp.defaultRequestRegEx,
                        );
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                        });

                        counter.getClientID(() => {
                            throw new Error('user error');
                        });
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value }) => {
                chai.expect(value.requests.length).to.be.equal(1);
                chai.expect(value.errors.usual.length).to.be.equal(1);
                chai.expect(value.errors.unhandledrejection.length).to.be.equal(
                    0,
                );
                chai.expect(value.errors.usual[0]).to.include('user error');
            });
    });
});
