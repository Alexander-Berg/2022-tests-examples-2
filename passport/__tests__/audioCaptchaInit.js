import destroyAudioCaptcha from '../destroyAudioCaptcha';
import playCaptcha from '../playCaptcha';
import audioCaptchaInit from '../audioCaptchaInit';
import {getAudioCaptchaSuccess, getAudioCaptchaFail, changeCaptchaPlayStatus} from '../';

jest.mock('../destroyAudioCaptcha');
jest.mock('../playCaptcha');
jest.mock('../', () => ({
    getAudioCaptchaSuccess: jest.fn(),
    getAudioCaptchaFail: jest.fn(),
    changeCaptchaPlayStatus: jest.fn()
}));

const dispatch = jest.fn();
const captcha = {
    voice: {
        intro_url: 'introUrl',
        url: 'soundUrl'
    }
};
const handlers = [];

const onFn = jest.fn((event, cb) => {
    handlers.push(cb);
});

const howlFn = jest.fn((params) => {
    function HowlerFn(p) {
        this.params = p;
        this.on = onFn;
    }

    return new HowlerFn(params);
});

Object.defineProperty(window, 'Howl', {
    value: howlFn
});

describe('Action: audioCaptchaInit', () => {
    beforeEach(() => {
        destroyAudioCaptcha.mockClear();
        playCaptcha.mockClear();
        getAudioCaptchaSuccess.mockClear();
        getAudioCaptchaFail.mockClear();
        changeCaptchaPlayStatus.mockClear();
        dispatch.mockClear();
        onFn.mockClear();
    });

    it('should sucessfully init sounds', () => {
        const loadSoundsPromises = audioCaptchaInit(captcha)(dispatch);

        expect(dispatch).toBeCalled();
        expect(dispatch.mock.calls.length).toBe(1);

        handlers[0]();
        handlers[3]();

        loadSoundsPromises.then(() => {
            expect(getAudioCaptchaSuccess).toBeCalled();
        });

        handlers.splice(0, handlers.length);
    });

    it('should failed init sounds', () => {
        const loadSoundsPromises = audioCaptchaInit(captcha)(dispatch);

        expect(dispatch).toBeCalled();
        expect(dispatch.mock.calls.length).toBe(1);

        handlers[1]();
        handlers[4]();

        loadSoundsPromises.catch(() => {
            expect(getAudioCaptchaFail).toBeCalled();
        });
    });
});
