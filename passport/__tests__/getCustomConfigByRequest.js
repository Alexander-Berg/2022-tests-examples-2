import getCustomConfigByRequest from '../getCustomConfigByRequest';

let req = {};

jest.mock('../getCustomConfig', () =>
    jest.fn().mockImplementation(
        (path) =>
            ({
                'customs.config.json': {
                    testStandardOrigin: {
                        bgNumber: 800
                    },
                    music: {
                        bgNumber: 100
                    },
                    cmnt_reply_open: {
                        bgNumber: 200
                    },
                    testAdditionalOrigin: {
                        socialExtended: true,
                        bgNumber: 123,
                        authModeMap: {
                            edit: 'register',
                            welcome: 'register',
                            addingAccount: 'register'
                        }
                    },
                    testAdditionalOrigin2: {
                        bgNumber: 123,
                        authModeMap: {
                            edit: 'add-user',
                            welcome: 'add-user',
                            addingAccount: 'add-user'
                        }
                    }
                },
                'additional-customs.config.json': [
                    {
                        origins: ['testAdditionalOrigin', 'testAdditionalOrigin2'],
                        config: {bgNumber: 300, authModeMap: {edit: 'add-user'}}
                    },
                    {
                        origins: ['testAdditionalOrigin', 'testAdditionalOriginWithoutNormalConfig'],
                        config: {providers: ['tw']}
                    }
                ],
                'customs.js': {
                    originMatcher: /^(music|cmnt)_?/,
                    originMatcherCmnt: /^cmnt_[^_]+_((reply|reaction)_open)-passport/,
                    domainToOriginMap: {
                        'passport.yandex.ru': 'music'
                    }
                }
            }[path])
    )
);

describe('passport/routes/common/getCustomConfigByRequest.js', () => {
    beforeEach(() => {
        jest.clearAllMocks();
        req = {
            _controller: {
                getUrl() {
                    return {
                        hostname: ''
                    };
                }
            },
            query: {
                origin: ''
            },
            body: {
                origin: ''
            }
        };
    });
    'should return undefined if origin is not String or not exist',
        () => {
            expect(getCustomConfigByRequest()).toEqual(undefined);
        };
    it.each([
        [undefined, undefined],
        [123, undefined],
        [{}, undefined],
        [[], undefined],
        [null, undefined],
        [NaN, undefined],
        ['configNotExist', undefined]
    ])('should for origin %s return %s', (origin, expected) => {
        req.query.origin = origin;
        expect(getCustomConfigByRequest(req)).toEqual(expected);
    });
    it('should return standard config if origin is testStandardOrigin', () => {
        req.query.origin = 'testStandardOrigin';
        expect(getCustomConfigByRequest(req)).toEqual({
            bgNumber: 800
        });
    });
    it('should return music config if origin is music_test', () => {
        req.query.origin = 'music_test';
        expect(getCustomConfigByRequest(req)).toEqual({
            bgNumber: 100
        });
    });
    it('should return cmnt_reply_open config if origin is cmnt_music_reply_open-passport', () => {
        req.query.origin = 'cmnt_music_reply_open-passport';
        expect(getCustomConfigByRequest(req)).toEqual({
            bgNumber: 200
        });
    });
    it.each([
        [
            'testAdditionalOrigin',
            {
                socialExtended: true,
                bgNumber: 300,
                authModeMap: {
                    edit: 'add-user',
                    welcome: 'register',
                    addingAccount: 'register'
                },
                providers: ['tw']
            }
        ],
        [
            'testAdditionalOrigin2',
            {
                bgNumber: 300,
                authModeMap: {
                    edit: 'add-user',
                    welcome: 'add-user',
                    addingAccount: 'add-user'
                }
            }
        ],
        [
            'testAdditionalOriginWithoutNormalConfig',
            {
                providers: ['tw']
            }
        ]
    ])('should for origin %s return config %o', (origin, expectedConfig) => {
        req.query.origin = origin;
        expect(getCustomConfigByRequest(req)).toEqual(expectedConfig);
    });
    it('should return music config if domain is passport.yandex.ru', () => {
        req = {
            _controller: {
                getUrl() {
                    return {
                        hostname: 'passport.yandex.ru'
                    };
                }
            }
        };
        expect(getCustomConfigByRequest(req)).toEqual({
            bgNumber: 100
        });
    });
});
