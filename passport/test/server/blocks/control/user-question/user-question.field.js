var expect = require('expect.js');
var sinon = require('sinon');
var _ = require('lodash');

var UserQuestionField = require('../../../../../blocks/control/user-question/user-question.field');

describe('UserQuestion Field', function() {
    beforeEach(function() {
        this.userQuestion = new UserQuestionField();

        this.formData = {
            hint_question_id: '99',
            hint_question: ' Who   did  you  want to be when you grew    up? '
        };

        this.api = {};
    });

    describe('isEmpty', function() {
        _.each(
            {
                'an empty string': '',
                'lotsa spaces': '       '
            },
            function(value, description) {
                it(`should return true if hint_question is ${description}`, function() {
                    this.formData.hint_question = value;
                    expect(this.userQuestion.isEmpty(this.formData, this.api)).to.be(true);
                });
            }
        );

        it('should return false if hint_question is a string with any characters besides \\s', function() {
            expect(this.userQuestion.isEmpty(this.formData, this.api)).to.be(false);
        });

        it('should return false if hint_question is an empty string, but hint_question_id is not "99"', function() {
            this.formData.hint_question_id = '5';
            this.formData.hint_question = '';
            expect(this.userQuestion.isEmpty(this.formData, this.api)).to.be(false);
        });
    });

    describe('onEmpty', function() {
        it('should set missingvalue error active if field is required', function() {
            this.userQuestion.setRequired().onEmpty(this.formData, this.api);
            expect(this.userQuestion.getErrorByCode('missingvalue').isActive()).to.be(true);
        });

        it('should not set missingvalue error active if field is optional', function() {
            this.userQuestion.setOptional().onEmpty(this.formData, this.api);
            expect(this.userQuestion.getErrorByCode('missingvalue').isActive()).to.be(false);
        });
    });

    describe('onValid', function() {
        it('should set field value to normalized hint_question contents', function() {
            sinon.stub(this.userQuestion, 'setValue');
            this.userQuestion.onValid(this.formData, this.api);
            expect(this.userQuestion.setValue.calledWithExactly('Who did you want to be when you grew up?')).to.be(
                true
            );
        });
    });
});
