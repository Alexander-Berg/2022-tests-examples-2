var expect = require('expect.js');
var sinon = require('sinon');
var when = require('when');
var _ = require('lodash');

describe('Http', function() {
    beforeEach(function() {
        this.Dao = require('../Http');

        var requestLib = sinon.stub();

        this.requestLib = requestLib;

        this.logId = 'odeogaaNg0paufoeyae7duox5wievash';

        var daoConfig = {
            baseUrl: 'localhost:6100/oauth',
            maxRetries: 8,
            retryAfter: 1,
            maxConnections: 100,
            timeout: 8000,
            apiFailCheck: sinon.stub().returns(false)
        };

        var Dao = this.Dao;

        this.daoConfig = daoConfig;
        this.getDao = function() {
            var dao = new Dao(
                this.logId,
                daoConfig.baseUrl,
                daoConfig.maxRetries,
                daoConfig.retryAfter,
                daoConfig.maxConnections,
                daoConfig.timeout,
                daoConfig.apiFailCheck
            );

            return dao.setRequestLib(requestLib);
        };
    });

    describe('Config', function() {
        beforeEach(function() {
            this.Config = this.Dao.Config;
            this.config = new this.Config();
        });

        describe('constructor', function() {
            it('should be a function', function() {
                expect(this.Config).to.be.a('function');
            });
        });

        var capitalize = function(string) {
            return string.substr(0, 1).toUpperCase() + string.substr(1);
        };

        var generateTests = function(setting, type, validArg) {
            var capitalized = capitalize(setting);

            var getter = 'get' + capitalized;

            describe(getter, function() {
                it('should throw if ' + setting + ' has not been defined yet', function() {
                    var that = this;

                    expect(function() {
                        that.config[getter]();
                    }).to.throwError(function(err) {
                        expect(err.message).to.be(
                            capitalized + ' is not defined yet, define it with set' + capitalized
                        );
                    });
                });
            });

            var setter = 'set' + capitalized;

            describe(setter, function() {
                it('should throw if no argument given', function() {
                    var that = this;

                    expect(function() {
                        that.config[setter]();
                    }).to.throwError(function(err) {
                        expect(err.message).to.be(capitalized + ' should be a ' + type);
                    });
                });

                it('should throw if argument is not a ' + type, function() {
                    var that = this;
                    var faultyArg = type === 'string' ? {} : 'hahanope';

                    expect(function() {
                        that.config[setter](faultyArg);
                    }).to.throwError(function(err) {
                        expect(err.message).to.be(capitalized + ' should be a ' + type);
                    });
                });

                it('should return instance for chaining', function() {
                    expect(this.config[setter](validArg)).to.be(this.config);
                });

                it('should set a value', function() {
                    this.config[setter](validArg);
                    expect(this.config[getter]()).to.be(validArg);
                });
            });
        };

        var settingsDefinitions = [
            ['baseUrl', 'string', 'http://oauth.yandex.ru/iface_api'],
            ['maxRetries', 'number', 2],
            ['retryAfter', 'number', 100],
            ['maxConnections', 'number', 500],
            ['timeout', 'number', 1000],
            ['apiFailCheck', 'function', function() {}]
        ];

        settingsDefinitions.forEach(function(definition) {
            generateTests.apply(null, definition);
        });

        describe('clone', function() {
            beforeEach(function() {
                var that = this;

                settingsDefinitions.forEach(function(definition) {
                    var setting = definition[0];
                    var capitalized = capitalize(setting);
                    var expectedValue = definition[2];
                    var getter = 'get' + capitalized;

                    sinon.stub(that.config, getter).returns(expectedValue);
                });
            });

            it('should return a Config', function() {
                expect(this.config.clone()).to.be.a(this.Config);
            });

            it('should not return a same instance', function() {
                expect(this.config.clone()).to.not.be(this.config);
            });

            settingsDefinitions.forEach(function(definition) {
                var setting = definition[0];

                it('should set ' + setting + ' to a current value of the config', function() {
                    var expectedValue = definition[2];
                    var getter = 'get' + capitalize(setting);

                    expect(this.config.clone()[getter]()).to.be(expectedValue);
                });
            });
        });

        describe('isValid', function() {
            it('should return false if any value was not set yet', function() {
                expect(this.config.isValid()).to.be(false);
            });

            it('should return true if every value was already set', function() {
                var that = this;

                //Set all values
                settingsDefinitions.forEach(function(definition) {
                    var setter = 'set' + capitalize(definition[0]);

                    that.config[setter](definition[2]);
                });

                expect(this.config.isValid()).to.be(true);
            });
        });
    });

    it('should be an abstract dao instance', function() {
        expect(this.getDao()).to.be.a(require('../Abstract'));
    });

    describe('constructor', function() {
        it('should be a function', function() {
            expect(this.Dao).to.be.a('function');
        });

        it('should throw if logID is not a string', function() {
            var that = this;
            var config = this.daoConfig;

            expect(function() {
                new that.Dao(
                    123,
                    config.baseUrl,
                    config.maxRetries,
                    config.retryAfter,
                    config.maxConnections,
                    config.timeout,
                    config.apiFailCheck
                );
            }).to.throwError(function(err) {
                expect(err.message).to.be('LogID should be a string');
            });
        });

        it('should throw if baseUrl is not a string', function() {
            var that = this;
            var config = this.daoConfig;

            expect(function() {
                new that.Dao(
                    that.logId,
                    123,
                    config.maxRetries,
                    config.retryAfter,
                    config.maxConnections,
                    config.timeout,
                    config.apiFailCheck
                );
            }).to.throwError(function(err) {
                expect(err.message).to.be('Base Url should be a string');
            });
        });

        it('should throw if maxRetries is not a number', function() {
            var that = this;
            var config = this.daoConfig;

            expect(function() {
                new that.Dao(
                    that.logId,
                    config.baseUrl,
                    'nope',
                    config.retryAfter,
                    config.maxConnections,
                    config.timeout,
                    config.apiFailCheck
                );
            }).to.throwError(function(err) {
                expect(err.message).to.be('Max Retries should be a number');
            });
        });

        it('should throw if retryAfter is not a number', function() {
            var that = this;
            var config = this.daoConfig;

            expect(function() {
                new that.Dao(
                    that.logId,
                    config.baseUrl,
                    config.maxRetries,
                    'nope',
                    config.maxConnections,
                    config.timeout,
                    config.apiFailCheck
                );
            }).to.throwError(function(err) {
                expect(err.message).to.be('Retry timeout should be a number in ms');
            });
        });

        it('should throw if maxConnections is not a number', function() {
            var that = this;
            var config = this.daoConfig;

            expect(function() {
                new that.Dao(
                    that.logId,
                    config.baseUrl,
                    config.maxRetries,
                    config.retryAfter,
                    'nope',
                    config.timeout,
                    config.apiFailCheck
                );
            }).to.throwError(function(err) {
                expect(err.message).to.be('Max Connections should be a number');
            });
        });

        it('should throw if timeout is not a number', function() {
            var that = this;
            var config = this.daoConfig;

            expect(function() {
                new that.Dao(
                    that.logId,
                    config.baseUrl,
                    config.maxRetries,
                    config.retryAfter,
                    config.maxConnections,
                    'nope',
                    config.apiFailCheck
                );
            }).to.throwError(function(err) {
                expect(err.message).to.be('Timeout should be a number');
            });
        });

        it('should throw if apiFailCheck is not a function if it is given', function() {
            var that = this;
            var config = this.daoConfig;

            expect(function() {
                new that.Dao(
                    that.logId,
                    config.baseUrl,
                    config.maxRetries,
                    config.retryAfter,
                    config.maxConnections,
                    config.timeout,
                    'nope'
                );
            }).to.throwError(function(err) {
                expect(err.message).to.be('Api Fail Check should be a function if given');
            });
        });

        it('should not throw if apiFailCheck is undefined', function() {
            var that = this;
            var config = this.daoConfig;

            expect(function() {
                new that.Dao(
                    that.logId,
                    config.baseUrl,
                    config.maxRetries,
                    config.retryAfter,
                    config.maxConnections,
                    config.timeout
                );
            }).to.not.throwError();
        });
    });

    describe('cloneConfig', function() {
        it('should return a copy of a default config', function() {
            var dao = this.getDao();

            var expectedResult = {};

            sinon.stub(dao._defaultConfig, 'clone').returns(expectedResult);

            expect(dao.cloneConfig()).to.be(expectedResult);
        });
    });

    describe('call', function() {
        beforeEach(function() {
            this.method = 'POST';
            this.handle = '/tokens/revoke';
            this.input = {
                whatso: 'ever',
                firstname: 'Arseny',
                lastname: 'Smoogly',
                login: 'smoogly',
                password: 'nopenopenope',
                password_confirm: 'whatsogoddamnever',
                phone_number: '8-965-359-03-23'
            };

            this.responseBody = {
                result: 'success'
            };
            this.response = {
                statusCode: 200
            };

            this.requestLib.callsArgWithAsync(1, null, this.response, this.responseBody);

            this.dao = this.getDao();
            this.callResult = this.dao.call(this.method, this.handle, this.input);
        });

        describe('arguments', function() {
            it('should throw if method is not one of "get", "post", "put", "delete"', function() {
                var that = this;

                expect(function() {
                    that.dao.call('invalid', that.handle, that.input);
                }).to.throwError(function(err) {
                    expect(err.message).to.be('Method should be an http method name');
                });
            });

            it('should throw if handle is not a string', function() {
                var that = this;

                expect(function() {
                    that.dao.call(that.method, 123, that.input);
                }).to.throwError(function(err) {
                    expect(err.message).to.be('Handle should be a string');
                });
            });

            it('should throw if input is not a plain object', function() {
                var that = this;

                expect(function() {
                    that.dao.call(that.method, that.handle, 'nope');
                }).to.throwError(function(err) {
                    expect(err.message).to.be('Input should be a plain object');
                });
            });

            it('should throw if config is not a Config object', function() {
                var that = this;

                expect(function() {
                    that.dao.call(that.method, that.handle, that.input, 'nope');
                }).to.throwError(function(err) {
                    expect(err.message).to.be('Config should be a Dao Config object if defined');
                });
            });

            it('should throw if given config is not valid', function() {
                var that = this;
                var config = this.dao.cloneConfig();

                sinon.stub(config, 'isValid').returns(false);

                expect(function() {
                    that.dao.call(that.method, that.handle, that.input, config);
                }).to.throwError(function(err) {
                    expect(err.message).to.be('Config should have all values set');
                });
            });
        });

        it('should call the request lib once in a good scenario', function() {
            expect(this.requestLib.calledOnce).to.be(true);
        });

        it('should pass the handle to the request lib along with base url', function() {
            expect(this.requestLib.firstCall.args[0]).to.have.property('url', this.daoConfig.baseUrl + this.handle);
        });

        it('should use baseUrl from an explicit config if it is defined', function() {
            var baseurl = 'baseurlOverride';

            this.dao.call(this.method, this.handle, this.input, this.dao.cloneConfig().setBaseUrl(baseurl));
            expect(this.requestLib.lastCall.args[0]).to.have.property('url', baseurl + this.handle);
        });

        it('should expect the json response', function() {
            expect(this.requestLib.firstCall.args[0]).to.have.property('json', true);
        });

        describe('when making POST request', function() {
            it('should pass http method to the request lib', function() {
                expect(this.requestLib.firstCall.args[0]).to.have.property('method', this.method.toLowerCase());
            });

            it('should pass the input to the request lib as a body string', function() {
                expect(this.requestLib.firstCall.args[0]).to.have.property(
                    'body',
                    require('querystring')
                        .stringify(this.input)
                        .replace('?', '')
                );
            });

            it('should set content-type header to application/x-www-form-urlencoded; charset=utf-8', function() {
                expect(this.requestLib.firstCall.args[0]).to.have.property('headers');
                expect(this.requestLib.firstCall.args[0].headers).to.have.property(
                    'Content-type',
                    'application/x-www-form-urlencoded; charset=utf-8'
                );
            });

            it('should pass logId as x-request-id header', function() {
                expect(this.requestLib.firstCall.args[0]).to.have.property('headers');
                expect(this.requestLib.firstCall.args[0].headers).to.have.property('X-Request-Id', this.logId);
            });
        });

        describe('when making a GET request', function() {
            beforeEach(function() {
                this.dao.call('get', this.handle, this.input);
            });

            it('should pass http method to the request lib', function() {
                expect(this.requestLib.secondCall.args[0]).to.have.property('method', 'get');
            });

            it('should pass the input to the request as an url query', function() {
                var expectedQuery = require('querystring')
                    .stringify(this.input)
                    .replace('?', '');
                var actualQuery = this.requestLib.secondCall.args[0].url.split('?').pop();

                expect(actualQuery).to.be(expectedQuery);
            });

            it('should append the input to the existing query in the url if any', function() {
                var existingQuery = '?existing=query';
                var handleWithAQuery = this.handle + existingQuery;

                this.dao.call('get', handleWithAQuery, this.input);

                var expectedQuery = (existingQuery + '&' + require('querystring').stringify(this.input)).replace(
                    /\?/g,
                    ''
                );
                var actualQuery = this.requestLib.thirdCall.args[0].url.split('?').pop();

                expect(actualQuery).to.be(expectedQuery);
            });

            it('should leave base url as is', function() {
                //An url before adding the query
                var url = this.requestLib.secondCall.args[0].url.split('?').shift();

                expect(url).to.be(this.daoConfig.baseUrl + this.handle);
            });

            it('should pass logId as x-request-id header', function() {
                expect(this.requestLib.firstCall.args[0]).to.have.property('headers');
                expect(this.requestLib.firstCall.args[0].headers).to.have.property('X-Request-Id', this.logId);
            });
        });

        it('should pass the maxConnections to the request lib', function() {
            expect(this.requestLib.firstCall.args[0]).to.have.property('pool');
            expect(this.requestLib.firstCall.args[0].pool).to.have.property(
                'maxSockets',
                this.daoConfig.maxConnections
            );
        });

        it('should use maxConnections from explicit config if it is defined', function() {
            var maxConnections = 12345;

            this.dao.call(
                this.method,
                this.handle,
                this.input,
                this.dao.cloneConfig().setMaxConnections(maxConnections)
            );

            expect(this.requestLib.lastCall.args[0]).to.have.property('pool');
            expect(this.requestLib.lastCall.args[0].pool).to.have.property('maxSockets', maxConnections);
        });

        it('should pass the timeout to the request lib', function() {
            expect(this.requestLib.firstCall.args[0]).to.have.property('timeout', this.daoConfig.timeout);
        });

        it('should use the timeout from explicit config if it is defined', function() {
            var timeout = 12345;

            this.dao.call(this.method, this.handle, this.input, this.dao.cloneConfig().setTimeout(timeout));

            expect(this.requestLib.lastCall.args[0]).to.have.property('timeout', timeout);
        });

        it('should return a when promise', function() {
            expect(when.isPromiseLike(this.callResult)).to.be(true);
        });

        it('should resolve the promise with the result of a request', function(done) {
            var that = this;

            this.callResult
                .then(function(response) {
                    expect(response).to.be(that.responseBody);
                    done();
                })
                .then(null, done);
        });

        it('should reject the promise if request failed', function(done) {
            var error = new Error();

            this.dao.setRequestLib(sinon.stub().callsArgWithAsync(1, error, this.response, this.responseBody));
            this.dao
                .call(this.method, this.handle, this.input)
                .then(asyncFail(done, 'Expected the promise to be rejected'), function() {
                    done();
                });
        });

        it('should use apiFailCheck from the explicit config if it is defined', function(done) {
            var apiFailCheck = sinon.stub();
            var defaultConfig = this.daoConfig;

            defaultConfig.apiFailCheck = sinon.stub();

            var requestLib = sinon.stub().callsArgWithAsync(1, null, this.response, this.responseBody);
            var dao = this.getDao();

            dao.setRequestLib(requestLib)
                .call(this.method, this.handle, this.input, dao.cloneConfig().setApiFailCheck(apiFailCheck))
                .then(function() {
                    expect(apiFailCheck.called).to.be(true);
                    expect(defaultConfig.apiFailCheck.called).to.be(false);
                    done();
                }, asyncFail(done, 'Expected the promise to be resolved'))
                .then(null, done);
        });

        describe('retries', function() {
            [
                //Node http error codes
                'ECONNREFUSED',
                'ECONNRESET',
                'ENOTFOUND',
                'ETIMEDOUT',
                'ESOCKETTIMEDOUT'
            ].forEach(function(networkErrorCode) {
                it('should retry if connection had an error ' + networkErrorCode, function(done) {
                    var error = new Error(networkErrorCode);

                    error.code = networkErrorCode;

                    var numRetries = 5;

                    this.daoConfig.maxRetries = numRetries;
                    var requestLib = sinon.stub().callsArgWithAsync(1, error, this.response, this.responseBody);

                    this.getDao()
                        .setRequestLib(requestLib)
                        .call(this.method, this.handle, this.input)
                        .then(asyncFail(done, 'Expected the promise to be rejected'), function() {
                            expect(requestLib.callCount).to.be(numRetries + 1); //Original call + numRetries
                            done();
                        })
                        .then(null, done);
                });

                it(
                    'should reject with a ConnectionError if last request had a connection problem ' + networkErrorCode,
                    function(done) {
                        var error = new Error(networkErrorCode);

                        this.daoConfig.maxRetries = 0;
                        var requestLib = sinon.stub().callsArgWithAsync(1, error, this.response, this.responseBody);

                        this.getDao()
                            .setRequestLib(requestLib)
                            .call(this.method, this.handle, this.input)
                            .then(asyncFail(done, 'Expected the promise to be rejected'), function(error) {
                                expect(error).to.be(error);
                                done();
                            })
                            .then(null, done);
                    }
                );
            });

            it('should retry if apiFailCheck returned an error for the response', function(done) {
                var numRetries = 3;

                this.daoConfig.maxRetries = numRetries;
                this.daoConfig.apiFailCheck = function() {
                    return new Error();
                }; //Always retry

                var requestLib = sinon.stub().callsArgWithAsync(1, null, this.response, this.responseBody);

                this.getDao()
                    .setRequestLib(requestLib)
                    .call(this.method, this.handle, this.input)
                    .then(asyncFail(done, 'Expected the promise to be rejected'), function() {
                        expect(requestLib.callCount).to.be(numRetries + 1); //Original call + numRetries
                        done();
                    })
                    .then(null, done);
            });

            it('should wait between timeouts', function(done) {
                var requestLib = sinon.stub().callsArgWithAsync(1, null, this.response, this.responseBody);

                var config = this.daoConfig;

                config.maxRetries = 1;
                config.retryAfter = 500;
                config.apiFailCheck = function() {
                    return new Error();
                }; //Always retry

                var start = Date.now();

                this.getDao()
                    .setRequestLib(requestLib)
                    .call(this.method, this.handle, this.input)
                    .then(asyncFail(done), function() {
                        expect(Date.now() - start).to.be.greaterThan(config.retryAfter);
                        done();
                    })
                    .then(null, done);
            });

            it(
                'should use a retryAfter value from the explicit config if it is ' + 'defined to wait between timeouts',
                function(done) {
                    var requestLib = sinon.stub().callsArgWithAsync(1, null, this.response, this.responseBody);

                    var defaultRetryAfter = 500;
                    var explicitRetryAfter = 300;

                    var defaultConfig = this.daoConfig;

                    defaultConfig.maxRetries = 1;
                    defaultConfig.retryAfter = defaultRetryAfter;
                    defaultConfig.apiFailCheck = function() {
                        return new Error();
                    }; //Always retry

                    var start = Date.now();
                    var dao = this.getDao();

                    dao.setRequestLib(requestLib)
                        .call(this.method, this.handle, this.input, dao.cloneConfig().setRetryAfter(explicitRetryAfter))
                        .then(asyncFail(done), function() {
                            var delta = Date.now() - start;

                            expect(delta).to.be.greaterThan(explicitRetryAfter);

                            //Potentially explosive expectation
                            expect(delta).to.be.lessThan(defaultRetryAfter);
                            done();
                        })
                        .then(null, done);
                }
            );

            it('should reject with an error apiFailCheck returned for the last request', function(done) {
                var error = new Error('Something-something error');

                this.daoConfig.maxRetries = 0;
                this.daoConfig.apiFailCheck = function() {
                    return error;
                }; //Always retry

                this.getDao()
                    .call(this.method, this.handle, this.input)
                    .then(asyncFail(done, 'Expected the promise to be rejected'), function(err) {
                        expect(err).to.be(error);
                        done();
                    })
                    .then(null, done);
            });

            it('should resolve if retry was successful', function(done) {
                this.daoConfig.maxRetries = 10;
                var requestLib = sinon.stub();

                requestLib
                    .onFirstCall()
                    .callsArgWithAsync(1, new Error(), null, null)
                    .onSecondCall()
                    .callsArgWithAsync(1, null, this.response, this.responseBody);

                var that = this;

                this.getDao()
                    .setRequestLib(requestLib)
                    .call(this.method, this.handle, this.input)
                    .then(function(response) {
                        expect(response).to.be(that.responseBody);
                        done();
                    }, asyncFail(done, 'Expected the promise to be resolved'))
                    .then(null, done);
            });
        });
    });

    describe('XMLParser', function() {
        beforeEach(function() {
            this.xml = '<?xml version="1.0" encoding="windows-1251"?><doc><message-sent id="127000000003456" /></doc>';
            this.parsedXml = {doc: {'message-sent': {$: {id: '127000000003456'}}}};

            this.requestLib.onFirstCall().callsArgWithAsync(1, null, this.response, this.xml);
        });

        it('should parse the response as xml if the response body starts with "<?xml "', function(done) {
            var expectedXml = this.parsedXml;

            this.getDao()
                .setRequestLib(this.requestLib)
                .call('get', '/handle', {})
                .then(function(response) {
                    expect(response).to.eql(expectedXml);
                    done();
                }, asyncFail(done))
                .then(null, done);
        });

        it('should parse xml before calling apiFailCheck, so that it receives with parsed data', function(done) {
            var that = this;

            this.getDao()
                .setRequestLib(this.requestLib)
                .call('get', '/handle', {})
                .then(function() {
                    expect(that.daoConfig.apiFailCheck.firstCall.args[2]).to.eql(that.parsedXml);
                    done();
                }, asyncFail(done))
                .then(null, done);
        });

        it('should reject the call if parser returned an error', function(done) {
            this.daoConfig.maxRetries = 0;
            this.requestLib
                .onFirstCall()
                .callsArgWithAsync(
                    1,
                    null,
                    this.response,
                    '<?xml version="1.0" encoding="UTF-8"?>garbage garbage garbage <'
                );

            this.getDao()
                .setRequestLib(this.requestLib)
                .call('get', '/handle', {})
                .then(asyncFail(done), function() {
                    done(); //Successfully rejected
                });
        });
    });

    describe('Mixing headers', function() {
        beforeEach(function() {
            this.headers = {
                'x-whatso-ever': 'whatever',
                'x-client-ip': '123.233.148.256'
            };

            this.dao = this.getDao()
                .setRequestLib(this.requestLib)
                .mixHeaders(this.headers);
        });

        it('should throw if headers are not a dict', function() {
            var dao = this.dao;

            expect(function() {
                dao.mixHeaders('Haha, nope');
            }).to.throwError(function(err) {
                expect(err.message).to.be('Headers should be a dict');
            });
        });

        it('should mix headers into request', function(done) {
            var headers = this.headers;
            var request = this.requestLib;

            this.requestLib.callsArgAsync(1);

            this.dao
                .call('get', '/handle', {})
                .then(function() {
                    expect(request.firstCall.args[0]).to.have.property('headers');

                    require('lodash').each(headers, function(val, key) {
                        expect(request.firstCall.args[0].headers).to.have.property(key, val);
                    });

                    done();
                })
                .then(null, asyncFail(done));
        });
    });

    describe('censorLog', function() {
        beforeEach(function() {
            this.dao = this.getDao();
        });

        it('should not censor arbitrary fields', function() {
            var input = {
                some: 'field'
            };

            expect(this.dao.censorLog(input)).to.have.property('some', 'field');
        });

        [
            'passwd',
            'password',
            'password_confirm',
            'password-confirm',
            'hint_answer',
            'hint-answer',
            'session',
            'sessionid',
            'sslsessionid'
        ].forEach(function(field) {
            it('should hide the field ' + field + ' contents', function() {
                var input = {
                    whatso: 'ever'
                };

                input[field] = 'contents';

                var censored = this.dao.censorLog(input);

                expect(censored).to.have.property('whatso', 'ever');
                expect(censored).to.have.property(field, '***');
            });
        });

        ['phone_number', 'phone-number', 'phone'].forEach(function(field) {
            it('should hide last 5 symbols of the ' + field + ' field', function() {
                var input = {
                    whatso: 'ever'
                };

                input[field] = 'contents';

                var censored = this.dao.censorLog(input);

                expect(censored).to.have.property('whatso', 'ever');
                expect(censored).to.have.property(field, 'con*****');
            });

            it(
                'should hide all the input contents of the ' +
                    field +
                    ' field if it is too short with matching number of stars',
                function() {
                    var input = {
                        whatso: 'ever'
                    };

                    input[field] = 'whoa';

                    var censored = this.dao.censorLog(input);

                    expect(censored).to.have.property('whatso', 'ever');
                    expect(censored).to.have.property(field, '****');
                }
            );
        });

        it('should not alter the original input', function() {
            var input = {
                password: 'hunter2'
            };
            var clonedInput = _.clone(input);

            this.dao.censorLog(input);
            expect(input).to.eql(clonedInput);
        });
    });
});
