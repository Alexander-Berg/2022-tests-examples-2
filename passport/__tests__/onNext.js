import {defaultCompleteLite} from '@blocks/AuthRegComplete/logic/configs/defaultCompleteLite';
import {STEPS} from '@blocks/UserEntryFlow/steps';
import {domikIsLoading} from '@blocks/auth/actions';
import {getFormErrors} from '@blocks/selectors';
import {getAuthRegCompleteConfig, getCurrentStep} from '@blocks/AuthRegComplete/logic';
import {getSuggestedLogins} from '@components/LoginSuggest/actions';
import {onNext} from '../onNext';
import {moveNextStep} from '../actions';

jest.mock('../actions', () => ({
    moveNextStep: jest.fn()
}));
jest.mock('@blocks/metrics', () => ({
    send: jest.fn(),
    goal: jest.fn()
}));
jest.mock('@blocks/auth/actions', () => ({
    domikIsLoading: jest.fn()
}));
jest.mock('@components/LoginSuggest/actions', () => ({
    getSuggestedLogins: jest.fn()
}));
jest.mock('@blocks/selectors', () => ({
    getFormErrors: jest.fn()
}));
jest.mock('@blocks/authv2/actions/registration/toggleHumanConfirmation', () => ({
    toggleHumanConfirmation: jest.fn()
}));
jest.mock('@blocks/AuthRegComplete/logic', () => ({
    getAuthRegCompleteConfig: jest.fn(),
    getCurrentStep: jest.fn()
}));
jest.mock('@components/Field/names', () => ({
    FIELDS_NAMES: jest.fn()
}));
jest.mock('@blocks/common/constants', () => ({
    SECURITY_QUESTION_ID: jest.fn()
}));
jest.mock('@blocks/UserEntryFlow/logic', () => ({
    confirmPhone: jest.fn()
}));
jest.mock('../actions', () => ({
    moveNextStep: jest.fn()
}));
jest.mock('../checkPhoneConfirmationCode', () => ({
    checkPhoneConfirmationCode: jest.fn()
}));
jest.mock('../validateSecurityAnswer', () => ({
    validateSecurityAnswer: jest.fn()
}));
jest.mock('../validationEmptyFields', () => ({
    validationEmptyFields: jest.fn()
}));

describe('@blocks/AuthRegComplete/actions/onNext.js', () => {
    afterEach(() => {
        jest.clearAllMocks();
    });
    it('should return before next step if it has errors ', async () => {
        const action = onNext();
        const dispatch = jest
            .fn()
            .mockImplementation((callback) => (typeof callback === 'function' ? callback() : undefined));
        const getState = jest.fn().mockReturnValue({
            form: {validation: {}},
            common: {},
            settings: {},
            person: {}
        });

        getAuthRegCompleteConfig.mockReturnValue(defaultCompleteLite);
        getCurrentStep.mockReturnValue(STEPS.PHONE);
        getFormErrors.mockReturnValue({
            phone: {code: 'phone_number.invalid'}
        });

        await action(dispatch, getState);

        expect(domikIsLoading).toBeCalled();
        expect(moveNextStep).not.toBeCalled();
    });
    it('should call moveNextStep', async () => {
        const action = onNext();
        const dispatch = jest
            .fn()
            .mockImplementation((callback) => (typeof callback === 'function' ? callback() : undefined));
        const getState = jest.fn().mockReturnValue({
            form: {validation: {}},
            common: {},
            settings: {},
            person: {}
        });

        getAuthRegCompleteConfig.mockReturnValue(defaultCompleteLite);
        getCurrentStep.mockReturnValue(STEPS.PHONE);
        getFormErrors.mockReturnValue({
            phone: {}
        });

        await action(dispatch, getState);

        expect(domikIsLoading).toBeCalled();
        expect(moveNextStep).toBeCalled();
    });
    it('should call getSuggestedLogins if nextStep is LOGIN', async () => {
        const action = onNext();
        const dispatch = jest
            .fn()
            .mockImplementation((callback) => (typeof callback === 'function' ? callback() : undefined));
        const getState = jest.fn().mockReturnValue({
            form: {validation: {}},
            common: {},
            settings: {},
            person: {}
        });

        getAuthRegCompleteConfig.mockReturnValue(defaultCompleteLite);
        getCurrentStep.mockReturnValue(STEPS.PERSONAL_DATA);
        getFormErrors.mockReturnValue({
            phone: {}
        });

        await action(dispatch, getState);

        expect(getSuggestedLogins).toBeCalled();
    });
});
