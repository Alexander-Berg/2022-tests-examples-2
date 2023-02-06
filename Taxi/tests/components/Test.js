import {Row, Col, Spin} from 'antd';
import PropTypes from 'prop-types';
import React from 'react';
import {connect} from 'react-redux';

import SpinWrapper from '../../../../../utils/Wrappers/spinWrapper';
import TestsApi from '../api/tests';

import Question from './Question';
import TestResults from './TestResults';

class Test extends React.PureComponent {
    static propTypes = {
        topic: PropTypes.string,
        question: PropTypes.object,
        results: PropTypes.object,

        loadQuestion: PropTypes.func,
        resetQuestion: PropTypes.func,
        getTestResults: PropTypes.func,
        resetResults: PropTypes.func
    }

    componentDidMount() {
        const {loadQuestion, topic} = this.props;

        loadQuestion(topic);
    }

    componentWillUnmount() {
        this.props.resetQuestion();
    }

    render() {
        const {question, loadQuestion, getTestResults, results, resetResults} = this.props;

        if (!question) {
            return (
                <SpinWrapper>
                    <Spin size="large"/>
                </SpinWrapper>
            );
        }

        return (
            <Row>
                <Col>
                    {!question.is_finished ? (
                        <Question
                            topic={question.topic}
                            loadQuestion={loadQuestion}
                        />
                    ) : (
                        <TestResults
                            topic={question.topic}
                            results={results}
                            getTestResults={getTestResults}
                            resetResults={resetResults}
                        />
                    )}
                </Col>
            </Row>
        );
    };
}

function mapStateToProps(state) {
    const {tests} = state;

    return {
        question: tests.question,
        results: tests.results
    };
}

function mapDispatchToProps(dispatch) {
    return {
        loadQuestion: topic => dispatch(TestsApi.loadQuestion(topic)),
        resetQuestion: () => dispatch(TestsApi.resetQuestion()),
        getTestResults: topic => dispatch(TestsApi.getResults(topic)),
        resetResults: () => dispatch(TestsApi.resetResults())
    };
}

export default connect(mapStateToProps, mapDispatchToProps)(Test);
