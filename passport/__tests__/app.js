import React from 'react';
import {shallow} from 'enzyme';
import {App} from '../App';

describe('pages/react/registration/app/app', () => {
    const getProps = (props = {}) => ({
        sendFingerprint: jest.fn(),
        canSendFingerprint: true,
        ...props
    });

    afterEach(() => {
        jest.clearAllMocks();
    });
    it('should call sendFingerprint if canSendFingerprint is true', () => {
        const props = getProps({
            canSendFingerprint: true
        });

        shallow(<App {...props} />);

        expect(props.sendFingerprint).toBeCalled();
    });
    it('should not call sendFingerprint if canSendFingerprint is false', () => {
        const props = getProps({
            canSendFingerprint: false
        });

        shallow(<App {...props} />);

        expect(props.sendFingerprint).not.toBeCalled();
    });
});
