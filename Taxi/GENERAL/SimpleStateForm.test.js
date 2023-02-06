import React from 'react';
import {mount} from 'enzyme';
import SimpleStateForm from './SimpleStateForm';

const Form = () => null;

const FIELD_NAME_1 = 'fieldName1';
const FIELD_NAME_2 = 'fieldName2';
const FIELD_NAMES = [FIELD_NAME_1, FIELD_NAME_2];
const VALUE = 'VALUE';

describe('Blocks/SimpleStateForm', () => {
    it('Рендерит переданный элемент и передает props вниз, добавляя form', () => {
        const props = {a: 'a', b: 'b'};

        const wrapper = mount(<SimpleStateForm fieldNames={FIELD_NAMES} props={props} component={Form}/>);

        const formElement = wrapper.find(Form);

        const {form, ...otherProps} = formElement.props();

        expect(otherProps).toMatchObject(props);

        expect(form).toBeDefined();
        expect(typeof form.submit).toBe('function');

        expect(Object.keys(form.fields)).toHaveLength(2);
        expect(Object.keys(form.fields)).toEqual(expect.arrayContaining(FIELD_NAMES));
    });

    it('Передает для поля onChange которое меняет значение поля в props', () => {
        const wrapper = mount(<SimpleStateForm fieldNames={FIELD_NAMES} component={Form}/>);

        const fieldsBefore = wrapper.find(Form).props().form.fields;

        expect(fieldsBefore[FIELD_NAME_1].value).toBeUndefined();
        expect(fieldsBefore[FIELD_NAME_2].value).toBeUndefined();

        fieldsBefore[FIELD_NAME_1].onChange(VALUE);

        wrapper.update();

        const fieldsAfter = wrapper.find(Form).props().form.fields;

        expect(fieldsAfter[FIELD_NAME_1].value).toBe(VALUE);
        expect(fieldsAfter[FIELD_NAME_2].value).toBeUndefined();
    });

    it('Принимает правила валидации и не вызывает onSubmit если валидация не прошла ', done => {
        const submitSpy = jest.fn();

        const wrapper = mount(
            <SimpleStateForm
                validate={{
                    [FIELD_NAME_1]: () => false
                }}
                onSubmit={submitSpy}
                fieldNames={FIELD_NAMES}
                component={Form}
            />
        );

        const {form} = wrapper.find(Form).props();

        form.fields[FIELD_NAME_1].onChange(VALUE);

        form.submit();

        process.nextTick(() => {
            wrapper.update();

            const {fields} = wrapper.find(Form).props().form;

            expect(fields[FIELD_NAME_1].error).toBeTruthy();
            expect(submitSpy).toHaveBeenCalledTimes(0);

            done();
        });
    });

    it('Принимает правила валидации и вызывает onSubmit если валидация прошла ', done => {
        const submitSpy = jest.fn();

        const wrapper = mount(
            <SimpleStateForm
                validate={{
                    [FIELD_NAME_1]: () => true
                }}
                onSubmit={submitSpy}
                fieldNames={FIELD_NAMES}
                component={Form}
            />
        );

        const {form} = wrapper.find(Form).props();

        form.fields[FIELD_NAME_1].onChange(VALUE);

        form.submit();

        process.nextTick(() => {
            wrapper.update();

            expect(submitSpy).toHaveBeenCalledTimes(1);
            expect(submitSpy).toHaveBeenCalledWith({[FIELD_NAME_1]: VALUE});

            done();
        });
    });

    it('Если после валидации поле было с ошибкой, то после изменения будет работать валидация', done => {
        const submitSpy = jest.fn();
        const VALUE_WRONG = 'VALUE_WRONG';

        const wrapper = mount(
            <SimpleStateForm
                validate={{
                    [FIELD_NAME_1]: value => (value === VALUE)
                }}
                onSubmit={submitSpy}
                fieldNames={FIELD_NAMES}
                component={Form}
            />
        );

        const {form} = wrapper.find(Form).props();

        form.fields[FIELD_NAME_1].onChange(VALUE_WRONG);

        form.submit();

        process.nextTick(() => {
            wrapper.update();

            const {form} = wrapper.find(Form).props();

            expect(form.fields[FIELD_NAME_1].error).toBeTruthy();
            expect(submitSpy).toHaveBeenCalledTimes(0);

            form.fields[FIELD_NAME_1].onChange(VALUE);

            process.nextTick(() => {
                wrapper.update();

                const {fields} = wrapper.find(Form).props().form;

                expect(fields[FIELD_NAME_1].error).toBeFalsy();

                done();
            });
        });
    });
});
