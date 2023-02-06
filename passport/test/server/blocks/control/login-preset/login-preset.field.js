var expect = require('expect.js');
var sinon = require('sinon');

var LoginField = require('../../../../../blocks/control/login/login.field');
var LoginPresetField = require('../../../../../blocks/control/login-preset/login-preset.field');

describe('LoginPreset Field', function() {
    beforeEach(function() {
        this.loginPreset = new LoginPresetField();
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

        it('should add compiled login field to the resulting object', function() {
            expect(this.loginPreset.compile(this.lang).login).to.eql(new LoginField().compile(this.lang));
        });
    });

    describe('normalize', function() {
        it('should return normalized login', function() {
            var form = {};

            form[new LoginField().getName()] = '   abc   ';

            var normalized = {};

            normalized[new LoginField().getName()] = 'abc';

            expect(this.loginPreset.normalize(form)).to.eql(normalized);
        });
    });

    describe('onValid', function() {
        it('should set missingvalue error active', function() {
            this.loginPreset.setRequired().onEmpty();
            expect(this.loginPreset.getErrorByCode('missingvalue').isActive()).to.be(true);
        });
    });
});
