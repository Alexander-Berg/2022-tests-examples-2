import {Button, Col, Row} from 'antd';
import PropTypes from 'prop-types';
import React from 'react';
import {connect} from 'react-redux';

import TestsApi from '../api/tests';

import MultipleAnswer from './MultipleAnswer';
import SingleAnswer from './SingleAnswer';

const QUESTION_TYPES = {
    single_answer: 'single_answer',
    multiple_answer: 'multiple_answer'
};

class Question extends React.PureComponent {
    static propTypes = {
        topic: PropTypes.string,
        question: PropTypes.object,

        validateAnswer: PropTypes.func,
        loadQuestion: PropTypes.func
    }

    state = {
        answered: false,
        answer: [],
        result: false
    }

    render() {
        const {question} = this.props;
        const {answered} = this.state;

        return (
            <Row>
                <Col lg={16} xl={12}>
                    <h3>{question.question}</h3>

                    {this.renderAnswers()}

                    <div style={{marginTop: '15px', display: 'flex', alignItems: 'center'}}>
                        {answered ? (
                            <Button onClick={this.nextQuestion}>
                                Далее
                            </Button>
                        ) : (
                            <Button
                                type="primary"
                                onClick={this.validateAnswer}
                                disabled={!this.state.answer.length}
                            >
                                Ответить
                            </Button>
                        )}

                        {this.renderResult()}
                    </div>
                </Col>
            </Row>
        );
    };

    renderAnswers = () => {
        const {question} = this.props;
        const {answered, answer} = this.state;

        const componentProps = {
            question,
            answered,
            answer,
            onChange: this.setAnswer
        };

        switch (question.type) {
            case QUESTION_TYPES.single_answer:
                return <SingleAnswer {...componentProps}/>;
            case QUESTION_TYPES.multiple_answer:
                return <MultipleAnswer {...componentProps}/>;
        }
    }

    renderResult = () => {
        const {result, answered} = this.state;

        if (!answered) {
            return null;
        }

        return (
            <div style={{marginLeft: '10px'}}>
                {result ? (
                    <span className="success">Верно</span>
                ) : (
                    <span className="error">Не верно</span>
                )}
            </div>
        );
    }

    nextQuestion = () => {
        const {loadQuestion, topic} = this.props;

        this.resetQuestion();
        loadQuestion(topic);
    }

    setAnswer = val => this.setState({answer: val})
    validateAnswer = () => {
        const {topic, validateAnswer, question} = this.props;
        const data = {
            _id: question._id,
            answer: this.state.answer
        };

        validateAnswer(data, topic).then(res => {
            this.setState({
                result: res.correct,
                answered: true
            });
        });
    }

    resetQuestion = () => {
        this.setState({result: false, answered: false, answer: []});
    }
}

function mapStateToProps(state) {
    return {
        question: state.tests.question
    };
}

function mapDispatchToProps(dispatch) {
    return {
        validateAnswer: (answer, topic) => dispatch(TestsApi.validateAnswer(answer, topic))
    };
}

export default connect(mapStateToProps, mapDispatchToProps)(Question);
