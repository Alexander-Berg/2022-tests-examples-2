import React from 'react';
import {shallow} from 'enzyme';
import {EulaPopup} from '../desktop/eula/EulaPopup.jsx';

const sendDataFn = jest.fn();

describe('EulaPopup', () => {
    it('should be visible when isEulaConfirmPopupShow prop is true', () => {
        const wrapper = shallow(
            <EulaPopup
                sendData={sendDataFn}
                isMobile={false}
                isEulaConfirmPopupShow={true}
                method='phone'
                isPDDRegistration={false}
            />
        );

        expect(wrapper.find('.eula-popup__show').length).toBe(1);
    });
    it('should not be visible when isEulaConfirmPopupShow prop is false', () => {
        const wrapper = shallow(
            <EulaPopup
                sendData={sendDataFn}
                isMobile={false}
                isEulaConfirmPopupShow={false}
                method='phone'
                isPDDRegistration={false}
            />
        );

        expect(wrapper.find('.eula-popup__show').length).toBe(0);
    });
    it('should have close method', () => {
        const wrapper = shallow(
            <EulaPopup
                sendData={sendDataFn}
                isMobile={false}
                isEulaConfirmPopupShow={false}
                method='phone'
                isPDDRegistration={false}
            />
        );

        expect(wrapper.instance().close).toBeDefined();
    });
});
