import React from 'react';
import {mount} from 'enzyme';
import ContextSetter from '../ContextSetter';
import Setter from '../Setter';
import Context from '../Context';

jest.mock('../Context', () => {
    const setValue = jest.fn();
    const context = {setValue};

    return {
        setValue,
        Consumer: props => props.children(context)
    };
});

describe('utils:context', () => {
    describe('ContextSetter', () => {
        it('Должен пробрасывать функцию setValue из контекста и prop value в Setter', () => {
            const testValue = {foo: 1};
            const wrapper = mount(<ContextSetter value={testValue}><div/></ContextSetter>);
            const setter = wrapper.find(Setter);
            expect(setter.prop('setValue')).toBe(Context.setValue);
            expect(setter.prop('value')).toBe(testValue);
        });
    });
});
