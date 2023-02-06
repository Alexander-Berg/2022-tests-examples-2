/* eslint-disable max-len */

const sinon = require('sinon');
const supertest = require('supertest');
const express = require('express');
const expect = require('expect.js');
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const proxyquire = require('proxyquire');
const Logger = require('plog');
const logSettings = Logger.configure();
const data = require('../../util/mock/mockData.js');
const b = data.basic;
const headers = data.headers;
const trackID = b.trackID;

logSettings
    .minLevel('critical')
    .setFormatter(logSettings.getFormatterByName('dev'))
    .setHandler(logSettings.getHandlerByName('console'));

describe('GET /passport?mode=logout', function() {
    let app;

    let request;
    const modeLogout = require('../../../routes/logout');

    beforeEach(function() {
        // Create an express application object
        app = express();

        app.use('*', function(req, res, next) {
            req.logID = '9999999';
            next();
        });

        app.use(cookieParser());
        app.use(
            bodyParser.urlencoded({
                extended: false
            })
        );

        app.set('view engine', 'js');
        app.set('views', __dirname);

        app.engine('js', function(path, options, callback) {
            callback(null, JSON.stringify(options));
        });

        // Bind a route to our application
        modeLogout.route(app);

        // Get a supertest instance so we can make requests
        request = supertest(app);
    });

    it('should respond with a 302 and set Location to /auth/finish', function(done) {
        const doAPILogoutStub = sinon.stub(modeLogout, 'doAPILogout').resolves({
            body: {
                status: 'ok',
                track_id: trackID,
                cookies: [
                    'Session_id=; expires=Tue, 19 Jan 2038 03:14:07 GMT; Path=/; HttpOnly',
                    'sessionid2=; Domain=.yandex.ru; expires=Tue, 19 Jan 2038 03:14:07 GMT; Path=/; secure; HttpOnly'
                ]
            }
        });

        request
            .get('/passport?mode=logout&yu=0123456789')
            .set(headers)
            .expect('Location', /auth\/finish/)
            .expect(302)
            .end(function(err) {
                doAPILogoutStub.restore();

                if (err) {
                    return done(err);
                }
                return done();
            });
    });

    it('should respond with a 302 and put track_id in Location', function(done) {
        const doAPILogoutStub = sinon.stub(modeLogout, 'doAPILogout').resolves({
            body: {
                status: 'ok',
                track_id: trackID,
                cookies: [
                    'Session_id=; expires=Tue, 19 Jan 2038 03:14:07 GMT; Path=/; HttpOnly',
                    'sessionid2=; Domain=.yandex.ru; expires=Tue, 19 Jan 2038 03:14:07 GMT; Path=/; secure; HttpOnly'
                ]
            }
        });

        request
            .get('/passport?mode=logout&yu=0123456789')
            .set(headers)
            .expect('Location', `https://passport.yandex.ru/auth/finish?track_id=${trackID}`)
            .expect(302)
            .end(function(err) {
                doAPILogoutStub.restore();

                if (err) {
                    return done(err);
                }
                return done();
            });
    });

    it('should respond with a 302 and set Location to /profile if yu is absent', function(done) {
        request
            .get('/passport?mode=logout')
            .set(headers)
            .expect('Location', /profile/)
            .expect(302)
            .end(function(err) {
                if (err) {
                    return done(err);
                }
                return done();
            });
    });

    it('should respond with a 302 and set cookies', function(done) {
        const doAPILogoutStub = sinon.stub(modeLogout, 'doAPILogout').resolves({
            body: {
                status: 'ok',
                track_id: trackID,
                cookies: [
                    'Session_id=; expires=Tue, 19 Jan 2038 03:14:07 GMT; Path=/; HttpOnly',
                    'sessionid2=; Domain=.yandex.ru; expires=Tue, 19 Jan 2038 03:14:07 GMT; Path=/; secure; HttpOnly'
                ]
            }
        });

        request
            .get('/passport?mode=logout&yu=0123456789')
            .set(headers)
            .expect('Set-Cookie', /Session_id/)
            .expect(302)
            .end(function(err) {
                doAPILogoutStub.restore();

                if (err) {
                    return done(err);
                }
                return done();
            });
    });

    it('should redirect to /auth if API rejected with sessionid.invalid', function(done) {
        const doAPILogoutStub = sinon.stub(modeLogout, 'doAPILogout').rejects(['sessionid.invalid']);

        request
            .get('/passport?mode=logout&yu=0123456789')
            .set(headers)
            .expect(302)
            .expect('Location', /auth$/)
            .end(function(err) {
                doAPILogoutStub.restore();

                if (err) {
                    return done(err);
                }
                return done();
            });
    });

    it('should redirect to /auth if API rejected  with sessionid.no_uid', function(done) {
        const doAPILogoutStub = sinon.stub(modeLogout, 'doAPILogout').rejects(['sessionid.no_uid']);

        request
            .get('/passport?mode=logout&yu=0123456789')
            .set(headers)
            .expect(302)
            .expect('Location', /auth$/)
            .end(function(err) {
                doAPILogoutStub.restore();

                if (err) {
                    return done(err);
                }
                return done();
            });
    });

    it('should redirect to /profile if API rejected with csrf_token.invalid', function(done) {
        request
            .get('/passport?mode=logout&yu=AAAAAA')
            .set(headers)
            .expect(302)
            .expect('Location', /profile$/)
            .end(function(err) {
                if (err) {
                    return done(err);
                }
                return done();
            });
    });

    it('should render page with error if API rejected with unexpected error', function(done) {
        const doAPILogoutStub = sinon.stub(modeLogout, 'doAPILogout').rejects(['unexpected.error']);

        request
            .get('/passport?mode=logout&yu=0123456789')
            .set(headers)
            .expect(400)
            .expect(/"msg":"unexpected.error"/)
            .end(function(err) {
                doAPILogoutStub.restore();

                if (err) {
                    return done(err);
                }
                return done();
            });
    });
});

describe('modeLogout', function() {
    const PControllerStub = sinon.stub();
    const PApiLogoutStub = sinon.stub();
    const PApiStub = sinon.stub();
    const modeLogout = proxyquire('../../../routes/logout', {
        '../lib/controller': PControllerStub,
        '../lib/passport-api': {
            client: PApiStub
        }
    });
    const doRequest = modeLogout.doRequest;
    const getSuccessHandler = modeLogout.getSuccessHandler;
    const getErrorHandler = modeLogout.getErrorHandler;
    const getController = modeLogout.getController;
    const doAPILogout = modeLogout.doAPILogout;
    const chooseWay = modeLogout.chooseWay;
    const handleError = modeLogout.handleError;
    const renderError = modeLogout.renderError;
    const getRender = modeLogout.getRender;

    let getControllerStub;

    let doAPILogoutSpy;

    let getRenderStub;
    const req = {
        query: {
            mode: 'logout',
            yu: '111',
            ci: '222',
            global: '1',
            origin: 'ololo',
            retpath: 'https://ya.ru/'
        },
        cookies: {
            yandexuid: '111'
        },
        logID: '000',
        headers: {
            foo: 'bar'
        },
        blackbox: {
            connection_id: '222'
        }
    };

    let getSuccessHandlerStub;

    let getErrorHandlerStub;
    const augmentSpy = sinon.spy();
    const nextSpy = sinon.spy();
    const writeStatboxStub = sinon.stub();
    const redirectToFinishStub = sinon.stub();
    const redirectToFrontpageStub = sinon.stub();
    const redirectToLocalUrlStub = sinon.stub();
    const successHandlerSpy = sinon.stub();
    const errorHandlerSpy = sinon.stub();
    const resStatusStub = sinon.stub();
    const resRenderStub = sinon.stub();
    const renderStub = sinon.stub();
    const getLanguageStub = sinon.stub();
    const res = {};

    describe('doRequest', function() {
        beforeEach(function() {
            getControllerStub = sinon.stub(modeLogout, 'getController').returns({
                writeStatbox: writeStatboxStub,
                augmentResponse: augmentSpy,
                redirectToFrontpage: redirectToFrontpageStub,
                redirectToFinish: redirectToFinishStub,
                getLanguage: sinon.stub().resolves('ru')
            });

            doAPILogoutSpy = sinon.stub(modeLogout, 'doAPILogout').resolves({
                body: {
                    status: 'ok',
                    track_id: trackID,
                    cookies: [
                        'Session_id=; expires=Tue, 19 Jan 2038 03:14:07 GMT; Path=/; HttpOnly',
                        'sessionid2=; Domain=.yandex.ru; expires=Tue, 19 Jan 2038 03:14:07 GMT; Path=/; secure; HttpOnly'
                    ]
                }
            });

            getSuccessHandlerStub = sinon.stub(modeLogout, 'getSuccessHandler').returns(successHandlerSpy);
            getErrorHandlerStub = sinon.stub(modeLogout, 'getErrorHandler').returns(errorHandlerSpy);
        });

        afterEach(function() {
            getControllerStub.restore();
            doAPILogoutSpy.restore();
            getSuccessHandlerStub.restore();
            getErrorHandlerStub.restore();
            successHandlerSpy.reset();
            errorHandlerSpy.reset();
            augmentSpy.reset();
            nextSpy.reset();
            writeStatboxStub.reset();
        });

        it('should call next if yu is absent', function() {
            doRequest(
                {
                    query: {
                        mode: 'logout'
                    }
                },
                {},
                nextSpy
            );

            expect(nextSpy.called).to.be.ok();
        });

        it('should call next if neither yu neither ci is present', function() {
            doRequest(
                {
                    query: {
                        mode: 'logout'
                    }
                },
                {},
                nextSpy
            );

            expect(nextSpy.called).to.be.ok();
        });

        it('should call next with proper error if yu doesnt match req.cookies.yandexuid', function() {
            doRequest(
                {
                    query: {
                        mode: 'logout',
                        yu: '000'
                    },
                    cookies: {
                        yandexuid: '111'
                    }
                },
                {},
                nextSpy
            );

            expect(nextSpy.called).to.be.ok();
        });

        it('should call next with proper error if ci doesnt match req.blackbox.connection_id', function() {
            doRequest(
                {
                    query: {
                        mode: 'logout',
                        ci: '000'
                    }
                },
                {},
                nextSpy
            );

            expect(nextSpy.called).to.be.ok();
        });

        it('should call doAPILogout with requested query params', function() {
            doRequest(req, res);

            expect(
                doAPILogoutSpy.calledWith(req, {
                    yu: req.query.yu,
                    ci: req.query.ci,
                    is_global: req.query.global === '1',
                    origin: req.query.origin,
                    retpath: req.query.retpath
                })
            ).to.be.ok();
        });

        it('should call getSuccessHandler with right params', function() {
            doRequest(req, 1, 2);

            expect(getSuccessHandlerStub.calledWith(req, 1, 2)).to.be.ok();
        });

        it('should call getErrorHandler with right params', function() {
            doRequest(req, 1, 2);

            expect(getErrorHandlerStub.calledWith(req.logID, 2)).to.be.ok();
        });

        it('should call successHandler if API request succeeded', function(done) {
            successHandlerSpy.callsFake(function() {
                done();
            });

            errorHandlerSpy.callsFake(function() {
                done(new Error());
            });

            doRequest(req, res);
        });

        it('should call errorHandler if API request returned error', function(done) {
            doAPILogoutSpy.restore();
            doAPILogoutSpy = sinon.stub(modeLogout, 'doAPILogout').rejects(['sessionid.invalid']);
            errorHandlerSpy.callsFake(function() {
                done();
            });

            successHandlerSpy.callsFake(function() {
                done(new Error());
            });

            doRequest(req, res, nextSpy);
        });
    });

    describe('getSuccessHandler', function() {
        beforeEach(function() {
            getControllerStub = sinon.stub(modeLogout, 'getController').returns({
                augmentResponse: augmentSpy,
                redirectToFrontpage: redirectToFrontpageStub,
                redirectToFinish: redirectToFinishStub,
                getLanguage: sinon.stub().resolves('ru')
            });
        });

        afterEach(function() {
            getControllerStub.restore();
            augmentSpy.reset();
            nextSpy.reset();
        });

        it('should return function', function() {
            expect(typeof getSuccessHandler(req, res, nextSpy) === 'function').to.be.ok();
        });

        it('should return function which calls next with error if there is no body', function() {
            const handler = getSuccessHandler(req, res, nextSpy);

            handler({
                ololo: 'pepep'
            });

            expect(redirectToFinishStub.called).to.not.be.ok();
            expect(nextSpy.called).to.be.ok();
            expect(nextSpy.calledOnce).to.be.ok();
            expect(nextSpy.firstCall.args[0] instanceof Error).to.be.ok();
        });

        it('should return function which does not call redirectToFinish if there is no body', function() {
            const handler = getSuccessHandler(req, res, nextSpy);

            handler({
                ololo: 'pepep'
            });

            expect(redirectToFinishStub.called).to.not.be.ok();
        });

        it('should return function which calls augmentResponse', function() {
            const handler = getSuccessHandler(req, res, nextSpy);

            handler({
                body: {
                    cookies: [
                        'Session_id=; expires=Tue, 19 Jan 2038 03:14:07 GMT; Path=/; HttpOnly',
                        'sessionid2=; Domain=.yandex.ru; expires=Tue, 19 Jan 2038 03:14:07 GMT; Path=/; secure; HttpOnly'
                    ]
                }
            });

            expect(augmentSpy.called).to.be.ok();
        });

        it('should return function which calls redirectToFinish if there is body', function() {
            const handler = getSuccessHandler(req, res, nextSpy);

            handler({
                body: {
                    cookies: [
                        'Session_id=; expires=Tue, 19 Jan 2038 03:14:07 GMT; Path=/; HttpOnly',
                        'sessionid2=; Domain=.yandex.ru; expires=Tue, 19 Jan 2038 03:14:07 GMT; Path=/; secure; HttpOnly'
                    ]
                }
            });

            expect(redirectToFinishStub.called).to.be.ok();
        });

        it('should return function which calls redirectToFinish with track_id from response', function() {
            const handler = getSuccessHandler(req, res, nextSpy);

            handler({
                body: {
                    track_id: trackID
                }
            });

            expect(redirectToFinishStub.calledWith(trackID)).to.be.ok();
        });
    });

    describe('getErrorHandler', function() {
        afterEach(function() {
            nextSpy.reset();
        });

        it('should return function', function() {
            expect(typeof getErrorHandler(req.logID, nextSpy) === 'function').to.be.ok();
        });

        it('should return function which calls next with error', function() {
            const handler = getErrorHandler(req.logID, nextSpy);
            const error = 'i am error';

            handler(error);

            expect(nextSpy.called).to.be.ok();
            expect(nextSpy.calledOnce).to.be.ok();
            expect(nextSpy.firstCall.args[0] === error).to.be.ok();
        });
    });

    describe('getController', function() {
        afterEach(function() {
            PControllerStub.reset();
        });

        it('should call PController if there is no _controller in request', function() {
            getController(req, res);

            expect(PControllerStub.called).to.be.ok();
        });

        it('should not call PController if there is _controller in request', function() {
            getController(
                {
                    _controller: true
                },
                res
            );

            expect(PControllerStub.called).to.not.be.ok();
        });
    });

    describe('doAPILogout', function() {
        beforeEach(function() {
            PApiStub.resolves({
                logout: PApiLogoutStub
            });
        });

        afterEach(function() {
            PApiStub.reset();
            PApiLogoutStub.reset();
        });

        it('should call PApi.client', function() {
            doAPILogout(req, {olo: 'lo'});

            expect(PApiStub.called).to.be.ok();
        });

        it('should call PApi.client with req.headers and req.logID', function() {
            doAPILogout(req, {olo: 'lo'});

            expect(PApiStub.calledWith(req)).to.be.ok();
        });

        it('should call method logout of PApi instance with opts', function(done) {
            PApiStub.reset();
            PApiStub.resolves({
                logout(opts) {
                    try {
                        expect(opts).to.eql({
                            olo: 'olo'
                        });
                        done();
                    } catch (e) {
                        done(e);
                    }
                }
            });
            doAPILogout(req, {olo: 'olo'});
        });
    });

    describe('chooseWay', function() {
        afterEach(function() {
            nextSpy.reset();
        });

        it('should call next without args if there is mode=logout in url', function() {
            chooseWay(req, res, nextSpy);

            expect(nextSpy.called).to.be.ok();
            expect(nextSpy.calledOnce).to.be.ok();
            expect(nextSpy.lastCall.args.length === 0).to.be.ok();
        });

        it('should call next with "route" if there is no mode=logout in url', function() {
            chooseWay(
                {
                    query: {
                        mode: 'login'
                    }
                },
                res,
                nextSpy
            );

            expect(nextSpy.called).to.be.ok();
            expect(nextSpy.calledOnce).to.be.ok();
            expect(nextSpy.calledWith('route')).to.be.ok();
        });
    });

    describe('handleError', function() {
        beforeEach(function() {
            getControllerStub = sinon.stub(modeLogout, 'getController').returns({
                writeStatbox: writeStatboxStub,
                augmentResponse: augmentSpy,
                redirectToFrontpage: redirectToFrontpageStub,
                redirectToLocalUrl: redirectToLocalUrlStub
            });
        });

        afterEach(function() {
            getControllerStub.restore();
            redirectToFrontpageStub.reset();
            redirectToLocalUrlStub.reset();
            nextSpy.reset();
            writeStatboxStub.reset();
        });

        it('should call getController', function() {
            handleError(['error.code'], req, res, nextSpy);

            expect(getControllerStub.called).to.be.ok();
            expect(getControllerStub.calledOnce).to.be.ok();
            expect(getControllerStub.lastCall.args.length === 2).to.be.ok();
        });

        it('should call next with Error if it is not Array', function() {
            handleError(new Error(), req, res, nextSpy);

            expect(nextSpy.called).to.be.ok();
            expect(nextSpy.calledOnce).to.be.ok();
            expect(nextSpy.lastCall.args[0] instanceof Error).to.be.ok();
        });

        it('should not call redirectTo* if Error is not Array', function() {
            handleError(new Error(), req, res, nextSpy);

            expect(redirectToFrontpageStub.called).to.not.be.ok();
            expect(redirectToLocalUrlStub.called).to.not.be.ok();
        });

        it('should call redirectToFrontpage if there is csrf_token.invalid error', function() {
            handleError(['csrf_token.invalid'], req, res, nextSpy);

            expect(writeStatboxStub.called).to.be.ok();
            expect(redirectToFrontpageStub.called).to.be.ok();
            expect(redirectToLocalUrlStub.called).to.not.be.ok();
            expect(nextSpy.called).to.not.be.ok();
        });

        it('should call redirectToLocalUrl if there is sessionid.invalid error', function() {
            handleError(['sessionid.invalid'], req, res, nextSpy);

            expect(redirectToLocalUrlStub.called).to.be.ok();
            expect(
                redirectToLocalUrlStub.calledWith({
                    pathname: 'auth'
                })
            ).to.be.ok();
            expect(redirectToFrontpageStub.called).to.not.be.ok();
            expect(nextSpy.called).to.not.be.ok();
        });

        it('should call redirectToLocalUrl if there is sessionid.no_uid error', function() {
            handleError(['sessionid.no_uid'], req, res, nextSpy);

            expect(redirectToLocalUrlStub.called).to.be.ok();
            expect(
                redirectToLocalUrlStub.calledWith({
                    pathname: 'auth'
                })
            ).to.be.ok();
            expect(redirectToFrontpageStub.called).to.not.be.ok();
            expect(nextSpy.called).to.not.be.ok();
        });

        it('should call next with error if there is unknown error', function() {
            handleError(['unknown.error'], req, res, nextSpy);

            expect(redirectToFrontpageStub.called).to.not.be.ok();
            expect(redirectToLocalUrlStub.called).to.not.be.ok();

            expect(nextSpy.called).to.be.ok();
            expect(nextSpy.calledWith(['unknown.error'])).to.be.ok();
        });
    });

    describe('renderError', function() {
        beforeEach(function() {
            res.status = resStatusStub.returns({
                render: resRenderStub
            });

            getControllerStub = sinon.stub(modeLogout, 'getController').returns({
                writeStatbox: writeStatboxStub,
                augmentResponse: augmentSpy,
                getLanguage: getLanguageStub.resolves('ru')
            });

            getRenderStub = sinon.stub(modeLogout, 'getRender').returns(renderStub);
        });

        afterEach(function() {
            getControllerStub.restore();
            getRenderStub.restore();
            resStatusStub.reset();
            resRenderStub.reset();
            renderStub.reset();
            getLanguageStub.reset();
            writeStatboxStub.reset();
        });

        it('should call getController', function() {
            renderError(['error.code'], req, res, nextSpy);

            expect(getControllerStub.called).to.be.ok();
            expect(getControllerStub.calledOnce).to.be.ok();
            expect(getControllerStub.lastCall.args.length === 2).to.be.ok();
        });

        it('should call controller.getLanguage', function() {
            renderError(['error.code'], req, res, nextSpy);

            expect(getLanguageStub.called).to.be.ok();
            expect(getLanguageStub.calledOnce).to.be.ok();
            expect(getLanguageStub.lastCall.args.length === 0).to.be.ok();
        });

        it('should call getRender with res and context', function() {
            renderError(['error.code'], req, res, nextSpy);

            expect(getRenderStub.called).to.be.ok();
            expect(getRenderStub.calledOnce).to.be.ok();
            expect(getRenderStub.lastCall.args.length === 2).to.be.ok();
        });

        it('should put msg in contect with error code if error is array', function() {
            renderError(['error.code'], req, res, nextSpy);

            expect(getRenderStub.lastCall.args[1]).to.eql({
                retpath: '/profile',
                statusCode: 400,
                msg: 'error.code'
            });
        });

        it('should not put msg in contect with error code if error is not array', function() {
            renderError(new Error(), req, res, nextSpy);

            expect(getRenderStub.lastCall.args[1]).to.eql({
                retpath: '/profile',
                statusCode: 400
            });
        });

        it('should call render with language from getLanguage', function(done) {
            getLanguageStub.reset();
            getLanguageStub.resolves('id');

            renderStub.reset();
            renderStub.callsFake(function(lang) {
                try {
                    expect(lang === 'id').to.be.ok();
                    done();
                } catch (e) {
                    done(e);
                }
            });

            renderError(['error.code'], req, res, nextSpy);
        });

        it('should call render without language if getLanguage rejects', function(done) {
            getLanguageStub.reset();
            getLanguageStub.rejects(new Error());

            renderStub.reset();
            renderStub.callsFake(function(lang) {
                try {
                    expect(lang === undefined).to.be.ok();
                    done();
                } catch (e) {
                    done(e);
                }
            });

            renderError(['error.code'], req, res, nextSpy);
        });
    });

    describe('getRender', function() {
        beforeEach(function() {
            res.status = resStatusStub.returns({
                render: resRenderStub
            });
        });

        afterEach(function() {
            resStatusStub.reset();
            resRenderStub.reset();
        });

        it('should return function', function() {
            expect(typeof getRender(res, {statusCode: 400}) === 'function').to.be.ok();
        });

        it('should return function which calls res.statusCode with context.statusCode', function() {
            const handler = getRender(res, {statusCode: 400});

            handler('ru');

            expect(resStatusStub.called).to.be.ok();
            expect(resStatusStub.calledOnce).to.be.ok();
            expect(resStatusStub.firstCall.args[0] === 400).to.be.ok();
        });

        it('should return function which calls res.render with language if it is set', function() {
            const context = {statusCode: 400};
            const handler = getRender(res, context);

            handler('uk');

            expect(resRenderStub.called).to.be.ok();
            expect(resRenderStub.calledOnce).to.be.ok();
            expect(resRenderStub.firstCall.args[0] === 'error.uk.js').to.be.ok();
            expect(resRenderStub.firstCall.args[1] === context).to.be.ok();
        });

        it('should return function which calls res.render with ru if language is absent', function() {
            const context = {statusCode: 400};
            const handler = getRender(res, context);

            handler();

            expect(resRenderStub.called).to.be.ok();
            expect(resRenderStub.calledOnce).to.be.ok();
            expect(resRenderStub.firstCall.args[0] === 'error.ru.js').to.be.ok();
            expect(resRenderStub.firstCall.args[1] === context).to.be.ok();
        });

        it('should return function which calls res.render with ru if language is unknown', function() {
            const context = {statusCode: 400};
            const handler = getRender(res, context);

            handler('ololo');

            expect(resRenderStub.called).to.be.ok();
            expect(resRenderStub.calledOnce).to.be.ok();
            expect(resRenderStub.firstCall.args[0] === 'error.ru.js').to.be.ok();
            expect(resRenderStub.firstCall.args[1] === context).to.be.ok();
        });
    });
});
