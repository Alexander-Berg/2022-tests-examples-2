var expect = require('expect.js');
var sinon = require('sinon');
var when = require('when');
var _ = require('lodash');

var PhoneField = require('../../../../../blocks/control/phone/phone.field');

describe('Phone Field', function() {
    beforeEach(function() {
        this.phone = new PhoneField();

        this.formData = {
            phone_number: '  8 (913) 910-65-15  '
        };

        this.apiDeferred = when.defer();
        this.api = {
            validatePhone: sinon.stub().returns(this.apiDeferred.promise)
        };

        this.responses = {
            successful: {
                field: 'phone_number',
                body: {
                    phone_number: '+71234567',
                    status: 'ok'
                }
            },
            failed: {
                field: 'phone_number',
                body: {
                    validation_errors: [
                        {
                            field: 'phone_number',
                            message: 'Wrong PhoneNumber value',
                            code: 'badphonenumber'
                        }
                    ],
                    status: 'ok'
                }
            }
        };
    });

    describe('isEmpty', function() {
        it('should return true if normalized phone_number is empty', function() {
            this.formData.phone_number = '  ';
            expect(this.phone.isEmpty(this.formData, this.api)).to.be(true);
        });

        it('should return false if phone_number is not empty', function() {
            expect(this.phone.isEmpty(this.formData, this.api)).to.be(false);
        });
    });

    describe('onEmpty', function() {
        it('should set missingvalue error active if field is required', function() {
            this.phone.setRequired().onEmpty(this.formData, this.api);
            expect(this.phone.getErrorByCode('missingvalue').isActive()).to.be(true);
        });

        it('should not set missingvalue error active if field is optional', function() {
            this.phone.setOptional().onEmpty(this.formData, this.api);
            expect(this.phone.getErrorByCode('missingvalue').isActive()).to.be(false);
        });
    });

    describe('validate', function() {
        it('should call api method validatePhone', function() {
            this.phone.validate(this.formData, this.api);
            expect(this.api.validatePhone.calledOnce).to.be(true);
        });

        it('should pass normalized phone_number to validatePhone', function() {
            this.phone.validate(this.formData, this.api);
            expect(this.api.validatePhone.firstCall.args[0]).to.have.property('phone_number', '8 (913) 910-65-15');
        });

        it('should resolve with [] if api returned no validation_errors', function(done) {
            this.phone
                .validate(this.formData, this.api)
                .then(function(result) {
                    expect(result).to.eql([]);
                    done();
                })
                .then(null, done);

            this.apiDeferred.resolve(this.responses.successful);
        });

        it('should resolve with errors api returned in validation_errors if any', function(done) {
            var codes = _.map(this.responses.failed.body.validation_errors, function(error) {
                return error.code;
            });

            this.phone
                .validate(this.formData, this.api)
                .then(function(result) {
                    expect(result).to.eql(codes);
                    done();
                })
                .then(null, done);

            this.apiDeferred.resolve(this.responses.failed);
        });
    });

    describe('onValid', function() {
        it('should set field value to normalized phone_number contents', function() {
            sinon.stub(this.phone, 'setValue');
            this.phone.onValid(this.formData, this.api);
            expect(this.phone.setValue.calledWithExactly('8 (913) 910-65-15')).to.be(true);
        });
    });

    describe('onInvalid', function() {
        beforeEach(function() {
            this.errors = ['badphonenumber'];
        });

        it('should set field value to normalized phone_number contents', function() {
            sinon.stub(this.phone, 'setValue');
            this.phone.onInvalid(this.errors, this.formData, this.api);
            expect(this.phone.setValue.calledWithExactly('8 (913) 910-65-15')).to.be(true);
        });

        it('should set active all the errors api returned', function() {
            var phone = this.phone;

            phone.onInvalid(this.errors, this.formData, this.api);

            this.errors.forEach(function(error) {
                expect(phone.getErrorByCode(error).isActive()).to.be(true);
            });
        });
    });
});
