/* eslint-disable max-len */
import React from 'react';
import DatePicker from '@yandex-taxi/corp-core/ui/DatePicker';
import {Time} from '@yandex-taxi/corp-ui/form';

import {mount} from 'enzyme';
import MockDate from 'mockdate';

import RadioButtonItem from 'amber-blocks/radio-button/item';

import {
    withMockConfigProvider,
    withMockI18n,
    withMockI18nProvider,
} from '../../../../../../tests/utils/hoc';

import {b as CustomDateAndTimeB} from './CustomDateAndTimePopup';
import OrderTime from './index';
import Popup from './Popup';

describe('OrderTime', () => {
    const EnhancedOrderTime = withMockConfigProvider({
        maxPermissibleDate: Date.now(),
    })(withMockI18nProvider()(withMockI18n()(OrderTime)));

    const createMockedProps = () => ({
        onSelectCustom: jest.fn(),
        onSelectDue: jest.fn(),
    });

    afterEach(() => MockDate.reset());

    it('показывается в дефолтном виде', async () => {
        const handlers = createMockedProps();
        const wrapper = await mount(<EnhancedOrderTime {...handlers} />);
        expect(handlers.onSelectCustom).not.toHaveBeenCalled();
        expect(handlers.onSelectDue).not.toHaveBeenCalled();

        expect(wrapper).toMatchSnapshot();
    });

    const clickCustomTime = wrapper => {
        const selectWrapper = wrapper.find('.Select-control');
        expect(selectWrapper.length).toBe(1);
        selectWrapper.simulate('mousedown', {button: 0});
        expect(wrapper.find('.Select-menu-outer').length).toBe(1);
        wrapper.find('.Select-option:last-child').simulate('mousedown', {button: 0});
    };

    it('должен позволять выбрать кастомную дату', async () => {
        MockDate.set('2019-03-14 12:00:00');
        const handlers = createMockedProps();
        const wrapper = mount(
            <EnhancedOrderTime day={3} time="16:25" zoneUTCOffset="+0300" {...handlers} />,
        );
        expect(wrapper).toMatchSnapshot();
        clickCustomTime(wrapper);
        const dayPopup = wrapper.find(Popup);
        expect(dayPopup.length).toBe(1);
        const radioOptions = dayPopup.find(RadioButtonItem);
        expect(radioOptions.length).toBe(4);
        expect(wrapper).toMatchSnapshot();
        radioOptions.last().find('input').simulate('change', {value: 'custom'});
        expect(wrapper.find(Popup).length).toBe(1);
        const popup = wrapper.find(Popup);
        expect(popup.find(DatePicker).length).toBe(1);
        // expect(wrapper).toMatchSnapshot();
    });

    const inputTime = (wrapper, time) => {
        const dayPopup = wrapper.find(Popup);
        expect(dayPopup.length).toBe(1);
        wrapper.find(Time).prop('onChange')(time);
    };

    it('при выборе опции "через десять минут" должно происходить событие', () => {
        const handlers = createMockedProps();
        const wrapper = mount(
            <EnhancedOrderTime zoneUTCOffset="+0300" time="14:41" {...handlers} />,
        );
        const selectWrapper = wrapper.find('.Select-control');
        expect(selectWrapper.length).toBe(1);
        selectWrapper.simulate('mousedown', {button: 0});
        expect(wrapper.find('.Select-menu-outer').length).toBe(1);
        wrapper.find('Option').at(1).simulate('mousedown', {button: 0});
        expect(handlers.onSelectDue).toHaveBeenCalledWith(10);
        expect(selectWrapper.length).toBe(1);
        selectWrapper.simulate('mousedown', {button: 0});
        wrapper.find('Option').at(2).simulate('mousedown', {button: 0});
        expect(handlers.onSelectDue).toHaveBeenCalledWith(15);
    });

    it('при открытии кастомной даты выбирается переданное время', () => {
        MockDate.set('2019-03-14 16:01:00', -300);
        const handlers = createMockedProps();
        const wrapper = mount(
            <EnhancedOrderTime zoneUTCOffset="+0300" time="14:41" {...handlers} />,
        );
        clickCustomTime(wrapper);
        wrapper.update();
        const timeInput = wrapper.find('TimeInput');
        expect(timeInput.prop('value')).toBe('14:41');
    });

    it('дата в прошлом превращается в текущее время', () => {
        MockDate.set('2019-03-14 16:01:00', -300);
        const dateInPast = '14:00';
        const handlers = createMockedProps();
        const wrapper = mount(<EnhancedOrderTime zoneUTCOffset="+0300" {...handlers} />);
        wrapper.update();
        clickCustomTime(wrapper);
        inputTime(wrapper, dateInPast);
        wrapper.update();
        const timeInput = wrapper.find('TimeInput');
        expect(timeInput.prop('value')).toBe(dateInPast);
        const okButton = wrapper.find('AmberButtonControl.' + CustomDateAndTimeB('ok-button'));
        expect(okButton.length).toBe(1);
        okButton.prop('onClick')();
        wrapper.update();
        expect(wrapper.find(Popup).length).toBe(0);
        expect(handlers.onSelectCustom).not.toHaveBeenCalled();
        expect(handlers.onSelectDue).toHaveBeenCalledWith(0);
    });

    it('две минуты до полуночи округляются в 00:00 следующего дня', () => {
        MockDate.set('2019-03-14 12:00:00');
        const almostMidnight = '23:58';
        const handlers = createMockedProps();
        const wrapper = mount(<EnhancedOrderTime zoneUTCOffset="+0300" {...handlers} />);
        clickCustomTime(wrapper);
        inputTime(wrapper, almostMidnight);
        wrapper.update();
        const timeInput = wrapper.find('TimeInput');
        expect(timeInput.prop('value')).toBe(almostMidnight);
        const okButton = wrapper.find('AmberButtonControl.' + CustomDateAndTimeB('ok-button'));
        expect(okButton.length).toBe(1);
        okButton.prop('onClick')();
        wrapper.update();
        expect(wrapper.find(Popup).length).toBe(0);
        expect(handlers.onSelectCustom).toHaveBeenCalledWith(1, '00:00');
    });
});
