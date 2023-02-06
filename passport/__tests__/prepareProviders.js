import {prepareProviders} from '../prepareProviders';

describe('passport/routes/common/socialSetup/prepareProviders.js', () => {
    it('should return same tld objects', () => {
        const result = prepareProviders(
            {
                domains: [
                    {tld: 'az', providers: []},
                    {tld: 'com', providers: []},
                    {tld: 'ru', providers: []}
                ]
            },
            'production'
        );

        expect(result).toEqual({az: {}, com: {}, ru: {}});
    });
    it('should filter disabled providers in production', () => {
        const result = prepareProviders(
            {
                providers: [
                    {id: 1, code: 'vk', name: 'vkontakte', display_name: {default: 'ВКонтакте'}},
                    {id: 2, code: 'fb', name: 'facebook', display_name: {default: 'Facebook'}}
                ],
                domains: [
                    {
                        tld: 'ru',
                        providers: [
                            {id: 1, enabled: true, primary: false},
                            {id: 2, enabled: false, primary: false}
                        ]
                    }
                ]
            },
            'production'
        );

        expect(result).toEqual({
            ru: {
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
    });
    it('should not filter disabled providers in testing', () => {
        const result = prepareProviders(
            {
                providers: [
                    {id: 1, code: 'vk', name: 'vkontakte', display_name: {default: 'ВКонтакте'}},
                    {id: 2, code: 'fb', name: 'facebook', display_name: {default: 'Facebook'}}
                ],
                domains: [
                    {
                        tld: 'ru',
                        providers: [
                            {id: 1, enabled: true, primary: false},
                            {id: 2, enabled: false, primary: false}
                        ]
                    }
                ]
            },
            'testing'
        );

        expect(result).toEqual({
            ru: {
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
                ]
            }
        });
    });
    it('should not filter disabled providers in development', () => {
        const result = prepareProviders(
            {
                providers: [
                    {id: 1, code: 'vk', name: 'vkontakte', display_name: {default: 'ВКонтакте'}},
                    {id: 2, code: 'fb', name: 'facebook', display_name: {default: 'Facebook'}}
                ],
                domains: [
                    {
                        tld: 'ru',
                        providers: [
                            {id: 1, enabled: true, primary: true},
                            {id: 2, enabled: false, primary: false}
                        ]
                    }
                ]
            },
            'development'
        );

        expect(result).toEqual({
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
        });
    });
    it('should copy provider to primary if it property = true', () => {
        const result = prepareProviders(
            {
                providers: [
                    {id: 1, code: 'vk', name: 'vkontakte', display_name: {default: 'ВКонтакте'}},
                    {id: 2, code: 'fb', name: 'facebook', display_name: {default: 'Facebook'}}
                ],
                domains: [
                    {
                        tld: 'ru',
                        providers: [
                            {id: 1, enabled: true, primary: true},
                            {id: 2, enabled: true, primary: true}
                        ]
                    }
                ]
            },
            'development'
        );

        expect(result).toEqual({
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
                        enabled: true,
                        primary: true,
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
                    },
                    {
                        id: 2,
                        enabled: true,
                        primary: true,
                        data: {
                            id: 2,
                            code: 'fb',
                            name: 'facebook',
                            display_name: {default: 'Facebook'}
                        }
                    }
                ]
            }
        });
    });
    it('should copy provider to secondary if it property = false', () => {
        const result = prepareProviders(
            {
                providers: [
                    {id: 1, code: 'vk', name: 'vkontakte', display_name: {default: 'ВКонтакте'}},
                    {id: 2, code: 'fb', name: 'facebook', display_name: {default: 'Facebook'}}
                ],
                domains: [
                    {
                        tld: 'ru',
                        providers: [
                            {id: 1, enabled: true, primary: false},
                            {id: 2, enabled: true, primary: false}
                        ]
                    }
                ]
            },
            'development'
        );

        expect(result).toEqual({
            ru: {
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
                    },
                    {
                        id: 2,
                        enabled: true,
                        primary: false,
                        data: {
                            id: 2,
                            code: 'fb',
                            name: 'facebook',
                            display_name: {default: 'Facebook'}
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
                    },
                    {
                        id: 2,
                        enabled: true,
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
        });
    });
});
