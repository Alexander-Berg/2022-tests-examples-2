import {Checkbox, List} from 'antd';
import map from 'lodash-es/map';
import PropTypes from 'prop-types';
import React from 'react';

export default class MultipleAnswer extends React.PureComponent {
    static propTypes = {
        question: PropTypes.object,
        answered: PropTypes.bool,
        answer: PropTypes.array,
        onChange: PropTypes.func
    };

    render() {
        const {question, answer, answered} = this.props;

        return (
            <React.Fragment>
                <p>Выберите ответы:</p>

                <Checkbox.Group onChange={this.onChange} value={answer} style={{width: '100%'}}>
                    <List bordered style={{maxWidth: '500px'}}>
                        {map(question.answer_options, (value, key) => (
                            <List.Item key={key}>
                                <Checkbox
                                    value={key}
                                    disabled={answered}
                                >
                                    {value}
                                </Checkbox>
                            </List.Item>
                        ))}
                    </List>
                </Checkbox.Group>
            </React.Fragment>
        );
    };

    onChange = e => {
        const {onChange} = this.props;

        onChange(e);
    }
}
