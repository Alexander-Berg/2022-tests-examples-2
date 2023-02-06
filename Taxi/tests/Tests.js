import {Row, Col, Spin} from 'antd';
import PropTypes from 'prop-types';
import React from 'react';

import SpinWrapper from '../../../../utils/Wrappers/spinWrapper';

import Topics from './components/Topics';
import WrappedComponent from './WrappedComponent';

export default class Tests extends React.PureComponent {
    static propTypes = {
        topics: PropTypes.oneOfType([PropTypes.string, PropTypes.array]),
        isTopicsLoad: PropTypes.bool
    };

    render() {
        const {topics, isTopicsLoad} = this.props;

        if (topics === 'error') {
            return null;
        }

        if (isTopicsLoad) {
            return (
                <SpinWrapper>
                    <Spin size="large"/>
                </SpinWrapper>
            );
        }

        return (
            <WrappedComponent>
                <Row>
                    <Col>
                        <Topics topics={topics}/>
                    </Col>
                </Row>
            </WrappedComponent>
        );
    }
}
