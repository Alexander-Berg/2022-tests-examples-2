import api from '@blocks/api';
import audioCaptchaInit from '../audioCaptchaInit';
import setCaptchaSound from '../setCaptchaSound';
import {getImageCaptchaSuccess, loadCaptcha, getCaptchaFail} from '../';
import getCaptcha from '../getCaptcha';

jest.mock('@blocks/api');
jest.mock('../audioCaptchaInit');
jest.mock('../setCaptchaSound');
jest.mock('../', () => ({
    getImageCaptchaSuccess: jest.fn(),
    loadCaptcha: jest.fn(),
    getCaptchaFail: jest.fn()
}));

const dispatch = jest.fn();

describe('Action: getCaptcha', () => {
    describe('success cases', () => {
        beforeEach(() => {
            api.__mockSuccess({key: 'key', image_url: 'imageUrl'});
            audioCaptchaInit.mockClear();
            setCaptchaSound.mockClear();
            getImageCaptchaSuccess.mockClear();
            loadCaptcha.mockClear();
            getCaptchaFail.mockClear();
            dispatch.mockClear();
        });

        it('should get captcha without init audio', () => {
            const state = {
                common: {
                    track_id: 'track_id',
                    uid: 'uid'
                },
                settings: {
                    language: 'language'
                },
                captcha: {
                    ocr: 'ocr'
                }
            };
            const getState = () => state;

            getCaptcha()(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(3);
            expect(getImageCaptchaSuccess).toBeCalled();
            expect(audioCaptchaInit).not.toBeCalled();
            expect(setCaptchaSound).toBeCalled();

            api.request.mockClear();

            state.common.captchaScaleFactor = true;

            getCaptcha()(dispatch, getState);

            expect(api.request).toBeCalledWith(
                'textcaptcha',
                {track_id: 'track_id', uid: 'uid', language: 'language', ocr: 'ocr', scale_factor: true},
                {abortPrevious: true}
            );
        });

        it('should get captcha and init audio', () => {
            const state = {
                common: {
                    track_id: 'track_id',
                    uid: 'uid'
                },
                settings: {
                    language: 'language'
                },
                captcha: {
                    ocr: 'ocr'
                }
            };
            const getState = () => state;

            getCaptcha(true)(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(3);
            expect(getImageCaptchaSuccess).toBeCalled();
            expect(audioCaptchaInit).toBeCalled();
            expect(setCaptchaSound).not.toBeCalled();
        });
    });

    describe('fail cases', () => {
        beforeEach(() => {
            api.__mockFail('error');
            audioCaptchaInit.mockClear();
            setCaptchaSound.mockClear();
            getImageCaptchaSuccess.mockClear();
            loadCaptcha.mockClear();
            getCaptchaFail.mockClear();
            dispatch.mockClear();
        });

        it('should get captcha and init audio', () => {
            const state = {
                common: {
                    track_id: 'track_id',
                    uid: 'uid'
                },
                settings: {
                    language: 'language'
                },
                captcha: {
                    ocr: 'ocr'
                }
            };
            const getState = () => state;

            getCaptcha(true)(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(2);
            expect(getCaptchaFail).toBeCalled();
        });
    });
});
