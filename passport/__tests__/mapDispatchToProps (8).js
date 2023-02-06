import {magicService} from '@blocks/AuthSilent/magicService';
import {changeCaptchaState} from '@blocks/authv2/actions';
import {magicInit} from '@blocks/authv2/actions/magic';
import {setCaptchaTrack} from '@components/Captcha/actions';
import {mapDispatchToProps} from '../mapDispatchToProps';

jest.mock('@blocks/AuthSilent/magicService', () => ({
    magicService: {
        restart: jest.fn(),
        stop: jest.fn()
    }
}));
jest.mock('@blocks/authv2/actions', () => ({
    changeCaptchaState: jest.fn()
}));
jest.mock('@blocks/authv2/actions/magic', () => ({
    magicInit: jest.fn()
}));
jest.mock('@components/Captcha/actions', () => ({
    setCaptchaTrack: jest.fn()
}));

describe('@blocks/authv2/components/MagicBookPage/mapDispatchToProps', () => {
    const dispatchMock = jest.fn();

    beforeEach(() => {
        jest.clearAllMocks();
    });
    describe('magicInit', () => {
        it('should call magicInit action', () => {
            mapDispatchToProps(dispatchMock).magicInit();
            expect(dispatchMock).toBeCalled();
            expect(magicInit).toBeCalled();
        });
    });
    describe('magicRestart', () => {
        it('should call magicService.restart', () => {
            mapDispatchToProps(dispatchMock).magicRestart();
            expect(magicService.restart).toBeCalled();
        });
    });
    describe('magicStop', () => {
        it('should call magicService.stop', () => {
            mapDispatchToProps(dispatchMock).magicStop();
            expect(magicService.stop).toBeCalled();
        });
    });
    describe('onCaptchaCheck', () => {
        it('should call onCaptchaCheck action', () => {
            mapDispatchToProps(dispatchMock).onCaptchaCheck();
            expect(dispatchMock).toBeCalled();
            expect(changeCaptchaState).toBeCalled();
        });
    });
    describe('captchaStart', () => {
        it('should start actions for run captcha', () => {
            mapDispatchToProps(dispatchMock).captchaStart();
            expect(dispatchMock).toBeCalled();
            dispatchMock.mock.calls[0][0](dispatchMock, () => ({auth: {magicTrack: 'zxv'}}));
            expect(magicService.stop).toBeCalled();
            expect(setCaptchaTrack).toBeCalledWith('zxv');
            expect(changeCaptchaState).toBeCalled();
        });
    });
});
