import {mapStateToProps} from '../mapStateToProps';

describe('pages/react/registration/app/mapStateToProps', () => {
    it.each([
        [{common: {experiments: {flags: ['passport-registration-fingerprint-exp']}}}, 'canSendFingerprint', true],
        [{common: {experiments: {flags: []}}}, 'canSendFingerprint', false],
        [{common: {experiments: {flags: ['some-other-exp']}}}, 'canSendFingerprint', false],
        [{}, 'canSendFingerprint', false]
    ])('should with state: %o return property "%s" = %o', (state, property, expected) => {
        expect(mapStateToProps(state)[property]).toEqual(expected);
    });
});
