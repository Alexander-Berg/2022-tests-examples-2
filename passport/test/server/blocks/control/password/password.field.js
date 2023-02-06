var expect = require('expect.js');
var sinon = require('sinon');
var when = require('when');
var _ = require('lodash');

var PasswordField = require('../../../../../blocks/control/password/password.field');

describe('Password Field', function() {
    beforeEach(function() {
        this.password = new PasswordField();

        this.formData = {
            password: ' wh@t5s0Evar ',
            login: 'vasya'
        };
        this.apiDeferred = when.defer();
        this.api = {
            validatePassword: sinon.stub().returns(this.apiDeferred.promise)
        };

        /**
         * @see http://wiki.yandex-team.ru/passport/python/api/#validacijaparolja
         */
        this.responses = {
            failed: {
                field: 'password',
                body: {
                    status: 'ok',
                    validation_errors: [
                        {
                            code: 'tooshort',
                            message: 'Password has less 6 symbols',
                            field: 'password'
                        },
                        {
                            code: 'weak',
                            message: 'Password is not strong',
                            field: 'password'
                        },
                        {
                            code: 'prohibitedsymbols',
                            message: 'Password has prohibited symbols',
                            field: 'password'
                        },
                        {
                            code: 'toolong',
                            message: 'Password has more 20 symbols',
                            field: 'password'
                        },
                        {
                            code: 'likelogin',
                            message: 'Password is the same as login',
                            field: 'password'
                        }
                    ],
                    validation_warnings: [
                        {
                            code: 'weak',
                            message: 'Password is not strong',
                            field: 'password'
                        }
                    ]
                }
            },
            successful: {
                field: 'password',
                body: {
                    status: 'ok'
                }
            },
            successfulWithWarning: {
                field: 'password',
                body: {
                    status: 'ok',
                    validation_warnings: [
                        {
                            code: 'weak',
                            message: 'Password is not strong',
                            field: 'password'
                        }
                    ]
                }
            }
        };
    });

    describe('isEmpty', function() {
        it('should return true if password is empty', function() {
            expect(this.password.isEmpty({password: ''}, this.api)).to.be(true);
        });

        it('should return false if password is a single space', function() {
            expect(this.password.isEmpty({password: ' '}, this.api)).to.be(false);
        });

        it('should return false if password is totally not empty', function() {
            expect(this.password.isEmpty(this.formData, this.api)).to.be(false);
        });
    });

    describe('onEmpty', function() {
        it('should set missingvalue error active if field is required', function() {
            this.password.setRequired().onEmpty(this.formData, this.api);
            expect(this.password.getErrorByCode('missingvalue').isActive()).to.be(true);
        });

        it('should not set missingvalue error active if field is optional', function() {
            this.password.setOptional().onEmpty(this.formData, this.api);
            expect(this.password.getErrorByCode('missingvalue').isActive()).to.be(false);
        });
    });

    describe('validate', function() {
        it('should call the api method validatePassword', function() {
            this.password.validate(this.formData, this.api);
            expect(this.api.validatePassword.calledOnce).to.be(true);
        });

        it('should pass the login and the password from the form to the api', function() {
            this.password.validate(this.formData, this.api);
            expect(this.api.validatePassword.firstCall.args[0]).to.have.property('login', this.formData.login);
            expect(this.api.validatePassword.firstCall.args[0]).to.have.property('password', this.formData.password);
        });

        it('should resolve with errors from validation_errors if api returned any', function(done) {
            var codes = _.map(this.responses.failed.body.validation_errors, function(error) {
                return error.code;
            });

            this.password
                .validate(this.formData, this.api)
                .then(function(result) {
                    expect(result).to.eql(codes);
                    done();
                })
                .then(null, done);

            this.apiDeferred.resolve(this.responses.failed);
        });

        it('should resolve with [] if api returned no validation_errors in body', function(done) {
            this.password
                .validate(this.formData, this.api)
                .then(function(result) {
                    expect(result).to.eql([]);
                    done();
                })
                .then(null, done);

            this.apiDeferred.resolve(this.responses.successful);
        });

        it('should resolve with [] even if there were warnings', function(done) {
            this.password
                .validate(this.formData, this.api)
                .then(function(result) {
                    expect(result).to.eql([]);
                    done();
                })
                .then(null, done);

            this.apiDeferred.resolve(this.responses.successfulWithWarning);
        });
    });

    describe('onValid', function() {
        it('should call setValue', function() {
            sinon.stub(this.password, 'setValue');
            this.password.onValid(this.formData, this.api);
            expect(this.password.setValue.called).to.be(true);
        });
    });

    describe('onInvalid', function() {
        beforeEach(function() {
            this.errors = ['tooshort', 'toolong'];
        });

        it('should call setValue', function() {
            sinon.stub(this.password, 'setValue');
            this.password.onInvalid(this.errors, this.formData, this.api);
            expect(this.password.setValue.called).to.be(true);
        });

        it('should set active all the errors api returned', function() {
            var password = this.password;

            password.onInvalid(this.errors, this.formData, this.api);

            this.errors.forEach(function(error) {
                expect(password.getErrorByCode(error).isActive()).to.be(true);
            });
        });
    });

    describe('normalize', function() {
        it('should not call normalizeValue — no trimming for password', function() {
            sinon.stub(this.password, 'normalizeValue');
            this.password.normalize(this.formData);
            expect(this.password.normalizeValue.called).to.be(false);
        });
    });
});
