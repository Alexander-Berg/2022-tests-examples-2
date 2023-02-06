var expect = require('expect.js');
var sinon = require('sinon');
var when = require('when');
var _ = require('lodash');

var AnswerField = require('../../../../../blocks/control/answer/answer.field');

describe('Answer Field', function() {
    beforeEach(function() {
        this.answer = new AnswerField();

        this.formData = {
            hint_question_id: '7',
            hint_question: 'Who did you want to be, Raymond. Who did you want to be?',
            hint_answer: 'A veterinarian'
        };

        this.apiDeferred = when.defer();
        this.api = {
            validateHint: sinon.stub().returns(this.apiDeferred.promise)
        };

        this.responses = {
            successful: {
                field: 'hint_answer',
                body: {
                    status: 'ok',
                    hint_question_id: 1,
                    hint_answer: 'бла'
                }
            },
            failed: {
                field: 'hint_answer',
                body: {
                    validation_errors: [
                        {
                            field: 'hint_answer',
                            message: 'Enter a value not more than 30 characters long',
                            code: 'toolong'
                        }
                    ],
                    status: 'ok'
                }
            }
        };
    });

    describe('isEmpty', function() {
        it('should return true if hint_answer is empty', function() {
            this.formData.hint_answer = '';
            expect(this.answer.isEmpty(this.formData, this.api)).to.be(true);
        });

        it('should return true if hint_answer only contains spaces', function() {
            this.formData.hint_answer = '   ';
            expect(this.answer.isEmpty(this.formData, this.api)).to.be(true);
        });

        it('should return false if hint_answer is not empty', function() {
            expect(this.answer.isEmpty(this.formData, this.api)).to.be(false);
        });
    });

    describe('onEmpty', function() {
        it('should set missingvalue error active if field is required', function() {
            this.answer.setRequired().onEmpty(this.formData, this.api);
            expect(this.answer.getErrorByCode('missingvalue').isActive()).to.be(true);
        });

        it('should not set missingvalue error active if field is optional', function() {
            this.answer.setOptional().onEmpty(this.formData, this.api);
            expect(this.answer.getErrorByCode('missingvalue').isActive()).to.be(false);
        });
    });

    describe('validate', function() {
        it('should call the api method validateHint', function() {
            this.answer.validate(this.formData, this.api);
            expect(this.api.validateHint.calledOnce).to.be(true);
        });

        it('should pass hint_answer and hint_question_id to validateHint if hint_question_id is not 99', function() {
            this.answer.validate(this.formData, this.api);

            var arg = this.api.validateHint.firstCall.args[0];

            expect(arg).to.have.property('hint_question_id', this.formData.hint_question_id);
            expect(arg).to.have.property('hint_answer', this.formData.hint_answer);
            expect(arg).to.not.have.property('hint_question');
        });

        it('should normalize hint_answer when passing it to api', function() {
            this.formData.hint_answer = '  an   answer  ';
            this.answer.validate(this.formData, this.api);
            expect(this.api.validateHint.firstCall.args[0]).to.have.property('hint_answer', 'an answer');
        });

        it('should pass hint_question and hint_answer to validateHint if hint_question_id is 99', function() {
            this.formData.hint_question_id = '99';
            this.answer.validate(this.formData, this.api);

            var arg = this.api.validateHint.firstCall.args[0];

            expect(arg).to.not.have.property('hint_question_id');
            expect(arg).to.have.property('hint_answer', this.formData.hint_answer);
            expect(arg).to.have.property('hint_question', this.formData.hint_question);
        });

        it('should normalize hint_question when passing it to api', function() {
            this.formData.hint_question_id = '99';
            this.formData.hint_question = ' normalize   me  ';
            this.answer.validate(this.formData, this.api);

            expect(this.api.validateHint.firstCall.args[0]).to.have.property('hint_question', 'normalize me');
        });

        it('should resolve with an array of errors api returned in validation_errors in body', function(done) {
            var codes = _.map(this.responses.failed.body.validation_errors, function(error) {
                return error.code;
            });

            this.answer
                .validate(this.formData, this.api)
                .then(function(result) {
                    expect(result).to.eql(codes);
                    done();
                })
                .then(null, done);

            this.apiDeferred.resolve(this.responses.failed);
        });

        it('should resolve with an empty array if api returned no validation_errors in body', function(done) {
            this.answer
                .validate(this.formData, this.api)
                .then(function(result) {
                    expect(result).to.eql([]);
                    done();
                })
                .then(null, done);

            this.apiDeferred.resolve(this.responses.successful);
        });
    });

    describe('onValid', function() {
        it('should set value for the field', function() {
            this.formData.hint_answer = '  A   veterinarian.  ';
            sinon.stub(this.answer, 'setValue');
            this.answer.onValid(this.formData, this.api);
            expect(this.answer.setValue.calledWithExactly('A veterinarian.')).to.be(true);
        });
    });

    describe('onInvalid', function() {
        beforeEach(function() {
            this.errors = ['toolong', 'missingvalue'];
        });

        it('should set field value to normalized hint_answer contents', function() {
            this.formData.hint_answer = '  A   veterinarian.  ';
            sinon.stub(this.answer, 'setValue');
            this.answer.onInvalid(this.errors, this.formData, this.api);
            expect(this.answer.setValue.calledWithExactly('A veterinarian.')).to.be(true);
        });

        it('should set active all the errors api returned', function() {
            var answer = this.answer;

            answer.onInvalid(this.errors, this.formData, this.api);

            this.errors.forEach(function(error) {
                expect(answer.getErrorByCode(error).isActive()).to.be(true);
            });
        });
    });
});
