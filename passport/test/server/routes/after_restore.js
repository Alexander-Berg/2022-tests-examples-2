var expect = require('expect.js');
var sinon = require('sinon');
var url = require('url');

var data = require('../../util/mock/mockData.js');
var b = data.basic;
var headers = data.headers;

var trackID = b.trackID;

describe('after_restore', function() {
    beforeEach(function(done) {
        this.after_restore = require('../../../routes/after_restore');
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

    describe('doAfterRestore', function() {
        beforeEach(function() {
            var req = this.req;

            req.headers = headers;
            req.hostname = headers['host'];
            req.nquery = {
                track_id: trackID
            };
            req.body = {};
            req.params = {};
            req._controller = {
                augmentResponse: sinon.spy()
            };

            this.res = {
                redirect: sinon.spy(),
                append: sinon.spy(),
                track_id: trackID
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

        it('redirects to /auth/finish/ if all is ok and cookies were set', function() {
            this.after_restore.doAfterRestore(this.req, this.res);

            expect(this.res.redirect.calledWith(this.finishRetpath)).to.be.ok();
        });

        it('send is_pdd to authSubmit  if pdd_domain is received in body', function() {
            var spy = sinon.spy();

            this.authSubmit.restore();
            this.authSubmit = sinon.stub(this.req.api, 'authSubmit').callsFake(function() {
                spy(arguments[1]);
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

            this.req.body['pdd_domain'] = 'lololo.lo';

            this.after_restore.doAfterRestore(this.req, this.res);

            expect(spy.calledWith({track_id: trackID, is_pdd: '1'})).to.be.ok();
        });

        it('send is_pdd to authSubmit  if pdd_domain is received in query', function() {
            var spy = sinon.spy();

            this.authSubmit.restore();
            this.authSubmit = sinon.stub(this.req.api, 'authSubmit').callsFake(function() {
                spy(arguments[1]);
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

            this.req.nquery['pdd_domain'] = 'lololo.lo';

            this.after_restore.doAfterRestore(this.req, this.res);

            expect(spy.calledWith({track_id: trackID, is_pdd: '1'})).to.be.ok();
        });

        it('send is_pdd to authSubmit  if pdd_domain is received in params', function() {
            var spy = sinon.spy();

            this.authSubmit.restore();
            this.authSubmit = sinon.stub(this.req.api, 'authSubmit').callsFake(function() {
                spy(arguments[1]);
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

            this.req.params['pdd_domain'] = 'lololo.lo';

            this.after_restore.doAfterRestore(this.req, this.res);

            expect(spy.calledWith({track_id: trackID, is_pdd: '1'})).to.be.ok();
        });

        it('sets cookie if all is ok and backend does not return cookies', function() {
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

            this.after_restore.doAfterRestore(this.req, this.res);
            expect(this.req._controller.augmentResponse.called).to.be.ok();
        });

        it('sets cookie if all is ok and backend return cookies', function() {
            this.after_restore.doAfterRestore(this.req, this.res);

            expect(this.req._controller.augmentResponse.called).to.be.ok();
        });

        it(
            'redirects to retpath if all is ok and cookies were not set and retpath ' + 'was succesfully validated',
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

                this.after_restore.doAfterRestore(this.req, this.res);
                expect(this.res.redirect.calledWith(b.retpathUrl)).to.be.ok();
            }
        );

        it(
            'redirects to mode=passport if all is ok and cookies were not set and retpath ' +
                'was not succesfully validated',
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

                this.after_restore.doAfterRestore(this.req, this.res);
                expect(this.res.redirect.calledWith(this.defaultRetpath)).to.be.ok();
            }
        );

        it('redirects to /finish/auth/ if all is ok even if user has domain in account details', function() {
            sinon.stub(this.after_restore, 'getConfig').returns({});

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

            this.after_restore.doAfterRestore(this.req, this.res);
            this.after_restore.getConfig.restore();
            expect(this.res.redirect.calledWith(this.finishRetpath)).to.be.ok();
        });

        it(
            'redirects to /auth/finish/ if all is ok and user has domain in account details ' +
                'and config.multiauth is set',
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

                this.after_restore.doAfterRestore(this.req, this.res);
                expect(this.res.redirect.calledWith(this.finishRetpath)).to.be.ok();
            }
        );

        it('calls next() f something wrong', function() {
            this.authSubmit.restore();
            this.authSubmit = sinon.stub(this.req.api, 'authSubmit').callsFake(function() {
                return {
                    done: function(func, error) {
                        error(new Error());
                    }
                };
            });

            this.after_restore.doAfterRestore(this.req, this.res, this.next);
            expect(this.next.called).to.be.ok();
        });
    });
});
