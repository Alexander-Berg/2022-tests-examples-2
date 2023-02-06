import sendApiRequest from '../../actions/send_api_request';
import skipAdditionalData from '../../actions/skip_additional_data';
import setSocialProfileAuth from '../../actions/set_social_profile_auth';
import sendMetrics from '../../actions/send_metrics';
import broker from '../../../authorized_broker';
import {
    goBack,
    allowSocialAuth,
    addSocialProfile,
    filterProvidersListByTLD,
    getSocialUserName
} from '../request_social.js';

jest.mock('../../actions/send_api_request');
jest.mock('../../actions/skip_additional_data');
jest.mock('../../actions/set_social_profile_auth');
jest.mock('../../actions/send_metrics');
jest.mock('../../../authorized_broker', () => ({
    start: jest.fn()
}));

const props = {
    dispatch: jest.fn()
};

const preventDefault = jest.fn();

describe('Component: RequestSocial', () => {
    beforeEach(() => {
        sendApiRequest.mockImplementation(() => () => {});
        skipAdditionalData.mockImplementation(() => () => {});
        setSocialProfileAuth.mockImplementation(() => () => {});
        sendMetrics.mockImplementation(() => () => {});
    });

    afterEach(() => {
        sendApiRequest.mockClear();
        skipAdditionalData.mockClear();
        setSocialProfileAuth.mockClear();
        sendMetrics.mockClear();
        preventDefault.mockClear();
        props.dispatch.mockClear();
    });

    it('should dispatch sendApiRequest action with skipAdditionalData action in args', () => {
        goBack.call({props});

        expect(props.dispatch).toBeCalled();
        expect(sendApiRequest).toBeCalledWith(skipAdditionalData);
    });

    it('should dispatch sendApiRequest action with setSocialProfileAuth action in args', () => {
        allowSocialAuth.call({props}, {preventDefault});

        expect(props.dispatch).toBeCalled();
        expect(preventDefault).toBeCalled();
        expect(sendApiRequest).toBeCalledWith(setSocialProfileAuth);
    });

    it('should call broker start with valid params', () => {
        const brokerParams = {
            provider: {provider_id: '123'},
            bind: 1,
            return_brief_profile: 1
        };

        addSocialProfile.call({props}, brokerParams.provider);

        expect(props.dispatch).toBeCalled();
        expect(sendMetrics).toBeCalled();
        expect(broker.start).toBeCalledWith(brokerParams);
    });

    it('should filter providers list with fb code', () => {
        const providers = [
            {
                data: {
                    code: 'fb',
                    display_name: {
                        ru: 'ru_name'
                    }
                }
            },
            {
                data: {code: 'ok'}
            }
        ];
        const tld = 'ru';
        const lang = 'ru';

        const providersList = filterProvidersListByTLD.call(null, providers, tld, lang);

        expect(providersList).toEqual([
            Object.assign({}, providers[0].data, {display_name: providers[0].data.display_name.ru})
        ]);
    });

    it('should filter providers list with vk code for KUBR', () => {
        const providers = [
            {
                data: {
                    code: 'vk',
                    display_name: {
                        ru: 'ru_name'
                    }
                }
            },
            {
                data: {code: 'ok'}
            }
        ];
        const tld = 'ru';
        const lang = 'ru';

        const providersList = filterProvidersListByTLD.call(null, providers, tld, lang);

        expect(providersList).toEqual([
            Object.assign({}, providers[0].data, {display_name: providers[0].data.display_name.ru})
        ]);
    });

    it('should filter providers list with gg code for not KUBR and ignore vk code for KUBR', () => {
        const providers = [
            {
                data: {
                    code: 'gg',
                    display_name: {
                        ru: 'ru_name'
                    }
                }
            },
            {
                data: {
                    code: 'vk',
                    display_name: {
                        ru: 'ru_name'
                    }
                }
            },
            {
                data: {code: 'ok'}
            }
        ];
        const tld = 'com';
        const lang = 'ru';

        const providersList = filterProvidersListByTLD.call(null, providers, tld, lang);

        expect(providersList).toEqual([
            Object.assign({}, providers[0].data, {display_name: providers[0].data.display_name.ru})
        ]);
    });

    it('should filter providers list with default social name', () => {
        const providers = [
            {
                data: {
                    code: 'fb',
                    display_name: {
                        en: 'en_name',
                        default: 'default_name'
                    }
                }
            },
            {
                data: {code: 'ok'}
            }
        ];
        const tld = 'ru';
        const lang = 'ru';

        const providersList = filterProvidersListByTLD.call(null, providers, tld, lang);

        expect(providersList).toEqual([
            Object.assign({}, providers[0].data, {display_name: providers[0].data.display_name.default})
        ]);
    });

    it('should return social user name with firstname and lastname', () => {
        const social = {
            firstname: 'Jon',
            lastname: 'Snow',
            username: 'jony snowchik',
            userid: '322'
        };

        const socialUserName = getSocialUserName(social);

        expect(socialUserName).toBe(`${social.firstname} ${social.lastname}`.trim());
    });

    it('should return social user name with username field', () => {
        const social = {
            firstname: '',
            lastname: '',
            username: 'jony snowchik',
            userid: '322'
        };

        const socialUserName = getSocialUserName(social);

        expect(socialUserName).toBe(social.username);
    });

    it('should return social user name with userid field', () => {
        const social = {
            firstname: '',
            lastname: '',
            username: '',
            userid: '322'
        };

        const socialUserName = getSocialUserName(social);

        expect(socialUserName).toBe(social.userid);
    });

    it('should return empty social user name for empty social data', () => {
        const socialUserName = getSocialUserName(null);

        expect(socialUserName).toBe('');
    });

    it('should return empty social user name for social data without params', () => {
        const socialUserName = getSocialUserName({});

        expect(socialUserName).toBe('');
    });
});
