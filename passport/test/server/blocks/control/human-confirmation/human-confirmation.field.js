var expect = require('expect.js');
var sinon = require('sinon');
var when = require('when');
var _ = require('lodash');

var mock = require('../../../../util/mock/mockData.js');

var HumanConfirmationField = require('../../../../../blocks/control/human-confirmation/human-confirmation.field');

describe('Human Confirmation Field', function() {
    beforeEach(function() {
        this.hc = new HumanConfirmationField();
        this.formData = {
            'human-confirmation': 'phone'
        };
        var API = require('../../../../../lib/passport-api');

        this.api = new API('ael3ai7acha6be4aethaL8faihieseex', mock.headers, mock.basic.track_id);

        sinon.stub(require('putils'), 'i18n').returns('localized');
    });

    afterEach(function() {
        require('putils').i18n.restore();
    });

    describe('isEmpty', function() {
        ['phone', 'captcha'].forEach(function(switchValue) {
            it(`should return false if human-confirmation is ${switchValue}`, function() {
                this.formData['human-confirmation'] = switchValue;
                expect(this.hc.isEmpty(this.formData)).to.be(false);
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
                it(`should return true if human-confirmation is ${description}`, function() {
                    this.formData['human-confirmation'] = value;
                    expect(this.hc.isEmpty(this.formData)).to.be(true);
                });
            }
        );
    });

    describe('onEmpty', function() {
        beforeEach(function() {
            sinon.stub(this.hc, 'setValue');
        });

        it('should set value of the field to "phone"', function() {
            this.hc.onEmpty();
            expect(this.hc.setValue.calledWithExactly('phone')).to.be(true);
        });

        it('should set unconfirmed error active', function() {
            var err = {
                setActive: sinon.stub()
            };

            sinon
                .stub(this.hc, 'getErrorByCode')
                .withArgs('unconfirmed')
                .returns(err);

            this.hc.onEmpty();

            expect(this.hc.getErrorByCode.calledWithExactly('unconfirmed'));
            expect(err.setActive.calledOnce).to.be(true);
        });
    });

    describe('validate', function() {
        beforeEach(function() {
            this.form = {
                setApi: sinon.stub(),
                validate: sinon.stub().returns(when.defer().promise)
            };
            sinon.stub(this.hc, '_getPhoneForm').returns(this.form);
            sinon.stub(this.hc, '_getCaptchaForm').returns(this.form);
        });

        var formValidations = function() {
            it('should set api for the form', function() {
                this.hc.validate(this.formData, this.api);
                expect(this.form.setApi.calledWithExactly(this.api)).to.be(true);
            });

            it('should validate the form', function() {
                this.hc.validate(this.formData, this.api);
                expect(this.form.validate.calledOnce).to.be(true);
                expect(this.form.validate.calledWithExactly(this.formData)).to.be(true);
            });

            it('should resolve with ["unconfirmed"] if form validation resolved with false', function(done) {
                var deferred = when.defer();

                this.form.validate.returns(deferred.promise);

                this.hc
                    .validate(this.formData, this.api)
                    .then(function(result) {
                        expect(result).to.eql(['unconfirmed']);
                        done();
                    })
                    .then(null, done);

                deferred.resolve(false);
            });

            it('should set unconfirmed error active if form validation resolved with false', function(done) {
                var deferred = when.defer();

                this.form.validate.returns(deferred.promise);

                var hc = this.hc;

                hc.validate(this.formData, this.api)
                    .then(function() {
                        expect(hc.getErrorByCode('unconfirmed').isActive()).to.be(true);
                        done();
                    })
                    .then(null, done);

                deferred.resolve(false);
            });

            it('should resolve with [] if form validation resolved with true', function(done) {
                var deferred = when.defer();

                this.form.validate.returns(deferred.promise);

                this.hc
                    .validate(this.formData, this.api)
                    .then(function(result) {
                        expect(result).to.eql([]);
                        done();
                    })
                    .then(null, done);

                deferred.resolve(true);
            });
        };

        describe('when switch is in "phone"', function() {
            beforeEach(function() {
                this.formData[this.hc.getName()] = 'phone';
            });

            it('should call _getPhoneForm to get the form', function() {
                this.hc.validate(this.formData, this.api);
                expect(this.hc._getPhoneForm.calledOnce).to.be(true);
            });

            it('should not call _getCaptchaForm', function() {
                this.hc.validate(this.formData, this.api);
                expect(this.hc._getCaptchaForm.called).to.be(false);
            });

            formValidations();
        });

        describe('when switch is in "captcha"', function() {
            beforeEach(function() {
                this.formData[this.hc.getName()] = 'captcha';
            });

            it('should call _getCaptchaForm to get the form', function() {
                this.hc.validate(this.formData, this.api);
                expect(this.hc._getCaptchaForm.calledOnce).to.be(true);
            });

            it('should not call _getPhoneForm', function() {
                this.hc.validate(this.formData, this.api);
                expect(this.hc._getPhoneForm.called).to.be(false);
            });

            formValidations();
        });
    });

    describe('onValid', function() {
        it('should set value according to the form', function() {
            sinon.stub(this.hc, 'setValue');
            this.hc.onValid(this.formData, this.api);
            expect(this.hc.setValue.calledWithExactly(this.formData['human-confirmation'])).to.be(true);
        });
    });
    describe('onInvalid', function() {
        beforeEach(function() {
            this.errors = ['unconfirmed'];
        });
        it('should set value according to the form', function() {
            sinon.stub(this.hc, 'setValue');
            this.hc.onInvalid(this.errors, this.formData, this.api);
            expect(this.hc.setValue.calledWithExactly(this.formData['human-confirmation'])).to.be(true);
        });

        it('should set errors active', function() {
            var hc = this.hc;

            hc.onInvalid(this.errors, this.formData, this.api);

            this.errors.forEach(function(error) {
                expect(hc.getErrorByCode(error).isActive()).to.be(true);
            });
        });
    });

    describe('compile', function() {
        beforeEach(function() {
            this.lang = 'ru';
        });
        it('should call setOption with value if value is set', function() {
            sinon.stub(this.hc, 'setOption');
            sinon.stub(this.hc, 'getValue').returns('kaboom');
            this.hc.compile(this.lang, this.api);
            expect(this.hc.setOption.calledWithExactly('value', 'kaboom')).to.be(true);
        });

        it('should show only captcha input if user exceeded SMS limit', function(done) {
            sinon.stub(this.api, 'getRegistrationLimits').returns(
                when.resolve({
                    status: 'ok',
                    sms_remained_count: 0,
                    confirmation_remained_count: 4
                })
            );
            var children = ['question', 'userQuestion', 'answer', 'captcha', 'phoneConfirm'];
            var hc = this.hc;

            children.forEach(function(child) {
                sinon.stub(hc[child], 'compile');
            });

            when(this.hc.compile(this.lang, this.api)).then(
                function(compiled) {
                    expect(compiled.options['no-switch']).to.be(true);
                    expect(compiled.options.value).to.be.equal('captcha');
                    done();
                    this.api.getRegistrationLimits.restore();
                }.bind(this)
            );
        });

        it('should not have unconfirmed error in the compiled output', function() {
            var compiled = this.hc.compile(this.lang, this.api);

            expect(
                _.find(compiled.errors, function(error) {
                    return error.code === 'unconfirmed';
                })
            ).to.be(undefined);
        });

        it('should call compile on all child blocks with the language passed', function() {
            var hc = this.hc;
            var lang = this.lang;
            var children = ['question', 'userQuestion', 'answer', 'captcha', 'phoneConfirm'];

            children.forEach(function(child) {
                sinon.stub(hc[child], 'compile');
            });

            hc.compile(lang, this.api);

            children.forEach(function(child) {
                expect(hc[child].compile.calledOnce).to.be(true);
                expect(hc[child].compile.calledWith(lang)).to.be(true);
            });
        });

        it('should return compiled child blocks as properties of the compiled field', function() {
            var hc = this.hc;
            var children = ['question', 'userQuestion', 'answer', 'captcha', 'phoneConfirm'];

            children.forEach(function(child) {
                //Making children's compile return child name
                sinon.stub(hc[child], 'compile').returns(child);
            });

            hc.compile(this.lang, this.api).then(function(compiled) {
                children.forEach(function(child) {
                    var childName = child;

                    if (child === 'userQuestion') {
                        childName = 'user_question';
                    }
                    if (child === 'phoneConfirm') {
                        childName = 'phone_confirm';
                    }
                    //See previous forEach for expectation
                    expect(compiled[childName]).to.be(child);
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

            sinon.stub(this.hc, '_getPhoneForm').returns(this.form);
            sinon.stub(this.hc, '_getCaptchaForm').returns(this.form);
        });

        var normalization = function() {
            it('should call normalize on the form', function() {
                this.hc.normalize(this.formData);
                expect(this.form.normalize.calledOnce).to.be(true);
                expect(this.form.normalize.calledWithExactly(this.formData)).to.be(true);
            });

            it("should return the result of normalization of the form extended with fields's own value", function() {
                expect(this.hc.normalize(this.formData)).to.eql(_.extend(_.clone(this.normalized), this.formData));
            });
        };

        describe('when the switch is in captcha', function() {
            beforeEach(function() {
                sinon.stub(this.hc, 'getValue').returns('captcha');
            });

            it('should call _getCaptchaForm', function() {
                this.hc.normalize(this.formData);
                expect(this.hc._getCaptchaForm.calledOnce).to.be(true);
            });

            it('should not call _getPhoneForm', function() {
                this.hc.normalize(this.formData);
                expect(this.hc._getPhoneForm.called).to.be(false);
            });

            normalization();
        });

        describe('when the switch is in phone', function() {
            beforeEach(function() {
                sinon.stub(this.hc, 'getValue').returns('phone');
            });

            it('should call _getPhoneForm', function() {
                this.hc.normalize(this.formData);
                expect(this.hc._getPhoneForm.calledOnce).to.be(true);
            });

            it('should not call _getCaptchaForm', function() {
                this.hc.normalize(this.formData);
                expect(this.hc._getCaptchaForm.called).to.be(false);
            });

            normalization();
        });
    });
});
