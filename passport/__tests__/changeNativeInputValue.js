import changeNativeInputValue from '../changeNativeInputValue';
import {NATIVE_INPUT_ID_PREFIX} from '@components/Field';

let nativeField = {value: ''};
const getElementById = jest.fn(() => nativeField);

Object.defineProperty(document, 'getElementById', {
    value: getElementById
});

describe('Action: changeNativeInputValue', () => {
    it('should find dom element by id and change value', () => {
        nativeField = {value: ''};

        const fieldName = 'login';
        const newValue = 'newValue';

        changeNativeInputValue(`${NATIVE_INPUT_ID_PREFIX}${fieldName}`, newValue)();

        expect(getElementById).toBeCalled();
        expect(nativeField.value).toBe(newValue);
    });
});
