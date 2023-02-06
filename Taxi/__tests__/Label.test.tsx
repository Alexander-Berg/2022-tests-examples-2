import React from 'react';
import {shallow} from 'enzyme';
import Label from '../Label';

describe('Components/label', () => {
    it('Если есть параметр textColor - цвет текста соответствующий', () => {
        const textColor = '#dddddd';
        const wrapper = shallow(<Label textColor={textColor}/>);
        expect(wrapper.prop('style').color).toEqual(textColor);
    });

    it('Если есть параметр backgroundColor - цвет фона соответствующий', () => {
        const backgroundColor = 'red';
        const wrapper = shallow(<Label color={backgroundColor}/>);
        expect(wrapper.prop('style').backgroundColor).toEqual(backgroundColor);
    });

    it('Если есть параметр borderColor - цвет границ соответствующий', () => {
        const color = 'red';
        const wrapper = shallow(<Label borderColor={color}/>);
        expect(wrapper.prop('style').borderColor).toEqual(color);
    });

    it('Если есть параметр borderColor - добавляется модификатор', () => {
        const color = 'red';
        const wrapper = shallow(<Label borderColor={color}/>);
        expect(wrapper.prop('className').split(' ')).toContain('amber-label_border');
    });
});
