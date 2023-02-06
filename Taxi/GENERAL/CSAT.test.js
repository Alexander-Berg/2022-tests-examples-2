import React from 'react';
import {shallow} from 'enzyme';

import CSAT from './index';
import Rate from './rate/Rate';
import {OPTIONS} from './const';

const i18n = {
    print: key => key,
    get: key => key
};

describe('webviewHelp CSAT', () => {
    it('Должен содержать верное число оценок и кнопку вопроса', () => {
        let wrapper = shallow(<CSAT options={OPTIONS} i18n={i18n}/>);

        expect(wrapper.find(Rate).length).toBe(OPTIONS.length);
        expect(wrapper.find('.CSAT-old__ask-button').length).toBe(1);
    });

    it('Клик по задать вопрос - вызывает обработчик с текстом', () => {
        const onAskSpy = jest.fn();
        let wrapper = shallow(<CSAT options={OPTIONS} onAsk={onAskSpy} i18n={i18n}/>);

        wrapper.find('.CSAT-old__ask-button').simulate('click');

        expect(onAskSpy).toHaveBeenCalledWith('webview.help.csat.continue');
    });

    it('Если элемент выбран - показывает кнопку сохранения и причины', () => {
        let wrapper = shallow(<CSAT options={OPTIONS} selected={OPTIONS[0]} i18n={i18n}/>);

        expect(wrapper.find('.CSAT-old__send-button').length).toBe(1);
        expect(wrapper.find('.CSAT-old__reasons').length).toBe(1);
        expect(wrapper.find('.CSAT-old__reason').length).toBe(OPTIONS[0].reasons.length);
    });

    it('Вызывается колбек на сохранение', () => {
        const onSaveSpy = jest.fn();
        let wrapper = shallow(<CSAT options={OPTIONS} selected={OPTIONS[0]} onSave={onSaveSpy} i18n={i18n}/>);

        wrapper.find('.CSAT-old__send-button').simulate('click');
        expect(onSaveSpy).toHaveBeenCalled();
    });

    it('Вызывается колбек на смену причины', () => {
        const onChangeReasonSpy = jest.fn();
        let wrapper = shallow(
            <CSAT options={OPTIONS} selected={OPTIONS[0]} i18n={i18n} onSelectReason={onChangeReasonSpy}/>
        );

        wrapper
            .find('.CSAT-old__reason')
            .at(1)
            .simulate('click');
        expect(onChangeReasonSpy).toHaveBeenCalledWith(OPTIONS[0].reasons[1].reason_key);
    });
});
