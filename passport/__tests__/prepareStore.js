import api from '@blocks/api';
import {updateTrack} from '@blocks/common/actions';
import {
    updateFormType,
    updateFormPrefix,
    updateValues,
    updateStates,
    updateValidationMethod,
    updateHumanConfirmationStatus
} from '@blocks/actions/form';
import {updatePerson} from '@blocks/authv2/actions';
import {restoreStateAndRedirect} from '@blocks/auth/actions';

import {prepareStore} from '../prepareStore';

jest.mock('@blocks/actions/form', () => ({
    updateFormType: jest.fn(),
    updateFormPrefix: jest.fn(),
    updateValues: jest.fn(),
    updateStates: jest.fn(),
    updateValidationMethod: jest.fn(),
    updateHumanConfirmationStatus: jest.fn()
}));
jest.mock('@blocks/common/actions', () => ({
    updateTrack: jest.fn()
}));
jest.mock('@blocks/api', () => ({
    doCompleteSubmit: jest.fn()
}));
jest.mock('@blocks/auth/actions', () => ({
    restoreStateAndRedirect: jest.fn()
}));
jest.mock('@blocks/authv2/actions', () => ({
    updatePerson: jest.fn()
}));

describe('@blocks/AuthRegComplete/actions/prepareStore.js', () => {
    afterEach(() => {
        jest.clearAllMocks();
    });
    it('should call all actions for complete_neophonish', async () => {
        expect.assertions(8);
        const action = prepareStore();
        const dispatch = jest.fn();
        const getState = jest.fn().mockReturnValueOnce({});

        api.doCompleteSubmit.mockResolvedValueOnce({
            status: 'ok',
            phone_number: '+123456789',
            state: 'complete_neophonish',
            ['human-confirmation']: 'phone'
        });

        await action(dispatch, getState);

        expect(updatePerson).toBeCalled();
        expect(updateTrack).toBeCalled();
        expect(updateFormType).toBeCalled();
        expect(updateValidationMethod).toBeCalled();
        expect(updateFormPrefix).toBeCalled();
        expect(updateValues).toBeCalled();
        expect(updateStates).toBeCalled();
        expect(updateHumanConfirmationStatus).toBeCalled();
    });
    it('should call restoreStateAndRedirect to /auth/secure if error sslsession.required', async () => {
        expect.assertions(1);
        const action = prepareStore();
        const dispatch = jest.fn();
        const getState = jest.fn().mockReturnValueOnce({
            settings: {
                host: 'https://passport.test.ru'
            }
        });

        api.doCompleteSubmit.mockResolvedValueOnce({
            status: 'error',
            errors: ['sslsession.required']
        });

        await action(dispatch, getState);

        expect(restoreStateAndRedirect).toBeCalledWith('https://passport.test.ru/auth/secure');
    });
    it('should call restoreStateAndRedirect to /auth if doCompleteSubmit return error sessionid.invalid', async () => {
        expect.assertions(1);
        const action = prepareStore();
        const dispatch = jest.fn();
        const getState = jest.fn().mockReturnValueOnce({
            settings: {
                host: 'https://passport.test.ru'
            }
        });

        api.doCompleteSubmit.mockResolvedValueOnce({
            status: 'error',
            errors: ['sessionid.invalid']
        });

        await action(dispatch, getState);

        expect(restoreStateAndRedirect).toBeCalledWith('https://passport.test.ru/auth');
    });
    it('should call restoreStateAndRedirect to /passport if return error action.not_required', async () => {
        expect.assertions(1);
        const action = prepareStore();
        const dispatch = jest.fn();
        const getState = jest.fn().mockReturnValueOnce({
            settings: {
                host: 'https://passport.test.ru'
            }
        });

        api.doCompleteSubmit.mockResolvedValueOnce({
            status: 'error',
            errors: ['action.not_required']
        });

        await action(dispatch, getState);

        expect(restoreStateAndRedirect).toBeCalledWith('https://passport.test.ru/passport?mode=passport');
    });
});
