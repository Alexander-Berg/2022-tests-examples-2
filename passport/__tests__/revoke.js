import * as extracted from '../revoke.js';

jest.mock('../../../../../metrics', () => ({
    send: jest.fn()
}));

describe('Morda.Forms.Password.Revoke', () => {
    let obj = null;

    beforeEach(() => {
        obj = {
            state: {
                data: {
                    revoke_other_yandex_tokens: true,
                    revoke_other_tokens: true,
                    tokens: [1, 2],
                    passTokens: [3, 4]
                }
            },
            props: {
                dispath: jest.fn(),
                revokers: {
                    revoke_app_passwords: false,
                    revoke_tokens: false,
                    revoke_web_sessions: false,
                    tokens: [{token: 1}, {token: 2}],
                    passTokens: [{token: 3}, {token: 4}],
                    otherTokens: [5, 6, 7]
                }
            }
        };
        obj.setState = jest.fn((any) => {
            obj.state = Object.assign({}, obj.state, typeof any === 'function' ? any(obj.state) : any);
        });
    });

    describe('sendData', () => {
        it('should call sendData', () => {
            obj.props.sendData = jest.fn();

            extracted.sendData.call(obj);
            expect(obj.props.sendData).toHaveBeenCalledTimes(1);
            expect(obj.props.sendData).toHaveBeenCalledWith(obj.state.data);
        });
    });

    describe('handleDefaults', () => {
        it('should toggle state revoke_web_sessions', () => {
            extracted.handleDefaults.call(obj, 'revoke_web_sessions');
            expect(obj.setState).toHaveBeenCalledTimes(1);
            expect(obj.state.data.revoke_web_sessions).toBe(true);
        });
        it('should toggle state revoke_tokens and set tokens', () => {
            extracted.handleDefaults.call(obj, 'revoke_tokens');
            expect(obj.setState).toHaveBeenCalledTimes(1);
            expect(obj.state.data.revoke_tokens).toBe(true);
            expect(obj.state.data.tokens).toEqual([1, 2]);
        });
        it('should toggle state revoke_app_passwords and set passTokens', () => {
            extracted.handleDefaults.call(obj, 'revoke_app_passwords');
            expect(obj.setState).toHaveBeenCalledTimes(1);
            expect(obj.state.data.revoke_app_passwords).toBe(true);
            expect(obj.state.data.passTokens).toEqual([3, 4]);
        });
        it('should clear tokens', () => {
            obj.state.data.revoke_tokens = true;
            extracted.handleDefaults.call(obj, 'revoke_tokens');
            expect(obj.setState).toHaveBeenCalledTimes(1);
            expect(obj.state.data.tokens.length).toBe(0);
        });
        it('should clear passTokens', () => {
            obj.state.data.revoke_app_passwords = true;
            extracted.handleDefaults.call(obj, 'revoke_app_passwords');
            expect(obj.setState).toHaveBeenCalledTimes(1);
            expect(obj.state.data.passTokens.length).toBe(0);
        });
        it('should not change state', () => {
            const state = Object.assign({}, obj.state);

            extracted.handleDefaults.call(obj, 'wrong_key');
            expect(obj.setState).toHaveBeenCalledTimes(1);
            expect(obj.state).toEqual(state);
        });
    });

    describe('handleDeviceToken', () => {
        it('should set remove token', () => {
            obj.state.data.tokens = [1];
            extracted.handleDeviceToken.call(obj, 2);
            expect(obj.state.data.revoke_tokens).toBe(true);
            expect(obj.state.data.tokens[1]).toBe(2);
        });
        it('should add token', () => {
            obj.state.data.tokens = [1];
            extracted.handleDeviceToken.call(obj, 1);
            expect(obj.state.data.revoke_tokens).toBe(false);
            expect(obj.state.data.tokens.length).toBe(0);
        });
    });

    describe('handlePassToken', () => {
        it('should set remove token', () => {
            obj.state.data.passTokens = [1];
            extracted.handlePassToken.call(obj, 2);
            expect(obj.state.data.revoke_app_passwords).toBe(true);
            expect(obj.state.data.passTokens[1]).toBe(2);
        });
        it('should add token', () => {
            obj.state.data.passTokens = [1];
            extracted.handlePassToken.call(obj, 1);
            expect(obj.state.data.revoke_app_passwords).toBe(false);
            expect(obj.state.data.passTokens.length).toBe(0);
        });
    });
});
