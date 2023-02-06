import React from 'react';
import {mount} from 'enzyme';
import {QrSecureAuth} from '../QrSecureAuth';

jest.mock('@components/CustomsBackground', () => ({
    CustomsBackground: () => null
}));

describe('QrSecureAuth component', () => {
    const props = {
        settings: {
            tld: 'ru'
        },
        am: {
            isAm: true
        },
        name: 'name',
        avatarLink: 'avatarLink',
        qrSecureAuth: {
            browser: 'browser',
            osFamily: 'os',
            regionName: 'region',
            deviceName: 'device',
            isAuthPrepareWithCredError: false,
            isLoading: false,
            error: null,
            isShowSuccessScreen: false,
            isTrackError: false
        },
        chooseAccount: jest.fn(),
        primaryActionTriggered: jest.fn(),
        setPopupSize: jest.fn(),
        hasUnitedAccounts: true,
        isAccountError: false,
        authPrepareWithCred: jest.fn(),
        authHref: 'href'
    };

    it('should render error with account error', () => {
        const wrapper = mount(<QrSecureAuth {...props} />);

        wrapper.setProps({isAccountError: true});

        const errorButton = wrapper.find('.QrSecureAuth-errorButton');

        expect(errorButton.length).toBe(1);
    });

    it('should render error with track error', () => {
        const wrapper = mount(<QrSecureAuth {...props} />);

        wrapper.setProps({qrSecureAuth: {...props.qrSecureAuth, isAuthPrepareWithCredError: true}});

        const errorButton = wrapper.find('.QrSecureAuth-errorButton');

        expect(errorButton.length).toBe(1);
    });

    it('should render error with submit error', () => {
        const wrapper = mount(<QrSecureAuth {...props} />);

        wrapper.setProps({qrSecureAuth: {...props.qrSecureAuth, isTrackError: true}});

        const errorButton = wrapper.find('.QrSecureAuth-errorButton');

        expect(errorButton.length).toBe(1);
    });

    it('should render card with submit buttons', () => {
        const wrapper = mount(<QrSecureAuth {...props} />);

        const submitButton = wrapper.find('.QrSecureAuth-submitButton');
        const carouselButton = wrapper.find('.QrSecureAuth-carouselButton');

        expect(carouselButton.length).toBe(1);
        expect(submitButton.length).toBe(1);
    });

    it('should render success', () => {
        const wrapper = mount(<QrSecureAuth {...props} />);

        wrapper.setProps({qrSecureAuth: {...props.qrSecureAuth, isShowSuccessScreen: true}});

        const successButton = wrapper.find('.QrSecureAuth-successButton');

        expect(successButton.length).toBe(1);
    });

    it('should render card without close button', () => {
        const wrapper = mount(<QrSecureAuth {...props} />);

        wrapper.setProps({am: {...props.am, isAm: false}});

        const closeButton = wrapper.find('.QrSecureAuth-close');

        expect(closeButton.length).toBe(0);
    });

    it('should renders with loader', () => {
        const wrapper = mount(<QrSecureAuth {...props} />);

        wrapper.setProps({qrSecureAuth: {...props.qrSecureAuth, isLoading: true}});

        const loaderOveraly = wrapper.find('.QrSecureAuth-loaderOverlay');
        const spin = wrapper.find('.QrSecureAuth-loader');

        expect(loaderOveraly.length).toBe(1);
        expect(spin.length).toBe(1);
    });
});
