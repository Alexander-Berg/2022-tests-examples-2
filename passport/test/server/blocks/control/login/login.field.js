var expect = require('expect.js');
var sinon = require('sinon');
var when = require('when');
var _ = require('lodash');

var LoginField = require('../../../../../blocks/control/login/login.field');

describe('Login Field', function() {
    beforeEach(function() {
        this.login = new LoginField();

        this.formData = {
            login: '  vasilkoff '
        };

        this.apiDeferred = when.defer();
        this.api = {
            validateLogin: sinon.stub().returns(this.apiDeferred.promise)
        };

        /**
         * @see http://wiki.yandex-team.ru/passport/python/api/#validacijalogina
         */
        this.responses = {
            successful: {
                field: 'login',
                body: {
                    status: 'ok'
                }
            },
            failed: {
                body: {
                    errors: [
                        'login.not_available',
                        'login.startswithdigit',
                        'login.long',
                        'login.startswithdot',
                        'login.startswithhyphen',
                        'login.endswithhyphen',
                        'login.doubleddot',
                        'login.doubledhyphen',
                        'login.prohibitedsymbols',
                        'login.dothyphen',
                        'login.hyphendot',
                        'login.endwithdot'
                    ]
                }
            }
        };
    });

    describe('isEmpty', function() {
        it('should return true if normalized login is empty', function() {
            this.formData.login = '   ';
            expect(this.login.isEmpty(this.formData, this.api)).to.be(true);
        });

        it('should return false if login is not empty', function() {
            expect(this.login.isEmpty(this.formData, this.api)).to.be(false);
        });
    });

    describe('onEmpty', function() {
        it('should set missingvalue error active if field is required', function() {
            this.login.setRequired().onEmpty(this.formData, this.api);
            expect(this.login.getErrorByCode('missingvalue').isActive()).to.be(true);
        });

        it('should not set missingvalue error active if field is optional', function() {
            this.login.setOptional().onEmpty(this.formData, this.api);
            expect(this.login.getErrorByCode('missingvalue').isActive()).to.be(false);
        });
    });

    describe('validate', function() {
        it('should call the api method validateLogin', function() {
            this.login.validate(this.formData, this.api);
            expect(this.api.validateLogin.calledOnce).to.be(true);
        });

        it('should pass normalized login to validateLogin', function() {
            this.login.validate(this.formData, this.api);
            expect(this.api.validateLogin.firstCall.args[0]).to.have.property('login', 'vasilkoff');
        });

        it('should resolve with [] if no validation_errors were present in api resopnse', function(done) {
            this.login
                .validate(this.formData, this.api)
                .then(function(result) {
                    expect(result).to.eql([]);
                    done();
                })
                .then(null, done);

            this.apiDeferred.resolve(this.responses.successful);
        });

        it('should resolve with api errors if any validation_errors were present in api response', function(done) {
            var codes = _.map(this.responses.failed.body.validation_errors, function(error) {
                return error.code;
            });

            this.login
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
        it('should set field value to normalized login contents', function() {
            sinon.stub(this.login, 'setValue');
            this.login.onValid(this.formData, this.api);
            expect(this.login.setValue.calledWithExactly('vasilkoff')).to.be(true);
        });
    });

    describe('onInvalid', function() {
        beforeEach(function() {
            this.errors = ['startswithdigit'];
        });

        it('should set field value to normalized login contents', function() {
            sinon.stub(this.login, 'setValue');
            this.login.onInvalid(this.errors, this.formData, this.api);
            expect(this.login.setValue.calledWithExactly('vasilkoff')).to.be(true);
        });

        it('should set active all the errors api returned', function() {
            var login = this.login;

            login.onInvalid(this.errors, this.formData, this.api);

            this.errors.forEach(function(error) {
                expect(login.getErrorByCode(error).isActive()).to.be(true);
            });
        });
    });
});
