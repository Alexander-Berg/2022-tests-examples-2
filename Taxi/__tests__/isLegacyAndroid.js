import isLegacyAndroid from '../isLegacyAndroid';

describe('isLegacyAndroid predicate', () => {
    it('Should be detect only android platform', () => {
        const requestStub = {
            uatraits: {
                OSFamily: 'iOS',
                OSVersion: '9'
            }
        };

        expect(isLegacyAndroid()(requestStub)).toBeFalsy();
        expect(isLegacyAndroid({minimalVersion: '10'})(requestStub)).toBeFalsy();
    });

    it('Should be return true if minimalVersion > detect os version', () => {
        const requestStub = {
            uatraits: {
                OSFamily: 'Android',
                OSVersion: '6.0'
            }
        };

        expect(isLegacyAndroid({minimalVersion: '9'})(requestStub)).toBeTruthy();
        expect(isLegacyAndroid({minimalVersion: '6.1'})(requestStub)).toBeTruthy();
        expect(isLegacyAndroid({minimalVersion: '6.1.0'})(requestStub)).toBeTruthy();
    });

    it('Should be return true if os version is invalid', () => {
        const requestStub = {
            uatraits: {
                OSFamily: 'Android',
                OSVersion: 'invalid version'
            }
        };

        expect(isLegacyAndroid()(requestStub)).toBeTruthy();
    });

    it('Should be return false if minimalVersion <= detect os version', () => {
        const requestStub = {
            uatraits: {
                OSFamily: 'Android',
                OSVersion: '6.0'
            }
        };

        expect(isLegacyAndroid({minimalVersion: '5'})(requestStub)).toBeFalsy();
        expect(isLegacyAndroid({minimalVersion: '6'})(requestStub)).toBeFalsy();
        expect(isLegacyAndroid({minimalVersion: '6.0'})(requestStub)).toBeFalsy();
        expect(isLegacyAndroid({minimalVersion: '6.0.0'})(requestStub)).toBeFalsy();
    });

    it('Should throw error if minimal version is invalid', () => {
        expect(() => {
            isLegacyAndroid({minimalVersion: 'invalid version'})();
        }).toThrow();
        expect(() => {
            isLegacyAndroid({minimalVersion: null})();
        }).toThrow();
    });

    it('Should throw error if missing express-http-uatratis', () => {
        expect(() => {
            isLegacyAndroid()({});
        }).toThrow();
    });
});
