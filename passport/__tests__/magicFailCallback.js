import {magicFailCallback} from '../magicFailCallback';
import {magicService} from '@blocks/AuthSilent/magicService';
import {setMagicError, changeCaptchaState} from '@blocks/authv2/actions';
import reAuthPasswordSubmit from '@blocks/authv2/actions/reAuthPasswordSubmit';
import {setCaptchaTrack} from '@components/Captcha/actions';

jest.mock('@blocks/AuthSilent/magicService', () => ({
    magicService: {
        stop: jest.fn(),
        restartPolling: jest.fn(),
        trackId: 'qwer'
    }
}));
jest.mock('@blocks/authv2/actions', () => ({
    setMagicError: jest.fn().mockImplementation(() => 'setMagicError'),
    changeCaptchaState: jest.fn().mockImplementation(() => 'changeCaptchaState')
}));
jest.mock('@blocks/authv2/actions/reAuthPasswordSubmit', () =>
    jest.fn().mockImplementation(() => 'reAuthPasswordSubmit')
);
jest.mock('@components/Captcha/actions', () => ({
    setCaptchaTrack: jest.fn().mockImplementation(() => 'setCaptchaTrack')
}));

describe('authv2/magic/magicFailCallback', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });
    it('should call setMagicError, reAuthPasswordSubmit, restartPolling on error password.not_matched', () => {
        const dispatchMock = jest.fn();
        const callback = magicFailCallback(dispatchMock);

        callback({errors: ['password.not_matched']});

        expect(magicService.stop).toBeCalled();
        expect(dispatchMock).toBeCalledWith('setMagicError');
        expect(dispatchMock).toBeCalledWith('reAuthPasswordSubmit');
        expect(setMagicError).toBeCalledWith('password.not_matched_2fa');
        expect(reAuthPasswordSubmit).toBeCalled();
        expect(magicService.restartPolling).toBeCalled();
    });
    it('should change location on state auth_challenge', () => {
        const dispatchMock = jest.fn();
        const callback = magicFailCallback(dispatchMock);

        callback({errors: ['captcha.required']});

        expect(magicService.stop).toBeCalled();
        expect(dispatchMock).toBeCalledWith('setCaptchaTrack');
        expect(dispatchMock).toBeCalledWith('changeCaptchaState');
        expect(setCaptchaTrack).toBeCalledWith(magicService.trackId);
        expect(changeCaptchaState).toBeCalledWith(true);
        expect(magicService.restartPolling).not.toBeCalled();
    });
    it('should change location on state auth_challenge', () => {
        magicService.trackNotFoundErrorCount = 0;

        const dispatchMock = jest.fn();
        const callback = magicFailCallback(dispatchMock);

        callback({errors: ['track.not_found']});

        expect(magicService.stop).not.toBeCalled();
        expect(dispatchMock).not.toBeCalled();
        expect(setMagicError).not.toBeCalled();
        expect(reAuthPasswordSubmit).not.toBeCalled();
        expect(magicService.trackNotFoundErrorCount).toEqual(1);
        expect(magicService.restartPolling).toBeCalled();

        callback({errors: ['track.not_found']});
        callback({errors: ['track.not_found']});
        callback({errors: ['track.not_found']});
        callback({errors: ['track.not_found']});
        callback({errors: ['track.not_found']});
        callback({errors: ['track.not_found']});

        expect(magicService.trackNotFoundErrorCount).toEqual(7);
        expect(magicService.stop).toBeCalled();
        expect(dispatchMock).toBeCalledWith('setMagicError');
        expect(dispatchMock).toBeCalledWith('reAuthPasswordSubmit');
        expect(setMagicError).toBeCalledWith('track.not_found');
        expect(reAuthPasswordSubmit).toBeCalled();
        expect(magicService.restartPolling).toBeCalled();
    });
});
