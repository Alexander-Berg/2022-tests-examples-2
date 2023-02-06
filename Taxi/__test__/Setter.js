import React from 'react';
import {shallow} from 'enzyme';

import Setter from '../Setter';

describe('utils:context', () => {
    describe('Setter', () => {
        it('Должен вызвать переданную функцию setValue при создании компонента', () => {
            const setValue = jest.fn();
            const wrapper = shallow(<Setter setValue={setValue} value={{}}><div/></Setter>);

            wrapper.setProps({value: {}});

            expect(setValue).toHaveBeenCalledTimes(1);
        });

        it('Должен вызвать переданную функцию setValue с заданным value', () => {
            const setValue = jest.fn();
            const testValue = {test: 1};

            shallow(<Setter setValue={setValue} value={testValue}><div/></Setter>);

            expect(setValue).toHaveBeenCalledWith(testValue);
        });
    });
});
