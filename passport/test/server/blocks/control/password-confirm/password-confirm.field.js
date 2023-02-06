var expect = require('expect.js');
var sinon = require('sinon');

var PasswordConfirmField = require('../../../../../blocks/control/password-confirm/password-confirm.field');

describe('PasswordConfirm Field', function() {
    beforeEach(function() {
        this.pconfirm = new PasswordConfirmField();
        this.formData = {
            password: 'Arseny is awesome',
            password_confirm: 'Arseny is awesome'
        };
        this.api = {};
    });

    describe('isEmpty', function() {
        it('should return true if password_confirm is empty', function() {
            this.formData.password_confirm = '';
            expect(this.pconfirm.isEmpty(this.formData, this.api)).to.be(true);
        });

        it('should return false if password_confirm is a single space', function() {
            this.formData.password_confirm = ' ';
            expect(this.pconfirm.isEmpty(this.formData, this.api)).to.be(false);
        });

        it('should return false if password_confirm is totally not empty', function() {
            expect(this.pconfirm.isEmpty(this.formData, this.api)).to.be(false);
        });
    });

    describe('onEmpty', function() {
        it('should set missingvalue error active if field is required', function() {
            this.pconfirm.setRequired().onEmpty(this.formData, this.api);
            expect(this.pconfirm.getErrorByCode('missingvalue').isActive()).to.be(true);
        });

        it('should not set missingvalue error active if field is optional', function() {
            this.pconfirm.setOptional().onEmpty(this.formData, this.api);
            expect(this.pconfirm.getErrorByCode('missingvalue').isActive()).to.be(false);
        });
    });

    describe('validate', function() {
        it('should return ["notequal"] if password_confirm differs from password', function() {
            this.formData.password_confirm = 'I wanna be different';
            expect(this.pconfirm.validate(this.formData, this.api)).to.eql(['notequal']);
        });

        it('should return [] if password_confirm matches password', function() {
            expect(this.pconfirm.validate(this.formData, this.api)).to.eql([]);
        });
    });

    describe('onValid', function() {
        it('should call setValue', function() {
            sinon.stub(this.pconfirm, 'setValue');
            this.pconfirm.onValid(this.formData, this.api);
            expect(this.pconfirm.setValue.called).to.be(true);
        });
    });

    describe('onInvalid', function() {
        beforeEach(function() {
            this.errors = ['notequal'];
        });

        it('should call setValue', function() {
            sinon.stub(this.pconfirm, 'setValue');
            this.pconfirm.onInvalid(this.errors, this.formData, this.api);
            expect(this.pconfirm.setValue.called).to.be(true);
        });

        it('should set active all the errors api returned', function() {
            var pconfirm = this.pconfirm;

            pconfirm.onInvalid(this.errors, this.formData, this.api);

            this.errors.forEach(function(error) {
                expect(pconfirm.getErrorByCode(error).isActive()).to.be(true);
            });
        });
    });

    describe('normalize', function() {
        it('should not call normalizeValue — no trimming for password', function() {
            sinon.stub(this.pconfirm, 'normalizeValue');
            this.pconfirm.normalize(this.formData);
            expect(this.pconfirm.normalizeValue.called).to.be(false);
        });
    });
});
