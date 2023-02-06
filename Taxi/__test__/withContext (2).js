import React from 'react';
import {mount} from 'enzyme';
import withContext from '../withContext';

jest.mock('../Context', () => {
    const context = {value: {foo: 1, bar: 2}};

    return {
        Consumer: props => props.children(context)
    };
});

describe('utils:context', () => {
    describe('withContext', () => {
        const Child = () => <div/>;

        it('Должен возвращать функцию, возвращающую stateless компонент', () => {
            const fooContext = withContext('foo');
            expect(fooContext).toEqual(expect.any(Function));
            expect(fooContext(Child)).toEqual(expect.any(Function));
        });

        it('Должен брать из контекста свойства по ключам из аргументов и пробрасывать в оборачиваемый компонент', () => {
            const WrappedChild = withContext('foo', 'bar')(Child);
            const wrapperChild = mount(<WrappedChild/>).find(Child);

            expect(wrapperChild.prop('foo')).toBe(1);
            expect(wrapperChild.prop('bar')).toBe(2);
        });
    });
});
