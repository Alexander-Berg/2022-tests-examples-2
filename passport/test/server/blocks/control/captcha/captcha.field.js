var expect = require('expect.js');
var sinon = require('sinon');
var when = require('when');
var _ = require('lodash');

var CaptchaField = require('../../../../../blocks/control/captcha/captcha.field');

describe('Captcha Field', function() {
    beforeEach(function() {
        this.captcha = new CaptchaField();

        this.formData = {
            key: 'aingoChah7shuobeepaeki7pheka5oos',
            answer: '1337',
            captcha_mode: 'audio'
        };

        this.apiDeferred = when.defer();
        this.api = {
            captchaCheck: sinon.stub().returns(this.apiDeferred.promise)
        };

        this.responses = {
            correct: {
                field: 'captcha',
                body: {
                    status: 'ok',
                    correct: true
                }
            },
            incorrect: {
                field: 'captcha',
                body: {
                    status: 'ok',
                    correct: false
                }
            }
        };

        sinon.stub(require('putils'), 'i18n').returns('localized');
    });

    afterEach(function() {
        require('putils').i18n.restore();
    });

    describe('Constructor', function() {
        it('should create captcha with text mode', function() {
            expect(this.captcha.getMode()).to.be('text');
        });
    });

    describe('setMode', function() {
        ['text', 'audio'].forEach(function(mode) {
            it(`should set mode to ${mode}`, function() {
                expect(this.captcha.setMode(mode).getMode()).to.be(mode);
            });
        });

        it('should set mode to text if called with an unknown mode', function() {
            expect(
                this.captcha
                    .setMode('audio')
                    .setMode('an unknown mode')
                    .getMode()
            ).to.be('text');
        });

        it('should return the captcha itself for chaining', function() {
            expect(this.captcha.setMode('text')).to.be(this.captcha);
        });
    });

    describe('compile', function() {
        beforeEach(function() {
            this.lang = 'ru';
            this.captchaGeneratorResponse = {
                field: 'captcha',
                body: {
                    status: 'ok',
                    image_url: 'http://u.captcha.yandex.net/image?key=40PGN6nHC5B2FLw9tP90tfR0PIRAVnwA',
                    key: '40PGN6nHC5B2FLw9tP90tfR0PIRAVnwA',
                    voice: {
                        intro_url: 'introUrl',
                        url: 'audioCaptchaUrl'
                    }
                }
            };

            this.captchaGenerateDeferred = when.defer();
            this.captchaGenerateDeferred.resolve(this.captchaGeneratorResponse);
            this.api['captchaGenerate'] = sinon.stub().returns(this.captchaGenerateDeferred.promise);
        });

        it('should call captchaGenerate', function() {
            this.captcha.compile(this.lang, this.api);
            expect(this.api.captchaGenerate.calledOnce).to.be(true);
        });

        it('should return a promise', function() {
            expect(when.isPromiseLike(this.captcha.compile(this.lang, this.api))).to.be(true);
        });

        it('should call setKey with a value from captchaGenerate response', function(done) {
            var captcha = this.captcha;
            var response = this.captchaGeneratorResponse;

            sinon.stub(captcha, 'setKey');
            captcha
                .compile(this.lang, this.api)
                .then(function() {
                    expect(captcha.setKey.calledWithExactly(response.body.key)).to.be(true);
                    done();
                })
                .then(null, done);
        });

        it('should add key value to the compiled captcha', function(done) {
            var captcha = this.captcha;
            var response = this.captchaGeneratorResponse;

            captcha
                .compile(this.lang, this.api)
                .then(function(compiled) {
                    expect(compiled.key).to.be(response.body.key);
                    done();
                })
                .then(null, done);
        });

        it('should add image url from captchaGenerate response to the compiled captcha', function(done) {
            var captcha = this.captcha;
            var response = this.captchaGeneratorResponse;

            captcha
                .compile(this.lang, this.api)
                .then(function(compiled) {
                    expect(compiled.image_url).to.be(response.body.image_url);
                    done();
                })
                .then(null, done);
        });

        it('should add current mode to the compiled captcha', function(done) {
            var captcha = this.captcha;
            var mode = 'whaasdfasdfkljashdfkljsdfh';

            sinon.stub(captcha, 'getMode').returns(mode);
            captcha
                .compile(this.lang, this.api)
                .then(function(compiled) {
                    expect(compiled.mode).to.be(mode);
                    done();
                })
                .then(null, done);
        });

        it('should add static path from config to the compiled.static', function(done) {
            var captcha = this.captcha;

            var staticPath = '/laethohvu7fieFiediph2chaeshomaa2';

            sinon.stub(captcha, 'getStaticPath').returns(staticPath);

            captcha
                .compile(this.lang, this.api)
                .then(function(compiled) {
                    expect(compiled.static).to.be(staticPath);
                    done();
                })
                .then(null, done);
        });

        it("should resolve with an object containing all the fields from parent's compile", function(done) {
            var compiledByParent = new (require('pform/Field'))('id').compile.call(this.captcha, this.lang);

            this.captcha
                .compile(this.lang, this.api)
                .then(function(compiled) {
                    _.each(compiledByParent, function(value, key) {
                        expect(compiled[key]).to.eql(value);
                    });

                    done();
                })
                .then(null, done);
        });
    });

    describe('isEmpty', function() {
        it('should return true if answer field is empty', function() {
            this.formData.answer = ' ';
            expect(this.captcha.isEmpty(this.formData, this.api)).to.be(true);
        });

        it('should return false if answer field is not empty', function() {
            expect(this.captcha.isEmpty(this.formData, this.api)).to.be(false);
        });
    });

    describe('onEmpty', function() {
        it('should set missingvalue error active if field is required', function() {
            this.captcha.setRequired().onEmpty(this.formData, this.api);
            expect(this.captcha.getErrorByCode('missingvalue').isActive()).to.be(true);
        });

        it('should not set missingvalue error active if field is optional', function() {
            this.captcha.setOptional().onEmpty(this.formData, this.api);
            expect(this.captcha.getErrorByCode('missingvalue').isActive()).to.be(false);
        });

        it('should set mode to the mode from formData', function() {
            sinon.stub(this.captcha, 'setMode');
            this.captcha.onEmpty(this.formData, this.api);
            expect(this.captcha.setMode.calledWithExactly(this.formData.captcha_mode)).to.be(true);
        });
    });

    describe('validate', function() {
        it('should return ["captchalocate"] if key is empty', function() {
            this.formData.key = ' ';
            expect(this.captcha.validate(this.formData, this.api)).to.eql(['captchalocate']);
        });

        it('should call captchaCheck method of api', function() {
            this.captcha.validate(this.formData, this.api);
            expect(this.api.captchaCheck.calledOnce).to.be(true);
        });

        it('should pass answer and key fields to captchaCheck', function() {
            this.captcha.validate(this.formData, this.api);
            var arg = this.api.captchaCheck.firstCall.args[0];

            expect(arg).to.have.property('answer', this.formData.answer);
            expect(arg).to.have.property('key', this.formData.key);
        });

        it('should normalize answer before passing it to captchaCheck', function() {
            this.formData.answer = ' normalize  me   ';
            this.captcha.validate(this.formData, this.api);
            expect(this.api.captchaCheck.firstCall.args[0]).to.have.property('answer', 'normalize me');
        });

        it('should resolve with an empty array if response contains "correct: true"', function(done) {
            this.captcha
                .validate(this.formData, this.api)
                .then(function(result) {
                    expect(result).to.eql([]);
                    done();
                })
                .then(null, done);

            this.apiDeferred.resolve(this.responses.correct);
        });

        it('should resolve with ["incorrect"] if response contains "correct: false"', function(done) {
            this.captcha
                .validate(this.formData, this.api)
                .then(function(result) {
                    expect(result).to.eql(['incorrect']);
                    done();
                })
                .then(null, done);

            this.apiDeferred.resolve(this.responses.incorrect);
        });
    });

    describe('onValid', function() {
        it('should not call setValue', function() {
            sinon.stub(this.captcha, 'setValue');
            this.captcha.onValid(this.formData, this.api);
            expect(this.captcha.setValue.called).to.be(false);
        });

        it('should set mode to the mode from formData', function() {
            sinon.stub(this.captcha, 'setMode');
            this.captcha.onValid(this.formData, this.api);
            expect(this.captcha.setMode.calledWithExactly(this.formData.captcha_mode)).to.be(true);
        });
    });

    describe('onInvalid', function() {
        beforeEach(function() {
            this.errors = ['incorrect'];
        });

        it('should not call setValue', function() {
            sinon.stub(this.captcha, 'setValue');
            this.captcha.onInvalid(this.errors, this.formData, this.api);
            expect(this.captcha.setValue.called).to.be(false);
        });

        it('should set active all the errors api returned', function() {
            this.captcha.onInvalid(this.errors, this.formData, this.api);

            var captcha = this.captcha;

            this.errors.forEach(function(error) {
                expect(captcha.getErrorByCode(error).isActive()).to.be(true);
            });
        });

        it('should set mode to the mode from formData', function() {
            sinon.stub(this.captcha, 'setMode');
            this.captcha.onInvalid(this.errors, this.formData, this.api);
            expect(this.captcha.setMode.calledWithExactly(this.formData.captcha_mode)).to.be(true);
        });
    });
});
