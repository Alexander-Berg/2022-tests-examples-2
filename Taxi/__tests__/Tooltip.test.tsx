import React from 'react';
import {mount, shallow} from 'enzyme';

import Popup from '../../popup/Popup';
import Button from '../../button/Button';
import Tooltip from '../Tooltip';

describe('Components/tooltip', () => {
    it('Можно прокинуть control через children', () => {
        const wrapper = shallow(
            <Tooltip content="123" enableClickListener>
                <Button>1</Button>
            </Tooltip>
        );
        expect(wrapper.find(Button).exists()).toBeTruthy();
    });

    it('По-умолчанию не выводит Popup', () => {
        const wrapper = mount(
            <Tooltip content="123" enableClickListener>
                <Button>1</Button>
            </Tooltip>
        );
        expect(wrapper.find(Popup).exists()).toBeFalsy();
    });

    it('Выводит Popup', () => {
        const wrapper = mount(
            <Tooltip content="123" open>
                <Button>1</Button>
            </Tooltip>
        );

        expect(wrapper.find(Popup).exists()).toBeTruthy();
    });

    it('Можно прокинуть placement', () => {
        const wrapper = mount(
            <Tooltip content="123" open placement="top">
                <Button>1</Button>
            </Tooltip>
        );

        expect(wrapper.find(Popup).prop('placement')).toEqual('top');
    });

    it('Можно прокинуть onClickOutside', () => {
        const fn = jest.fn();
        const wrapper = mount(
            <Tooltip content="123" open onClickOutside={fn}>
                <Button>1</Button>
            </Tooltip>
        );

        expect(wrapper.find(Popup).prop('onClickOutside')).toEqual(fn);
    });

    it('Не должен падать, если внутри ничего нет', () => {
        const wrapper = mount(
            <Tooltip content="123" enableClickListener>{undefined}</Tooltip>
        );

        expect(wrapper.find(Popup).exists()).toBeFalsy();
    });
});
