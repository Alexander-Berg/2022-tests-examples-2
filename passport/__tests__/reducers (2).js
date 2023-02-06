import reducer from '../reducers';

describe('Reducer: Captcha', () => {
    it('should handle CHANGE_CAPTCHA_PLAY_STATUS action', () => {
        const state = {};
        const action = {
            type: 'CHANGE_CAPTCHA_PLAY_STATUS',
            playing: true
        };
        const result = reducer(state, action);

        expect(result).toEqual({
            playing: true
        });
    });

    it('should handle CHANGE_CAPTCHA_TYPE action', () => {
        const state = {
            type: 'text'
        };
        const action = {
            type: 'CHANGE_CAPTCHA_TYPE'
        };

        let result = reducer(state, action);

        expect(result).toEqual({
            type: 'audio'
        });

        state.type = 'audio';

        result = reducer(state, action);

        expect(result).toEqual({
            type: 'text'
        });
    });

    it('should handle LOAD_CAPTCHA action', () => {
        const state = {};
        const action = {
            type: 'LOAD_CAPTCHA'
        };
        const result = reducer(state, action);

        expect(result).toEqual({
            loading: true,
            loadingAudio: true
        });
    });

    it('should handle GET_AUDIO_CAPTCHA action', () => {
        const state = {};
        const action = {
            type: 'GET_AUDIO_CAPTCHA'
        };
        const result = reducer(state, action);

        expect(result).toEqual({
            loadingAudio: true
        });
    });

    it('should handle GET_IMAGE_CAPTCHA_SUCCESS action', () => {
        const state = {};
        const action = {
            type: 'GET_IMAGE_CAPTCHA_SUCCESS',
            key: 'key',
            imageUrl: 'imageUrl'
        };
        const result = reducer(state, action);

        expect(result).toEqual({
            loading: false,
            key: 'key',
            imageUrl: 'imageUrl'
        });
    });

    it('should handle GET_AUDIO_CAPTCHA_SUCCESS action', () => {
        const state = {};
        const action = {
            type: 'GET_AUDIO_CAPTCHA_SUCCESS',
            key: 'key'
        };

        let result = reducer(state, action);

        expect(result).toEqual({
            loadingAudio: false,
            key: 'key',
            captchaSound: null
        });

        action.introSound = 'introSound';
        action.captchaSound = 'captchaSound';
        result = reducer(state, action);

        expect(result).toEqual({
            loadingAudio: false,
            key: 'key',
            captchaSound: 'captchaSound',
            introSound: 'introSound'
        });
    });

    it('should handle GET_AUDIO_CAPTCHA_FAIL action', () => {
        const state = {};
        const action = {
            type: 'GET_AUDIO_CAPTCHA_FAIL'
        };
        const result = reducer(state, action);

        expect(result).toEqual({
            loadingAudio: false
        });
    });

    it('should handle CLEAR_CAPTCHA_PROPS action', () => {
        const state = {};
        const action = {
            type: 'CLEAR_CAPTCHA_PROPS'
        };
        const result = reducer(state, action);

        expect(result).toEqual({
            loading: false,
            loadingAudio: false,
            playing: false,
            type: 'text',
            key: null,
            imageUrl: null,
            introSound: null,
            captchaSound: null,
            trackId: null
        });
    });

    it('should handle SET_CAPTCHA_TRACK action', () => {
        const state = {};
        const action = {
            type: 'SET_CAPTCHA_TRACK',
            trackId: 'trackId'
        };
        const result = reducer(state, action);

        expect(result).toEqual({
            trackId: 'trackId'
        });
    });

    it('should handle unknown action', () => {
        const state = {
            foo: 'bar'
        };
        const action = {
            type: 'UNKNOWN_ACTION'
        };
        const result = reducer(state, action);

        expect(result).toEqual({foo: 'bar'});
    });

    it('should fallback to initial state', () => {
        const result = reducer(undefined, {});

        expect(result).toEqual({});
    });
});
