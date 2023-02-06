var expect = require('expect.js');
var sinon = require('sinon');
var when = require('when');
var _ = require('lodash');

var PForm = require('../Form');

/**
 * @type {Field}
 */
var PField = require('../Field');
var AsyncField = require('inherit')(PField, {
    __constructor: function(compileResult, validationResult) {
        this._init('login');

        this.compileResult = compileResult;
        this.validationResult = validationResult;
    },

    compile: function() {
        var deferred = when.defer();
        var result = this.compileResult;

        setTimeout(function() {
            deferred.resolve(result);
        }, 20);

        return deferred.promise;
    },

    validate: function() {
        var deferred = when.defer();
        var result = this.validationResult;

        setTimeout(function() {
            deferred.resolve(result);
        }, 20);

        return deferred.promise;
    }
});

/*

* Form is created with PassportField objects
* Form should be able to compile into the form, suitable for templating.
    That means, basically, calling .compile() on every PassportField in the form
* Form should be able to match the form object that came from clientside against the PassportFields it was created with
    * Every field that matched the value from the clientside should be validated.
        It should have it's relevant errors set to active.
    * Form is valid if all the matched fields have no active errors and all the required PassportFields are matched

 */

describe('Passport-form', function() {
    beforeEach(function() {
        this.login = new PField('login').setRequired();
        this.password = new PField('password').setRequired();
        this.phone = new PField('phone').setOptional();

        this.required = [this.login, this.password];
        this.optional = [this.phone];

        this.allFields = this.required.concat(this.optional);
        this.api = {api: 'stub'};
        this.form = new PForm(this.login, this.password, this.phone).setApi(this.api);

        this.formData = {
            login: 'vasya',
            password: 'password1'
        };

        this.asyncField = AsyncField;
    });

    describe('Constructor', function() {
        it('should successfully create an instance given the PassportFields', function() {
            expect(new PForm(this.login, this.password, this.phone)).to.be.a(PForm);
        });

        it("should successfully create an instance given the PassportField's ancestor", function() {
            var Ancestor = require('inherit')(PField, {
                __constructor: function() {
                    this._init('I am an ancestor');
                }
            });

            expect(new PForm(new Ancestor().setRequired(), new Ancestor())).to.be.a(PForm);
        });

        it('should throw if no fields passed', function() {
            expect(function() {
                new PForm();
            }).to.throwError(function(e) {
                expect(e.message).to.be('At least one required field should be present');
            });
        });

        it('should throw if no required fields passed', function() {
            var optionalField = this.phone;

            expect(function() {
                new PForm(optionalField);
            }).to.throwError(function(e) {
                expect(e.message).to.be('At least one required field should be present');
            });
        });

        it('should throw if any object in arguments is not a PassportField', function() {
            expect(function() {
                new PForm({});
            }).to.throwError(function(e) {
                expect(e.message).to.be('All the arguments should be Fields');
            });
        });

        it('should create form that is not valid by default', function() {
            expect(this.form.isValid()).to.be(false);
        });
    });

    describe('getFields', function() {
        it('should return an array of fields the form was created with', function() {
            expect(this.form.getFields()).to.eql(this.allFields);
        });
    });

    describe('getField', function() {
        it('should return the requested field', function() {
            expect(this.form.getField('login')).to.eql(this.login);
        });
    });

    describe('compile', function(done) {
        beforeEach(function() {
            this.lang = 'ru';
            this.util = require('putils');
            sinon.stub(this.util, 'i18n').returnsArg(1);
        });
        afterEach(function() {
            this.util.i18n.restore();
        });

        it('should throw if form has no api set', function() {
            var lang = this.lang;
            var form = new PForm(this.login);

            expect(function() {
                form.compile(lang);
            }).to.throwError(function(e) {
                expect(e.message).to.be('Compilation requires API, set it using form.setApi(yourApi)');
            });
        });

        it('should throw if lang is not defined', function() {
            var form = new PForm(this.login).setApi(this.api);

            expect(function() {
                form.compile();
            }).to.throwError(function(e) {
                expect(e.message).to.be('Language code should be defined');
            });
        });

        it(
            'should create a form object suitable for templating by calling .compile() on ' +
                'every PassportField in the form and passing the lang',
            function() {
                var lang = this.lang;
                var api = this.api;
                var allFields = this.allFields;

                allFields.forEach(function(field) {
                    sinon.spy(field, 'compile');
                });

                this.form
                    .compile(lang)
                    .then(function() {
                        allFields.forEach(function(field) {
                            expect(field.compile.calledOnce).to.be(true);
                            expect(field.compile.calledWithExactly(lang, api)).to.be(true);
                        });

                        done();
                    })
                    .then(null, done);
            }
        );

        it('should support async .compile() on PassportFields', function(done) {
            var compileResult = {com: 'piled'};
            var form = new PForm(new this.asyncField(compileResult).setRequired());

            form.setApi(this.api)
                .compile(this.lang)
                .then(function(compiled) {
                    expect(compiled).to.eql([compileResult]);
                    done();
                })
                .then(null, done);
        });

        it(
            'should resolve with the result of the compiled fields in order they ' + 'were passed to constructor',
            function(done) {
                var field1 = new PField('field1').setRequired();
                var field1CompilationResult = {compiled: 'field1'};

                sinon.stub(field1, 'compile').returns(field1CompilationResult);

                var field2 = new PField('field2').setRequired();
                var field2CompilationResult = {compiled: 'field2'};

                sinon.stub(field2, 'compile').returns(field2CompilationResult);

                new PForm(field1, field2)
                    .setApi(this.api)
                    .compile(this.lang)
                    .then(function(compiled) {
                        expect(compiled).to.eql([field1CompilationResult, field2CompilationResult]);
                        done();
                    })
                    .then(null, done);
            }
        );
    });

    describe('validate', function() {
        beforeEach(function() {
            this.form.setApi(this.api);
        });

        _.each(
            {
                'a string': 'whatever',
                'an empty string': '',
                'a number': 1,
                'an array': [],
                true: true,
                false: true,
                null: null,
                undefined: undefined,
                'an instance of a custom constructor': new (function() {})()
            },
            function(value, description) {
                it('should throw if the argument is ' + description, function() {
                    var form = this.form;

                    expect(function() {
                        form.validate(value);
                    }).to.throwError(function(e) {
                        expect(e.message).to.be('formData should be a plain object');
                    });
                });
            }
        );

        it('should throw if form has no api set', function() {
            var form = new PForm(this.login);

            expect(function() {
                form.validate();
            }).to.throwError(function(e) {
                expect(e.message).to.be('Validation requires API, set it using form.setApi(yourApi)');
            });
        });

        it('should call .validate() on fields that return true on field.isPresent(fd)', function(done) {
            this.allFields.forEach(function(field) {
                //Returns an error to make sure all fields are validated no matter the result
                sinon.stub(field, 'validate').returns(['error_code']);
            });

            var required = this.required;
            var optional = this.optional;

            required.forEach(function(field) {
                sinon.stub(field, 'isPresent').returns(true);
            });

            optional.forEach(function(field) {
                sinon.stub(field, 'isPresent').returns(false);
            });

            this.form
                .validate({})
                .then(function() {
                    required.forEach(function(field) {
                        //all required fields return true for isPresent
                        expect(field.validate.calledOnce).to.be(true);
                    });

                    optional.forEach(function(field) {
                        //all optional fields return false for isPresent and should not be called
                        expect(field.validate.called).to.be(false);
                    });

                    done();
                })
                .then(null, done);
        });

        it('should support async .validate() calls', function(done) {
            //AsyncField has "login" as name and id
            new PForm(new this.asyncField(null, false).setRequired())
                .setApi(this.api)
                .validate(this.formData)
                .then(function(result) {
                    expect(result).to.be(false);
                    done();
                })
                .then(null, done);
        });

        it('should resolve with true if all matched fields returned no errors', function(done) {
            var field = new PField('field').setRequired();

            sinon.stub(field, 'validate').returns([]);
            new PForm(field)
                .setApi(this.api)
                .validate({field: 'whatever'})
                .then(function(result) {
                    expect(result).to.be(true);
                    done();
                })
                .then(null, done);
        });

        it('should set form valid if all matched fields returned no errors', function(done) {
            var field = new PField('field').setRequired();

            sinon.stub(field, 'validate').returns([]);

            var form = new PForm(field);

            form.setApi(this.api)
                .validate({field: 'whatever'})
                .then(function() {
                    expect(form.isValid()).to.be(true);
                    done();
                })
                .then(null, done);
        });

        it('should resolve with false if any of matched fields returned errors', function(done) {
            var field1 = new PField('field1').setRequired();

            sinon.stub(field1, 'validate').returns([]);

            var field2 = new PField('field2').setOptional();

            sinon.stub(field2, 'validate').returns(['error_code']);

            new PForm(field1, field2)
                .setApi(this.api)
                .validate({
                    field1: 'whatso',
                    field2: 'ever'
                })
                .then(function(result) {
                    expect(result).to.be(false);
                    done();
                })
                .then(null, done);
        });

        it('should not set form valid if any of matched fields returned errors', function(done) {
            var field = new PField('field').setRequired();

            sinon.stub(field, 'validate').returns(['error_code']);

            var form = new PForm(field);

            form.setApi(this.api)
                .validate({
                    field: 'whatso'
                })
                .then(function() {
                    expect(form.isValid()).to.be(false);
                    done();
                })
                .then(null, done);
        });

        it('should resolve with false if any required field is not present in the form data', function(done) {
            var field1 = new PField('field1').setRequired();

            sinon.stub(field1, 'validate').returns([]);
            sinon.stub(field1, 'isPresent').returns(false);

            var field2 = new PField('field2').setRequired();

            sinon.stub(field2, 'validate').returns([]);
            sinon.stub(field2, 'isPresent').returns(true);

            new PForm(field1, field2)
                .setApi(this.api)
                .validate({})
                .then(function(result) {
                    expect(result).to.be(false);
                    done();
                })
                .then(null, done);
        });

        it('should pass whole input to the matched fields', function(done) {
            var formData = this.formData;
            var required = this.required;

            required.forEach(function(field) {
                sinon.spy(field, 'validate');
            });

            var api = this.api; //Currently passing the API to validations

            this.form
                .validate(formData)
                .then(function() {
                    required.forEach(function(field) {
                        expect(field.validate.calledWithExactly(formData, api)).to.be(true);
                    });

                    done();
                })
                .then(null, done);
        });

        it('should not validate empty fields', function(done) {
            var required = this.required;

            required.forEach(function(field) {
                sinon.stub(field, 'isEmpty').returns(true);
                sinon.spy(field, 'validate');
            });

            this.form
                .validate(this.formData)
                .then(function() {
                    required.forEach(function(field) {
                        expect(field.validate.called).to.be(false);
                    });

                    done();
                })
                .then(null, done);
        });

        it('should support async isEmpty calls', function(done) {
            var clock = sinon.useFakeTimers();

            var isEmptyDeferred = when.defer();
            var field = new PField('field').setRequired();

            sinon.stub(field, 'isEmpty').returns(isEmptyDeferred.promise);
            sinon.spy(field, 'validate');

            var validatePromise = new PForm(field).setApi(this.api).validate({field: 'whatever'});

            clock.tick(1000);
            expect(validatePromise.inspect().state).to.be('pending');

            //Resolve a deferred to check for async support. Form should wait for resolution.
            isEmptyDeferred.resolve(true);
            validatePromise
                .finally(function() {
                    clock.restore();
                })
                .then(function() {
                    done();
                })
                .then(null, done);
        });

        it('should call onEmpty on empty fields with formData and api', function(done) {
            var required = this.required;

            required.forEach(function(field) {
                sinon.stub(field, 'isEmpty').returns(true);
                sinon.stub(field, 'onEmpty');
            });

            var api = this.api;
            var formData = this.formData;

            this.form
                .validate(formData)
                .then(function() {
                    required.forEach(function(field) {
                        expect(field.onEmpty.calledWithExactly(formData, api)).to.be(true);
                    });
                    done();
                })
                .then(null, done);
        });

        it('should support async onEmpty calls', function(done) {
            var clock = sinon.useFakeTimers();

            var onEmptyDeferred = when.defer();

            this.required.forEach(function(field) {
                sinon.stub(field, 'isEmpty').returns(true);
                sinon.stub(field, 'onEmpty').returns(onEmptyDeferred.promise);
            });

            var validatePromise = this.form.validate(this.formData);

            clock.tick(1000);
            expect(validatePromise.inspect().state).to.be('pending');

            onEmptyDeferred.resolve();
            validatePromise
                .finally(function() {
                    clock.restore();
                })
                .then(function() {
                    done();
                })
                .then(null, done);
        });

        it('should call onValid on valid fields with formData and api', function(done) {
            var required = this.required;

            required.forEach(function(field) {
                sinon.stub(field, 'isEmpty').returns(false);
                sinon.stub(field, 'onValid');
                sinon.stub(field, 'onInvalid');
            });

            var api = this.api;
            var formData = this.formData;

            this.form
                .validate(formData)
                .then(function() {
                    required.forEach(function(field) {
                        expect(field.onValid.calledWithExactly(formData, api)).to.be(true);
                        expect(field.onInvalid.called).to.be(false);
                    });
                    done();
                })
                .then(null, done);
        });

        it('should support async onValid calls', function(done) {
            var clock = sinon.useFakeTimers();

            var onValidDeferred = when.defer();

            this.required.forEach(function(field) {
                sinon.stub(field, 'isEmpty').returns(false);
                sinon.stub(field, 'onValid').returns(onValidDeferred.promise);
                sinon.stub(field, 'onInvalid');
            });

            var validatePromise = this.form.validate(this.formData);

            clock.tick(1000);
            expect(validatePromise.inspect().state).to.be('pending');

            onValidDeferred.resolve();
            validatePromise
                .finally(function() {
                    clock.restore();
                })
                .then(function() {
                    done();
                })
                .then(null, done);
        });

        it('should call onInvalid on invalid fields with errors from validate, formData and api', function(done) {
            var required = this.required;
            var errors = ['error_code'];

            required.forEach(function(field) {
                sinon.stub(field, 'isEmpty').returns(false);
                sinon.stub(field, 'validate').returns(errors);
                sinon.stub(field, 'onValid');
                sinon.stub(field, 'onInvalid');
            });

            var api = this.api;
            var formData = this.formData;

            this.form
                .validate(formData)
                .then(function() {
                    required.forEach(function(field) {
                        expect(field.onInvalid.calledWithExactly(errors, formData, api)).to.be(true);
                        expect(field.onValid.called).to.be(false);
                    });
                    done();
                })
                .then(null, done);
        });

        it('should support async onInvalid calls', function(done) {
            var clock = sinon.useFakeTimers();

            var onInvalidDeferred = when.defer();

            this.required.forEach(function(field) {
                sinon.stub(field, 'isEmpty').returns(false);
                sinon.stub(field, 'validate').returns(['error_code']);
                sinon.stub(field, 'onValid');
                sinon.stub(field, 'onInvalid').returns(onInvalidDeferred.promise);
            });

            var validatePromise = this.form.validate(this.formData);

            clock.tick(1000);
            expect(validatePromise.inspect().state).to.be('pending');

            onInvalidDeferred.resolve();
            validatePromise
                .finally(function() {
                    clock.restore();
                })
                .then(function() {
                    done();
                })
                .then(null, done);
        });

        it(
            'should call onInvalid after validation deferred is resolved with errors, ' + 'if it returns a deferred',
            function() {
                var validateDeferred = when.defer();
                var field = this.optional[0];

                sinon.stub(field, 'isEmpty').returns(false);
                sinon.stub(field, 'validate').returns(validateDeferred.promise);
                sinon.stub(field, 'onValid');
                sinon.stub(field, 'onInvalid');

                var validatePromise = this.form.validate(this.formData);

                expect(field.onInvalid.called).to.be(false);
                validateDeferred.resolve(['error_code']);

                validatePromise.then(function() {
                    //Check called only after validation resolution
                    expect(field.onInvalid.calledOnce).to.be(true);
                    expect(field.onValid.called).to.be(false);
                });
            }
        );

        it(
            'should call onValid after validation deferred is resolved with no errors, ' + 'if it returns a deferred',
            function() {
                var validateDeferred = when.defer();
                var field = this.optional[0];

                sinon.stub(field, 'isEmpty').returns(false);
                sinon.stub(field, 'validate').returns(validateDeferred.promise);
                sinon.stub(field, 'onValid');
                sinon.stub(field, 'onInvalid');

                var validatePromise = this.form.validate(this.formData);

                expect(field.onValid.called).to.be(false);
                validateDeferred.resolve([]);

                validatePromise.then(function() {
                    //Check called only after validation resolution
                    expect(field.onValid.calledOnce).to.be(true);
                    expect(field.onInvalid.called).to.be(false);
                });
            }
        );
    });

    describe('normalize', function() {
        beforeEach(function() {
            this.allFields.forEach(function(field) {
                sinon.stub(field, 'normalize');
            });
        });

        it('should call normalize on all fields', function() {
            this.form.normalize(this.formData);
            this.allFields.forEach(function(field) {
                expect(field.normalize.calledOnce).to.be(true);
            });
        });

        it("should pass formData to fields' normalize method", function() {
            var formData = this.formData;

            this.form.normalize(formData);
            this.allFields.forEach(function(field) {
                expect(field.normalize.calledWithExactly(formData)).to.be(true);
            });
        });

        it('should return a resulting form', function() {
            var expectedResult = {};

            this.allFields.forEach(function(field) {
                var normalized = {};

                normalized[field.getName()] = field.getName() + '-value';
                _.extend(expectedResult, normalized);
                field.normalize.returns(normalized);
            });

            expect(this.form.normalize(this.formData)).to.eql(expectedResult);
        });
    });
});
