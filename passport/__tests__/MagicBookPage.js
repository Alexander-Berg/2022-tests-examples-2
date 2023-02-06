import React from 'react';
import {shallow} from 'enzyme';
import MagicField from '@blocks/authv2/components/MagicField/MagicField.jsx';
import {Captcha} from '@screens/Captcha';
import metrics from '@blocks/metrics';
import {MagicBookPage} from '../MagicBookPage';

jest.mock('@blocks/metrics', () => ({
    send: jest.fn()
}));

describe('@blocks/authv2/components/MagicBookPage', () => {
    const defaultProps = {
        updateMagicTokens: jest.fn(),
        magicInit: jest.fn(),
        magicRestart: jest.fn(),
        magicStop: jest.fn(),
        captchaStart: jest.fn(),
        onCaptchaCheck: jest.fn()
    };
    const getProps = (props = {}) => ({
        ...defaultProps,
        ...props
    });

    afterEach(() => {
        jest.clearAllMocks();
    });
    it('Should render MagicField on start', () => {
        const props = getProps();
        const magicBookPageComponent = shallow(<MagicBookPage {...props} />);

        expect(magicBookPageComponent.find(MagicField).length).toBe(1);
    });
    it('Should call magicInit on start', () => {
        const props = getProps({
            csrfToken: 'asd',
            trackId: 'qwe'
        });

        shallow(<MagicBookPage {...props} />);

        expect(defaultProps.magicInit).toBeCalled();
    });
    it('Should call updateMagicTokens if csrfToken or/and trackId are null', () => {
        const props = getProps();

        shallow(<MagicBookPage {...props} />);

        expect(defaultProps.updateMagicTokens).toBeCalled();
    });
    it('Should call magicInit if csrfToken or/and trackId are changed', () => {
        const props = getProps();

        const magicBookPageComponent = shallow(<MagicBookPage {...props} />);

        expect(defaultProps.magicInit).toHaveBeenCalledTimes(0);

        magicBookPageComponent.setProps(
            getProps({
                csrfToken: 'asdf',
                trackId: 'qwer'
            })
        );

        expect(defaultProps.magicInit).toHaveBeenCalledTimes(1);
    });
    it('Should render Captcha if required', () => {
        const props = getProps({
            isCaptchaRequired: true
        });
        const magicBookPageComponent = shallow(<MagicBookPage {...props} />);

        expect(magicBookPageComponent.find(Captcha).length).toBe(1);
    });
    it('Should render error', () => {
        const props = getProps({
            fieldError: 'Error message'
        });
        const magicBookPageComponent = shallow(<MagicBookPage {...props} />);

        expect(magicBookPageComponent.find('.MagicBookPage-error').length).toBe(1);
    });
    it('Should call metric.send', () => {
        const props = getProps();

        shallow(<MagicBookPage {...props} />);

        expect(metrics.send).toBeCalled();
    });
});
