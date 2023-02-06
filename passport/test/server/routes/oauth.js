var expect = require('expect.js');
var sinon = require('sinon');
var url = require('url');

var data = require('../../util/mock/mockData.js');
var b = data.basic;
var headers = data.headers;

var trackID = b.trackID;

describe('oauth', function() {
    beforeEach(function(done) {
        this.oauth = require('../../../routes/oauth');
        this.api = require('../../../lib/passport-api/index.js');
        var req = (this.req = {});

        req.headers = headers;
        req.hostname = headers['host'];
        req.nquery = {
            retpath: b.retpathUrl,
            type: 'trusted-pdd-partner'
        };
        req.body = {};
        req._controller = {
            augmentResponse: sinon.spy()
        };

        this.api
            .client({
                headers: headers,
                track_id: trackID,
                logID: 'siuH2sheabuquocoo4faed1utui8aete',
                language: 'ru'
            })
            .then(function(a) {
                req.api = a;
                done();
            });
    });

    describe('doOauthRequest', function() {
        beforeEach(function() {
            this.res = {
                redirect: sinon.spy(),
                append: sinon.spy(),
                track_id: trackID
            };

            this.next = sinon.spy();

            this.finishRetpath = url.format({
                protocol: headers['x-real-scheme'],
                hostname: headers['host'],
                pathname: '/auth/finish/',
                query: {
                    track_id: trackID
                }
            });

            this.tracksubmitRetpath = url.format({
                protocol: headers['x-real-scheme'],
                hostname: headers['host'],
                pathname: 'auth',
                query: {
                    track_id: trackID,
                    retpath: b.retpathUrl
                }
            });

            this.passportRetpath = url.format({
                protocol: headers['x-real-scheme'],
                hostname: headers['host'],
                pathname: 'passport',
                query: {
                    mode: 'passport'
                }
            });

            this.pddFinishRetpath = url.format({
                protocol: headers['x-real-scheme'],
                hostname: headers['host'],
                pathname: '/for/okna.ru/finish/',
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

        it('redirects to /auth/finish/ if all is ok and cookies were set', function() {
            this.oauth.doOauthRequest(this.req, this.res, this.next);

            expect(this.res.redirect.calledWith(this.finishRetpath)).to.be.ok();
        });

        it('sets no cookie if backend does not return cookies', function() {
            this.authSubmit.restore();
            this.authSubmit = sinon.stub(this.req.api, 'authSubmit').callsFake(function() {
                return {
                    done: function(func) {
                        func({
                            body: {
                                track_id: trackID,
                                account: {}
                            }
                        });
                    }
                };
            });

            this.oauth.doOauthRequest(this.req, this.res, this.next);
            expect(this.req._controller.augmentResponse.called).to.be.ok();
        });

        it('does set cookie if all is ok and backend return cookies', function() {
            this.oauth.doOauthRequest(this.req, this.res, this.next);

            expect(this.req._controller.augmentResponse.called).to.be.ok();
        });

        it(
            'redirects to /for/okna.ru/finish/ if all is ok and user has domain ' +
                'in account details and !config.multiauth is set',
            function() {
                sinon.stub(this.oauth, 'getConfig').returns({});

                this.authSubmit.restore();
                this.authSubmit = sinon.stub(this.req.api, 'authSubmit').callsFake(function() {
                    return {
                        done: function(func) {
                            func({
                                body: {
                                    track_id: trackID,
                                    account: {
                                        domain: {
                                            unicode: 'okna.ru'
                                        }
                                    },
                                    cookies: 'cookies'
                                }
                            });
                        }
                    };
                });

                this.oauth.doOauthRequest(this.req, this.res, this.next);
                this.oauth.getConfig.restore();
                expect(this.res.redirect.calledWith(this.pddFinishRetpath)).to.be.ok();
            }
        );

        it(
            'redirects to /auth/finish/ if all is ok and user has domain in account ' +
                'details and config.multiauth is set',
            function() {
                this.authSubmit.restore();
                this.authSubmit = sinon.stub(this.req.api, 'authSubmit').callsFake(function() {
                    return {
                        done: function(func) {
                            func({
                                body: {
                                    track_id: trackID,
                                    account: {
                                        domain: {
                                            unicode: 'okna.ru'
                                        }
                                    },
                                    cookies: 'cookies'
                                }
                            });
                        }
                    };
                });

                this.oauth.doOauthRequest(this.req, this.res, this.next);
                expect(this.res.redirect.calledWith(this.finishRetpath)).to.be.ok();
            }
        );

        it('call redirect to retpath if backend does not return cookie but return retpath', function() {
            this.authSubmit.restore();
            this.authSubmit = sinon.stub(this.req.api, 'authSubmit').callsFake(function() {
                return {
                    done: function(func) {
                        func({
                            body: {
                                track_id: trackID,
                                retpath: 'lololo'
                            }
                        });
                    }
                };
            });

            this.oauth.doOauthRequest(this.req, this.res, this.next);
            expect(this.res.redirect.calledWith('lololo')).to.be.ok();
        });

        it('call redirect to mpde=passport if backend does not return cookie and does not return retpath', function() {
            this.authSubmit.restore();
            this.authSubmit = sinon.stub(this.req.api, 'authSubmit').callsFake(function() {
                return {
                    done: function(func) {
                        func({
                            body: {
                                track_id: trackID
                            }
                        });
                    }
                };
            });

            this.oauth.doOauthRequest(this.req, this.res, this.next);
            expect(this.res.redirect.calledWith(this.passportRetpath)).to.be.ok();
        });

        it('call redirect to tracksubmit if backend return state', function() {
            this.authSubmit.restore();
            this.authSubmit = sinon.stub(this.req.api, 'authSubmit').callsFake(function() {
                return {
                    done: function(func) {
                        func({
                            body: {
                                track_id: trackID,
                                state: 'lololo',
                                retpath: b.retpathUrl
                            }
                        });
                    }
                };
            });

            this.oauth.doOauthRequest(this.req, this.res, this.next);
            expect(this.res.redirect.calledWith(this.tracksubmitRetpath)).to.be.ok();
        });

        it('call next if backend does not return track_id', function() {
            this.authSubmit.restore();
            this.authSubmit = sinon.stub(this.req.api, 'authSubmit').callsFake(function() {
                return {
                    done: function(func) {
                        func({
                            body: {}
                        });
                    }
                };
            });

            this.oauth.doOauthRequest(this.req, this.res, this.next);
            expect(this.next.called).to.be.ok();
        });

        it('call next if backend does not return body', function() {
            this.authSubmit.restore();
            this.authSubmit = sinon.stub(this.req.api, 'authSubmit').callsFake(function() {
                return {
                    done: function(func) {
                        func({});
                    }
                };
            });

            this.oauth.doOauthRequest(this.req, this.res, this.next);
            expect(this.next.called).to.be.ok();
        });

        it('call next if backend returns status=error', function() {
            this.authSubmit.restore();
            this.authSubmit = sinon.stub(this.req.api, 'authSubmit').callsFake(function() {
                return {
                    done: function(func, error) {
                        error(new Error());
                    }
                };
            });

            this.oauth.doOauthRequest(this.req, this.res, this.next);
            expect(this.next.called).to.be.ok();
        });
    });

    describe('errorHandler', function() {
        beforeEach(function() {
            this.err = new Error();

            this.res = {
                render: sinon.spy(),
                locals: {
                    language: 'en'
                }
            };

            this.next = sinon.spy();

            this.authRetpath = url.format({
                protocol: headers['x-real-scheme'],
                hostname: headers['host'],
                pathname: '/auth/',
                query: {
                    retpath: b.retpathUrl
                }
            });
        });

        it('call res.render', function() {
            this.oauth.errorHandler(this.err, this.req, this.res, this.next);
            expect(this.res.render.called).to.be.ok();
        });
    });
});
