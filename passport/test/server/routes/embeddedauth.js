var expect = require('expect.js');
var sinon = require('sinon');
var supertest = require('supertest');
var app = require('../../../app.js');

var request = supertest(app);

var embeddedUrl = '/passport?mode=embeddedauth';
var embeddedPddUrl = '/for/okna.ru?mode=embeddedauth';

require('../../util/mock/mockApi.js');

var data = require('../../util/mock/mockData.js');
var b = data.basic;
var s = data.sets;
var headers = data.headers;

var trackID = b.trackID;

describe(`POST ${embeddedUrl}`, function() {
    it('return redirect to finish if login credentials are valid', function(done) {
        request
            .post(embeddedUrl)
            .type('form')
            .set(headers)
            .send({
                login: b.goodLogin,
                password: b.goodPass,
                retpath: b.retpathUrl
            })
            .expect('Location', /\/auth\/finish\//)
            .expect(302, done);
    });

    it('return Session_id cookie if login credentials are valid', function(done) {
        request
            .post(embeddedUrl)
            .type('form')
            .set(headers)
            .send({
                login: b.goodLogin,
                password: b.goodPass,
                retpath: b.retpathUrl
            })
            .expect('Set-Cookie', /Session_id/)
            .expect(302, done);
    });

    it('return status=password-invalid as GET-param in location if password is invalid', function(done) {
        request
            .post(embeddedUrl)
            .type('form')
            .set(headers)
            .send(s.wrongPassword)
            .expect('Location', /status=password-invalid/)
            .expect(302, done);
    });

    it('return status=account-not-found as GET-param in location if login is invalid', function(done) {
        request
            .post(embeddedUrl)
            .type('form')
            .set(headers)
            .send(s.inValidLoginData)
            .expect('Location', /status=account-not-found/)
            .expect(302, done);
    });

    it('return status=password-empty as GET-param in location if password is empty', function(done) {
        request
            .post(embeddedUrl)
            .type('form')
            .set(headers)
            .send(s.emptyPassword)
            .expect('Location', /status=password-empty/)
            .expect(302, done);
    });

    it('return status=password-empty as GET-param in location if no password was sent', function(done) {
        request
            .post(embeddedUrl)
            .type('form')
            .set(headers)
            .send(s.noPassword)
            .expect('Location', /status=password-empty/)
            .expect(302, done);
    });

    it('return status=login-empty as GET-param in location if login is empty', function(done) {
        request
            .post(embeddedUrl)
            .type('form')
            .set(headers)
            .send(s.emptyLogin)
            .expect('Location', /status=login-empty/)
            .expect(302, done);
    });

    it('return status=login-empty as GET-param in location if no login was sent', function(done) {
        request
            .post(embeddedUrl)
            .type('form')
            .set(headers)
            .send(s.noLogin)
            .expect('Location', /status=login-empty/)
            .expect(302, done);
    });

    it('return status=captcha-invalid as GET-param in location if captcha is invalid', function(done) {
        request
            .post(embeddedUrl)
            .type('form')
            .set(headers)
            .send({idkey: trackID})
            .send(s.loginDataWithBadCaptcha)
            .expect('Location', /status=captcha-invalid/)
            .expect(302, done);
    });

    it('return captcha-url as GET-param in location if captcha is invalid', function(done) {
        request
            .post(embeddedUrl)
            .type('form')
            .set(headers)
            .send({idkey: trackID})
            .send(s.loginDataWithBadCaptcha)
            .expect('Location', /captcha_url=/)
            .expect(302, done);
    });

    it('does not return status=captcha-invalid as GET-param in location if captcha is valid', function(done) {
        request
            .post(embeddedUrl)
            .type('form')
            .set(headers)
            .send({idkey: trackID})
            .send(s.loginDataWithGoodCaptcha)
            .expect('Location', /finish/)
            .expect(302, done);
    });

    it('return status=captcha-required as GET-param in location if captcha is required', function(done) {
        request
            .post(embeddedUrl)
            .type('form')
            .set(headers)
            .send({
                login: b.needCaptchaLogin,
                password: b.goodPass,
                retpath: b.retpathUrl
            })
            .expect('Location', /status=captcha-required/)
            .expect(302, done);
    });

    it('return captcha_url as GET-param in location if captcha is required', function(done) {
        request
            .post(embeddedUrl)
            .type('form')
            .set(headers)
            .send({
                login: b.needCaptchaLogin,
                password: b.goodPass,
                retpath: b.retpathUrl
            })
            .expect('Location', /captcha_url=/)
            .expect(302, done);
    });

    it(
        'return status=internal-exception as GET-param in location if captcha_answer ' + 'was send without idkey',
        function(done) {
            request
                .post(embeddedUrl)
                .type('form')
                .set(headers)
                .send(s.loginDataWithGoodCaptcha)
                .expect('Location', /status=internal-exception/)
                .expect(302, done);
        }
    );

    it('returns status=other as GET-param in location if user need to complete registration', function(done) {
        request
            .post(embeddedUrl)
            .type('form')
            .set(headers)
            .send({
                login: b.needCompleteLogin,
                password: b.goodPass,
                retpath: b.retpathUrl
            })
            .expect('Location', /status=other/)
            .expect('Location', /url=/)
            .expect(302, done);
    });

    it('returns status=other as GET-param in location if user need to change password', function(done) {
        request
            .post(embeddedUrl)
            .type('form')
            .set(headers)
            .send({
                login: b.needChangePassLogin,
                password: b.goodPass,
                retpath: b.retpathUrl
            })
            .expect('Location', /status=other/)
            .expect('Location', /url=/)
            .expect(302, done);
    });

    it('return sessional cookie if no twoweeks', function(done) {
        request
            .post(embeddedUrl)
            .type('form')
            .set(headers)
            .send({
                login: b.goodLogin,
                password: b.goodPass,
                retpath: b.retpathUrl
            })
            .expect('Set-Cookie', /2014/)
            .expect(302, done);
    });

    it('return forewer cookie if twoweeks=1', function(done) {
        request
            .post(embeddedUrl)
            .type('form')
            .set(headers)
            .send({twoweeks: '1'})
            .send({
                login: b.goodLogin,
                password: b.goodPass,
                retpath: b.retpathUrl
            })
            .expect('Set-Cookie', /2038/)
            .expect(302, done);
    });

    it('return Eda_id cookie if login contains @domain.ru', function(done) {
        request
            .post(embeddedUrl)
            .type('form')
            .set(headers)
            .send({
                login: b.goodPddLogin,
                password: b.goodPass,
                retpath: b.retpathUrl
            })
            .expect('Set-Cookie', /Eda_id/)
            .expect(302, done);
    });
});

describe('embeddedauth', function() {
    beforeEach(function(done) {
        this.embeddedauth = require('../../../routes/embeddedauth');
        this.api = require('../../../lib/passport-api/index.js');
        var req = (this.req = {});

        this.api
            .client({
                headers: headers,
                track_id: b.trackID,
                language: 'ru',
                logID: 'ael3ai7acha6be4aethaL8faihieseex'
            })
            .then(function(a) {
                req.api = a;
                done();
            });
    });

    describe('checkCaptcha with goodCaptcha', function() {
        beforeEach(function(done) {
            var req = this.req;
            var res = (this.res = {});
            var target = this.embeddedauth.checkCaptcha;

            req.body = {
                captcha_answer: b.goodCaptcha,
                idkey: b.trackID,
                retpath: b.retpathUrl
            };
            target(req, res, done);
        });

        it('does not put captcha.invalid in sumbitErrors if captcha is valid', function() {
            expect(this.res.submitErrors && this.res.submitErrors.indexOf('captcha.invalid') !== -1).to.not.be.ok();
        });

        it('sets track from idkey', function() {
            expect(this.req.api.track()).to.be(b.trackID);
        });
    });

    describe('checkCaptcha with badCaptcha', function() {
        beforeEach(function(done) {
            var req = this.req;
            var res = (this.res = {});
            var target = this.embeddedauth.checkCaptcha;

            req.body = {
                captcha_answer: b.badCaptcha,
                idkey: b.trackID,
                retpath: b.retpathUrl
            };
            target(req, res, done);
        });

        it('put captcha.invalid in sumbitErrors if captcha is invalid', function() {
            expect(this.res.submitErrors && this.res.submitErrors.indexOf('captcha.invalid') !== -1).to.be.ok();
        });
    });

    describe('redirectToFinish', function() {
        beforeEach(function() {
            this.req = {
                headers: headers,
                host: 'yandex.ru',
                body: {}
            };
            this.res = {
                redirect: sinon.spy(),
                trackId: b.trackID
            };
            this.next = sinon.spy();
        });

        it('redirects if auth is finished', function() {
            this.res.authFinished = true;
            this.embeddedauth.redirectToFinish(this.req, this.res, this.next);

            expect(this.res.redirect.called).to.be.ok();
        });

        it('does not redirects to pdd-domain if config.multiauth is set and account contains @domain', function() {
            this.res.authFinished = true;
            this.res.account = {
                domain: {
                    unicode: 'okna.ru'
                }
            };

            this.embeddedauth.redirectToFinish(this.req, this.res, this.next);
            expect(this.res.redirect.args[0][1]).to.not.match(/\/for\/okna\.ru\//);
        });
    });

    describe('multiAuth', function() {
        beforeEach(function() {
            var req = this.req;

            req.headers = headers;
            req.hostname = 'yandex.ru';
            req.cookies = {
                yandexuid: '123456789'
            };
            req.body = {
                uid: '0000000',
                retpath: 'retpath',
                yu: '123456789'
            };
            req.query = {};
            req._controller = {
                augmentResponse: sinon.spy()
            };

            this.res = {
                redirect: sinon.spy(),
                track_id: b.trackID
            };

            this.next = sinon.spy();

            this.writeTrack = sinon.stub(req.api, 'writeTrack').callsFake(function() {
                return {
                    then: function(func) {
                        func({
                            body: {
                                id: b.trackID
                            }
                        });
                    }
                };
            });

            this.authSubmit = sinon.stub(req.api, 'authSubmit').callsFake(function() {
                return {
                    then: function(func) {
                        func({
                            body: {
                                track_id: b.trackID,
                                account: {},
                                cookies: 'cookies'
                            }
                        });
                    }
                };
            });
        });

        it('next is always called', function() {
            this.embeddedauth.multiAuth('lololo')(this.req, this.res, this.next);
            this.embeddedauth.multiAuth('change_default')(this.req, this.res, this.next);
            this.embeddedauth.multiAuth('logout')(this.req, this.res, this.next);

            expect(this.next.calledThrice).to.be.ok();
        });

        it('returns noop if action is unknown', function() {
            this.embeddedauth.multiAuth('lololo')(this.req, this.res, this.next);

            expect(this.authSubmit.called).to.not.be.ok();
            expect(this.writeTrack.called).to.not.be.ok();
        });

        it('does something if action is known', function() {
            this.embeddedauth.multiAuth('change_default')(this.req, this.res, this.next);
            this.embeddedauth.multiAuth('logout')(this.req, this.res, this.next);

            expect(this.authSubmit.calledTwice).to.be.ok();
            expect(this.writeTrack.calledTwice).to.be.ok();
            expect(this.next.calledTwice).to.be.ok();
        });

        it('returns middleware, that set cookies if action is change_default', function() {
            this.embeddedauth.multiAuth('change_default')(this.req, this.res, this.next);

            expect(this.res.authFinished).to.be.ok();
            expect(this.req._controller.augmentResponse.called).to.be.ok();
            expect(this.next.called).to.be.ok();
        });

        it('returns middleware, that set cookies if action is logout', function() {
            this.embeddedauth.multiAuth('logout')(this.req, this.res, this.next);

            expect(this.res.authFinished).to.be.ok();
            expect(this.req._controller.augmentResponse.called).to.be.ok();
            expect(this.next.called).to.be.ok();
        });

        it('returns middleware, that called writeTrack with retpath', function() {
            this.embeddedauth.multiAuth('logout')(this.req, this.res, this.next);

            expect(this.writeTrack.calledWith({retpath: 'retpath'})).to.be.ok();
        });

        it('returns middleware, that called authSubmit with right uid and track_id', function() {
            this.embeddedauth.multiAuth('logout')(this.req, this.res, this.next);

            expect(
                this.authSubmit.calledWith('/1/bundle/auth/logout/', {uid: '0000000', track_id: b.trackID})
            ).to.be.ok();
        });

        it('returns middleware, that set submitErrors to ["uid.empty"] if not uid send', function() {
            delete this.req.body.uid;
            this.embeddedauth.multiAuth('logout')(this.req, this.res, this.next);

            expect(this.res.submitErrors).to.be.ok();
            expect(this.res.submitErrors.indexOf('uid.empty') !== -1).to.be.ok();
        });

        it('returns middleware, that set submitErrors to ["yu.empty"] if not yu send', function() {
            delete this.req.body.yu;
            this.embeddedauth.multiAuth('logout')(this.req, this.res, this.next);

            expect(this.res.submitErrors).to.be.ok();
            expect(this.res.submitErrors.indexOf('yu.empty') !== -1).to.be.ok();
        });

        it(
            'returns middleware, that set submitErrors to ["yu.invalid"] if yu is not equal to ' + 'yandexuid cookie',
            function() {
                this.req.body.yu = '987654321';
                this.embeddedauth.multiAuth('logout')(this.req, this.res, this.next);

                expect(this.res.submitErrors).to.be.ok();
                expect(this.res.submitErrors.indexOf('yu.invalid') !== -1).to.be.ok();
            }
        );

        it('returns middleware, that set submitErrors to returned error', function() {
            this.writeTrack.restore();
            this.writeTrack = sinon.stub(this.req.api, 'writeTrack').callsFake(function() {
                return {
                    then: function(func, error) {
                        error('OMG');
                    }
                };
            });

            this.embeddedauth.multiAuth('logout')(this.req, this.res, this.next);

            expect(this.res.submitErrors).to.be.ok();
            expect(this.res.submitErrors.indexOf('OMG') !== -1).to.be.ok();
            expect(this.next.calledWith()).to.be.ok();
        });

        it('returns middleware, that call error handler with Error if api return Error object', function() {
            this.writeTrack.restore();
            this.writeTrack = sinon.stub(this.req.api, 'writeTrack').callsFake(function() {
                return {
                    then: function(func, error) {
                        error(new Error());
                    }
                };
            });

            this.embeddedauth.multiAuth('logout')(this.req, this.res, this.next);

            expect(this.res.submitErrors).to.not.be.ok();
            expect(this.next.firstCall.args[0] instanceof Error).to.be.ok();
        });
    });
});

describe(`POST ${embeddedPddUrl}`, function() {
    it('return Eda_id cookie if login credentials are valid', function(done) {
        request
            .post(embeddedPddUrl)
            .type('form')
            .set(headers)
            .send({
                login: b.goodPddLogin,
                password: b.goodPass,
                retpath: b.retpathUrl
            })
            .expect('Set-Cookie', /Eda_id/)
            .expect(302, done);
    });
});
