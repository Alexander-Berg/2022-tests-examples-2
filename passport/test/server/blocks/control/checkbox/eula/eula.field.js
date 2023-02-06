var expect = require('expect.js');
var sinon = require('sinon');
var _ = require('lodash');

var EulaField = require('../../../../../../blocks/control/checkbox/eula/eula.field');

describe('Eula Field', function() {
    beforeEach(function() {
        this.eula = new EulaField();
        this.formData = {
            eula_accepted: 'on'
        };
        this.api = {};
    });

    it('should have name eula_accepted', function() {
        //Music registration specifically requests eula by it's name via form.getField('eula_accepted')
        expect(this.eula.getName()).to.be('eula_accepted');
    });

    describe('isEmpty', function() {
        _.each(
            {
                empty: '',
                off: 'off',
                'off with normalization': '  off   ',
                '0': '0',
                false: false,
                null: null
            },
            function(value, description) {
                it(`should return true if eula is ${description}`, function() {
                    this.formData.eula_accepted = value;
                    expect(this.eula.isEmpty(this.formData, this.api)).to.be(true);
                });
            }
        );

        _.each(
            {
                on: 'on',
                true: true,
                int: 1
            },
            function(value, description) {
                it(`should return false if eula is ${description}`, function() {
                    this.formData.eula_accepted = value;
                    expect(this.eula.isEmpty(this.formData, this.api)).to.be(false);
                });
            }
        );
    });

    describe('onEmpty', function() {
        it('should set "missingvalue" error active if field is required', function() {
            this.eula.setRequired().onEmpty(this.formData, this.api);
            expect(this.eula.getErrorByCode('missingvalue').isActive()).to.be(true);
        });

        it('should not set "missingvalue" error active if field is optional', function() {
            this.eula.setOptional().onEmpty(this.formData, this.api);
            expect(this.eula.getErrorByCode('missingvalue').isActive()).to.be(false);
        });
    });

    describe('onValid', function() {
        it('should set field value to "on"', function() {
            sinon.stub(this.eula, 'setValue');
            this.eula.onValid(this.formData, this.api);
            expect(this.eula.setValue.calledWithExactly('on')).to.be(true);
        });
    });
});
