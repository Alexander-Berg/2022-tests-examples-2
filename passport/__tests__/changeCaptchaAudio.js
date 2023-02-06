import api from '@blocks/api';
import setCaptchaSound from '../setCaptchaSound';
import stopCaptchaSound from '../stopCaptchaSound';
import {getAudioCaptchaFail, getAudioCaptcha} from '../';
import changeCaptchaAudio from '../changeCaptchaAudio';

jest.mock('@blocks/api');
jest.mock('../setCaptchaSound');
jest.mock('../stopCaptchaSound');
jest.mock('../', () => ({
    getAudioCaptchaFail: jest.fn(),
    getAudioCaptcha: jest.fn()
}));

const dispatch = jest.fn();

describe('Action: changeCaptchaAudio', () => {
    describe('success cases', () => {
        beforeEach(() => {
            api.__mockSuccess('captcha');
            getAudioCaptchaFail.mockClear();
            getAudioCaptcha.mockClear();
            setCaptchaSound.mockClear();
            stopCaptchaSound.mockClear();
            dispatch.mockClear();
        });

        it('should handle success case', () => {
            const getState = () => ({
                common: {
                    track_id: 'track_id',
                    uid: 'uid'
                },
                settings: {
                    language: 'language'
                },
                captcha: {
                    trackId: 'track_id'
                }
            });

            changeCaptchaAudio()(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(stopCaptchaSound).toBeCalled();
            expect(getAudioCaptcha).toBeCalled();
            expect(api.request).toBeCalledWith(
                'audiocaptcha',
                {track_id: 'track_id', uid: 'uid', language: 'language'},
                {abortPrevious: true}
            );
            expect(setCaptchaSound).toBeCalledWith('captcha', true);
        });
    });

    describe('fail cases', () => {
        beforeEach(() => {
            api.__mockFail('error');
            getAudioCaptchaFail.mockClear();
            getAudioCaptcha.mockClear();
            setCaptchaSound.mockClear();
            stopCaptchaSound.mockClear();
            dispatch.mockClear();
        });

        it('should handle fail case', () => {
            const getState = () => ({
                common: {
                    track_id: 'track_id',
                    uid: 'uid'
                },
                settings: {
                    language: 'language'
                },
                captcha: {
                    trackId: 'track_id'
                }
            });

            changeCaptchaAudio()(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(stopCaptchaSound).toBeCalled();
            expect(getAudioCaptcha).toBeCalled();
            expect(api.request).toBeCalledWith(
                'audiocaptcha',
                {track_id: 'track_id', uid: 'uid', language: 'language'},
                {abortPrevious: true}
            );
            expect(getAudioCaptchaFail).toBeCalledWith('error');
        });
    });
});
