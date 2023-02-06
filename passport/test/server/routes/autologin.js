var expect = require('expect.js');
var sinon = require('sinon');
var url = require('url');

var data = require('../../util/mock/mockData.js');
var b = data.basic;
var headers = data.headers;

var trackID = b.trackID;

describe('autologin', function() {
    beforeEach(function(done) {
        this.autologin = require('../../../routes/autologin');
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

    describe('doAutoLogin', function() {
        beforeEach(function() {
            var req = this.req;

            req.headers = headers;
            req.hostname = headers['host'];
            req.nquery = {
                key: trackID,
                retpath: b.retpathUrl
            };
            req.body = {};
            req._controller = {
                augmentResponse: sinon.spy()
            };

            this.res = {
                redirect: sinon.spy(),
                append: sinon.spy(),
                track_id: trackID
            };

            this.authRetpath = url.format({
                protocol: headers['x-real-scheme'],
                hostname: headers['host'],
                pathname: '/auth/',
                query: {
                    retpath: b.retpathUrl
                }
            });

            this.finishRetpath = url.format({
                protocol: headers['x-real-scheme'],
                hostname: headers['host'],
                pathname: '/auth/finish/',
                query: {
                    track_id: trackID
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

            this.defaultRetpath = url.format({
                protocol: headers['x-real-scheme'],
                hostname: headers['host'],
                pathname: 'passport',
                query: {
                    mode: 'passport'
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

        it('res.redirect is always called', function() {
            this.autologin.doAutoLogin(this.req, this.res);

            this.authSubmit.restore();
            this.authSubmit = sinon.stub(this.req.api, 'authSubmit').callsFake(function() {
                return {
                    done: function(func, error) {
                        error(new Error());
                    }
                };
            });

            this.autologin.doAutoLogin(this.req, this.res);

            expect(this.res.redirect.calledTwice).to.be.ok();
        });

        it('redirects to /auth/finish/ if all is ok and cookies were set', function() {
            this.autologin.doAutoLogin(this.req, this.res);

            expect(this.res.redirect.calledWith(this.finishRetpath)).to.be.ok();
        });

        it('does not set cookie if all is ok and backend do not return cookies', function() {
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

            this.autologin.doAutoLogin(this.req, this.res);
            expect(this.req._controller.augmentResponse.called).to.not.be.ok();
        });

        it('sets cookie if all is ok and backend return cookies', function() {
            this.autologin.doAutoLogin(this.req, this.res);

            expect(this.req._controller.augmentResponse.called).to.be.ok();
        });

        it(
            'redirects to retpath if all is ok and cookies were not set and ' + 'retpath was succesfully validated',
            function() {
                this.authSubmit.restore();
                this.authSubmit = sinon.stub(this.req.api, 'authSubmit').callsFake(function() {
                    return {
                        done: function(func) {
                            func({
                                body: {
                                    track_id: trackID,
                                    retpath: b.retpathUrl
                                }
                            });
                        }
                    };
                });

                this.autologin.doAutoLogin(this.req, this.res);
                expect(this.res.redirect.calledWith(b.retpathUrl)).to.be.ok();
            }
        );

        it(
            'redirects to mode=passport if all is ok and cookies were not set and ' +
                'retpath was not succesfully validated',
            function() {
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

                this.autologin.doAutoLogin(this.req, this.res);
                expect(this.res.redirect.calledWith(this.defaultRetpath)).to.be.ok();
            }
        );

        it('redirects to /auth/finish/ if all is ok and user has domain in account details', function() {
            sinon.stub(this.autologin, 'getConfig').returns({});

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

            this.autologin.doAutoLogin(this.req, this.res);
            this.autologin.getConfig.restore();
            expect(this.res.redirect.calledWith(this.finishRetpath)).to.be.ok();
        });

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

                this.autologin.doAutoLogin(this.req, this.res);
                expect(this.res.redirect.calledWith(this.finishRetpath)).to.be.ok();
            }
        );

        it('redirects to /auth/ if something wrong', function() {
            this.authSubmit.restore();
            this.authSubmit = sinon.stub(this.req.api, 'authSubmit').callsFake(function() {
                return {
                    done: function(func, error) {
                        error(new Error());
                    }
                };
            });

            this.autologin.doAutoLogin(this.req, this.res);
            expect(this.res.redirect.calledWith(this.authRetpath)).to.be.ok();
        });
    });
});
