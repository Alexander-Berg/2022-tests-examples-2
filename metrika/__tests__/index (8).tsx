import { mount } from 'enzyme';
import * as React from 'react';

import { Button } from 'lego';
import { MetrikaModal } from '..';

const StatefullModal = () => {
    const [visisble, setVisibility] = React.useState(true);
    return (
        <MetrikaModal
            visible={visisble}
            closable={true}
            onCloseButtonClick={() => setVisibility(false)}
        >
            content
        </MetrikaModal>
    );
};

describe('ClosableModal', () => {
    it('hide by click on close icon', () => {
        const wrapper = mount(<StatefullModal />);

        wrapper.find(Button).simulate('click');
        expect(wrapper.find(MetrikaModal).prop('visible')).toBe(false);
    });
});
