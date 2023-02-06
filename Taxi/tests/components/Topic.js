import {CheckOutlined} from '@ant-design/icons';
import {Button, Card} from 'antd';
import {push} from 'connected-react-router';
import PropTypes from 'prop-types';
import React from 'react';
import {connect} from 'react-redux';

class Topic extends React.PureComponent {
    static propTypes = {
        topic: PropTypes.object,
        pathname: PropTypes.string,
        changeRouteTo: PropTypes.func
    };

    render() {
        const {topic} = this.props;

        return (
            <Card
                title={topic.topic_name}
                actions={[this.renderStartTestButton(topic)]}
            >
                <div className="card-body">
                    {topic.questions_avail ? (
                        <React.Fragment>
                            Вопросы:
                            <br/>
                            осталось
                            <strong> {topic.questions_avail}</strong> из
                            <strong> {topic.questions_total}</strong>
                        </React.Fragment>
                    ) : (
                        <span>
                            Вы ответили на все вопросы.
                        </span>
                    )}

                </div>
            </Card>
        );
    };

    renderStartTestButton = topic => {
        if (!topic.questions_avail) {
            return <CheckOutlined style={{color: '#52c41a', fontSize: '20px', marginTop: '5px'}}/>;
        }

        let text = 'Начать тест';

        if (topic.questions_avail !== topic.questions_total) {
            text = 'Продолжить тест';
        }

        return (
            <Button
                style={{width: '100%'}}
                type="primary"
                onClick={this.startTest}
                disabled={!topic.questions_avail}
            >
                {text}
            </Button>
        );
    }

    startTest = () => {
        const {topic: {topic}, changeRouteTo, pathname} = this.props;

        changeRouteTo(topic, pathname);
    }
}

function mapStateToProps(state) {
    return {
        pathname: state.router.location.pathname
    };
}

function mapDispatchToProps(dispatch) {
    return {
        changeRouteTo: (topic, pathname) => dispatch(push({
            pathname: `${pathname}/tests/${topic}`
        }))
    };
}

export default connect(mapStateToProps, mapDispatchToProps)(Topic);
