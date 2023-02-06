'use strict';

var expect = require('expect.js');
var sinon = require('sinon');
var when = require('when');
var ysa = require('../../../routes/ysa');

describe('ysa', function() {
    describe('getEsecId', function() {
        var req, res, apiResult, middleware; // eslint-disable-line one-var, one-var-declaration-per-line

        beforeEach(function() {
            res = {
                locals: {
                    extendedLogging: true
                }
            };
            req = {
                api: {}
            };
            apiResult = {
                body: {
                    esec_id: 'foo'
                }
            };
            middleware = {
                next: function() {} // eslint-disable-line no-empty-function
            };
        });

        it('Should return function', function() {
            expect(ysa.getEsecId()).to.be.a('function');
        });

        it('Should create ysa object on res.locals with namespace', function(done) {
            var getEsecId = ysa.getEsecId('foo');
            var promise = when.reject();
            var next = sinon.stub(middleware, 'next').callsFake(function() {
                expect(res.locals.ysa).to.be.a('object');
                expect(res.locals.ysa.namespace).to.be('foo');
                done();
            });

            req.api.ysaGetEsecId = sinon.stub().returns(promise);
            getEsecId(req, res, next);
        });

        it('Should set esecId and md5 namespace on res.locals.ysa on successful api answer', function(done) {
            var getEsecId = ysa.getEsecId('pssp_phone');
            var promise = when.resolve(apiResult);
            var next = sinon.stub(middleware, 'next').callsFake(function() {
                expect(res.locals.ysa).to.be.a('object');
                expect(res.locals.ysa.namespace).to.be('pssp_phone');
                expect(res.locals.ysa.esecId).to.be('foo');
                expect(res.locals.ysa.namespaceMd5).to.be('161e7e0fa5ac3f15ea92dc63e71fa65b');
                done();
            });

            req.api.ysaGetEsecId = sinon.stub().returns(promise);
            getEsecId(req, res, next);
        });

        it('Should call api.ysaGetEsecId with namespace', function(done) {
            var getEsecId = ysa.getEsecId('foo');
            var promise = when.reject();
            var next = sinon.stub(middleware, 'next').callsFake(function() {
                expect(req.api.ysaGetEsecId.calledOnce).to.be(true);
                expect(req.api.ysaGetEsecId.calledWithExactly('foo')).to.be(true);
                done();
            });

            req.api.ysaGetEsecId = sinon.stub().returns(promise);
            getEsecId(req, res, next);
        });

        it('Should call next on api reject', function(done) {
            var getEsecId = ysa.getEsecId('foo');
            var promise = when.reject();
            var next = sinon.stub(middleware, 'next').callsFake(function() {
                expect(next.calledOnce).to.be(true);
                done();
            });

            req.api.ysaGetEsecId = sinon.stub().returns(promise);
            getEsecId(req, res, next);
        });

        it('Should call next on api resolve', function(done) {
            var getEsecId = ysa.getEsecId('foo');
            var promise = when.resolve(apiResult);
            var next = sinon.stub(middleware, 'next').callsFake(function() {
                expect(next.calledOnce).to.be(true);
                done();
            });

            req.api.ysaGetEsecId = sinon.stub().returns(promise);
            getEsecId(req, res, next);
        });
    });

    describe('writeUserEnv', function() {
        var req, res, middleware; // eslint-disable-line one-var, one-var-declaration-per-line

        beforeEach(function() {
            res = {
                _yandexuid: 'uid',
                locals: {
                    track: 'track',
                    ysa: {
                        namespace: 'pssp_phone',
                        esecId: 'foo'
                    },
                    extendedLogging: true
                }
            };
            req = {
                headers: {
                    'x-real-ip': 'ip'
                },
                cookies: {},
                api: {}
            };
            middleware = {
                next: function() {} // eslint-disable-line no-empty-function
            };
        });

        it('Should call api.ysaWriteUserEvent with data', function(done) {
            var promise = when.resolve();
            var next = sinon.stub(middleware, 'next').callsFake(function() {
                var data = req.api.ysaWriteUserEvent.args[0][0];

                expect(req.api.ysaWriteUserEvent.calledOnce).to.be(true);
                expect(data.namespace).to.be(res.locals.ysa.namespace);
                expect(data.esecId).to.be(res.locals.ysa.esecId);
                expect(data.events.length).to.be(1);
                expect(data.events[0].name).to.be('env');
                expect(data.events[0].ts).to.be.a('number');
                expect(data.events[0].payload).to.be.a('object');
                expect(data.events[0].payload.track_id).to.be(res.locals.track);
                expect(data.events[0].payload.ip).to.be(req.headers['x-real-ip']);
                expect(data.events[0].payload.cookies).to.be(req.cookies);
                expect(data.events[0].payload.yandexuid).to.be(res._yandexuid);
                done();
            });

            req.api.ysaWriteUserEvent = sinon.stub().returns(promise);
            ysa.writeUserEnv(req, res, next);
        });

        it('Should call next on api success answer', function(done) {
            var promise = when.resolve();
            var next = sinon.stub(middleware, 'next').callsFake(function() {
                expect(next.calledOnce).to.be(true);
                done();
            });

            req.api.ysaWriteUserEvent = sinon.stub().returns(promise);
            ysa.writeUserEnv(req, res, next);
        });

        it('Should call next on api success answer', function(done) {
            var promise = when.reject();
            var next = sinon.stub(middleware, 'next').callsFake(function() {
                expect(next.calledOnce).to.be(true);
                done();
            });

            req.api.ysaWriteUserEvent = sinon.stub().returns(promise);
            ysa.writeUserEnv(req, res, next);
        });
    });

    describe('checkRobot', function() {
        var req, res, middleware; // eslint-disable-line one-var, one-var-declaration-per-line

        beforeEach(function() {
            res = {
                json: function() {} // eslint-disable-line no-empty-function
            };
            req = {
                cookies: {
                    yandexuid: '09'
                },
                body: {
                    ysaNamespace: 'namespace',
                    ysaEsecId: 'esecid'
                },
                api: {}
            };
            middleware = {
                next: function() {} // eslint-disable-line no-empty-function
            };
        });

        it('Should call api.captchaCheckStatus', function(done) {
            var promise = when.reject();

            sinon.stub(res, 'json').callsFake(function() {
                expect(req.api.captchaCheckStatus.calledOnce).to.be(true);
                done();
            });
            req.api.captchaCheckStatus = sinon.stub().returns(promise);
            req.api.ysaGetRobotness = sinon.stub().returns(promise);
            ysa.checkRobot(req, res, middleware.next);
        });

        it('Should call api.ysaGetRobotness', function(done) {
            var promise = when.reject();

            sinon.stub(res, 'json').callsFake(function() {
                var data = req.api.ysaGetRobotness.args[0][0];

                expect(req.api.ysaGetRobotness.calledOnce).to.be(true);
                expect(data.namespace).to.be(req.body.ysaNamespace);
                expect(data.esecId).to.be(req.body.ysaEsecId);
                done();
            });
            req.api.captchaCheckStatus = sinon.stub().returns(promise);
            req.api.ysaGetRobotness = sinon.stub().returns(promise);
            ysa.checkRobot(req, res, middleware.next);
        });

        it('Should send json on api error', function(done) {
            var captchaPromise = when.reject(['captcha_error']);
            var ysaPromise = when.resolve();
            var json = sinon.stub(res, 'json').callsFake(function() {
                var data = json.args[0][0];

                expect(data.status).to.be('error');
                expect(data.errors[0]).to.be('captcha_error');
                done();
            });

            req.api.captchaCheckStatus = sinon.stub().returns(captchaPromise);
            req.api.ysaGetRobotness = sinon.stub().returns(ysaPromise);
            ysa.checkRobot(req, res, middleware.next);
        });

        it('Should send json with internal error if api rejects not array', function(done) {
            var captchaPromise = when.reject('captcha_error');
            var ysaPromise = when.resolve();
            var json = sinon.stub(res, 'json').callsFake(function() {
                var data = json.args[0][0];

                expect(data.status).to.be('error');
                expect(data.errors[0]).to.be('internal');
                done();
            });

            req.api.captchaCheckStatus = sinon.stub().returns(captchaPromise);
            req.api.ysaGetRobotness = sinon.stub().returns(ysaPromise);
            ysa.checkRobot(req, res, middleware.next);
        });

        it('Should call next if robotness < ROBOTNESS_LIMIT', function(done) {
            var captchaPromise = when.resolve({body: {}});
            var ysaPromise = when.resolve({body: {robotness: 0}});
            var next = sinon.stub(middleware, 'next').callsFake(function() {
                expect(next.calledOnce).to.be(true);
                done();
            });

            req.api.captchaCheckStatus = sinon.stub().returns(captchaPromise);
            req.api.ysaGetRobotness = sinon.stub().returns(ysaPromise);
            ysa.checkRobot(req, res, next);
        });

        it('Should call next if robontess > ROBOTNESS_LIMIT and captcha solved', function(done) {
            var captchaPromise = when.resolve({body: {is_recognized: true, is_checked: true}});
            var ysaPromise = when.resolve({body: {robotness: 1}});
            var next = sinon.stub(middleware, 'next').callsFake(function() {
                expect(next.calledOnce).to.be(true);
                done();
            });

            req.api.captchaCheckStatus = sinon.stub().returns(captchaPromise);
            req.api.ysaGetRobotness = sinon.stub().returns(ysaPromise);
            req.api.ysaWriteUserEvent = sinon.stub();
            ysa.checkRobot(req, res, next);
        });

        it('Should call api.ysaWriteUserEvent if robontess > ROBOTNESS_LIMIT and captcha solved', function(done) {
            var captchaPromise = when.resolve({body: {is_recognized: true, is_checked: true}});
            var ysaPromise = when.resolve({body: {robotness: 1}});
            var next = sinon.stub(middleware, 'next').callsFake(function() {
                var data = req.api.ysaWriteUserEvent.args[0][0];

                expect(req.api.ysaWriteUserEvent.calledOnce).to.be(true);
                expect(data.namespace).to.be(req.body.ysaNamespace);
                expect(data.esecId).to.be(req.body.ysaEsecId);
                expect(data.events.length).to.be(1);
                expect(data.events[0].name).to.be('mark');
                expect(data.events[0].ts).to.be.a('number');
                expect(data.events[0].payload).to.be.a('object');
                expect(data.events[0].payload.value).to.be(0);
                done();
            });

            req.api.captchaCheckStatus = sinon.stub().returns(captchaPromise);
            req.api.ysaGetRobotness = sinon.stub().returns(ysaPromise);
            req.api.ysaWriteUserEvent = sinon.stub();
            ysa.checkRobot(req, res, next);
        });

        it('Should call res.json if robontess > ROBOTNESS_LIMIT and captcha was not checked', function(done) {
            var captchaPromise = when.resolve({body: {is_recognized: false, is_checked: false}});
            var ysaPromise = when.resolve({body: {robotness: 1}});

            sinon.stub(res, 'json').callsFake(function() {
                var data = res.json.args[0][0];

                expect(res.json.calledOnce).to.be(true);
                expect(data.status).to.be('error');
                expect(data.errors.length).to.be(1);
                expect(data.errors[0]).to.be('captcha.required');
                done();
            });
            req.api.captchaCheckStatus = sinon.stub().returns(captchaPromise);
            req.api.ysaGetRobotness = sinon.stub().returns(ysaPromise);
            ysa.checkRobot(req, res, middleware.next);
        });

        it('Should call res.json if robontess > ROBOTNESS_LIMIT and captcha was not recognized', function(done) {
            var captchaPromise = when.resolve({body: {is_recognized: false, is_checked: true}});
            var ysaPromise = when.resolve({body: {robotness: 1}});

            sinon.stub(res, 'json').callsFake(function() {
                var data = res.json.args[0][0];

                expect(res.json.calledOnce).to.be(true);
                expect(data.status).to.be('error');
                expect(data.errors.length).to.be(1);
                expect(data.errors[0]).to.be('captcha.required');
                done();
            });
            req.api.captchaCheckStatus = sinon.stub().returns(captchaPromise);
            req.api.ysaGetRobotness = sinon.stub().returns(ysaPromise);
            req.api.ysaWriteUserEvent = sinon.stub();
            ysa.checkRobot(req, res, middleware.next);
        });

        it(
            'Should call api.writeUserEvent if robontess > ROBOTNESS_LIMIT' + ' and captcha was not recognized',
            function(done) {
                var captchaPromise = when.resolve({body: {is_recognized: false, is_checked: true}});
                var ysaPromise = when.resolve({body: {robotness: 1}});

                sinon.stub(res, 'json').callsFake(function() {
                    var data = req.api.ysaWriteUserEvent.args[0][0];

                    expect(req.api.ysaWriteUserEvent.calledOnce).to.be(true);
                    expect(data.namespace).to.be(req.body.ysaNamespace);
                    expect(data.esecId).to.be(req.body.ysaEsecId);
                    expect(data.events.length).to.be(1);
                    expect(data.events[0].name).to.be('mark');
                    expect(data.events[0].ts).to.be.a('number');
                    expect(data.events[0].payload).to.be.a('object');
                    expect(data.events[0].payload.value).to.be(1);
                    done();
                });
                req.api.captchaCheckStatus = sinon.stub().returns(captchaPromise);
                req.api.ysaGetRobotness = sinon.stub().returns(ysaPromise);
                req.api.ysaWriteUserEvent = sinon.stub();
                ysa.checkRobot(req, res, middleware.next);
            }
        );
    });

    describe('ysa/event route', function() {
        var req, res; // eslint-disable-line one-var, one-var-declaration-per-line

        beforeEach(function() {
            res = {
                json: function() {} // eslint-disable-line no-empty-function
            };
            req = {
                api: {},
                body: {
                    namespace: 'namespace',
                    esecId: 'esecId'
                }
            };
        });

        it('Should call JSON.parse', function(done) {
            sinon.stub(JSON, 'parse');

            sinon.stub(res, 'json').callsFake(function() {
                expect(JSON.parse.calledOnce).to.be(true);
                JSON.parse.restore();
                done();
            });

            ysa.writeUserEvent(req, res);
        });

        it('Should call res.json on JSON parse error', function(done) {
            sinon.stub(res, 'json').callsFake(function() {
                var data = res.json.args[0][0];

                expect(res.json.calledOnce).to.be(true);
                expect(data.status).to.be('error');
                expect(data.errors.length).to.be(1);
                expect(data.errors[0]).to.be('internal');
                done();
            });
            ysa.writeUserEvent(req, res);
        });

        it('Should call api.writeUserEvent', function(done) {
            sinon.stub(res, 'json').callsFake(function() {
                var data = req.api.ysaWriteUserEvent.args[0][0];

                expect(req.api.ysaWriteUserEvent.calledOnce).to.be(true);
                expect(data.namespace).to.be(req.body.ysaNamespace);
                expect(data.esecId).to.be(req.body.ysaEsecId);
                expect(data.events.length).to.be(1);
                expect(data.events[0].name).to.be('focus');
                expect(data.events[0].ts).to.be.a('number');
                expect(data.events[0].payload).to.be.a('object');
                done();
            });
            req.body.events = JSON.stringify([
                {
                    name: 'focus',
                    ts: Date.now(),
                    payload: {}
                }
            ]);
            req.api.ysaWriteUserEvent = sinon.stub().returns(when.resolve({body: 'foo'}));
            ysa.writeUserEvent(req, res);
        });

        it('Should have country if event.name is "provide-phone-number"', function(done) {
            sinon.stub(res, 'json').callsFake(function() {
                var data = req.api.ysaWriteUserEvent.args[0][0];

                expect(data.events[0].payload.country).to.be('ru');
                done();
            });

            req.body.events = JSON.stringify([
                {
                    name: 'provide-phone-number',
                    ts: Date.now(),
                    payload: {}
                }
            ]);
            req.api.ysaWriteUserEvent = sinon.stub().returns(when.resolve({body: 'foo'}));
            req.api.params = sinon.stub().returns(when.resolve({body: {country: ['ru']}}));
            ysa.writeUserEvent(req, res);
        });

        it('Should call res.json if api.writeUserEvent returns error', function(done) {
            sinon.stub(res, 'json').callsFake(function() {
                var data = res.json.args[0][0];

                expect(data.status).to.be('error');
                expect(data.errors[0]).to.be('errors');
                done();
            });

            req.body.events = JSON.stringify([
                {
                    name: 'focus',
                    ts: Date.now(),
                    payload: {}
                }
            ]);
            req.api.ysaWriteUserEvent = sinon.stub().returns(when.reject(['errors']));
            ysa.writeUserEvent(req, res);
        });

        it('Should call res.json with internal error if api rejects with not array', function(done) {
            sinon.stub(res, 'json').callsFake(function() {
                var data = res.json.args[0][0];

                expect(data.status).to.be('error');
                expect(data.errors[0]).to.be('internal');
                done();
            });

            req.body.events = JSON.stringify([
                {
                    name: 'focus',
                    ts: Date.now(),
                    payload: {}
                }
            ]);
            req.api.ysaWriteUserEvent = sinon.stub().returns(when.reject('errors'));
            ysa.writeUserEvent(req, res);
        });

        it('Should call res.json if api.writeUserEvent returns success', function(done) {
            sinon.stub(res, 'json').callsFake(function() {
                var data = res.json.args[0][0];

                expect(data).to.be('success');
                done();
            });

            req.body.events = JSON.stringify([
                {
                    name: 'focus',
                    ts: Date.now(),
                    payload: {}
                }
            ]);
            req.api.ysaWriteUserEvent = sinon.stub().returns(when.resolve({body: 'success'}));
            ysa.writeUserEvent(req, res);
        });
    });
});
