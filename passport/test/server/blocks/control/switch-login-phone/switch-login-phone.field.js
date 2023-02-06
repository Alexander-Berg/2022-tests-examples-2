var expect = require('expect.js');
var sinon = require('sinon');
var when = require('when');
var _ = require('lodash');

var LoginPhoneField = require('../../../../../blocks/control/switch-login-phone/switch-login-phone.field');

describe('Switch-login-phone Field', function() {
    beforeEach(function() {
        this.loginPhone = new LoginPhoneField();
        this.formData = {
            'switch-login-phone': 'login'
        };

        sinon.stub(require('putils'), 'i18n').returns('localized');
    });

    afterEach(function() {
        require('putils').i18n.restore();
    });

    describe('isEmpty', function() {
        ['phone', 'login'].forEach(function(switchValue) {
            it(`should return false if switch-login-phone is ${switchValue}`, function() {
                this.formData['switch-login-phone'] = switchValue;
                expect(this.loginPhone.isEmpty(this.formData)).to.be(false);
            });
        });

        _.each(
            {
                null: null,
                undefined: undefined,
                'any string besides phone or captcha': 'hey-hey-hey',
                'a boolean': true,
                'a number': 1
            },
            function(value, description) {
                it(`should return true if switch-login-phone is ${description}`, function() {
                    this.formData['switch-login-phone'] = value;
                    expect(this.loginPhone.isEmpty(this.formData)).to.be(true);
                });
            }
        );
    });

    describe('onEmpty', function() {
        beforeEach(function() {
            sinon.stub(this.loginPhone, 'setValue');
        });

        it('should set value of the field to "login"', function() {
            this.loginPhone.onEmpty();
            expect(this.loginPhone.setValue.calledWithExactly('login')).to.be(true);
        });
    });

    describe('validate', function() {
        beforeEach(function() {
            this.form = {
                setApi: sinon.stub(),
                validate: sinon.stub().returns(when.defer().promise)
            };
            sinon.stub(this.loginPhone, '_getPhoneForm').returns(this.form);
            sinon.stub(this.loginPhone, '_getLoginForm').returns(this.form);
        });

        var formValidations = function() {
            it('should set api for the form', function() {
                this.loginPhone.validate(this.formData, this.api);
                expect(this.form.setApi.calledWithExactly(this.api)).to.be(true);
            });

            it('should validate the form', function() {
                this.loginPhone.validate(this.formData, this.api);
                expect(this.form.validate.calledOnce).to.be(true);
                expect(this.form.validate.calledWithExactly(this.formData)).to.be(true);
            });

            it('should resolve with [] if form validation resolved with true', function(done) {
                var deferred = when.defer();

                this.form.validate.returns(deferred.promise);

                this.loginPhone
                    .validate(this.formData, this.api)
                    .then(function(result) {
                        expect(result).to.eql([]);
                        done();
                    })
                    .then(null, done);

                deferred.resolve(true);
            });
        };

        describe('when switch is in "login"', function() {
            beforeEach(function() {
                this.formData[this.loginPhone.getName()] = 'login';
            });

            it('should call _getLoginForm to get the form', function() {
                this.loginPhone.validate(this.formData, this.api);
                expect(this.loginPhone._getLoginForm.calledOnce).to.be(true);
            });

            it('should not call _getPhoneForm', function() {
                this.loginPhone.validate(this.formData, this.api);
                expect(this.loginPhone._getPhoneForm.called).to.be(false);
            });

            formValidations();
        });

        describe('when switch is in "phone"', function() {
            beforeEach(function() {
                this.formData[this.loginPhone.getName()] = 'phone';
            });

            it('should call _getPhoneForm to get the form', function() {
                this.loginPhone.validate(this.formData, this.api);
                expect(this.loginPhone._getPhoneForm.calledOnce).to.be(true);
            });

            it('should not call _getLoginForm', function() {
                this.loginPhone.validate(this.formData, this.api);
                expect(this.loginPhone._getLoginForm.called).to.be(false);
            });

            formValidations();
        });
    });

    describe('onValid', function() {
        it('should set value according to the form', function() {
            sinon.stub(this.loginPhone, 'setValue');
            this.loginPhone.onValid(this.formData, this.api);
            expect(this.loginPhone.setValue.calledWithExactly(this.formData['switch-login-phone'])).to.be(true);
        });
    });

    describe('onInvalid', function() {
        beforeEach(function() {
            this.errors = ['unconfirmed'];
        });
        it('should set value according to the form', function() {
            sinon.stub(this.loginPhone, 'setValue');
            this.loginPhone.onInvalid(this.errors, this.formData, this.api);
            expect(this.loginPhone.setValue.calledWithExactly(this.formData['switch-login-phone'])).to.be(true);
        });
    });

    describe('compile', function() {
        beforeEach(function() {
            this.lang = 'ru';
        });
        it('should set value to login if no value is set', function() {
            sinon.stub(this.loginPhone, 'setValue');
            sinon.stub(this.loginPhone, 'getValue').returns(null);
            this.loginPhone.compile(this.lang, this.api);
            expect(this.loginPhone.setValue.calledWithExactly('login')).to.be(true);
        });

        it('should have all the fields parent compile returns', function(done) {
            var compiledByParent = new (require('pform/Field'))('id').compile.call(this.loginPhone, this.lang);

            this.loginPhone
                .compile(this.lang, this.api)
                .then(function(compiled) {
                    _.each(compiledByParent, function(value, key) {
                        expect(compiled[key]).to.eql(value);
                    });

                    done();
                })
                .then(null, done);
        });

        it('should not have unconfirmed error in the compiled output', function() {
            var compiled = this.loginPhone.compile(this.lang, this.api);

            expect(
                _.find(compiled.errors, function(error) {
                    return error.code === 'unconfirmed';
                })
            ).to.be(undefined);
        });

        it('should call compile on all child blocks with the language passed', function() {
            var loginPhone = this.loginPhone;
            var lang = this.lang;
            var children = ['login', 'phone'];

            children.forEach(function(child) {
                sinon.stub(loginPhone[child], 'compile');
            });

            loginPhone.compile(lang);

            children.forEach(function(child) {
                expect(loginPhone[child].compile.calledOnce).to.be(true);
                expect(loginPhone[child].compile.calledWith(lang)).to.be(true);
            });
        });

        it('should return compiled child blocks as properties of the compiled field', function() {
            var loginPhone = this.loginPhone;
            var children = ['login', 'phone'];

            children.forEach(function(child) {
                //Making children's compile return child name
                sinon.stub(loginPhone[child], 'compile').returns(child);
            });

            loginPhone.compile(this.lang).then(function(compiled) {
                children.forEach(function(child) {
                    //See previous forEach for expectation
                    expect(compiled[child]).to.be(child);
                });
            });
        });
    });

    describe('normalize', function() {
        beforeEach(function() {
            this.normalized = {a: 'b', c: 'd', e: 'f'};
            this.form = {
                normalize: sinon.stub().returns(this.normalized)
            };

            sinon.stub(this.loginPhone, '_getLoginForm').returns(this.form);
            sinon.stub(this.loginPhone, '_getPhoneForm').returns(this.form);
        });

        var normalization = function() {
            it('should call normalize on the form', function() {
                this.loginPhone.normalize(this.formData);
                expect(this.form.normalize.calledOnce).to.be(true);
                expect(this.form.normalize.calledWithExactly(this.formData)).to.be(true);
            });

            it("should return the result of normalization of the form extended with fields's own value", function() {
                expect(this.loginPhone.normalize(this.formData)).to.eql(
                    _.extend(_.clone(this.normalized), this.formData)
                );
            });
        };

        describe('when the switch is in login', function() {
            beforeEach(function() {
                sinon.stub(this.loginPhone, 'getValue').returns('login');
            });

            it('should call _getLoginForm', function() {
                this.loginPhone.normalize(this.formData);
                expect(this.loginPhone._getLoginForm.calledOnce).to.be(true);
            });

            it('should not call _getPhoneForm', function() {
                this.loginPhone.normalize(this.formData);
                expect(this.loginPhone._getPhoneForm.called).to.be(false);
            });

            normalization();
        });

        describe('when the switch is in phone', function() {
            beforeEach(function() {
                sinon.stub(this.loginPhone, 'getValue').returns('phone');
            });

            it('should call _getPhoneForm', function() {
                this.loginPhone.normalize(this.formData);
                expect(this.loginPhone._getPhoneForm.calledOnce).to.be(true);
            });

            it('should not call _getCaptchaForm', function() {
                this.loginPhone.normalize(this.formData);
                expect(this.loginPhone._getLoginForm.called).to.be(false);
            });

            normalization();
        });
    });
});
