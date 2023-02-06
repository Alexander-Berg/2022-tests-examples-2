var expect = require('expect.js');
var sinon = require('sinon');
var when = require('when');

var PhoneField = require('../../../../../blocks/control/phone/phone.field');
var PhoneConfirmField = require('../../../../../blocks/control/phone-confirm/phone-confirm.field');

describe('PhoneConfirm Field', function() {
    beforeEach(function() {
        this.phoneConfirm = new PhoneConfirmField();
        this.formData = {};

        this.apiDeferreds = {
            validatePhone: when.defer()
        };
        this.api = {
            validatePhone: sinon.stub().returns(this.apiDeferreds.validatePhone.promise)
        };
    });

    describe('compile', function() {
        beforeEach(function() {
            this.lang = 'ru';
            this.util = require('putils');
            sinon.stub(this.util, 'i18n').returnsArg(1);
        });
        afterEach(function() {
            this.util.i18n.restore();
        });

        it('should add compiled phone field to the resulting object', function() {
            expect(this.phoneConfirm.compile(this.lang).phone).to.eql(new PhoneField().compile(this.lang));
        });
    });

    describe('validate', function() {
        it('should call api.validatePhone (hopefuly through super-method)', function() {
            this.phoneConfirm.validate(this.formData, this.api);
            expect(this.api.validatePhone.calledOnce).to.be(true);
        });

        //TODO: it should call the api to check if phone is confirmed
    });

    describe('normalize', function() {
        it('should return normalized phone', function() {
            var form = {};

            form[new PhoneField().getName()] = '   abc   ';

            var normalized = {};

            normalized[new PhoneField().getName()] = 'abc';

            expect(this.phoneConfirm.normalize(form)).to.eql(normalized);
        });
    });

    describe('onValid', function() {
        it('should set missingvalue error active', function() {
            this.phoneConfirm.setRequired().onEmpty();
            expect(this.phoneConfirm.getErrorByCode('missingvalue').isActive()).to.be(true);
        });
    });
});
