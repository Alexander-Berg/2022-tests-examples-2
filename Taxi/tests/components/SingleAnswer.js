import {Radio, List} from 'antd';
import map from 'lodash-es/map';
import PropTypes from 'prop-types';
import React from 'react';

export default class SingleAnswer extends React.PureComponent {
    static propTypes = {
        question: PropTypes.object,
        answered: PropTypes.bool,
        answer: PropTypes.array,
        onChange: PropTypes.func
    };

    render() {
        const {question, answered, answer} = this.props;

        return (
            <React.Fragment>
                <p>Варианты ответа:</p>
                <Radio.Group
                    onChange={this.onChange}
                    value={answer[0]}
                    style={{width: '100%'}}
                >
                    <List bordered style={{maxWidth: '500px'}}>
                        {map(question.answer_options, (value, key) => (
                            <List.Item key={key}>
                                <Radio
                                    value={key}
                                    style={{display: 'block', height: '30px', lineHeight: '30px'}}
                                    disabled={answered}
                                >
                                    {value}
                                </Radio>
                            </List.Item>
                        ))}
                    </List>
                </Radio.Group>
            </React.Fragment>
        );
    };

    onChange = e => {
        const {onChange} = this.props;

        onChange([e.target.value]);
    }
}
