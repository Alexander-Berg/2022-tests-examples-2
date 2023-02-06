import React from 'react';
import {shallow} from 'enzyme';
import ButtonGroup from '../ButtonGroup';
import Button from '../../button/Button';

describe('Components/button-group', () => {
    it('Показывем группу кнопок', () => {
        const buttons = [
            <Button theme="fill" key="button1">
                Нажать
            </Button>,
            <Button theme="outline" key="button2">
                Нажать
            </Button>
        ];
        const wrapper = shallow(<ButtonGroup>{buttons}</ButtonGroup>);
        expect(wrapper.contains(buttons)).toBeTruthy();
    });
});
