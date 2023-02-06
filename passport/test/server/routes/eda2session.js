var expect = require('expect.js');
var sinon = require('sinon');
var url = require('url');

var data = require('../../util/mock/mockData.js');
var b = data.basic;
var headers = data.headers;

var trackID = b.trackID;

describe('eda2session', function() {
    beforeEach(function(done) {
        this.eda2session = require('../../../routes/eda2session.js');
        this.api = require('../../../lib/passport-api/index.js');
        var req = (this.req = {});

        req.headers = headers;
        req.hostname = headers['host'];
        req.nquery = {
            retpath: b.retpathUrl
        };
        req.body = {};
        req._controller = {
            augmentResponse: sinon.spy()
        };

        this.res = {
            redirect: sinon.spy(),
            track_id: trackID
        };

        this.next = sinon.spy();

        this.api
            .client({
                headers: headers,
                track_id: trackID,
                language: 'ru',
                logID: 'ael3ai7acha6be4aethaL8faihieseex'
            })
            .then(function(a) {
                req.api = a;
                done();
            });
    });

    describe('doMigration', function() {
        beforeEach(function() {
            this.finishRetpath = url.format({
                protocol: headers['x-real-scheme'],
                hostname: headers['host'],
                pathname: '/auth/finish/',
                query: {
                    track_id: trackID
                }
            });

            this.authSubmit = sinon.stub(this.req.api, 'authSubmit').callsFake(function() {
                return {
                    done: function(func) {
                        func({
                            body: {
                                track_id: trackID,
                                account: {},
                                cookies: 'cookies'
                            }
                        });
                    }
                };
            });
        });

        it('receives retpath as argument', function() {
            this.eda2session.doMigration('otherRetpath')(this.req, this.res);

            expect(
                this.authSubmit.calledWithExactly('/1/bundle/auth/migrate_pdd/', {retpath: 'otherRetpath'})
            ).to.be.ok();
        });

        it('takes retpath from request if argument was not set', function() {
            this.eda2session.doMigration()(this.req, this.res);

            expect(
                this.authSubmit.calledWithExactly('/1/bundle/auth/migrate_pdd/', {retpath: b.retpathUrl})
            ).to.be.ok();
        });

        it('return middleware that redirects to /auth/finish/ if all is ok and cookies were set', function() {
            this.eda2session.doMigration()(this.req, this.res);

            expect(this.res.redirect.calledWithExactly(this.finishRetpath)).to.be.ok();
        });

        it('return middleware that set cookies if all is ok and backend returned cookies', function() {
            this.eda2session.doMigration()(this.req, this.res);

            expect(this.req._controller.augmentResponse.called).to.be(true);
        });

        it(
            'return middleware that set redirects to retpath if backend did not ' +
                'return cookies but returned retpath',
            function() {
                this.authSubmit.restore();
                this.authSubmit = sinon.stub(this.req.api, 'authSubmit').callsFake(function() {
                    return {
                        done: function(func) {
                            func({
                                body: {
                                    retpath: b.retpathUrl
                                }
                            });
                        }
                    };
                });

                this.eda2session.doMigration()(this.req, this.res);
                expect(this.res.redirect.calledWithExactly(b.retpathUrl)).to.be.ok();
            }
        );

        it('return middleware that calls next() if backend returns error', function() {
            this.authSubmit.restore();
            this.authSubmit = sinon.stub(this.req.api, 'authSubmit').callsFake(function() {
                return {
                    done: function(func, error) {
                        error(new Error());
                    }
                };
            });

            this.eda2session.doMigration()(this.req, this.res, this.next);

            expect(this.next.called).to.be.ok();
        });

        it('return middleware that calls next() if backend returns ok, but no cookies or retpath', function() {
            this.authSubmit.restore();
            this.authSubmit = sinon.stub(this.req.api, 'authSubmit').callsFake(function() {
                return {
                    done: function(func) {
                        func({
                            body: {
                                status: 'ok'
                            }
                        });
                    }
                };
            });

            this.eda2session.doMigration()(this.req, this.res, this.next);

            expect(this.next.called).to.be.ok();
        });
    });

    describe('redirectToAuthIfError', function() {
        beforeEach(function() {
            this.authRetpath = url.format({
                protocol: headers['x-real-scheme'],
                hostname: headers['host'],
                pathname: '/auth/',
                query: {
                    retpath: b.retpathUrl
                }
            });
        });

        it('redirects to /auth/', function() {
            this.eda2session.redirectToAuthIfError(new Error(), this.req, this.res, this.next);

            expect(this.res.redirect.called).to.be.ok();
        });

        it('redirects to /auth/ with received retpath', function() {
            this.eda2session.redirectToAuthIfError(new Error(), this.req, this.res, this.next);

            expect(this.res.redirect.calledWithExactly(this.authRetpath)).to.be.ok();
        });
    });
});
