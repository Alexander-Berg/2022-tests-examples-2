// eslint-disable-next-line no-unused-vars
import React from 'react';
import {shallow} from 'enzyme';

import {Button} from '@components/Button';

import regMethods from '../../registration/methods/basicRegistrationMethods';
import scrollToError from '../../registration/methods/scrollToError';
import {
    updateErrorStates,
    updateQuestionCustomState,
    updateErrors,
    updateGroupErrors,
    updateValues,
    updateErrorsValid
} from '@blocks/actions/form';
import {REGISTRATION_PDD_GOAL_PREFIX} from '../../registration/actions';
import {errorsTxt} from '../../registration/errors.js';
import metrics from '../../metrics';

import * as extracted from '../form.js';
import EulaPopup from '../../registration/desktop/eula/EulaPopup';

jest.mock('@blocks/actions/form', () => ({
    updateErrorStates: jest.fn(),
    updateQuestionCustomState: jest.fn(),
    updateErrors: jest.fn(),
    updateGroupErrors: jest.fn(),
    updateValues: jest.fn(),
    updateErrorsValid: jest.fn()
}));

jest.mock('../../registration/actions', () => ({
    setName: jest.fn(),
    REGISTRATION_PDD_GOAL_PREFIX: 'REGISTRATION_PDD_GOAL_PREFIX'
}));
jest.mock('../../metrics', () => ({
    send: jest.fn(),
    goal: jest.fn()
}));

jest.mock('../../registration/methods/basicRegistrationMethods');
jest.mock('../../registration/methods/scrollToError');

describe('Connect.Form', () => {
    let obj = null;

    beforeEach(() => {
        obj = {
            prefix: REGISTRATION_PDD_GOAL_PREFIX,
            state: {
                eulaChecked: true
            },
            setState: jest.fn((any) => (typeof any === 'function' ? any({}) : any)),
            props: {
                dispatch: jest.fn(),
                form: {
                    validation: {
                        method: 'phone',
                        humanConfirmationDone: true
                    },
                    states: {},
                    values: {}
                }
            }
        };
        regMethods.submitRegistration = jest.fn();
    });
    afterEach(() => {
        updateValues.mockClear();
        updateErrorsValid.mockClear();
        scrollToError.mockClear();
        metrics.send.mockClear();
        metrics.goal.mockClear();
    });
    describe('handleEula', () => {
        it('should call setState', () => {
            extracted.handleEula.call(obj);
            expect(obj.setState).toHaveBeenCalledTimes(1);
        });
    });
    describe('updateUserField', () => {
        it('should dispatch updateValues and updateErrorsValid', () => {
            const value = 'value';
            const name = 'field';
            const fieldinfo = {value, field: name};

            extracted.updateUserField.call(obj, {target: {value, name}});
            expect(obj.props.dispatch).toHaveBeenCalledTimes(2);
            expect(updateValues).toHaveBeenCalledTimes(1);
            expect(updateValues).toHaveBeenCalledWith(fieldinfo);
            expect(updateErrorsValid).toHaveBeenCalledTimes(1);
            expect(updateErrorsValid).toHaveBeenCalledWith(name);
        });
    });
    describe('onFormSubmit', () => {
        it('should call send and goal of metrics, and call preventDefault of event', () => {
            const event = {
                preventDefault: jest.fn()
            };

            obj.state.eulaChecked = false;

            extracted.onFormSubmit.call(obj, event);

            expect(event.preventDefault).toHaveBeenCalledTimes(1);
            expect(metrics.send).toHaveBeenCalledTimes(1);
            expect(metrics.send).toHaveBeenCalledWith(['Форма', 'Попытка отправки']);
            expect(metrics.goal).toHaveBeenCalledTimes(1);
            expect(metrics.goal).toHaveBeenCalledWith(`${REGISTRATION_PDD_GOAL_PREFIX}_form_submitted`);
        });
    });
    describe('validateForm', () => {
        beforeEach(() => {
            regMethods.submitRegistration.mockClear();
            metrics.send.mockClear();
            metrics.goal.mockClear();
            updateQuestionCustomState.mockClear();
            updateErrors.mockClear();
            updateErrorStates.mockClear();
            updateGroupErrors.mockClear();
        });

        it('shouldnt call any dispatch', () => {
            obj.state.eulaChecked = false;
            extracted.validateForm.call(obj);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(0);
        });
        it('should reject submit', () => {
            obj.props.form = Object.assign({}, obj.props.form, {
                values: {
                    phoneCode: '2322'
                },
                validation: {
                    method: 'phone',
                    humanConfirmationDone: false
                }
            });
            extracted.validateForm.call(obj);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(2);
            expect(updateErrorStates).toHaveBeenCalledTimes(1);
            expect(updateGroupErrors).toHaveBeenCalledTimes(1);
            expect(metrics.send).toHaveBeenCalledTimes(1);
            expect(metrics.send).toHaveBeenCalledWith(['Форма', 'Показ ошибок']);
            expect(metrics.goal).toHaveBeenCalledTimes(1);
            expect(metrics.goal).toHaveBeenCalledWith(`${REGISTRATION_PDD_GOAL_PREFIX}_form_invalid`);
            expect(scrollToError).toHaveBeenCalledTimes(1);
        });
        it('should submit form', () => {
            extracted.validateForm.call(obj);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
            expect(regMethods.submitRegistration).toHaveBeenCalledTimes(1);
            expect(metrics.send).toHaveBeenCalledTimes(1);
            expect(metrics.send).toHaveBeenCalledWith(['Форма', 'Отправка формы']);
            expect(metrics.goal).toHaveBeenCalledTimes(1);
            expect(metrics.goal).toHaveBeenCalledWith(`${REGISTRATION_PDD_GOAL_PREFIX}_form_valid`);
        });
        it('should dispatch updateQuestionCustomState and updateErrors', () => {
            const hintQuestionErrorObj = {
                code: 'missingvalue',
                text: errorsTxt.hint.hintQuestionErrors.missingvalue
            };

            obj.props.form = Object.assign({}, obj.props.form, {
                validation: {
                    method: 'captcha'
                },
                values: {
                    hint_question_id: '99',
                    hint_question_custom: false
                },
                states: {
                    password: 'invalid',
                    phone: 'invalid',
                    login: 'invalid'
                },
                errors: {
                    password: {
                        warning: true
                    },
                    phone: {
                        code: 'missingvalue'
                    },
                    login: {}
                }
            });
            extracted.validateForm.call(obj);
            expect(updateQuestionCustomState).toHaveBeenCalledTimes(1);
            expect(updateQuestionCustomState).toHaveBeenCalledWith({status: 'not_valid'});
            expect(updateErrors).toHaveBeenCalledTimes(1);
            expect(updateErrors).toHaveBeenCalledWith({
                field: 'hint_question_custom',
                error: hintQuestionErrorObj,
                active: true
            });
        });
    });
    describe('submit', () => {
        it('renders correctly', () => {
            const wrapper = shallow(extracted.submit.call(obj));

            expect(wrapper.find(Button).length).toBe(1);
            expect(wrapper.find(EulaPopup).length).toBe(1);
        });
        it('should be disabled', () => {
            obj.state.eulaChecked = false;
            expect(shallow(extracted.submit.call(obj)).props('disabled')).toBeTruthy();

            obj.state.eulaChecked = true;
            obj.props.isFetching = true;
            expect(shallow(extracted.submit.call(obj)).props('disabled')).toBeTruthy();

            obj.props.isFetching = false;
            obj.props.form.states.phoneCodeStatus = 'code_sent';
            expect(shallow(extracted.submit.call(obj)).props('disabled')).toBeTruthy();
        });
    });
});
