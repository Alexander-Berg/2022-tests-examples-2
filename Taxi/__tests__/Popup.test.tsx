import React from 'react';
import {Popper} from 'react-popper';
import {mount, shallow} from 'enzyme';

import Popup from '../../popup/Popup';
import PopupContent from '../../popup/PopupContent';

const PopupChildren = 'PopupContent';

describe('Components/popup', () => {
    it('Если не передать referenceElement, то ничего не рендерит', () => {
        const wrapper = shallow(
            <Popup referenceElement={null}>
                {PopupChildren}
            </Popup>
        );

        expect(wrapper.find(Popper).exists()).toBeFalsy();
    });

    it('Рендерит внутри себя Popper и PopupContent', () => {
        const wrapper = mount(
            <Popup referenceElement={{} as any}>
                {PopupChildren}
            </Popup>
        );

        expect(wrapper.find(Popper).exists()).toBeTruthy();
        expect(wrapper.find(PopupContent).exists()).toBeTruthy();
    });

    it('Можно прокинуть style на PopupContent', () => {
        const style = {width: 100};
        const wrapper = mount(
            <Popup style={style} referenceElement={{} as any}>
                {PopupChildren}
            </Popup>
        );

        expect(wrapper.find(PopupContent).prop('style')).toHaveProperty('width');
    });
});
