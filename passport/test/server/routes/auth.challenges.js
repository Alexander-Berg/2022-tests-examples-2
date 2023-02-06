var expect = require('expect.js');
var sinon = require('sinon');
var url = require('url');
var when = require('when');

var data = require('../../util/mock/mockData.js');
var b = data.basic;
var headers = data.headers;

var trackID = b.trackID;

describe('auth_challenges', function() {
    beforeEach(function(done) {
        this.auth_challenges = require('../../../routes/auth.challenges');
        this.api = require('../../../lib/passport-api/index.js');
        var req = (this.req = {});

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

    describe('initChallenges', function() {
        beforeEach(function() {
            var req = this.req;

            req.headers = headers;
            req.hostname = headers['host'];
            req.nquery = {
                track_id: trackID
            };
            req.body = {};

            this.res = {
                redirect: sinon.spy(),
                append: sinon.spy(),
                track_id: trackID
            };

            this.res.locals = {
                challenges: {
                    default: 'phone',
                    enabled_challenges: {},
                    phone_hint: 'Введите телефон',
                    email_hint: 'Введите email'
                },
                track_id: trackID
            };

            this.authRetpath = url.format({
                protocol: headers['x-real-scheme'],
                hostname: headers['host'],
                pathname: '/auth/'
            });

            this.next = sinon.spy();

            this.challengesSubmit = sinon.stub(this.req.api, 'challengesSubmit').returns(
                when.resolve({
                    body: {
                        challenges_enabled: {},
                        default_challenge: 'phone',
                        track_id: trackID
                    }
                })
            );
            this.challengesSubmit.catch = sinon.spy();
        });

        it('redirects to "/auth" if track_id is undefined', function() {
            this.req.nquery.track_id = '';
            this.auth_challenges.initChallenges(this.req, this.res, this.next);
            expect(this.res.redirect.calledWith(this.authRetpath)).to.be.ok();
        });

        it('sets res.locals.challenges if backend returns challenge data', function() {
            this.auth_challenges.initChallenges(this.req, this.res, this.next);
            expect(this.res.locals.challenges).to.not.be.empty();
            this.challengesSubmit.restore();
        });

        it('sets res.locals.track_id if backend returns challenge data', function() {
            this.auth_challenges.initChallenges(this.req, this.res, this.next);
            expect(this.res.locals.track_id).to.not.be.empty();
            this.challengesSubmit.restore();
        });

        it('should call processError function when fails', function() {
            var that = this;

            expect(function() {
                that.auth_challenges.initChallenges(this.req, this.res, this.next);
            }).to.throwError(function(e) {
                expect(function() {
                    that.auth_challenges.processError.calledWith(e, this.req, this.res).to.be.ok();
                });
            });
        });
    });

    describe('processError', function() {
        beforeEach(function() {
            var req = this.req;

            req.headers = headers;
            req.hostname = headers['host'];
            req.nquery = {
                track_id: trackID
            };
            req.body = {};
            req.logID = 'siuH2sheabuquocoo4faed1utui8aete';

            this.res = {
                redirect: sinon.spy(),
                append: sinon.spy(),
                render: sinon.spy(),
                track_id: trackID,
                locals: {}
            };

            this.error = ['error'];
            this.errorCode = '';
        });

        it('should not process error if it is not array', function() {
            this.error = {};
            this.auth_challenges.processError(this.error, this.req, this.res);
            expect(this.errorCode).to.be.empty();
        });

        it('should set res.locals.error if error is array', function() {
            this.auth_challenges.processError(this.error, this.req, this.res);
            expect(this.res.locals.error).not.to.be.empty();
        });

        it('should set res.locals.isFailed if challenge not passed', function() {
            this.errorCode = ['challenge.not_passed'];
            this.auth_challenges.processError(this.errorCode, this.req, this.res);
            expect(this.res.locals.isFailed).to.be.ok();
        });

        it('should redirect if challenge not enabled', function() {
            this.errorCode = ['challenge.not_enabled'];
            this.auth_challenges.processError(this.errorCode, this.req, this.res);
            expect(this.res.redirect.calledOnce).to.be.ok();
        });
    });
});
