import React from 'react';
import {shallow, mount} from 'enzyme';
import Tabs from '../Tabs';
import Tab from '../Tab';

describe('Components/tabs', () => {
    it('Если есть параметр className - то применяется соответствующий класс', () => {
        const customClassName = 'customClass';
        const wrapper = shallow(
            <Tabs className={customClassName}>
                <Tab tabname={<span>Таб 1</span>}>
                    <p>Контент таба 1</p>
                </Tab>
                <Tab tabname={<span>Таб 2</span>}>
                    <p>Контент таба 2</p>
                </Tab>
                <Tab tabname="Таб 3" disabled>
                    <p>Контент таба 3</p>
                </Tab>
                <Tab tabname={<b>Таб 4</b>} disabled active>
                    <p>Контент таба 4</p>
                </Tab>
            </Tabs>
        );
        expect(wrapper.prop('className')).toContain(customClassName);
    });

    it('Если есть параметр defaultActiveTabIndex - то активен соответствующий таб', () => {
        const activeTabIndex = 1;
        const wrapper = shallow(
            <Tabs defaultActiveTabIndex={activeTabIndex}>
                <Tab tabname={<span>Таб 1</span>}>
                    <p>Контент таба 1</p>
                </Tab>
                <Tab tabname={<span>Таб 2</span>}>
                    <p>Контент таба 2</p>
                </Tab>
                <Tab tabname={<span>Таб 3</span>}>
                    <p>Контент таба 3</p>
                </Tab>
            </Tabs>
        );

        expect(wrapper.state('activeTabIndex')).toBe(activeTabIndex);
        expect(
            wrapper
                .find(Tab)
                .at(activeTabIndex)
                .prop('active')
        ).toBeTruthy();
    });

    describe('Tabs:onChange', () => {
        const activeTabIndex = 1;
        const onChange = jest.fn();
        const wrapper = mount(
            <Tabs defaultActiveTabIndex={activeTabIndex} onChange={onChange}>
                <Tab tabname="tab 1">
                    <p>Контент таба 1</p>
                </Tab>
                <Tab tabname="tab 2">
                    <p>Контент таба 2</p>
                </Tab>
                <Tab tabname="tab 3">
                    <p>Контент таба 3</p>
                </Tab>
            </Tabs>
        );

        it('`onChange` should not be called on a click on the current `Tab`', () => {
            wrapper
                .find(Tab)
                .at(activeTabIndex)
                .simulate('click');
            expect(onChange.mock.calls.length).toBe(0);
        });

        it('`onChange` should be called with active tab index', () => {
            wrapper
                .find(Tab)
                .at(0)
                .simulate('click');
            expect(onChange.mock.calls.length).toBe(1);
            expect(onChange.mock.calls[0][0]).toBe(0);
        });
    });
});
