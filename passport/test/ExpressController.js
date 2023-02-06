var expect = require('expect.js');
var sinon = require('sinon');
var reqRes = require('./../tools/expressReqRes');
var _ = require('lodash');

describe('ExpressController', function() {
    beforeEach(function() {
        this.req = reqRes.req();
        this.res = reqRes.res();
        this.logId = 'ainohBa3jooth3ohgoo2oosheebah9ie';

        this.Controller = require('../ExpressController');
        this.controller = new this.Controller(this.req, this.res, this.logId);
    });

    describe('Constructor', function() {
        it('should throw if request is not an instance of http.IncomingMessage', function() {
            //Express request is inherited (badly) from http.IncomingMessage

            var res = this.res;
            var Controller = this.Controller;

            expect(function() {
                new Controller('nope', res);
            }).to.throwError(function(e) {
                expect(e.message).to.be('Request should be an instance of Express request');
            });
        });

        it('should throw if request is an instance of http.IncomingMessage, but not an ExpressRequest', function() {
            var incomingMessage = new (require('http').IncomingMessage)();

            var res = this.res;
            var Controller = this.Controller;

            expect(function() {
                new Controller(incomingMessage, res);
            }).to.throwError(function(e) {
                expect(e.message).to.be('Request should be an instance of Express request');
            });
        });

        it('should throw if response is not an instance of http.ServerResponse', function() {
            //Express response is inherited (badly) from http.ServerResponse

            var req = this.req;
            var Controller = this.Controller;

            expect(function() {
                new Controller(req, 'nope');
            }).to.throwError(function(e) {
                expect(e.message).to.be('Response should be an instance of Express response');
            });
        });

        it('should throw if request is an instance of http.ServerResponse, but not an ExpressResponse', function() {
            var serverResponse = new (require('http').ServerResponse)({
                method: sinon.stub()
            });

            var req = this.req;
            var Controller = this.Controller;

            expect(function() {
                new Controller(req, serverResponse);
            }).to.throwError(function(e) {
                expect(e.message).to.be('Response should be an instance of Express response');
            });
        });

        it('should not throw if called with express request and response', function() {
            var req = this.req;
            var res = this.res;
            var Controller = this.Controller;

            expect(function() {
                new Controller(req, res);
            }).to.not.throwError();
        });
    });

    describe('getLogId', function() {
        it('should return the logId controller was created with', function() {
            expect(this.controller.getLogId()).to.be(this.logId);
        });
    });

    describe('getAuth', function() {
        it('should return an Auth Controller', function() {
            expect(this.controller.getAuth()).to.be.a(require('../Authentication'));
        });

        it('should return same Auth Controller when called multiple times', function() {
            expect(this.controller.getAuth()).to.be(this.controller.getAuth());
        });
    });

    describe('getUrl', function() {
        beforeEach(function() {
            sinon.stub(require('url'), 'parse');
        });
        afterEach(function() {
            if (typeof require('url').parse.restore === 'function') {
                require('url').parse.restore();
            }
        });

        it(
            'should call url.parse with url constructed from x-real-scheme header, ' +
                'host header and req.originalUrl',
            function() {
                var scheme = 'totally-not-provided-by-child-army';
                var host = 'democratic-respublic-of-congo.congo';
                var originalUrl = '/produce/diamonds/in/exchange?for=violence';

                sinon
                    .stub(this.controller, 'getHeader')
                    .withArgs('x-real-scheme')
                    .returns(scheme)
                    .withArgs('host')
                    .returns(host);

                this.req.originalUrl = originalUrl;

                this.controller.getUrl();
                expect(require('url').parse.calledWithExactly(scheme + '://' + host + originalUrl));
            }
        );

        it('should return the result of parsing the url', function() {
            var result = {whatso: 'ever'};

            require('url').parse.returns(result);

            expect(this.controller.getUrl()).to.eql(result);
        });

        it('should not call url.parse twice', function() {
            var url = require('url');

            url.parse.returns({});

            this.controller.getUrl();
            this.controller.getUrl();

            expect(url.parse.calledOnce).to.be(true);
        });

        it('should return cached url on the second call', function() {
            var result = {whatso: 'ever'};
            var url = require('url');

            url.parse.returns(result);

            this.controller.getUrl();
            expect(this.controller.getUrl()).to.eql(result);

            url.parse.restore();
        });

        it('should return a copy of parsed url, so that altering it does not affects later uses', function() {
            var url = require('url');

            url.parse.returns({save: 'me'});

            this.controller.getUrl().another = 'one';
            this.controller.getUrl().additional = 'one';
            this.controller.getUrl().multiple = 'ones';

            expect(this.controller.getUrl()).to.eql({save: 'me'});

            url.parse.restore();
        });
    });

    describe('getTld', function() {
        _.each(
            {
                'yandex.ru': 'ru',
                'yandex.com': 'com',
                'yandex.com.tr': 'com.tr',
                'yandex.st': 'st',
                'ya.ru': 'ru',
                nope: 'ru',
                'passport.yandex.ru': 'ru',
                'passport.yandex.com.tr': 'com.tr',
                'passport-test.yandex.ua': 'ua',
                'iamevil_yandex.com': 'ru'
            },
            function(expectedValue, hostname) {
                it('should return ' + expectedValue + ' for hostname ' + hostname, function() {
                    var url = require('url');

                    sinon.stub(url, 'parse').returns({
                        hostname: hostname
                    });

                    expect(this.controller.getTld()).to.be(expectedValue);

                    url.parse.restore();
                });
            }
        );
    });

    describe('requestedWithRetpath', function() {
        beforeEach(function() {
            sinon.stub(this.controller, 'getRequestParam');
        });

        it('should return true if controller\'s getRequestParam("retpath") returns a truthy value', function() {
            this.controller.getRequestParam.withArgs('retpath').returns('http://mail.yandex.ru');
            expect(this.controller.requestedWithRetpath()).to.be(true);
        });

        it('should return false if controller\'s getRequestParam("retpath") returns a falsey value', function() {
            this.controller.getRequestParam.withArgs('retpath').returns('');
            expect(this.controller.requestedWithRetpath()).to.be(false);
        });
    });

    describe('getCookie', function() {
        beforeEach(function() {
            sinon.stub(this.res, 'cookie');
        });

        it('should throw if cookie name is not a string', function() {
            var getCookie = this.controller.getCookie;

            expect(function() {
                getCookie(123);
            }).to.throwError(function(e) {
                expect(e.message).to.be('Cookie name should be a string');
            });
        });

        it('should return cookie by name', function() {
            var myCookie = {};

            this.req.cookies = {
                myCookie: myCookie
            };
            expect(this.controller.getCookie('myCookie')).to.be(myCookie);
        });

        it('should return value that was set by setCookie', function() {
            var name = 'myCookie';
            var val = 'cookieValue';

            this.controller.setCookie(name, val);
            expect(this.controller.getCookie(name)).to.be(val);
        });
    });

    describe('setCookie', function() {
        beforeEach(function() {
            this.name = 'myCookie';
            this.contents = 'lorem ipsum dolor sit amet';
            this.options = {
                expires: '1',
                path: '/'
            };

            this.res.cookie = sinon.stub();
        });
        it('should throw if cookie name is not a string', function() {
            var that = this;
            var setCookie = this.controller.setCookie;

            expect(function() {
                setCookie(false, that.contents);
            }).to.throwError(function(e) {
                expect(e.message).to.be('Cookie name should be a string');
            });
        });

        _.each(
            {
                'an empty string': '',
                'a digit': 1,
                'a boolean': true,
                undefined: undefined,
                null: null,
                'not a plain object': new (function() {
                    this.smth = function() {};
                })()
            },
            function(value, description) {
                it('should throw if cookie contents is ' + description, function() {
                    var that = this;
                    var setCookie = this.controller.setCookie;

                    expect(function() {
                        setCookie(that.name, value);
                    }).to.throwError(function(e) {
                        expect(e.message).to.be('Cookie contents should be a string or a plain object');
                    });
                });
            }
        );

        it('should throw if options are present and not a plain object', function() {
            var that = this;
            var setCookie = this.controller.setCookie;

            expect(function() {
                setCookie(that.name, that.contents, true);
            }).to.throwError(function(e) {
                expect(e.message).to.be('Cookie options should be a plain object if present');
            });
        });

        it('should call request.cookie with provided arguments', function() {
            this.controller.setCookie(this.name, this.contents, this.options);
            expect(this.res.cookie.calledWithExactly(this.name, this.contents, this.options)).to.be(true);
        });

        it('should not pass options to request.cookie, if they are not set', function() {
            this.controller.setCookie(this.name, this.contents);
            expect(this.res.cookie.calledWithExactly(this.name, this.contents)).to.be(true);
        });
    });

    describe('getHeader', function() {
        it('should throw if header name is not a string', function() {
            var getHeader = this.controller.getHeader;

            expect(function() {
                getHeader({});
            }).to.throwError(function(e) {
                expect(e.message).to.be('Header name should be a string');
            });
        });

        it('should return a header by its name', function() {
            var myHeader = {};

            this.req.headers = {
                myHeader: myHeader
            };

            expect(this.controller.getHeader('myHeader')).to.be(myHeader);
        });
    });

    describe('getIp', function() {
        it('should return the value of x-real-ip header', function() {
            var ip = '127.0.0.1';

            sinon
                .stub(this.controller, 'getHeader')
                .withArgs('x-real-ip')
                .returns(ip);
            expect(this.controller.getIp()).to.be(ip);
        });
    });

    describe('getRequestParam', function() {
        beforeEach(function() {
            this.req.nquery = {};
            this.req.body = {};
            this.req.query = {};
            this.req.params = {};
        });

        it('should throw if param name is not a string', function() {
            var getRequestParam = this.controller.getRequestParam;

            expect(function() {
                getRequestParam({});
            }).to.throwError(function(e) {
                expect(e.message).to.be('Param name should be a string');
            });
        });

        it('should return value form request.nquery even if body or param or query has one with same name', function() {
            var rightValue = '123';
            var wrongValue = '456';

            this.req.nquery['myValue'] = rightValue;
            this.req.body['myValue'] = wrongValue;
            this.req.query['myValue'] = wrongValue;
            this.req.params['myValue'] = wrongValue;

            expect(this.controller.getRequestParam('myValue')).to.be(rightValue);
        });

        it('should use request.query if value is not found in request.nquery', function() {
            var rightValue = '123';
            var wrongValue = '456';

            this.req.query['myValue'] = rightValue;
            this.req.body['myValue'] = wrongValue;
            this.req.params['myValue'] = wrongValue;

            expect(this.controller.getRequestParam('myValue')).to.be(rightValue);
        });

        it('should use request.body if value is not found in request.nquery or request.query', function() {
            var rightValue = '123';
            var wrongValue = '456';

            this.req.body['myValue'] = rightValue;
            this.req.params['myValue'] = wrongValue;

            expect(this.controller.getRequestParam('myValue')).to.be(rightValue);
        });

        it(
            'should use request.params if value is not found in ' + 'request.nquery or request.query or request.body',
            function() {
                var rightValue = '123';

                this.req.params['myValue'] = rightValue;

                expect(this.controller.getRequestParam('myValue')).to.be(rightValue);
            }
        );
    });

    describe('getFormData', function() {
        it('should return request body', function() {
            this.req.body = {};
            expect(this.controller.getFormData()).to.be(this.req.body);
        });
    });

    describe('render', function() {
        beforeEach(function() {
            this.res.render = sinon.stub();

            this.skin = 'registration.ru.js';
            this.template = {
                form: {
                    control: [
                        {
                            id: 'submit',
                            value: 'Поехали!'
                        }
                    ]
                }
            };
        });

        it('should throw if skinName is not a string', function() {
            var that = this;

            expect(function() {
                that.controller.render(null, that.template);
            }).to.throwError(function(e) {
                expect(e.message).to.be('Skin name should be a string');
            });
        });

        it('should throw if templateData is not a plainObject', function() {
            var that = this;

            expect(function() {
                that.controller.render(that.skin, 'template!');
            }).to.throwError(function(e) {
                expect(e.message).to.be('Template data should be a plain object');
            });
        });

        it('should call response.render with skinName and templateData', function() {
            this.controller.render(this.skin, this.template);
            expect(this.res.render.calledOnce).to.be(true);
            expect(this.res.render.calledWithExactly(this.skin, this.template));
        });
    });

    describe('sendPage', function() {
        beforeEach(function() {
            sinon.stub(this.res, 'send');
            this._status = sinon.spy();
            var self = this;

            this.res.status = function() {
                self._status.apply(self, arguments);
                return self.res;
            };
            this.html = '<html><head></head><body></body></html>';
            this.code = 403;
        });

        it('should throw if first arg is not a string', function() {
            var controller = this.controller;

            expect(function() {
                controller.sendPage({});
            }).to.throwError(function(err) {
                expect(err.message).to.be('Value to send to client should be a string');
            });
        });

        it('should throw if code is not a string', function() {
            var html = this.html;
            var controller = this.controller;

            expect(function() {
                controller.sendPage(html, {});
            }).to.throwError(function(err) {
                expect(err.message).to.be('Response code should be a number');
            });
        });

        it('should call send method of the response object', function() {
            this.controller.sendPage(this.html);
            expect(this._status.calledOnce).to.be(true);
        });

        it(
            'should call status and send methods of the response object ' +
                'with the given html and code 200 if no code is given',
            function() {
                this.controller.sendPage(this.html);
                expect(this._status.calledWithExactly(200)).to.be(true);
                expect(this.res.send.calledWithExactly(this.html)).to.be(true);
            }
        );

        it('should call status and send methods of the response object with the given html and code', function() {
            this.controller.sendPage(this.html, this.code);
            expect(this._status.calledWithExactly(this.code)).to.be(true);
            expect(this.res.send.calledWithExactly(this.html)).to.be(true);
        });

        it('should return the promise', function() {
            var when = require('when');

            expect(when.isPromiseLike(this.controller.sendPage(this.html))).to.be(true);
        });
    });

    describe('redirect', function() {
        beforeEach(function() {
            this.res.redirect = sinon.stub();
            this.url = 'http://mail.yandex.ru/neo2#inbox';
        });

        it('should throw if url is not a string', function() {
            var that = this;

            expect(function() {
                that.controller.redirect(null);
            }).to.throwError(function(e) {
                expect(e.message).to.be('Url should be a string');
            });
        });

        it('should call response.redirect with the given url', function() {
            this.controller.redirect(this.url);
            expect(this.res.redirect.calledOnce).to.be(true);
            expect(this.res.redirect.calledWithExactly(this.url)).to.be(true);
        });
    });

    describe('getMethod', function() {
        beforeEach(function() {
            this.req.method = 'Scratch';
        });

        it('should return an instance of controller.HTTPMethod', function() {
            expect(this.controller.getMethod()).to.be.a(this.Controller.HTTPMethod);
        });

        it('should return an HTTPMethod instance set up with value of request.method', function() {
            expect(this.controller.getMethod().toString()).to.be(this.req.method.toLowerCase());
        });

        it('should always return the same instance', function() {
            expect(this.controller.getMethod()).to.be(this.controller.getMethod());
        });
    });

    describe('HTTPMethod type', function() {
        beforeEach(function() {
            this.value = 'PoSt';
            this.Method = this.Controller.HTTPMethod;
            this.method = new this.Method(this.value);
        });
        describe('constructor', function() {
            _.each(
                {
                    'not defined': undefined,
                    'not a string': 123
                },
                function(value, description) {
                    it('should throw if first argument is ' + description, function() {
                        var Method = this.Method;

                        expect(function() {
                            new Method(value);
                        }).to.throwError(function(err) {
                            expect(err.message).to.be('Method should be instantiated with HTTP method string');
                        });
                    });
                }
            );
        });

        describe('toString', function() {
            it('should return the lowercase string value the object was created with', function() {
                expect(this.method.toString()).to.be(this.value.toLowerCase());
            });
        });

        describe('isPost', function() {
            it('should return true if object was created with "post" string', function() {
                expect(this.method.isPost()).to.be(true);
            });

            it('should return false if object was not created with "post" string', function() {
                expect(new this.Method('get').isPost()).to.be(false);
            });
        });

        describe('isGet', function() {
            it('should return true if object was created with "get" string', function() {
                expect(new this.Method('GET').isGet()).to.be(true);
            });

            it('should return false if object was not created with "get" string', function() {
                expect(this.method.isGet()).to.be(false);
            });
        });
    });
});
