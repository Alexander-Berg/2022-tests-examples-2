var expect = require('expect.js');
var sinon = require('sinon');
var when = require('when');
var _ = require('lodash');
var reqRes = require('./../tools/expressReqRes');

var AuthenticationController = require('../Authentication');

describe('BlackboxAO', function() {
    beforeEach(function() {
        this.AO = AuthenticationController.BlackboxAO;
    });

    describe('apiFailCheck', function() {
        beforeEach(function() {
            this.logger = new (require('plog'))('safsadfdsf');

            this.okBody = {
                error: 'OK',
                data: 'whatso'
            };

            this.erroneousBody = {
                exception: {
                    value: 'whatsoever',
                    id: 1
                },
                error: 'whatever'
            };

            this.response = {
                statusCode: 200
            };

            this.RetryCondition = require('pdao').RetryCondition;
        });

        it('should return a RetryCondition error if status is not 200', function() {
            this.response.statusCode = 500;
            expect(this.AO.apiFailCheck(this.logger, this.response, this.okBody)).to.be.a(this.RetryCondition);
        });

        it('should return a RetryCondition error if response has DB_FETCHFAILED exception', function() {
            this.erroneousBody.exception.id = AuthenticationController.BlackboxErrorTypes.DB_FETCHFAILED;
            expect(this.AO.apiFailCheck(this.logger, this.response, this.erroneousBody)).to.be.a(this.RetryCondition);
        });

        it('should return a RetryCondition error if response has DB_EXCEPTION exception', function() {
            this.erroneousBody.exception.id = AuthenticationController.BlackboxErrorTypes.DB_EXCEPTION;
            expect(this.AO.apiFailCheck(this.logger, this.response, this.erroneousBody)).to.be.a(this.RetryCondition);
        });

        it('should return undefined for an okayish blackbox response', function() {
            expect(this.AO.apiFailCheck(this.logger, this.response, this.okBody)).to.be(undefined);
        });
    });

    describe('constructor', function() {
        it('should bind apiFailCheck to __self', function() {
            sinon.stub(this.AO.apiFailCheck, 'bind');

            new this.AO('safsdfdsf', 'safsdfdsf');
            expect(this.AO.apiFailCheck.bind.calledOnce).to.be(true);
            expect(this.AO.apiFailCheck.bind.calledWithExactly(this.AO)).to.be(true);

            this.AO.apiFailCheck.bind.restore();
        });
    });
});

describe('Authentication controller', function() {
    beforeEach(function() {
        this.sinon = sinon.sandbox.create();

        this.req = reqRes.req();
        this.res = reqRes.res();
        this.logId = 'EVoaDephoot7fu0ooZ2osai5cah6Eefi';

        this.authController = new AuthenticationController(this.req, this.res, this.logId);
    });
    afterEach(function() {
        this.sinon.restore();
    });

    describe('static', function() {
        describe('getBlackboxErrorType', function() {
            beforeEach(function() {
                this.bbResponse = {
                    exception: {
                        value: 'whatsoever',
                        id: 1
                    },
                    error: 'whatever'
                };
                this.Types = AuthenticationController.BlackboxErrorTypes;
            });

            it('should return null if nothing is passed', function() {
                expect(AuthenticationController.getBlackboxErrorType()).to.be(null);
            });

            it('should return null if there is no exception field', function() {
                delete this.bbResponse.exception;
                expect(AuthenticationController.getBlackboxErrorType(this.bbResponse)).to.be(null);
            });

            it('should return UNKNOWN type if exception.id is unknown', function() {
                this.bbResponse.exception.id = 123123123;
                expect(AuthenticationController.getBlackboxErrorType(this.bbResponse)).to.be(this.Types.UNKNOWN);
            });

            _.each(AuthenticationController.BlackboxErrorTypes, function(value, key) {
                it('should return ' + key + ' type if exception.id is ' + value, function() {
                    this.bbResponse.exception.id = value;
                    expect(AuthenticationController.getBlackboxErrorType(this.bbResponse)).to.be(this.Types[key]);
                });
            });
        });
    });

    describe('blackbox', function() {
        describe('get', function() {
            it('should throw if setBlackbox was not called before', function() {
                var controller = this.authController;

                expect(function() {
                    controller.getBlackbox();
                }).to.throwError(function(e) {
                    expect(e.message).to.be('Set the blackbox path with auth.setBlackbox(path)');
                });
            });
        });

        describe('set', function() {
            it('should throw if called with anything but a string', function() {
                var controller = this.authController;

                expect(function() {
                    controller.setBlackbox(123);
                }).to.throwError(function(e) {
                    expect(e.message).to.be('Blackbox path should be an url string');
                });
            });

            it('should throw when called with an empty string', function() {
                var controller = this.authController;

                expect(function() {
                    controller.setBlackbox('');
                }).to.throwError(function(e) {
                    expect(e.message).to.be('Blackbox path should be an url string');
                });
            });

            it('should set the blackbox path', function() {
                var blackboxHost = 'mda-dev.yandex.net';

                expect(this.authController.setBlackbox(blackboxHost).getBlackbox()).to.be(blackboxHost);
            });
        });
    });

    describe('sessionID', function() {
        beforeEach(function() {
            this.sessionid = '123';
            this.sessionid2 = '456';
            this.sinon
                .stub(this.authController, 'getCookie')
                .withArgs('Session_id')
                .returns(this.sessionid)
                .withArgs('sessionid2')
                .returns(this.sessionid2);

            this.ip = '257.258.259.300';
            this.sinon.stub(this.authController, 'getIp').returns(this.ip);

            this.host = 'billgates.com';
            this.sinon
                .stub(this.authController, 'getHeader')
                .withArgs('host')
                .returns(this.host);

            this.sinon.stub(this.authController, 'resign');

            this.blackbox = {
                some: 'data',
                error: 'OK',
                status: {
                    value: null,
                    id: null
                }
            };

            this.blackboxAO = new AuthenticationController.BlackboxAO(this.logId, 'blackboxpath');
            sinon.stub(this.blackboxAO, 'call').returns(when.resolve(this.blackbox));

            this.sinon.stub(this.authController, 'getBlackboxAO').returns(this.blackboxAO);
        });

        it('should return a promise', function() {
            expect(when.isPromiseLike(this.authController.sessionID())).to.be(true);
        });

        it('should pass user ip to blackbox', function() {
            this.authController.sessionID();
            expect(this.blackboxAO.call.firstCall.args[2]).to.have.property('userip', this.ip);
        });

        it('should pass sessionid to blackbox', function() {
            this.authController.sessionID();
            expect(this.blackboxAO.call.firstCall.args[2]).to.have.property('sessionid', this.sessionid);
        });

        it('should pass sslsessionid to blackbox', function() {
            this.authController.sessionID();
            expect(this.blackboxAO.call.firstCall.args[2]).to.have.property('sslsessionid', this.sessionid2);
        });

        it('should pass host to blackbox', function() {
            this.authController.sessionID();
            expect(this.blackboxAO.call.firstCall.args[2]).to.have.property('host', this.host);
        });

        it('should remove port from the host before passing it to blackbox', function() {
            this.authController.getHeader.withArgs('host').returns(this.host + ':123123123');

            this.authController.sessionID();
            expect(this.blackboxAO.call.firstCall.args[2]).to.have.property('host', this.host);
        });

        it('should call blackboxAO with get to sessionid', function() {
            this.authController.sessionID();
            expect(this.blackboxAO.call.calledWith('get', 'sessionid')).to.be(true);
        });

        it('should resolve with blackbox response if cookie status is VALID', function(done) {
            var that = this;

            this.blackbox.status.value = 'VALID';

            this.authController
                .sessionID()
                .then(function(response) {
                    expect(response).to.eql(that.blackbox);
                    done();
                })
                .then(null, done);
        });

        it('should save the blackbox response if cookie status is VALID', function(done) {
            var blackbox = this.blackbox;

            this.blackbox.status.value = 'VALID';

            var authController = this.authController;

            authController
                .sessionID()
                .then(function() {
                    expect(authController._getLastLoginInfo()).to.eql(blackbox);
                    done();
                })
                .then(null, done);
        });

        it('should not make second request to blackbox', function(done) {
            var bbAO = this.blackboxAO;

            when.all([
                this.authController.sessionID(),
                this.authController.sessionID(),
                this.authController.sessionID()
            ])
                .then(
                    function() {
                        expect(bbAO.call.calledOnce).to.be(true);
                        done();
                    },
                    function() {
                        done('Expected the promise to be resolved');
                    }
                )
                .then(null, done);
        });

        it('should resolve with null if blackbox successfully responded with an empty message', function(done) {
            this.blackboxAO.call.returns(when.resolve());
            this.authController
                .sessionID()
                .then(function(result) {
                    expect(result).to.be(null);
                    done();
                })
                .then(null, done);
        });

        it(
            'should resolve with null if user is in root mda domain and cookie status it ' +
                'neither VALID, nor NEED_RESET',
            function(done) {
                this.blackbox.status.value = 'BLAH';

                this.authController
                    .sessionID()
                    .then(function(result) {
                        expect(result).to.be(null);
                        done();
                    })
                    .then(null, done);
            }
        );

        it(
            'should throw error need_resign if user is in root mda domain and cookie ' + 'status is NEED_RESET',
            function(done) {
                this.blackbox.status.value = 'NEED_RESET';

                this.authController
                    .sessionID()
                    .then(
                        function() {
                            throw new Error('Expected the promise to be rejected, the process should not proceed');
                        },
                        function(err) {
                            expect(err.code === 'need_resign').to.be(true);
                            done();
                        }
                    )
                    .then(null, done);
            }
        );

        it('should resolve with null if user is not in root mda domain and cookie status is NOAUTH', function(done) {
            this.blackbox.status.value = 'NOAUTH';

            this.authController
                .sessionID()
                .then(function(result) {
                    expect(result).to.be(null);
                    done();
                })
                .then(null, done);
        });

        it('should not save the blackbox response if cookie status is not VALID', function(done) {
            this.blackbox.status.value = 'BLAH';

            var authController = this.authController;

            authController
                .sessionID()
                .then(function() {
                    expect(authController._getLastLoginInfo()).to.eql({});

                    done();
                })
                .then(null, done);
        });

        it('should reject with an error if blackbox responded with an error', function(done) {
            this.blackbox.exception = {
                id: AuthenticationController.BlackboxErrorTypes.ACCESS_DENIED
            };
            this.blackboxAO.call.returns(when.resolve(this.blackbox));

            var BlackboxException = AuthenticationController.BlackboxException;

            this.authController
                .sessionID()
                .then(
                    function() {
                        throw new Error('Expected the deferred to be rejected');
                    },
                    function(err) {
                        expect(err).to.be.a(BlackboxException);
                        done();
                    }
                )
                .then(null, done);
        });

        it(
            'should resolve with null without calling blackbox if sessionid cookie is empty ' +
                'and user is on an mda root domain',
            function(done) {
                var bbAO = this.blackboxAO;

                this.authController.getCookie.withArgs('Session_id').returns('');

                this.authController
                    .sessionID()
                    .then(
                        function(result) {
                            expect(result).to.be(null);
                            expect(bbAO.call.called).to.be(false);
                            done();
                        },
                        function() {
                            throw new Error('Expected the deferred to be resolved');
                        }
                    )
                    .then(null, done);
            }
        );

        it('should make a request to blackbox if sessionid2 cookie is empty and ' + 'protocol is https', function(
            done
        ) {
            var bbAO = this.blackboxAO;

            this.authController.getCookie.withArgs('sessionid2').returns('');

            this.sinon.stub(this.authController, 'getUrl').returns({
                protocol: 'https:'
            });

            this.authController
                .sessionID()
                .then(
                    function() {
                        expect(bbAO.call.called).to.be(true);
                        done();
                    },
                    function() {
                        throw new Error('Expected the deferred to be resolved');
                    }
                )
                .then(null, done);
        });

        describe('queryparams', function() {
            beforeEach(function() {
                this.default = {
                    iama: 'default'
                };
                this.sinon.stub(this.authController, 'getDeaultQueryParams').returns(this.default);
            });
            it('should be passed to blackbox route if any are given', function() {
                this.authController.sessionID({a: 'bc'});
                expect(this.blackboxAO.call.firstCall.args[2]).to.have.property('a', 'bc');
            });

            it('should be extended with default query params', function() {
                var explicit = {a: 'bc'};

                this.authController.sessionID(explicit);
                expect(this.blackboxAO.call.firstCall.args[2]).to.have.property('iama', this.default.iama);
            });

            it('should not be overwritten by default query params', function() {
                this.authController.sessionID({iama: 'explicit'});
                expect(this.blackboxAO.call.firstCall.args[2]).to.have.property('iama', 'explicit');
            });
        });
    });

    describe('loggedIn', function() {
        beforeEach(function() {
            this.sinon.stub(this.authController, 'sessionID').returns(when.resolve(null));
        });

        it('should resolve with true if sessionid request returns a truthy value', function(done) {
            this.authController.sessionID.returns(when.resolve({some: 'data'}));
            this.authController
                .loggedIn()
                .then(function(loggedIn) {
                    expect(loggedIn).to.be(true);
                    done();
                })
                .then(null, done);
        });

        it('should resolve with false if sessionid request returns a falsey value', function(done) {
            this.authController
                .loggedIn()
                .then(function(loggedIn) {
                    expect(loggedIn).to.be(false);
                    done();
                })
                .then(null, done);
        });
    });

    describe('attributeWasRequested', function() {
        beforeEach(function() {
            this.attribute = AuthenticationController.BB_ATTRIBUTES.GLOBAL_LOGOUT_TIME;

            sinon.stub(this.authController, 'getBlackboxAO').returns({call: when.resolve()});

            sinon.stub(this.authController, 'getCookie').returns('');
        });

        it('should throw if unknown attribute is given', function() {
            var that = this;

            expect(function() {
                that.authController.attributeWasRequested('uknown');
            }).to.throwError(function(err) {
                expect(err.message).to.be('Unknown attribute');
            });
        });

        it('should return false if attribute was requested but the response was not received yet', function() {
            this.authController.sessionID({attributes: this.attribute});
            expect(this.authController.attributeWasRequested(this.attribute)).to.be(false);
        });

        it('should return false if attribute was not requested', function(done) {
            var that = this;

            this.authController
                .sessionID()
                .then(function() {
                    expect(that.authController.attributeWasRequested(that.attribute)).to.be(false);

                    done();
                })
                .catch(done);
        });
    });

    describe('getAttribute', function() {
        beforeEach(function() {
            this.response = {attributes: {}};
            this.attributeKey = 'GLOBAL_LOGOUT_TIME';
            this.attribute = AuthenticationController.BB_ATTRIBUTES[this.attributeKey];
            this.response.attributes[this.attribute] = '1418650230';

            this.sinon.stub(this.authController, '_getLastLoginInfo').returns(this.response);
            sinon.stub(this.authController, 'attributeWasRequested').returns(true);
        });

        it('should throw if unknown attribute is passed', function() {
            this.authController.attributeWasRequested.restore();

            var that = this;

            expect(function() {
                that.authController.getAttribute('uknown');
            }).to.throwError(function(err) {
                expect(err.message).to.be('Unknown attribute');
            });
        });

        it('should return an attribute from the last sessionid call response', function() {
            expect(this.authController.getAttribute(this.attribute)).to.be(this.response.attributes[this.attribute]);
        });

        it('should return an attribute when arg is an int', function() {
            expect(this.authController.getAttribute(Number(this.attribute))).to.be(
                this.response.attributes[this.attribute]
            );
        });

        it('should throw if attribute was not requested', function() {
            this.authController.attributeWasRequested.returns(false);

            var that = this;

            expect(function() {
                that.authController.getAttribute(that.attribute);
            }).to.throwError(function(err) {
                expect(err.message).to.be('Attribute was not requested');
            });
        });

        it('should return default attribute value if attribute was not present in the last response', function() {
            this.authController._getLastLoginInfo.returns({});
            expect(this.authController.getAttribute(this.attribute)).to.be(
                AuthenticationController.BB_ATTRIBUTE_DEFAULTS[this.attributeKey]
            );
        });
    });

    var testRedirectMethod = function(methodName, urlPathname) {
        describe(methodName, function() {
            beforeEach(function() {
                this.url = 'http://google.com/search?q=123';
                this.sinon.stub(this.authController, 'getUrl').returns(require('url').parse(this.url));
                this.sinon.stub(this.authController, 'getTld').returns('com');

                this.sinon.stub(this.authController, 'redirect');
                this.authController[methodName]();
            });

            it('should accept redirect method and call it', function() {
                expect(this.authController.redirect.calledOnce).to.be(true);
            });

            it('should redirect to auth', function() {
                var separatorChar = urlPathname.indexOf('?') > -1 ? '\\&' : '\\?';

                expect(this.authController.redirect.firstCall.args[0]).to.match(
                    new RegExp('^.+\\.yandex\\.(:?ru|com|com\\.tr)\\/' + urlPathname + separatorChar + 'retpath=')
                );
            });

            ['ru', 'com', 'com.tr', 'ua', 'kz'].forEach(function(domain) {
                it('should redirect to passport at domain .' + domain + ' when user is on .' + domain, function() {
                    this.authController.getTld.returns(domain);
                    this.authController[methodName]();
                    expect(this.authController.redirect.secondCall.args[0]).to.match(
                        new RegExp('^https:\\/{2}passport\\.yandex\\.' + domain + '\\/')
                    );
                });
            });

            it('should create a retpath by urlencoding protocol, host and pathname', function() {
                var parsedRedirect = require('url').parse(this.authController.redirect.firstCall.args[0]);

                expect(parsedRedirect.query).to.be.a('string');

                var retpath = parsedRedirect.query.match(/retpath=([^&]+)/);

                expect(retpath.length).to.be.greaterThan(0);
                expect(retpath[0]).to.be('retpath=' + encodeURIComponent(this.url));
            });

            [
                {
                    name: 'development',
                    host: '0.passportdev',
                    regexp: /https:\/\/0\.passportdev\.yandex\./
                },
                {
                    name: 'testing',
                    host: 'passport-test',
                    regexp: /https:\/\/passport-test\.yandex\./
                },
                {
                    name: 'rc',
                    host: 'passport-rc',
                    regexp: /https:\/\/passport-rc\.yandex\./
                }
            ].forEach(function(env) {
                it('should redirect to ' + env.host + ' if NODE_ENV is "' + env.name + '"', function() {
                    var originalNODEENV = process.env.NODE_ENV;

                    process.env.NODE_ENV = env.name;

                    this.authController[methodName]();
                    expect(this.authController.redirect.secondCall.args[0]).to.match(env.regexp);

                    process.env.NODE_ENV = originalNODEENV;
                });
            });
        });
    };

    testRedirectMethod('authorize', 'auth');
    testRedirectMethod('lightauth2full', '\\?mode=lightauth2full');
    testRedirectMethod('obtainSecureCookie', 'auth/secure');

    describe('isLoggedIn', function() {
        beforeEach(function() {
            this.sinon.stub(this.authController, 'getUid');
        });

        it('should return true if uid is known', function() {
            this.authController.getUid.returns('123123');
            expect(this.authController.isLoggedIn()).to.be(true);
        });

        it('should return false if uid is null', function() {
            this.authController.getUid.returns(null);
            expect(this.authController.isLoggedIn()).to.be(false);
        });
    });

    describe('isHosted', function() {
        beforeEach(function() {
            this.response = {
                uid: {
                    hosted: 1
                }
            };
            this.sinon.stub(this.authController, '_getLastLoginInfo').returns(this.response);
        });

        it('should return true if blackbox response had truthy uid.hosted value', function() {
            this.response.uid.hosted = 1;
            expect(this.authController.isHosted()).to.be(true);
        });

        it('should return false if blackbox response had falsey uid.hosted value', function() {
            this.response.uid.hosted = 0;
            expect(this.authController.isHosted()).to.be(false);
        });
    });

    describe('isLite', function() {
        beforeEach(function() {
            this.response = {
                uid: {
                    lite: 1
                }
            };
            this.sinon.stub(this.authController, '_getLastLoginInfo').returns(this.response);
        });

        it('should return true if blackbox response had truthy uid.lite value', function() {
            this.response.uid.lite = 1;
            expect(this.authController.isLite()).to.be(true);
        });

        it('should return false if blackbox response had falsey uid.lite value', function() {
            this.response.uid.lite = 0;
            expect(this.authController.isLite()).to.be(false);
        });
    });

    describe('getGLogoutTime', function() {
        beforeEach(function() {
            this.ggtime = {};
            sinon.stub(this.authController, 'getAttribute').returns(this.ggtime);
        });

        it('should call getAttribute for the glogout time attribute', function() {
            this.authController.getGLogoutTime();
            expect(this.authController.getAttribute.calledOnce).to.be(true);

            expect(
                this.authController.getAttribute.calledWithExactly(
                    AuthenticationController.BB_ATTRIBUTES.GLOBAL_LOGOUT_TIME
                )
            ).to.be(true);
        });

        it('should return the result of calling getAttribute', function() {
            expect(this.authController.getGLogoutTime()).to.be(this.ggtime);
        });
    });

    describe('getPasswordEntryDate', function() {
        beforeEach(function() {
            this.now = Math.floor(Date.now() / 1000);
            this.response = {authid: {time: this.now}, auth: {password_verification_age: 10}};
            this.sinon.stub(this.authController, '_getLastLoginInfo').returns(this.response);
        });

        it('should return Date in common cases', function() {
            expect(this.authController.getPasswordEntryDate() instanceof Date).to.be(true);
        });

        it('should return valid Date', function() {
            expect(isNaN(this.authController.getPasswordEntryDate())).to.be(false);
        });

        it('should return valid Date in past', function() {
            expect(this.authController.getPasswordEntryDate()).to.be.below(new Date());
        });

        it('should return null when password_verification_age is -1', function() {
            this.response.auth.password_verification_age = -1;
            expect(this.authController.getPasswordEntryDate()).to.be(null);
        });

        it('should return null when there is no auth data', function() {
            delete this.response.auth;
            expect(this.authController.getPasswordEntryDate()).to.be(null);
        });
    });

    describe('isAutologged', function() {
        it('should return false when isLite returns false', function() {
            this.sinon.stub(this.authController, 'isLite').returns(false);
            expect(this.authController.isAutologged()).to.be(false);
        });

        it('should return false when user has verified password', function() {
            this.sinon.stub(this.authController, 'getPasswordEntryDate').returns(new Date(Date.now() - 10000));
            expect(this.authController.isAutologged()).to.be(false);
        });

        it("should return true if user has't verified password", function() {
            this.sinon.stub(this.authController, 'isLite').returns(true);
            this.sinon.stub(this.authController, 'getPasswordEntryDate').returns(null);
            expect(this.authController.isAutologged()).to.be(true);
        });
    });

    describe('hasPassword', function() {
        beforeEach(function() {
            this.response = {have_password: 1};
            this.sinon.stub(this.authController, '_getLastLoginInfo').returns(this.response);
        });

        it('should return true if blackbox response had truthy have_password value', function() {
            this.response.have_password = 1;
            expect(this.authController.hasPassword()).to.be(true);
        });

        it('should return false if blackbox response had falsey have_password value', function() {
            this.response.have_password = 0;
            expect(this.authController.hasPassword()).to.be(false);
        });
    });

    describe('resign', function() {
        beforeEach(function() {
            this.sinon.stub(this.authController, 'redirect');
            this.sinon.stub(this.authController, 'setCookie');
        });

        it('should redirect to error page if there is ?nocookiesupport=yes in query params', function() {
            this.sinon
                .stub(this.authController, 'getRequestParam')
                .withArgs('nocookiesupport')
                .returns('yes');

            var that = this;

            that.authController.resign();
            expect(this.authController.redirect.calledOnce).to.be(true);

            var url = this.authController.redirect.firstCall.args[0];
            var query = require('url').parse(url, true).query;

            expect(query).to.have.property('mode', 'error');
            expect(query).to.have.property('error', 'nocki');
        });

        it('should set Cookie_check cookie', function() {
            this.authController.resign();

            expect(this.authController.setCookie.calledOnce).to.be(true);
            expect(this.authController.setCookie.calledWith('Cookie_check')).to.be(true);
        });

        it('should set domain and path for Cookie_check cookie', function() {
            var tld = 'blah';

            this.sinon.stub(this.authController, 'getTld').returns(tld);

            this.authController.resign();

            expect(this.authController.setCookie.calledOnce).to.be(true);
            expect(this.authController.setCookie.firstCall.args[2]).to.have.property('domain', '.yandex.' + tld);
            expect(this.authController.setCookie.firstCall.args[2]).to.have.property('path', '/');
        });

        it('should redirect once', function() {
            this.authController.resign();
            expect(this.authController.redirect.calledOnce).to.be(true);
        });

        it('should redirect to an https url', function() {
            this.authController.resign();

            expect(require('url').parse(this.authController.redirect.firstCall.args[0])).to.have.property(
                'protocol',
                'https:'
            );
        });

        it('should redirect to passport. at current domain', function() {
            this.sinon.stub(this.authController, 'getUrl').returns({
                hostname: 'yandex.com'
            });

            this.authController.resign();

            expect(require('url').parse(this.authController.redirect.firstCall.args[0])).to.have.property(
                'hostname',
                'passport.yandex.com'
            );
        });

        it('should redirect to yandex-team if in intranet', function() {
            var tmp = process.env.INTRANET;

            process.env.INTRANET = 'intranet';

            this.sinon.stub(this.authController, 'getUrl').returns({
                hostname: 'yandex-team.ru'
            });

            this.authController.resign();

            expect(require('url').parse(this.authController.redirect.firstCall.args[0])).to.have.property(
                'hostname',
                'passport.yandex-team.ru'
            );

            process.env.INTRANET = tmp;
        });

        it('should not redirect to yandex-team if in intranet env variable is not "intranet"', function() {
            var tmp = process.env.INTRANET;

            process.env.INTRANET = 'blah';

            this.sinon.stub(this.authController, 'getUrl').returns({
                hostname: 'yandex-team.ru'
            });

            this.authController.resign();

            expect(require('url').parse(this.authController.redirect.firstCall.args[0])).to.have.property(
                'hostname',
                'passport.yandex.ru'
            );

            process.env.INTRANET = tmp;
        });

        it('should redirect to /auth/update if current domain is a root mda domain', function() {
            this.authController.resign();

            expect(require('url').parse(this.authController.redirect.firstCall.args[0])).to.have.property(
                'pathname',
                '/auth/update'
            );
        });

        it('should append encoded retpath as a query parameter', function() {
            var href = 'http://google.com/search?q=123';

            this.sinon.stub(this.authController, 'getUrl').returns(require('url').parse(href));

            this.authController.resign();

            var parsedRedirect = require('url').parse(this.authController.redirect.firstCall.args[0]);

            expect(parsedRedirect.query).to.be('retpath=' + encodeURIComponent(href));
        });
    });

    describe('canChangePassword', function() {
        beforeEach(function() {
            this.fakeDao = {
                call: sinon.stub().returns(when.resolve())
            };

            this.sinon.stub(AuthenticationController, 'getBlackboxAO').returns(this.fakeDao);

            this.domain_id = 'bhal';
            this.domain = 'blah.ru';
            this.sinon.stub(this.authController, '_getLastLoginInfo').returns({
                uid: {
                    value: '123',
                    domid: this.domain_id,
                    domain: this.domain
                }
            });

            this.sinon.stub(this.authController, 'getBlackbox').returns('blackbox.yandex.ru');
        });

        describe('when the user is not hosted', function() {
            beforeEach(function() {
                this.sinon.stub(this.authController, 'isHosted').returns(false);
            });

            describe('if user has password', function() {
                beforeEach(function() {
                    this.sinon.stub(this.authController, 'hasPassword').returns(true);
                });

                it('should return a promise that resolves to true', function(done) {
                    this.authController
                        .canChangePassword()
                        .then(function(canChangePassword) {
                            expect(canChangePassword).to.be(true);
                            done();
                        })
                        .then(null, done);
                });
            });

            describe('if user has no password', function() {
                beforeEach(function() {
                    this.sinon.stub(this.authController, 'hasPassword').returns(false);
                });

                it('should return a promise that resolves to false', function(done) {
                    this.authController
                        .canChangePassword()
                        .then(function(canChangePassword) {
                            expect(canChangePassword).to.be(false);
                            done();
                        })
                        .then(null, done);
                });
            });
        });

        describe('when the user is hosted', function() {
            beforeEach(function() {
                this.sinon.stub(this.authController, 'isHosted').returns(true);
            });

            it('should return a promise that rejects if there is no uid info', function(done) {
                this.authController._getLastLoginInfo.returns({});
                this.authController
                    .canChangePassword()
                    .then(
                        function() {
                            done('Expected to be rejected');
                        },
                        function(err) {
                            expect(err).to.be.an(Error);
                            expect(err.message).to.be('No uid info, has the sessionid request been made?');
                            done();
                        }
                    )
                    .then(null, done);
            });

            it('should call blackbox dao once', function() {
                this.authController.canChangePassword();
                expect(this.fakeDao.call.calledOnce).to.be(true);
            });

            it('should call blackbox dao with post to hosted_domains', function() {
                this.authController.canChangePassword();
                expect(this.fakeDao.call.calledWith('post', 'hosted_domains')).to.be(true);
            });

            it('should call blackbox dao with domain_id and domain from the sessionid response', function() {
                this.authController.canChangePassword();
                expect(this.fakeDao.call.firstCall.args[2]).to.have.property('domain', this.domain);
                expect(this.fakeDao.call.firstCall.args[2]).to.have.property('domain_id', this.domain_id);
            });

            it('should call blackbox dao with format=json', function() {
                this.authController.canChangePassword();
                expect(this.fakeDao.call.firstCall.args[2]).to.have.property('format', 'json');
            });

            it('should resolve with false if blackbox response specifies user can not change password', function(done) {
                this.fakeDao.call.returns(
                    when.resolve({
                        hosted_domains: [
                            {
                                options: {
                                    can_users_change_password: false
                                }
                            }
                        ]
                    })
                );

                this.authController
                    .canChangePassword()
                    .then(function(result) {
                        expect(result).to.be(false);
                        done();
                    })
                    .then(null, done);
            });

            it('should resolve with true if blackbox response specifies user can change password', function(done) {
                this.fakeDao.call.returns(
                    when.resolve({
                        hosted_domains: [
                            {
                                options: {
                                    can_users_change_password: true
                                }
                            }
                        ]
                    })
                );

                this.authController
                    .canChangePassword()
                    .then(function(result) {
                        expect(result).to.be(true);
                        done();
                    })
                    .then(null, done);
            });

            it(
                'should resolve with true if blackbox response does not specifies if' + ' user can change password',
                function(done) {
                    this.fakeDao.call.returns(
                        when.resolve({
                            hosted_domains: []
                        })
                    );

                    this.authController
                        .canChangePassword()
                        .then(function(result) {
                            expect(result).to.be(true);
                            done();
                        })
                        .then(null, done);
                }
            );
        });
    });

    describe('setSession', function() {
        beforeEach(function() {
            this.host = 'passaporte.yandex.com.cn';
            this.track = 'aiThaengooLohmephoh7eehig1sah9ie';
            this.retpath = 'http://google.com/i/am/evil';
            this.cookies = 'sohT3iephie5yingooPh7iep0Ephohxi4Choh6maothaelohgheeRuidaehad0de';
            this.sinon.stub(this.authController._response, 'header');
            this.sinon.stub(this.authController, 'redirect');
            this.sinon.stub(this.authController, '_getPassportHost').returns(this.host);
        });

        it('should throw if cookies are not defined', function() {
            var that = this;

            expect(function() {
                that.authController.setSession(undefined, that.track);
            }).to.throwError(function(err) {
                expect(err.message).to.be('Cookies should be defined');
            });
        });

        it('should throw if track is not defined', function() {
            var that = this;

            expect(function() {
                that.authController.setSession(that.cookies);
            }).to.throwError(function(err) {
                expect(err.message).to.be('Track id should be a string');
            });
        });

        it('should throw if retpath is not a string if it is defined', function() {
            var that = this;

            expect(function() {
                that.authController.setSession(that.cookies, that.track, 123);
            }).to.throwError(function(err) {
                expect(err.message).to.be('Retpath should be a string if defined');
            });
        });

        it('should set cookies to the provided value', function() {
            this.authController.setSession(this.cookies, this.track);
            expect(this.authController._response.header.calledOnce).to.be(true);
            expect(this.authController._response.header.calledWithExactly('Set-Cookie', this.cookies)).to.be(true);
        });

        it('should redirect to /auth/finish on a passport host', function() {
            this.authController.setSession(this.cookies, this.track);
            expect(this.authController.redirect.calledOnce).to.be(true);

            var redirectUrl = require('url').parse(this.authController.redirect.firstCall.args[0], true);

            expect(redirectUrl.hostname).to.be(this.host);
            expect(redirectUrl.pathname).to.be('/auth/finish');
        });

        it('should add track id as a query to redirect url', function() {
            this.authController.setSession(this.cookies, this.track);

            var redirectUrl = require('url').parse(this.authController.redirect.firstCall.args[0], true);

            expect(redirectUrl.query).to.have.property('track_id', this.track);
        });

        it('should add a retpath as a query to redirect if it is given', function() {
            this.authController.setSession(this.cookies, this.track, this.retpath);

            var redirectUrl = require('url').parse(this.authController.redirect.firstCall.args[0], true);

            expect(redirectUrl.query).to.have.property('retpath', this.retpath);
        });
    });
});
