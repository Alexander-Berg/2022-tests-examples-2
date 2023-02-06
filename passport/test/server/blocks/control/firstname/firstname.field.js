var expect = require('expect.js');
var sinon = require('sinon');

var FirstnameField = require('../../../../../blocks/control/firstname/firstname.field');

describe('FirstName Field', function() {
    beforeEach(function() {
        this.nameField = new FirstnameField();
        this.formData = {
            firstname: ' Vasya '
        };
        this.api = {};
    });

    describe('isEmpty', function() {
        it('should return true if name is empty after normalization', function() {
            this.formData.firstname = '   ';
            expect(this.nameField.isEmpty(this.formData, this.api)).to.be(true);
        });

        it('should return false if name is not empty', function() {
            expect(this.nameField.isEmpty(this.formData, this.api)).to.be(false);
        });
    });

    describe('onEmpty', function() {
        it('should set missingvalue error active if field is required', function() {
            this.nameField.setRequired().onEmpty(this.formData, this.api);
            expect(this.nameField.getErrorByCode('missingvalue').isActive()).to.be(true);
        });

        it('should not set missingvalue error active if field is optional', function() {
            this.nameField.setOptional().onEmpty(this.formData, this.api);
            expect(this.nameField.getErrorByCode('missingvalue').isActive()).to.be(false);
        });
    });

    describe('validate', function() {
        it('should return ["toolong"] if name is over 50 characters long after normalization', function() {
            this.formData.firstname = `                 ${new Array(52).join('a')}               `;
            expect(this.nameField.validate(this.formData, this.api)).to.eql(['toolong']);
        });

        it('should return [] if name is within 50 characters long', function() {
            expect(this.nameField.validate(this.formData, this.api)).to.eql([]);
        });
    });

    describe('onValid', function() {
        it('should set field value to normalized firstname contents', function() {
            sinon.stub(this.nameField, 'setValue');
            this.nameField.onValid(this.formData, this.api);
            expect(this.nameField.setValue.calledWithExactly('Vasya')).to.be(true);
        });
    });

    describe('onInvalid', function() {
        beforeEach(function() {
            this.errors = ['toolong', 'missingvalue'];
        });

        it('should set field value to normalized firstname contents', function() {
            sinon.stub(this.nameField, 'setValue');
            this.nameField.onInvalid(this.errors, this.formData, this.api);
            expect(this.nameField.setValue.calledWithExactly('Vasya')).to.be(true);
        });

        it('should set active all the errors api returned', function() {
            this.nameField.onInvalid(this.errors, this.formData, this.api);

            var nameField = this.nameField;

            this.errors.forEach(function(error) {
                expect(nameField.getErrorByCode(error).isActive()).to.be(true);
            });
        });
    });
});
