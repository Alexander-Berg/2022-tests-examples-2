import React from 'react';
import {shallow, mount} from 'enzyme';
import Modal from '../Modal';
import ModalCloseButton from '../ModalCloseButton';

describe('Modal', () => {
    describe('компонент закрытия', () => {
        it('Если не передевали кастомный компонент - рендерится дефолтный', () => {
            const wrapper = shallow(<Modal/>);
            expect(wrapper.find(ModalCloseButton).exists()).toBe(true);
        });
        it('Если передавали кастомный компонент - он должен отрендериться', () => {
            const CustomClose = (): any => null;
            const wrapper = shallow(<Modal CloseComponent={CustomClose}/>);
            expect(wrapper.find(CustomClose).exists()).toBe(true);
        });
        it('Если передавали onCloseRequest - он должен триггериться', () => {
            let onCloseRequestStore: any;
            const spy = jest.fn();
            const CustomClose = ({onCloseRequest}: any): any => {
                onCloseRequestStore = onCloseRequest;
                return null;
            };
            mount(<Modal CloseComponent={CustomClose} onCloseRequest={spy}/>);
            onCloseRequestStore();
            expect(spy.mock.calls.length).toBe(1);
        });
        it('Если передавали onCloseRequest - он должен триггериться при клике на бэкграунд', () => {
            const spy = jest.fn();
            const wrapper = shallow(<Modal onCloseRequest={spy}/>);
            wrapper.find('.amber-modal__backdrop').simulate('click');
            expect(spy.mock.calls.length).toBe(1);
        });
        it('Если передавали onCloseRequest и shouldCloseOnBackdropClick === false, то не триггерим закрытие', () => {
            const spy = jest.fn();
            const wrapper = shallow(<Modal onCloseRequest={spy} shouldCloseOnBackdropClick={false}/>);
            expect(wrapper.find('.amber-modal__click-catcher').exists()).toBe(false);
        });
    });
    it('должен передавать tabIndex в wrapper', () => {
        const wrapper = shallow(<Modal tabIndex={1}/>);
        expect(wrapper.find('.amber-modal__wrapper').prop('tabIndex')).toBe(1);
    });
});
