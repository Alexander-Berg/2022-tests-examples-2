import React from 'react';
import {shallow} from 'enzyme';

import Rate from './Rate';

const ITEM = {option_key: 'horrible', option_name: 'Ужасно'};

describe('webviewHelp CSAT Rate', () => {
    it('Рендерится ожидаемых html', () => {
        let wrapper = shallow(<Rate item={ITEM} className="MyRate"/>);

        expect(wrapper.text()).toBe(ITEM.option_name);
        expect(wrapper.find('.CSAT-Rate__icon').length).toBe(1);
        expect(wrapper.find('.CSAT-Rate__name').length).toBe(1);
        expect(wrapper.is('.MyRate')).toBeTruthy();
    });

    it('Если оценка дана - то имя не выводится', () => {
        let wrapper = shallow(<Rate item={ITEM} finished/>);

        expect(wrapper.find('.CSAT-Rate__name').length).toBe(0);
    });

    it('Должен вызывать обработчик с верным id', () => {
        const spy = jest.fn();
        let wrapper = shallow(<Rate item={ITEM} onChange={spy}/>);

        wrapper.simulate('click');
        expect(spy).toHaveBeenCalledWith(ITEM);
    });

    it('Не должен вызывать обработчик если disabled', () => {
        const spy = jest.fn();
        let wrapper = shallow(<Rate item={ITEM} onChange={spy} disabled/>);

        wrapper.simulate('click');
        expect(spy).toHaveBeenCalledTimes(0);
    });

    it('Должен сбрасывать значение при клике на уже выбранный', () => {
        const spy = jest.fn();
        let wrapper = shallow(<Rate item={ITEM} onChange={spy} isSelected/>);

        wrapper.simulate('click');
        expect(spy).toHaveBeenCalledWith(undefined);
    });
});
