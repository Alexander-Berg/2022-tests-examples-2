import {getAudioCaptchaFail, getAudioCaptchaSuccess} from '../';
import playCaptchaSound from '../playCaptchaSound';
import setCaptchaSound from '../setCaptchaSound';

jest.mock('../playCaptchaSound');
jest.mock('../', () => ({
    getAudioCaptchaFail: jest.fn(),
    getAudioCaptchaSuccess: jest.fn()
}));

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
const dispatch = jest.fn();

Object.defineProperty(window, 'Howl', {
    value: howlFn
});

describe('Action: setCaptchaSound', () => {
    beforeEach(() => {
        getAudioCaptchaFail.mockClear();
        playCaptchaSound.mockClear();
        getAudioCaptchaSuccess.mockClear();
        dispatch.mockClear();
    });

    it('should handle load event', () => {
        setCaptchaSound({key: 'key', voice: {url: 'voiceUrl'}}, false)(dispatch);

        handlers[0]();

        expect(dispatch).toBeCalled();
        expect(dispatch.mock.calls.length).toBe(1);
        expect(getAudioCaptchaSuccess).toBeCalled();
        expect(playCaptchaSound).not.toBeCalled();
        expect(getAudioCaptchaFail).not.toBeCalled();

        handlers.splice(0, handlers.length);
    });

    it('should handle load event', () => {
        setCaptchaSound({key: 'key', voice: {url: 'voiceUrl'}}, true)(dispatch);

        handlers[0]();

        expect(dispatch).toBeCalled();
        expect(dispatch.mock.calls.length).toBe(2);
        expect(getAudioCaptchaSuccess).toBeCalled();
        expect(playCaptchaSound).toBeCalled();
        expect(getAudioCaptchaFail).not.toBeCalled();

        handlers.splice(0, handlers.length);
    });

    it('should handle loaderror event', () => {
        setCaptchaSound({key: 'key', voice: {url: 'voiceUrl'}}, false)(dispatch);

        handlers[1]();

        expect(dispatch).toBeCalled();
        expect(dispatch.mock.calls.length).toBe(1);
        expect(getAudioCaptchaSuccess).not.toBeCalled();
        expect(playCaptchaSound).not.toBeCalled();
        expect(getAudioCaptchaFail).toBeCalled();
    });
});
