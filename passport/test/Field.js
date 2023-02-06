var expect = require('expect.js');
var sinon = require('sinon');
var _ = require('lodash');

var Field = require('../Field');

describe('Passport-form Field Error', function() {
    beforeEach(function() {
        this.code = 'missingvalue';
        this.message = 'Пожалуйста, укажите значение';

        this.error = new Field.Error(this.code, this.message);
    });
    describe('Constructor', function() {
        it('should accept code and message', function() {
            expect(this.error.getCode()).to.be(this.code);
            expect(this.error.getMessage()).to.be(this.message);
            expect(this.error.isActive()).to.be(false);
        });

        it('should accept code, message and isActive and create active error', function() {
            var error = new Field.Error(this.code, this.message, true);

            expect(error.isActive()).to.be(true);
        });

        it('should throw if code is not passed', function() {
            expect(function() {
                new Field.Error();
            }).to.throwError(function(e) {
                expect(e.message).to.be('Error Code Required');
            });
        });

        it('should throw if message is not passed', function() {
            var code = this.code;

            expect(function() {
                new Field.Error(code);
            }).to.throwError(function(e) {
                expect(e.message).to.be('Description message localization key required');
            });
        });
    });

    describe('setActive', function() {
        it('should set error active', function() {
            this.error.setActive();
            expect(this.error.isActive()).to.be(true);
        });

        it('should return that error object', function() {
            expect(this.error.setActive()).to.eql(this.error);
        });
    });

    describe('setInactive', function() {
        beforeEach(function() {
            this.error.setActive();
        });

        it('should set error inactive', function() {
            this.error.setInactive();
            expect(this.error.isActive()).to.be(false);
        });

        it('should return that error object', function() {
            expect(this.error.setInactive()).to.eql(this.error);
        });
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

        it('should throw if lang is not defined', function() {
            var error = this.error;

            expect(function() {
                error.compile();
            }).to.throwError(function(e) {
                expect(e.message).to.be('Language code is not defined');
            });
        });

        it('should return an object with code set to error code', function() {
            expect(this.error.compile(this.lang)).to.have.property('code', this.code);
        });

        it('should return an object with message set to translated message', function() {
            expect(this.error.compile(this.lang)).to.have.property('message', this.message); //i18n proxies arguments
        });

        it('should call i18n to translate error message', function() {
            this.error.compile(this.lang);
            expect(this.util.i18n.calledOnce).to.be(true);
            expect(this.util.i18n.calledWithExactly(this.lang, this.message)).to.be(true);
        });

        it('should return an object with "active: true" if error is active', function() {
            this.error.setActive();
            expect(this.error.compile(this.lang)).to.have.property('active', true);
        });

        it('should return an object without "active" field if error is inactive', function() {
            expect(this.error.compile(this.lang)).to.not.have.property('active');
        });
    });
});

describe('Passport-form Field', function() {
    beforeEach(function() {
        this.id = 'fieldID';
        this.name = 'field_name';
        this.label = 'Some Field Label';
        this.value = '  Some field value  ';

        this.field = new Field(this.id);
    });

    describe('Constructor', function() {
        it('should accept id', function() {
            expect(this.field.getID()).to.be(this.id);
        });

        it('should throw if no id passed', function() {
            expect(function() {
                new Field();
            }).to.throwError(function(e) {
                expect(e.message).to.be('ID String Required');
            });
        });

        it('should set name and id to same passed value', function() {
            expect(this.field.getName()).to.be(this.id);
        });

        it('should make field optional by default', function() {
            expect(this.field.isRequired()).to.be(false);
        });

        it('should make field visible by default', function() {
            expect(this.field.isHidden()).to.be(false);
        });
    });

    describe('setValue', function() {
        it('should return that field instance', function() {
            expect(this.field.setValue('')).to.eql(this.field);
        });

        it('should set value so that it can later be fetched', function() {
            var value = 'some Value';

            expect(this.field.setValue(value).getValue()).to.be(value);
        });
    });

    describe('setOptions', function() {
        it('should throw if options is not an object', function() {
            var field = this.field;

            expect(function() {
                field.setOptions('nope');
            }).to.throwError(function(e) {
                expect(e.message).to.be('Options should be a plain object');
            });
        });

        it('should return that field instance', function() {
            expect(this.field.setOptions({})).to.eql(this.field);
        });

        it('should set options so that they can later be fetched', function() {
            var opts = {
                key: 'value'
            };

            expect(this.field.setOptions(opts).getOptions()).to.eql(opts);
        });
    });

    describe('setOption', function() {
        it('should throw if option is not a string', function() {
            var field = this.field;

            expect(function() {
                field.setOption(null);
            }).to.throwError(function(e) {
                expect(e.message).to.be('Option should be a string');
            });
        });

        it('should set option to the given value', function() {
            expect(this.field.setOption('key', 'val').getOption('key')).to.be('val');
        });

        it('should set option value to true if it is undefined', function() {
            expect(this.field.setOption('flag').getOption('flag')).to.be(true);
        });

        it('should return that field instance', function() {
            expect(this.field.setOption('key', 'val')).to.eql(this.field);
        });
    });

    describe('setLabel', function() {
        it("should set field's label", function() {
            this.field.setLabel(this.label);
            expect(this.field.getLabel()).to.be(this.label);
        });

        it('should return that field instance', function() {
            expect(this.field.setLabel(this.label)).to.eql(this.field);
        });
    });

    describe('isRequired', function() {
        it('should return true if field is set to required', function() {
            expect(this.field.setRequired().isRequired()).to.be(true);
        });
        it('should return false if field is set to optional', function() {
            expect(this.field.setOptional().isRequired()).to.be(false);
        });
    });

    describe('isHidden', function() {
        it('should return true if field is set to hidden', function() {
            expect(this.field.setHidden().isHidden()).to.be(true);
        });

        it('should return false if field is set to visible', function() {
            expect(this.field.setVisible().isHidden()).to.be(false);
        });
    });

    describe('addError', function() {
        beforeEach(function() {
            this.error = new Field.Error('ErrorCode', 'Some unnecessary polite message');
        });

        it("should add error to the list of field's possible errors", function() {
            this.field.addError(this.error);
            expect(this.field.getErrors()).to.contain(this.error);
        });

        it('should return that field instance', function() {
            expect(this.field.addError(this.error)).to.eql(this.field);
        });
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

        it('should throw if lang is not defined', function() {
            var field = this.field;

            expect(function() {
                field.compile();
            }).to.throwError(function(e) {
                expect(e.message).to.be('Language code should be defined');
            });
        });

        it("should return an object with field's id", function() {
            expect(this.field.compile(this.lang)).to.have.property('id', this.id);
        });

        ['Name', 'Label', 'Value'].forEach(function(field) {
            var lowercase = field.toLowerCase();

            it('should return an object with ' + field + ', if present', function() {
                var value = this[lowercase];

                expect(this.field['set' + field](value).compile(this.lang)).to.have.property(
                    lowercase,
                    this.field['get' + field]()
                );
            });

            it('should return an object without ' + field + ', if not present', function() {
                expect(this.field['set' + field]('').compile(this.lang)).to.not.have.property(lowercase);
            });
        });

        it('should return an object with Options, if present', function() {
            var value = {
                key: 'value'
            };

            expect(this.field.setOptions(value).compile(this.lang).options).to.eql(this.field.getOptions());
        });

        it('should return an object with empty Options, if not present', function() {
            expect(this.field.compile(this.lang).options).to.eql({});
        });

        it('should localize the label', function() {
            this.field.setLabel(this.label).compile(this.lang);
            expect(this.util.i18n.calledWithExactly(this.lang, this.label)).to.be(true);
        });

        it('should return an object with "hidden: true" if field is set to hidden', function() {
            expect(this.field.setHidden().compile(this.lang)).to.have.property('hidden', true);
        });

        it('should return an object without "hidden" if field is set to visible', function() {
            expect(this.field.setVisible().compile(this.lang)).to.not.have.property('hidden');
        });

        it('should return an object with "required: true" if field is set to required', function() {
            expect(this.field.setRequired().compile(this.lang)).to.have.property('required', true);
        });

        it('should return an object without "required" if field is not set to required', function() {
            expect(this.field.compile(this.lang)).to.not.have.property('required');
        });

        it('should return an object without "optional" parameter', function() {
            this.field.setRequired();
            var compiled = this.field.compile(this.lang);

            expect(compiled).to.not.have.property('optional');
        });

        it('should return an object with an array of compiled errors if any', function() {
            var lang = this.lang;
            var field = this.field;
            var compiledErrors = [new Field.Error('code1', 'msg1'), new Field.Error('code2', 'msg2')].map(function(
                error
            ) {
                field.addError(error);
                return error.compile(lang);
            });

            expect(field.compile(lang).error).to.eql(compiledErrors);
        });

        it('should return an object without "errors" field if no errors were added', function() {
            expect(this.field.compile(this.lang)).to.not.have.property('errors');
        });

        it('should return a copy of stored values in case someone writes into a compiled object', function() {
            var compiled = this.field.setOption('whaa', 'tever').compile(this.lang);

            compiled.options.whaa = 'notTever';
            expect(this.field.compile(this.lang).options).to.have.property('whaa', 'tever');
        });
    });

    describe('validate', function() {
        it('should return an empty array by default', function() {
            expect(this.field.validate()).to.eql([]);
        });
    });

    describe('getErrorByCode', function() {
        it('should throw if code is not a string', function() {
            var field = this.field;

            expect(function() {
                field.getErrorByCode(null);
            }).to.throwError(function(e) {
                expect(e.message).to.be('Code should be a string');
            });
        });

        it('should return null if no error with such code exists', function() {
            expect(this.field.getErrorByCode('nonexistentError')).to.be(null);
        });

        it('should return matching error', function() {
            var code = 'errorcode';
            var error = new Field.Error(code, 'error message');

            expect(this.field.addError(error).getErrorByCode(code)).to.be(error);
        });
    });

    describe('setErrorsActive', function() {
        it('should throw if argument is not an array', function() {
            var field = this.field;

            expect(function() {
                field.setErrorsActive(null);
            }).to.throwError(function(e) {
                expect(e.message).to.be('Errors are expected to be an array of string error codes');
            });
        });

        it('should set active the errors referenced by error codes', function() {
            var one = new Field.Error('one', 'one');
            var two = new Field.Error('two', 'two');

            this.field.addError(one);
            this.field.addError(two);

            this.field.setErrorsActive(['two', 'one']);

            expect(this.field.getErrorByCode('one').isActive()).to.be(true);
            expect(this.field.getErrorByCode('two').isActive()).to.be(true);
        });

        it('should not throw if code references an error that does not exists', function() {
            var field = this.field;

            expect(function() {
                field.setErrorsActive(['nonexistent']);
            }).to.not.throwError();
        });
    });

    describe('normalizeValue', function() {
        /**
         * @type {Object<expectation, value>}
         */
        _.each(
            {
                '': null,
                0: 0,
                trimming: ' trimming ',
                'multiple spaces': 'multiple   spaces',
                'trimming and spaces': '     trimming   and spaces    '
            },
            function(input, expectation) {
                var name = '"' + expectation + '"';

                if (!expectation) {
                    name = 'empty string';
                }

                it('should return ' + name + ' for ' + typeof input + ' "' + input + '"', function() {
                    expect(this.field.normalizeValue(input)).to.be(expectation);
                });
            }
        );
    });

    describe('normalize', function() {
        it('should return an object', function() {
            expect(this.field.normalize({})).to.be.an('object');
        });

        it("should set normalized value of a field to object's property derived from this.getName()", function() {
            var normalized = 'abcdef';

            sinon.stub(this.field, 'normalizeValue').returns(normalized);

            var name = 'fields-name';

            sinon.stub(this.field, 'getName').returns(name);

            expect(this.field.normalize({})).to.have.property(name, normalized);
        });
    });

    describe('isPresent', function() {
        it('should throw if form data is not a plain object', function() {
            var field = this.field;

            expect(function() {
                field.isPresent('nope');
            }).to.throwError(function(err) {
                expect(err.message).to.be('Argument should be a posted form data');
            });
        });

        it('should return true if form has a field named like this field', function() {
            var fd = {};

            fd[this.field.getName()] = 'someValue';
            expect(this.field.isPresent(fd)).to.be(true);
        });

        it('should return false if form has no field named like this field', function() {
            expect(this.field.isPresent({})).to.be(false);
        });
    });
});
