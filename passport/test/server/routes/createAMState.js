const express = require('express');
const request = require('supertest');
const expect = require('expect.js');
const {rootRoute} = require('../../../routes/auth.v2');
const {urlParse} = require('../../../routes/common/urlFormat');

describe('#createAmState', function() {
    beforeEach(function() {
        this.mockMiddleware = (req, res, next) => {
            Object.assign(req, {
                body: {},
                logID: '0',
                cookies: {},
                _controller: {
                    getUatraits() {
                        return Promise.resolve({
                            BrowserVersion: 0
                        });
                    },
                    getLanguage() {
                        return Promise.resolve('ru');
                    },
                    getYaExperimentInfoPromise() {
                        return Promise.resolve({flags: []});
                    },
                    getUrl() {
                        return urlParse('https://yandex.ru/am');
                    },
                    getTld() {
                        return 'ru';
                    },
                    getLanglist() {
                        return Promise.resolve(['ru']);
                    },
                    getRequestParam() {
                        return;
                    },
                    getCookie() {
                        return;
                    },
                    getAuth() {
                        return {
                            sessionID() {
                                return Promise.resolve();
                            }
                        };
                    },
                    hasExp() {
                        return;
                    },
                    _getApiPromise() {
                        return Promise.resolve({
                            validateBackpath() {
                                return Promise.resolve({});
                            },
                            authSuggest() {
                                return Promise.resolve({});
                            }
                        });
                    },
                    writeStatbox() {}
                }
            });

            this._res = res;

            next();
        };
    });

    it('should create proper state', function(done) {
        const app = express();

        app.get('/', [
            this.mockMiddleware,
            ...rootRoute.slice(0, rootRoute.length - 1),
            function(_, res) {
                res.status(200);
                res.send();
            }
        ]);

        request
            .agent(app)
            .get('/?app_platform=ios')
            .timeout(2000)
            .expect(200, (error) => {
                expect(this._res.locals.store.am.isAm).equal(true);
                expect(this._res.locals.store.common.isWebView).equal(true);

                done(error);
            });
    });

    it('should redirect to error when app_platform invalid', function(done) {
        const app = express();

        app.get('/', [
            this.mockMiddleware,
            ...rootRoute.slice(0, rootRoute.length - 1),
            function(_, res) {
                res.status(200);
                res.send();
            }
        ]);

        request
            .agent(app)
            .get('/')
            .timeout(2000)
            .expect(302, (error, res) => {
                if (error) {
                    return done(error);
                }

                expect(res.headers['location']).to.equal('/am/finish?status=error');

                done();
            });
    });
});
