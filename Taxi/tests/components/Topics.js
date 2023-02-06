import {Col, Row} from 'antd';
import PropTypes from 'prop-types';
import React from 'react';

import Topic from './Topic';

export default class Topics extends React.PureComponent {
    static propTypes = {
        topics: PropTypes.array
    };

    render() {
        const {topics} = this.props;

        return (
            <Row gutter={16} type="flex" justify="start">
                {topics && topics.map(topic => (
                    <Col style={{width: 330}} key={topic.topic}>
                        <Topic topic={topic}/>
                    </Col>
                ))}
            </Row>
        );
    };
}
