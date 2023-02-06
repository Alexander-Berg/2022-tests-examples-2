import * as React from 'react';
import { shallow, mount } from 'enzyme';

import CustomMenu from './CustomMenu';

describe('CustomMenu', () => {
    it('renders', () => {
        const component = shallow(
            <CustomMenu>
                <CustomMenu.Title>Some Title</CustomMenu.Title>
                <CustomMenu.Divider />
                <CustomMenu.List>
                    <CustomMenu.Item>Some Item</CustomMenu.Item>
                    <CustomMenu.Item>
                        <CustomMenu.Section collapsed={true}>
                            Some section
                        </CustomMenu.Section>
                        <CustomMenu.Item level={1}>Inner item</CustomMenu.Item>
                        <CustomMenu.Item level={1} padding={20}>
                            Inner item with pad
                        </CustomMenu.Item>
                    </CustomMenu.Item>
                </CustomMenu.List>
            </CustomMenu>,
        );
        expect(component).toMatchSnapshot();
    });
});

describe('CustomMenu.Section', () => {
    it('renders and toggles', () => {
        const clickFn = jest.fn();
        const component = mount(
            <CustomMenu.Section onToggle={clickFn}>Section</CustomMenu.Section>,
        );

        component.find('div').forEach((wrapper) => wrapper.simulate('click'));

        expect(clickFn).toBeCalled();
    });
});
