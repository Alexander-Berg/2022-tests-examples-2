import {shallow} from 'enzyme';
import React from 'react';

import Button, {ButtonProps} from '__components/Button';

import Desktop from '../desktop';
import Mobile from '../mobile';

describe('Проверяем Already Registered [common]', () => {
    const correctCommonStyles: ButtonProps = {
        size: 'large',
        className: 'bordered',
    };
    const correctDownloadStyles: ButtonProps = {
        ...correctCommonStyles,
        type: 'default',
    };
    const correctSupportStyles: ButtonProps = {
        ...correctCommonStyles,
        type: 'primary',
    };

    it('Должна содержать две кнопки с корректными текстами', () => {
        const componentMobile = shallow(<Mobile/>);
        const componentDesktop = shallow(<Desktop/>);

        [componentDesktop, componentMobile].forEach(component => {
            expect(component.find(Button).first().props().children).toBe('Скачать приложение');
            expect(component.find(Button).at(1).props().children).toBe('Написать');
        });
    });

    it('Должна содержать две кнопки с корректными стилями', () => {
        const componentMobile = shallow(<Mobile/>);
        const componentDesktop = shallow(<Desktop/>);

        [componentDesktop, componentMobile].forEach(component => {
            expect(component.find(Button).first().props())
                .toMatchObject(expect.objectContaining(correctDownloadStyles));
            expect(component.find(Button).at(1).props())
                .toMatchObject(expect.objectContaining(correctSupportStyles));
        });
    });
});
