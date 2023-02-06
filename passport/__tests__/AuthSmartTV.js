import React from 'react';
import {shallow} from 'enzyme';
import {AuthSmartTV} from '../AuthSmartTV';

describe.only('@blocks/AuthSmartTV/AuthSmartTV.jsx', () => {
    const defaultProps = {
        settings: {
            lang: 'ru',
            tld: 'ru',
            staticPath: '/st'
        },
        isNoQrScreen: false,
        retpath: '/profile',
        userCode: '123456',
        common: {
            csrf: 'qwerty'
        },
        willShowSkipButton: false,
        isSecondDesignVersion: false
    };

    beforeEach(() => {
        jest.spyOn(global, 'i18n').mockImplementation(
            (key) => (key === 'Frontend.smarttv.qr-title' && 'Title %s %s') || key
        );
    });
    afterEach(() => {
        global.i18n.mockRestore();
    });

    it('should show text for default page qr with link', () => {
        const props = {...defaultProps, isSecondDesignVersion: false};
        const authSmartTVWrapper = shallow(<AuthSmartTV {...props} />);

        expect(authSmartTVWrapper.find('.PassportSmarttv-qr .PassportSmarttv-label').html()).toMatchSnapshot();
        expect(authSmartTVWrapper.find('.PassportSmarttv-qrLabel').text()).toBe('Frontend.smarttv.qr-2fa');
        expect(
            authSmartTVWrapper
                .find('.PassportSmarttv-codeMain .PassportSmarttv-label')
                .at(0)
                .text()
        ).toBe('Frontend.smarttv.code-go-to-page');
    });
    it('should show text for ya smart TV page qr with link', () => {
        const props = {...defaultProps, isSecondDesignVersion: true};
        const authSmartTVWrapper = shallow(<AuthSmartTV {...props} />);

        expect(authSmartTVWrapper.find('.PassportSmarttv-qr .PassportSmarttv-label').length).toBe(0);
        expect(authSmartTVWrapper.find('.PassportSmarttv-qrLabel').text()).toBe('');
        expect(
            authSmartTVWrapper.find('.PassportSmarttv-codeMain .PassportSmarttv-codeLabel').text()
        ).toMatchSnapshot();
    });
});
