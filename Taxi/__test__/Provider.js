/* eslint-disable react/no-multi-comp */

import React from 'react';
import {mount, shallow} from 'enzyme';

import Provider from '../Provider';
import Context from '../Context';

jest.mock('../Context', () => {
    let context;
    return {
        Consumer: props => props.children(context),
        Provider: props => {
            context = props.value;
            return props.children;
        }
    };
});

describe('utils:context', () => {
    describe('Provider', () => {
        const Child = () => <div/>;
        const Consumer = () => <Context.Consumer>{context => <Child context={context}/>}</Context.Consumer>;
        const TestApp = () => (
            <Provider>
                <Consumer/>
            </Provider>
        );

        it('Должен установить контекст с полями value и setValue', () => {
            const wrapper = mount(<TestApp/>);
            const childContext = wrapper.find(Child).prop('context');

            expect(childContext).toMatchObject({
                setValue: expect.any(Function),
                value: expect.any(Object)
            });
        });

        it('Метод setValue должен мержить data.value с переданным объектом', () => {
            const instance = shallow(<Provider/>).instance();
            const testValue1 = {foo: 1};

            instance.setValue(testValue1);
            expect(instance.data.value).toMatchObject(testValue1);

            instance.setValue({bar: 2});
            expect(instance.data.value).toMatchObject({foo: 1, bar: 2});
        });
    });
});
