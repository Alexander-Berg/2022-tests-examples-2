import {shallow} from 'enzyme';
import React from 'react';

import {Hotkey} from '../../hotkey';
import Button from '../Button';

describe('Button', () => {
    it('обычный рендер', () => {
        const button = shallow(<Button text="button"/>);

        expect(button).toMatchSnapshot();
        expect(button.text()).toEqual('button');
    });

    it('должен вызываться onClick', () => {
        const onClick = jest.fn();
        const button = shallow(<Button text="button" onClick={onClick}/>);

        button.find('button').simulate('click');

        expect(onClick).toHaveBeenCalled();
    });

    it('должна отображаться икнока', () => {
        const Icon = (): JSX.Element => null;
        const button = shallow(<Button text="button" icon={<Icon/>}/>);
        const icon = button.find(Icon);

        expect(button).toMatchSnapshot();
        expect(icon).toHaveLength(1);
    });

    it('должна отображаться подсказка для горячих клавиш', () => {
        const button = shallow(<Button text="button" hotkey="alt+q"/>);
        const hotkey = button.find(Hotkey);

        expect(button).toMatchSnapshot();
        expect(hotkey).toHaveLength(1);
    });
});
