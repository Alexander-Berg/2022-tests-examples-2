import {getSocialProviders} from '../getSocialProviders';
import {getPreparedSocialProviders} from '../getPreparedSocialProviders';

jest.mock('../getPreparedSocialProviders', () => ({
    getPreparedSocialProviders: jest.fn()
}));

describe('passport/routes/common/socialSetup/getSocialProviders.js', () => {
    const defaultSocialProviders = {
        ru: {
            providers: [
                {
                    id: 1,
                    enabled: true,
                    primary: true,
                    data: {
                        id: 1,
                        code: 'vk',
                        name: 'vkontakte',
                        display_name: {default: 'ВКонтакте'}
                    }
                },
                {
                    id: 2,
                    enabled: false,
                    primary: false,
                    data: {
                        id: 2,
                        code: 'fb',
                        name: 'facebook',
                        display_name: {default: 'Facebook'}
                    }
                }
            ],
            primary: [
                {
                    id: 1,
                    enabled: true,
                    primary: true,
                    data: {
                        id: 1,
                        code: 'vk',
                        name: 'vkontakte',
                        display_name: {default: 'ВКонтакте'}
                    }
                }
            ],
            secondary: [
                {
                    id: 2,
                    enabled: false,
                    primary: false,
                    data: {
                        id: 2,
                        code: 'fb',
                        name: 'facebook',
                        display_name: {default: 'Facebook'}
                    }
                }
            ]
        }
    };

    beforeEach(() => {
        jest.clearAllMocks();
        getPreparedSocialProviders.mockReset();
    });

    it('should do nothing if socialProviders exist', () => {
        getPreparedSocialProviders.mockReturnValueOnce(defaultSocialProviders);
        const mockReq = {
            _controller: {
                getTld: jest.fn()
            }
        };
        const mockRes = {
            locals: {
                experiments: {flags: []},
                socialProviders: {
                    providers: []
                }
            }
        };
        const mockNext = jest.fn();

        getSocialProviders(mockReq, mockRes, mockNext);

        expect(mockRes.locals.socialProviders).toEqual({
            providers: []
        });
        expect(mockReq._controller.getTld).not.toBeCalled();
    });
    it('should contain vkontakte', () => {
        getPreparedSocialProviders.mockReturnValueOnce(defaultSocialProviders);
        const mockReq = {
            _controller: {
                getTld: jest.fn().mockReturnValueOnce('ru')
            }
        };
        const mockRes = {
            locals: {
                experiments: {flags: []}
            }
        };
        const mockNext = jest.fn();

        getSocialProviders(mockReq, mockRes, mockNext);

        expect(mockRes.locals.socialProviders.providers).toContainEqual({
            id: 1,
            enabled: true,
            primary: true,
            data: {
                id: 1,
                code: 'vk',
                name: 'vkontakte',
                display_name: {default: 'ВКонтакте'}
            }
        });
        expect(mockRes.locals.socialProviders.primary).toContainEqual({
            id: 1,
            enabled: true,
            primary: true,
            data: {
                id: 1,
                code: 'vk',
                name: 'vkontakte',
                display_name: {default: 'ВКонтакте'}
            }
        });
    });
    it('should not filter facebook with social-provider-fb-exp', () => {
        getPreparedSocialProviders.mockReturnValueOnce(defaultSocialProviders);
        const mockReq = {
            _controller: {
                getTld: jest.fn().mockReturnValueOnce('ru')
            }
        };
        const mockRes = {
            locals: {
                experiments: {flags: ['social-provider-fb-exp']}
            }
        };
        const mockNext = jest.fn();

        getSocialProviders(mockReq, mockRes, mockNext);

        expect(mockRes.locals.socialProviders.providers).toContainEqual({
            id: 2,
            enabled: false,
            primary: false,
            data: {
                id: 2,
                code: 'fb',
                name: 'facebook',
                display_name: {default: 'Facebook'}
            }
        });
        expect(mockRes.locals.socialProviders.secondary).toContainEqual({
            id: 2,
            enabled: false,
            primary: false,
            data: {
                id: 2,
                code: 'fb',
                name: 'facebook',
                display_name: {default: 'Facebook'}
            }
        });
    });
    it('should filter facebook without social-provider-fb-exp', () => {
        getPreparedSocialProviders.mockReturnValueOnce(defaultSocialProviders);
        const mockReq = {
            _controller: {
                getTld: jest.fn().mockReturnValueOnce('ru')
            }
        };
        const mockRes = {
            locals: {
                experiments: {flags: []}
            }
        };
        const mockNext = jest.fn();

        getSocialProviders(mockReq, mockRes, mockNext);

        expect(mockRes.locals.socialProviders.providers).not.toContainEqual({
            id: 2,
            enabled: false,
            primary: false,
            data: {
                id: 2,
                code: 'fb',
                name: 'facebook',
                display_name: {default: 'Facebook'}
            }
        });
        expect(mockRes.locals.socialProviders.secondary).not.toContainEqual({
            id: 2,
            enabled: false,
            primary: false,
            data: {
                id: 2,
                code: 'fb',
                name: 'facebook',
                display_name: {default: 'Facebook'}
            }
        });
    });
    it('should return empty secondary for com if every providers is primary', () => {
        getPreparedSocialProviders.mockReturnValueOnce({
            com: {
                providers: [
                    {
                        id: 1,
                        enabled: true,
                        primary: true,
                        data: {
                            id: 1,
                            code: 'vk',
                            name: 'vkontakte',
                            display_name: {default: 'ВКонтакте'}
                        }
                    }
                ],
                primary: [
                    {
                        id: 1,
                        enabled: true,
                        primary: true,
                        data: {
                            id: 1,
                            code: 'vk',
                            name: 'vkontakte',
                            display_name: {default: 'ВКонтакте'}
                        }
                    }
                ]
            }
        });
        const mockReq = {
            _controller: {
                getTld: jest.fn().mockReturnValueOnce('com')
            }
        };
        const mockRes = {
            locals: {
                experiments: {flags: []}
            }
        };
        const mockNext = jest.fn();

        getSocialProviders(mockReq, mockRes, mockNext);

        expect(mockRes.locals.socialProviders.providers).toContainEqual({
            id: 1,
            enabled: true,
            primary: true,
            data: {
                id: 1,
                code: 'vk',
                name: 'vkontakte',
                display_name: {default: 'ВКонтакте'}
            }
        });
        expect(mockRes.locals.socialProviders.primary).toContainEqual({
            id: 1,
            enabled: true,
            primary: true,
            data: {
                id: 1,
                code: 'vk',
                name: 'vkontakte',
                display_name: {default: 'ВКонтакте'}
            }
        });
        expect(mockRes.locals.socialProviders.secondary).toHaveLength(0);
    });
    it('should return empty primary for kz if every providers is secondary', () => {
        getPreparedSocialProviders.mockReturnValueOnce({
            kz: {
                providers: [
                    {
                        id: 1,
                        enabled: true,
                        primary: false,
                        data: {
                            id: 1,
                            code: 'vk',
                            name: 'vkontakte',
                            display_name: {default: 'ВКонтакте'}
                        }
                    }
                ],
                secondary: [
                    {
                        id: 1,
                        enabled: true,
                        primary: false,
                        data: {
                            id: 1,
                            code: 'vk',
                            name: 'vkontakte',
                            display_name: {default: 'ВКонтакте'}
                        }
                    }
                ]
            }
        });
        const mockReq = {
            _controller: {
                getTld: jest.fn().mockReturnValueOnce('kz')
            }
        };
        const mockRes = {
            locals: {
                experiments: {flags: []}
            }
        };
        const mockNext = jest.fn();

        getSocialProviders(mockReq, mockRes, mockNext);

        expect(mockRes.locals.socialProviders.providers).toContainEqual({
            id: 1,
            enabled: true,
            primary: false,
            data: {
                id: 1,
                code: 'vk',
                name: 'vkontakte',
                display_name: {default: 'ВКонтакте'}
            }
        });
        expect(mockRes.locals.socialProviders.secondary).toContainEqual({
            id: 1,
            enabled: true,
            primary: false,
            data: {
                id: 1,
                code: 'vk',
                name: 'vkontakte',
                display_name: {default: 'ВКонтакте'}
            }
        });
        expect(mockRes.locals.socialProviders.primary).toHaveLength(0);
    });
    it('should return empty providers for new domain name', () => {
        getPreparedSocialProviders.mockReturnValueOnce({});
        const mockReq = {
            _controller: {
                getTld: jest.fn().mockReturnValueOnce('rf')
            }
        };
        const mockRes = {
            locals: {
                experiments: {flags: []}
            }
        };
        const mockNext = jest.fn();

        getSocialProviders(mockReq, mockRes, mockNext);

        expect(mockRes.locals.socialProviders.providers).toHaveLength(0);
        expect(mockRes.locals.socialProviders.secondary).toHaveLength(0);
        expect(mockRes.locals.socialProviders.primary).toHaveLength(0);
    });
});
