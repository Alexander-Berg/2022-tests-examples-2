import React, {ComponentType} from 'react';
import {shallow, mount} from 'enzyme';

import Alert from '../Alert';

import Info from '../../icon/Info';
import Warning from '../../icon/Warning';
import Check from '../../icon/Check';

describe('Alert', () => {
    it('должен пробрасывать клики', () => {
        const handler = jest.fn();
        const wrapper = shallow(<Alert onClick={handler}/>);
        wrapper.find('.amber-alert').simulate('click');
        expect(handler).toHaveBeenCalled();
    });
    describe('кнопка закрытия', () => {
        it('не должен рисовать кнопку без хендлера', () => {
            const wrapper = shallow(<Alert/>);
            expect(wrapper.find('.amber-alert__close .amber-icon').length).toBe(0);
        });
        it('должен рисовать кнопку и пробрасывать клики на при наличии хендлера', () => {
            const handler = jest.fn();
            const wrapper = mount(<Alert onCloseClick={handler}/>);
            expect(wrapper.find('.amber-alert__close .amber-icon').length).toBe(1);
            wrapper.find('.amber-alert__close .amber-icon svg').simulate('click');
            expect(handler).toHaveBeenCalled();
        });
    });
    describe('иконка', () => {
        it('должен рисовать иконку info по умолчанию', () => {
            const wrapper = shallow(<Alert/>);
            expect(wrapper.find(Info).length).toBe(1);
        });
        it('должен рисовать иконку warning при типе error', () => {
            const wrapper = shallow(<Alert type="error"/>);
            expect(wrapper.find(Warning).length).toBe(1);
        });
        it('должен рисовать иконку check при типе success', () => {
            const wrapper = shallow(<Alert type="success"/>);
            expect(wrapper.find(Check).length).toBe(1);
        });
        it('должен рисовать кастомную иконку, если она передана', () => {
            const Icon: ComponentType = (): any => 'icon';
            const wrapper = shallow(<Alert iconComponent={Icon}/>);
            expect(wrapper.find(Icon).length).toBe(1);
        });
    });
});
