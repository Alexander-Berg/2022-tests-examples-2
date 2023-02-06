var expect = require('expect.js');
var sinon = require('sinon');
var when = require('when');
var _ = require('lodash');

var QuestionField = require('../../../../../blocks/control/question/question.field');

describe('Question Field', function() {
    beforeEach(function() {
        this.question = new QuestionField();

        this.formData = {
            hint_question_id: '  7  '
        };

        this.getQuestionsDeferred = when.defer();
        this.api = {
            getQuestions: sinon.stub().returns(this.getQuestionsDeferred.promise)
        };

        this.getQuestionsResponses = {
            successful: {
                field: 'question',
                body: {
                    status: 'ok',
                    questions: [
                        {
                            id: 0,
                            value: 'не выбран'
                        },
                        {
                            id: 1,
                            value: 'Девичья фамилия матери'
                        },
                        {
                            id: 2,
                            value: 'Любимое блюдо'
                        },
                        {
                            id: 3,
                            value: 'Почтовый индекс родителей'
                        },
                        {
                            id: 4,
                            value: 'Дата рождения бабушки'
                        },
                        {
                            id: 5,
                            value: 'Ваше прозвище в школе'
                        },
                        {
                            id: 6,
                            value: 'Номер паспорта'
                        },
                        {
                            id: 7,
                            value: 'Пять последних цифр кред. карты'
                        },
                        {
                            id: 8,
                            value: 'Пять последних цифр ИНН'
                        },
                        {
                            id: 9,
                            value: 'Ваш любимый номер телефона'
                        },
                        {
                            id: 99,
                            value: 'Задайте собственный вопрос'
                        }
                    ]
                }
            }
        };
    });

    describe('Compile', function() {
        beforeEach(function() {
            this.lang = 'ru';
            this.util = require('putils');
            sinon.stub(this.util, 'i18n').returnsArg(1);
        });
        afterEach(function() {
            this.util.i18n.restore();
        });

        it('should have same fields super method returns', function(done) {
            var compiledByParent = new (require('pform/Field'))('id').compile.call(this.question, this.lang);

            this.question
                .compile(this.lang, this.api)
                .then(function(compiled) {
                    _.each(compiledByParent, function(value, key) {
                        expect(compiled[key]).to.eql(value);
                    });

                    done();
                })
                .then(null, done);
            this.getQuestionsDeferred.resolve(this.getQuestionsResponses.successful);
        });

        it('should call api.getQuestions', function() {
            this.question.compile(this.lang, this.api);
            expect(this.api.getQuestions.calledOnce).to.be(true);
        });

        it('should add option field to compiled object with api response inside', function(done) {
            var questions = this.getQuestionsResponses.successful.body.questions;

            this.question
                .compile(this.lang, this.api)
                .then(function(compiled) {
                    expect(compiled.option).to.eql(questions);
                    done();
                })
                .then(null, done);

            this.getQuestionsDeferred.resolve(this.getQuestionsResponses.successful);
        });
    });

    describe('isEmpty', function() {
        _.each(
            {
                null: null,
                false: false,
                'an empty string': '',
                'a string with nondigits': 'a',
                zero: '0',
                'not an integer': '1.5'
            },
            function(value, description) {
                it(`should return true if hint_question_id is ${description}`, function() {
                    this.formData.hint_question_id = value;
                    expect(this.question.isEmpty(this.formData, this.api)).to.be(true);
                });
            }
        );

        for (var i = 1; i < 12; i++) {
            (function(i) {
                it(`should return false if hint_question_id is ${i}`, function() {
                    this.formData.hint_question_id = String(i);
                    expect(this.question.isEmpty(this.formData, this.api)).to.be(false);
                });
            })(i);
        }

        it('should return false if hint_question_id is 99', function() {
            this.formData.hint_question_id = '99';
            expect(this.question.isEmpty(this.formData, this.api)).to.be(false);
        });

        it('should normalize the hint_question_id', function() {
            expect(this.question.isEmpty(this.formData, this.api)).to.be(false);
        });
    });

    describe('onEmpty', function() {
        it('should set missingvalue error active if field is required', function() {
            this.question.setRequired().onEmpty(this.formData, this.api);
            expect(this.question.getErrorByCode('missingvalue').isActive()).to.be(true);
        });

        it('should not set missingvalue error active if field is optional', function() {
            this.question.setOptional().onEmpty(this.formData, this.api);
            expect(this.question.getErrorByCode('missingvalue').isActive()).to.be(false);
        });
    });

    describe('onValid', function() {
        it('should set field value to normalized hint_question_id', function() {
            sinon.stub(this.question, 'setValue');
            this.question.onValid(this.formData, this.api);
            expect(this.question.setValue.calledWithExactly('7')).to.be(true);
        });
    });
});
