import {STEPS} from '@blocks/UserEntryFlow/steps';
import {FIELDS_NAMES} from '@components/Field/names';
import {validationEmptyFields} from '../validationEmptyFields';

describe('@blocks/AuthRegComplete/actions/validationEmptyFields', () => {
    afterEach(() => {
        jest.clearAllMocks();
    });
    it('should throw undefined if has errors', async () => {
        expect.assertions(2);
        const action = validationEmptyFields();
        const dispatchMock = jest.fn();
        const getStateMock = jest.fn().mockReturnValueOnce({
            completeFlow: {step: STEPS.SQ_SA},
            form: {
                values: {[FIELDS_NAMES.HINT_ANSWER]: 'someText'},
                errors: {[FIELDS_NAMES.HINT_ANSWER]: {code: 'someErro'}}
            }
        });

        try {
            await action(dispatchMock, getStateMock);
        } catch (error) {
            expect(error).toEqual(undefined);
        }
        expect(dispatchMock).toBeCalled();
    });
    it('should throw undefined if has errors', async () => {
        expect.assertions(2);
        const action = validationEmptyFields();
        const dispatchMock = jest.fn();
        const getStateMock = jest.fn().mockReturnValueOnce({
            completeFlow: {step: STEPS.SQ_SA},
            form: {values: {[FIELDS_NAMES.HINT_ANSWER]: ''}, errors: {}}
        });

        try {
            await action(dispatchMock, getStateMock);
        } catch (error) {
            expect(error).toEqual(undefined);
        }
        expect(dispatchMock).toBeCalled();
    });
    it('should resolve with undefined if has not errors', async () => {
        const action = validationEmptyFields();
        const dispatchMock = jest.fn();
        const getStateMock = jest.fn().mockReturnValueOnce({
            completeFlow: {step: STEPS.SQ_SA},
            form: {values: {[FIELDS_NAMES.HINT_ANSWER]: 'someText'}, errors: {}}
        });

        expect(await action(dispatchMock, getStateMock)).toEqual(undefined);
        expect(dispatchMock).not.toBeCalled();
    });
});
