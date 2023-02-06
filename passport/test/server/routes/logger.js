var expect = require('expect.js');
var sinon = require('sinon');
var logger = require('../../../routes/logger');
var putils = require('putils');
var Plog = require('plog');
var api = require('../../../lib/passport-api');

describe('Logger', function() {
    describe('normalizeUrl', function() {
        var expectations = {
            'https://passport.yandex.ru/': '/',
            'https://passport.yandex.ru/registration': '/registration',
            'https://passport.yandex.ru/registration/': '/registration',
            'https://passport.yandex.ru/registration/mail': '/registration/mail',
            'https://passport.yandex.ru/registration/mail/': '/registration/mail',
            'https://passport.yandex.ru/registration/mail/digit': '/registration/mail/digit',
            'https://passport.yandex.ru/registration/mail/digit/': '/registration/mail/digit',
            'https://passport.yandex.ru/registration/?from=mail&origin=whatever&login=vasya@mail.ru': '/registration'
        };

        for (var url in expectations) {
            (function(url) {
                it(`should convert "${url}" to "${expectations[url]}"`, function() {
                    expect(logger.normalizeUrl(url)).to.be(expectations[url]);
                });
            })(url);
        }
    });

    describe('normalizeAction', function() {
        var expectations = {
            cAmElCaSe: 'camelcase',
            'spaces to underscores': 'spaces_to_underscores',
            'multiple   spaces': 'multiple_spaces',
            'CamelCase AnD  Spaces  to   Lowercase   aNd underscores':
                'camelcase_and_spaces_to_lowercase_and_underscores'
        };

        for (var action in expectations) {
            (function(action) {
                it(`should convert "${action}" to "${expectations[action]}"`, function() {
                    expect(logger.normalizeAction(action)).to.be(expectations[action]);
                });
            })(action);
        }
    });

    describe('getKey', function() {
        var expectations = {
            '123': `${logger.token.salt}::` + `123`,
            defaultValue: `${logger.token.salt}::` + `0`
        };

        it('Should return salt concated with string or zero if invoked without arguments', function() {
            expect(logger.token.getKey('123')).to.be(expectations['123']);
            expect(logger.token.getKey()).to.be(expectations['defaultValue']);
        });
    });

    describe('create', function() {
        var key = 'qwe';
        var time = '1453738549835';
        var origCipherAlgorightm = logger.token.cipherAlgorightm;
        var cipherdTimestamp = '7ed0b4c79f3ec90a363bcbf3e697b4f6';
        var cipherAlgorightm = 'aes128';

        it('Should return ciphered timestamp in hex encoding', function() {
            logger.token.cipherAlgorightm = cipherAlgorightm;
            sinon.stub(logger.token, 'getKey').returns(key);
            sinon.stub(Date.prototype, 'getTime').returns(time);
            expect(logger.token.create()).to.be(cipherdTimestamp);
            logger.token.getKey.restore();
            Date.prototype.getTime.restore();
            logger.token.cipherAlgorightm = origCipherAlgorightm;
        });
    });

    describe('check', function() {
        var yandexuid = 'qwe';
        var anotherYandexuid = 'ewq';
        var maxTimestamp = 9999999999999;

        it('Should return true if token was created with yandexuid cookie', function() {
            var token = logger.token.create(yandexuid);

            expect(logger.token.check(token, yandexuid)).to.be(true);
        });

        it('Should return false if token was create with another yandexuid cookie', function() {
            var token = logger.token.create(yandexuid);

            expect(logger.token.check(token, anotherYandexuid)).to.be(false);
        });

        it('Should return false if yandexuid argument is undefined', function() {
            var token = logger.token.create(yandexuid);

            expect(logger.token.check(token)).to.be(false);
        });

        it('Should return false if token was expired', function() {
            var token = logger.token.create(yandexuid);

            sinon.stub(Date.prototype, 'getTime').returns(maxTimestamp);
            expect(logger.token.check(token, yandexuid)).to.be(false);
            Date.prototype.getTime.restore();
        });
    });

    describe('route handler', function() {
        var reqMock = {
            body: {
                log: 'log',
                track_id: 'track_id'
            },
            cookies: {
                yandexuid: 'yandexuid'
            },
            headers: {
                'x-real-ip': 'ip'
            }
        };
        var resMock = {
            locals: {
                expriments: {}
            }
        };
        var logMock = {
            url: 'http://yandex.ru/foo/bar?foo=foo&baz=baz',
            action: 'normalizedAction',
            withTrackId: true
        };
        var info = {
            ignoreMissedTrack: true,
            ip: reqMock.headers['x-real-ip'],
            yandexuid: reqMock.cookies.yandexuid,
            url: logger.utils.normalizeUrl(logMock.url),
            action: logger.utils.normalizeAction(logMock.action),
            user_agent: undefined,
            host: undefined
        };
        var plogMock;
        var apiMock;

        beforeEach(function() {
            plogMock = {
                logId: sinon.stub(),
                type: sinon.stub(),
                write: sinon.stub()
            };
            apiMock = {
                then: function(callback) {
                    callback(apiMock);
                },
                statboxLogger: sinon.stub()
            };
            sinon.stub(logger.utils, 'tryToGetLog');
            sinon.stub(logger.utils, 'normalizeUrl');
            sinon.stub(logger.utils, 'normalizeAction');
            sinon.stub(Plog, 'debug');
            sinon.stub(api, 'client');
            Plog.debug.returns(plogMock);
            plogMock.logId.returns(plogMock);
            plogMock.type.returns(plogMock);
            plogMock.write.returns(plogMock);
            api.client.returns(apiMock);
        });

        afterEach(function() {
            logger.utils.tryToGetLog.restore && logger.utils.tryToGetLog.restore();
            logger.utils.normalizeUrl.restore && logger.utils.normalizeUrl.restore();
            logger.utils.normalizeAction.restore && logger.utils.normalizeAction.restore();
            Plog.debug.restore && Plog.debug.restore();
            api.client.restore && api.client.restore();
        });

        it('Should call tryToGetLog with req.body.log req.body.track_id', function() {
            logger(reqMock, resMock);
            expect(logger.utils.tryToGetLog.calledOnce).to.be(true);
            expect(logger.utils.tryToGetLog.calledWithExactly(reqMock.body.log, reqMock.body.track_id)).to.be(true);
        });

        it('Should return false if tryToGetLog returns null', function() {
            logger.utils.tryToGetLog.returns(null);
            expect(logger(reqMock, resMock)).to.be(false);
        });

        it('Should call normalizeUrl with log.url if log is loggable', function() {
            logger.utils.tryToGetLog.returns(logMock);
            logger(reqMock, resMock);
            expect(logger.utils.normalizeUrl.calledOnce).to.be(true);
            expect(logger.utils.normalizeUrl.calledWithExactly(logMock.url));
        });

        it('Should call normalizeAction with log.action if log is loggable', function() {
            logger.utils.tryToGetLog.returns(logMock);
            logger(reqMock, resMock);
            expect(logger.utils.normalizeAction.calledOnce).to.be(true);
            expect(logger.utils.normalizeAction.calledWithExactly(logMock.action)).to.be(true);
        });

        it('Should call Plog.debug without arguments if log is loggable', function() {
            logger.utils.tryToGetLog.returns(logMock);
            logger(reqMock, resMock);
            expect(Plog.debug.calledOnce).to.be(true);
            expect(Plog.debug.calledWithExactly()).to.be(true);
        });

        it('Should call Plog.logId with req.logId if log is loggable', function() {
            logger.utils.tryToGetLog.returns(logMock);
            logger(reqMock, resMock);
            expect(plogMock.logId.calledOnce).to.be(true);
            expect(plogMock.logId.calledWithExactly(reqMock.logId)).to.be(true);
        });

        it('Should call Plog.type with loggerroute arg if log is loggable', function() {
            logger.utils.tryToGetLog.returns(logMock);
            logger(reqMock, resMock);
            expect(plogMock.type.calledOnce).to.be(true);
            expect(plogMock.type.calledWithExactly('loggerroute')).to.be(true);
        });

        it('Should call Plog.write if log is loggable', function() {
            logger.utils.tryToGetLog.returns(logMock);
            logger(reqMock, resMock);
            expect(plogMock.write.calledOnce).to.be(true);
        });

        it('Should call api.client with req if log is loggable', function() {
            logger.utils.tryToGetLog.returns(logMock);
            logger(reqMock, resMock);
            expect(api.client.calledOnce).to.be(true);
            expect(api.client.calledWithExactly(reqMock)).to.be(true);
        });

        it('Should call api.statboxLogger if ok', function() {
            logger.utils.tryToGetLog.returns(logMock);
            logger.utils.normalizeUrl.restore();
            logger.utils.normalizeAction.restore();
            logger(reqMock, resMock);
            expect(apiMock.statboxLogger.calledOnce).to.be(true);
            expect(apiMock.statboxLogger.calledWithExactly(info)).to.be(true);
        });
    });

    describe('tryToGetLog', function() {
        var yandexuid = '123456789';
        var secret = 'secret';
        var log = {
            url: 'url',
            action: 'action',
            token: logger.token.create(yandexuid)
        };
        var json = JSON.stringify(log);
        var encodedJSON = putils.simpleCipher.encode(secret, json);
        var invalidJSON = json.slice(1);
        var sampleString = 'sample';

        it('Should return null if was called with less then 2 args', function() {
            expect(logger.utils.tryToGetLog()).to.be(null);
            expect(logger.utils.tryToGetLog(sampleString)).to.be(null);
        });

        it('Should return null if first argument isnt json and secret is missing', function() {
            expect(logger.utils.tryToGetLog(encodedJSON, yandexuid)).to.be(null);
        });

        it('Should return null if it failes to decode JSON', function() {
            expect(logger.utils.tryToGetLog(encodedJSON, yandexuid, 'another_secret')).to.be(null);
        });

        it('Should return null if it failes to parse JSON', function() {
            expect(logger.utils.tryToGetLog(invalidJSON, yandexuid)).to.be(null);
        });

        it('Should return null if json doesnt contains url, action and token', function() {
            var log = {
                foo: 'foo',
                token: logger.token.create(yandexuid)
            };
            var json = JSON.stringify(log);

            expect(logger.utils.tryToGetLog(json, yandexuid)).to.be(null);
        });

        it('Should return null if json has withTrackId field but dont have track_id', function() {
            log.withTrackId = true;
            var jsonWithTrackId = JSON.stringify(log);

            delete log.withTrackId;
            expect(logger.utils.tryToGetLog(jsonWithTrackId, yandexuid)).to.be(null);
        });

        it('Should return log object if everything is ok', function() {
            expect(logger.utils.tryToGetLog(json)).to.eql(log);
            expect(logger.utils.tryToGetLog(encodedJSON, secret)).to.eql(log);
        });
    });
});
