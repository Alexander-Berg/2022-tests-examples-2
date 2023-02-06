import getSocial from '../getSocial';

jest.mock('../../../../common/getCustomConfigByRequest', () => () => undefined);
jest.mock('../../../../../configs/current', () => ({
    paths: {broker: 'testBrokerPath'},
    brokerParams: {}
}));

describe('passport/routes/common/getSocial.js', () => {
    it('should save providers from res.locals.socialProviders', () => {
        const mockReq = {
            _controller: {
                hasExp: (flag) => flag === 'social-provider-disable-fb-exp',
                getTld() {
                    return 'ru';
                }
            }
        };
        const mockRes = {
            locals: {
                socialProviders: {
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
                    ]
                }
            }
        };
        const mockNext = jest.fn();

        getSocial()[1](mockReq, mockRes, mockNext);

        expect(mockRes.locals.store.social.providers).toEqual([
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
        ]);
    });
});
