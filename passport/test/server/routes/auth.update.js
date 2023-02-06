/* global describe, it, afterEach, beforeEach, require */

var url = require('url');
var expect = require('expect.js');
var sinon = require('sinon');
var data = require('../../util/mock/mockData.js');
var b = data.basic;
var headers = data.headers;
var trackID = b.trackID;
var target = {};

target.authUpdate = require('../../../routes/auth.update');
target.api = require('../../../lib/passport-api/index.js');

describe('authUpdate', function() {
    beforeEach(function(done) {
        var req = (target.req = {});

        target.api
            .client({
                headers: headers,
                track_id: trackID,
                language: 'ru',
                logID: 'ael3ai7acha6be4aethaL8faihieseex'
            })
            .then(function(api) {
                req.api = api;
                done();
            });
    });

    describe('doSessionUpdateRequest', function() {
        beforeEach(function() {
            var req = target.req;

            req.headers = headers;
            req.hostname = headers.host;
            req.query = {
                retpath: b.retpathUrl
            };
            req.body = {};
            req._controller = {
                augmentResponse: sinon.spy()
            };

            target.defaultRetpath = url.format({
                protocol: headers['x-real-scheme'],
                hostname: headers.host,
                pathname: 'passport',
                query: {
                    mode: 'passport'
                }
            });

            target.res = {
                redirect: sinon.spy(),
                append: sinon.spy(),
                send: sinon.spy(),
                type: sinon.spy(),
                removeHeader: sinon.spy(),
                track_id: trackID,
                locals: {}
            };

            target.next = sinon.spy();

            target.authSubmit = sinon.stub(target.req.api, 'authSubmit').callsFake(function() {
                return {
                    then: function(func) {
                        func({
                            body: {
                                status: 'ok',
                                track_id: trackID,
                                account: {},
                                cookies: 'cookies',
                                retpath: b.retpathUrl
                            }
                        });

                        return {
                            catch: sinon.spy()
                        };
                    }
                };
            });
        });

        afterEach(function() {
            target.authSubmit.restore();
        });

        it('sends retpath to api', function() {
            target.authUpdate.doSessionUpdateRequest(target.req, target.res, target.next);
            expect(
                target.authSubmit.calledWith('/1/bundle/session/update/', {
                    passErrors: true,
                    retpath: b.retpathUrl
                })
            ).to.be.ok();
        });

        it('redirects to retpath if all is OK and retpath is given', function() {
            target.authUpdate.doSessionUpdateRequest(target.req, target.res, target.next);
            expect(target.res.redirect.calledWith(b.retpathUrl)).to.be.ok();
        });

        it('redirects to default retpath if all is OK and retpath is invalid', function() {
            target.authSubmit.restore();
            target.authSubmit = sinon.stub(target.req.api, 'authSubmit').callsFake(function() {
                return {
                    then: function(func) {
                        func({
                            body: {
                                track_id: trackID,
                                account: {},
                                status: 'ok'
                            }
                        });

                        return {
                            catch: sinon.spy()
                        };
                    }
                };
            });

            target.authUpdate.doSessionUpdateRequest(target.req, target.res, target.next);
            expect(target.res.redirect.calledWith(target.defaultRetpath)).to.be.ok();
        });

        it('proceeds to error if body status is not OK', function() {
            target.authSubmit.restore();
            target.authSubmit = sinon.stub(target.req.api, 'authSubmit').callsFake(function() {
                return {
                    then: function(func) {
                        func({
                            body: {
                                track_id: trackID,
                                account: {},
                                retpath: b.retpathUrl,
                                errors: ['oh!']
                            }
                        });

                        return {
                            catch: sinon.spy()
                        };
                    }
                };
            });

            target.authUpdate.doSessionUpdateRequest(target.req, target.res, target.next);
            expect(target.next.calledWith(['oh!'])).to.be.ok();
        });

        it('returns JSON if no retpath is given', function() {
            target.req.query = {};
            target.authUpdate.doSessionUpdateRequest(target.req, target.res, target.next);
            expect(target.res.type.calledWith('application/json')).to.be.ok();
        });

        it('returns JSON with status:ok if all is OK and no retpath is given', function() {
            target.req.query = {};
            target.authUpdate.doSessionUpdateRequest(target.req, target.res, target.next);
            expect(target.res.send.calledWith({status: 'ok'})).to.be.ok();
        });

        it('returns JSON with status:error if error happens and no retpath is given', function() {
            target.req.query = {};
            target.authSubmit.restore();
            target.authSubmit = sinon.stub(target.req.api, 'authSubmit').callsFake(function() {
                return {
                    then: function(func) {
                        func({
                            body: {
                                track_id: trackID,
                                account: {},
                                errors: ['oh!']
                            }
                        });

                        return {
                            catch: sinon.spy()
                        };
                    }
                };
            });
            target.authUpdate.doSessionUpdateRequest(target.req, target.res, target.next);
            expect(target.res.send.calledWith({status: 'error'})).to.be.ok();
        });
    });
});
