import {PoweroffOutlined} from '@ant-design/icons';
import {Button} from 'antd';
import PropTypes from 'prop-types';
import React from 'react';

export default class TestResults extends React.PureComponent {
    static propTypes = {
        topic: PropTypes.string,
        results: PropTypes.object,
        getTestResults: PropTypes.func,
        resetResults: PropTypes.func
    };

    state = {
        loading: false
    }

    componentWillUnmount() {
        this.props.resetResults();
    }

    render() {
        const {results} = this.props;

        return (
            <React.Fragment>
                <h3>Тест завершен</h3>
                {results && (
                    <p style={{fontSize: '16px'}}>
                        Вы ответили правильно на
                        <strong> {results.correct}</strong> из
                        <strong> {results.total}</strong> вопросов.
                    </p>
                )}

                {!results && (
                    <Button
                        type="primary"
                        icon={<PoweroffOutlined/>}
                        loading={this.state.loading}
                        onClick={this.getTestResults}
                    >
                        Показать результаты
                    </Button>
                )}
            </React.Fragment>
        );
    };

    getTestResults = () => {
        const {getTestResults, topic} = this.props;

        this.setState({loading: true});

        getTestResults(topic).then(() => {
            this.setState({loading: false});
        });
    }
}
