import {getEULATexts, isBookQREnabled} from '../selectors';

describe('Selectors', () => {
    describe('#getEULATexts', () => {
        it('should return correct eula for am[platform=ios]', () => {
            expect(
                getEULATexts({
                    am: {
                        isAm: true,
                        platform: 'ios',
                        eulaStrings: {
                            regFormat: 'test %@ hello %@',
                            userAgreementText: '1',
                            userAgreementUrl: 'ya.ru',
                            privacyPolicyText: 'world',
                            privacyPolicyUrl: 'world.ru',
                            taxiAgreementText: '',
                            taxiAgreementUrl: ''
                        }
                    }
                })
            ).toEqual(
                expect.objectContaining({
                    description: [
                        'test <a href="ya.ru" target="_blank">1</a> ',
                        'hello <a href="world.ru" target="_blank">world</a>'
                    ].join('')
                })
            );
        });

        it('should return correct eula for am[platform=android]', () => {
            expect(
                getEULATexts({
                    am: {
                        isAm: true,
                        platform: 'android',
                        eulaStrings: {
                            regFormat: 'test %1$s hello %2$s',
                            userAgreementText: '1',
                            userAgreementUrl: 'ya.ru',
                            privacyPolicyText: 'world',
                            privacyPolicyUrl: 'world.ru',
                            taxiAgreementText: '',
                            taxiAgreementUrl: ''
                        }
                    }
                })
            ).toEqual(
                expect.objectContaining({
                    description: [
                        'test <a href="ya.ru" target="_blank">1</a> ',
                        'hello <a href="world.ru" target="_blank">world</a>'
                    ].join('')
                })
            );
        });

        it('should return correct eula for am for taxi', () => {
            expect(
                getEULATexts({
                    am: {
                        isAm: true,
                        platform: 'ios',
                        eulaStrings: {
                            appType: 'taxi',
                            regFormat: 'test %@ test2 %@ hello %@',
                            userAgreementText: '1',
                            userAgreementUrl: 'ya.ru',
                            privacyPolicyText: 'world',
                            privacyPolicyUrl: 'world.ru',
                            taxiAgreementText: 'agree',
                            taxiAgreementUrl: 'agree.net'
                        }
                    }
                })
            ).toEqual(
                expect.objectContaining({
                    description: [
                        'test <a href="ya.ru" target="_blank">1</a> ',
                        'test2 <a href="agree.net" target="_blank">agree</a> ',
                        'hello <a href="world.ru" target="_blank">world</a>'
                    ].join('')
                })
            );
        });

        it('should validate eula strings', () => {
            expect(
                getEULATexts({
                    am: {
                        isAm: true,
                        platform: 'ios',
                        eulaStrings: {
                            appType: 'taxi',
                            regFormat: 'test %@ test2 %@ hello %@',
                            userAgreementText: '1',
                            userAgreementUrl: 'ya.ru',
                            privacyPolicyText: 'world',
                            privacyPolicyUrl: 'world.ru'
                        }
                    }
                })
            ).toEqual({
                button: '_AUTH_.accept.button',
                description: '_AUTH_.money.acceptance.common',
                title: '_AUTH_.acceptance.popup.title'
            });
        });

        it('should ignore am eula', () => {
            expect(
                getEULATexts({
                    am: {
                        isAm: true,
                        platform: 'ios'
                    }
                })
            ).toEqual({
                button: '_AUTH_.accept.button',
                description: '_AUTH_.money.acceptance.common',
                title: '_AUTH_.acceptance.popup.title'
            });
        });
    });
    describe('isBookQREnabled', () => {
        it.each([
            [{router: {location: {pathname: '/auth'}}, auth: {isBookQREnabled: true}}, true],
            [{router: {location: {pathname: '/auth/add'}}, auth: {isBookQREnabled: true}}, true],
            [{router: {location: {pathname: '/auth/list'}}, auth: {isBookQREnabled: true}}, false],
            [{router: {location: {pathname: '/profile'}}, auth: {isBookQREnabled: true}}, false],
            [{router: {location: {pathname: '/auth'}}, auth: {isBookQREnabled: false}}, false],
            [{router: {location: {pathname: '/auth/add'}}, auth: {isBookQREnabled: false}}, false],
            [{router: {location: {pathname: '/auth/list'}}, auth: {isBookQREnabled: false}}, false],
            [{router: {location: {pathname: '/profile'}}, auth: {isBookQREnabled: false}}, false],
            [{router: {location: {}}, auth: {isBookQREnabled: false}}, false],
            [{router: {}, auth: {isBookQREnabled: false}}, false],
            [{auth: {isBookQREnabled: false}}, false],
            [{router: {location: {}}, auth: {isBookQREnabled: true}}, false],
            [{router: {}, auth: {isBookQREnabled: true}}, false],
            [{auth: {isBookQREnabled: true}}, false],
            [{router: {location: {pathname: '/auth/add'}}}, false],
            [{router: {location: {pathname: '/auth/add'}}, auth: {}}, false]
        ])('should return correct result for state: %s expected: %s', (state, expected) => {
            expect(isBookQREnabled(state)).toEqual(expected);
        });
    });
});
