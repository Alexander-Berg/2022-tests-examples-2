// eslint-disable-next-line no-unused-vars
import React from 'react';
import {shallow} from 'enzyme';

import {Button} from '@components/Button';
import EulaPopup from '../../registration/desktop/eula/EulaPopup.jsx';

import regMethods from '../../registration/methods/basicRegistrationMethods';

import {
    REGISTRATION_COMPLETE_GOAL_PREFIX,
    REGISTRATION_COMPLETE_MOBILE_GOAL_PREFIX,
    updateRegistrationErrors
} from '../../registration/actions';

import {
    updateErrorStates,
    updateQuestionCustomState,
    updateErrors,
    updateGroupErrors,
    updateValues,
    updateErrorsValid,
    updateValidationMethod
} from '@blocks/actions/form';

import metrics from '../../metrics';

import * as extracted from '../form.js';

jest.mock('../../registration/actions', () => ({
    updateRegistrationErrors: jest.fn(),
    REGISTRATION_COMPLETE_GOAL_PREFIX: 'complete',
    REGISTRATION_COMPLETE_MOBILE_GOAL_PREFIX: 'mobile'
}));

jest.mock('@blocks/actions/form', () => ({
    updateErrorStates: jest.fn(),
    updateQuestionCustomState: jest.fn(),
    updateErrors: jest.fn(),
    updateGroupErrors: jest.fn(),
    updateValues: jest.fn(),
    updateErrorsValid: jest.fn(),
    updateValidationMethod: jest.fn(),
    showEulaPopup: jest.fn()
}));

jest.mock('../../metrics', () => ({
    send: jest.fn(),
    goal: jest.fn()
}));

jest.mock('../../registration/methods/basicRegistrationMethods');

describe('Complete.Form', () => {
    let obj = null;

    beforeEach(() => {
        obj = {
            setState: jest.fn((any) => (typeof any === 'function' ? any({}) : any)),
            state: {
                eulaChecked: false
            },
            props: {
                dispatch: jest.fn(),
                isMobile: false,
                form: {
                    type: 'complete_lite',
                    states: {
                        captcha: 'valid'
                    },
                    validation: {
                        method: 'phone',
                        humanConfirmationDone: true
                    },
                    values: {},
                    errors: {
                        password: {}
                    }
                },
                person: {
                    hasRecoveryMethod: false
                }
            }
        };
        regMethods.submitRegistration = jest.fn();
        regMethods.prepareFormData.mockImplementation((states) => {
            const clone = Object.assign({}, states);

            delete clone.hint_question_custom;
            return clone;
        });
    });
    afterEach(() => {
        regMethods.submitRegistration.mockClear();
        metrics.send.mockClear();
        metrics.goal.mockClear();
        updateQuestionCustomState.mockClear();
        updateErrors.mockClear();
        updateErrorStates.mockClear();
        updateGroupErrors.mockClear();
        updateValues.mockClear();
        updateErrorsValid.mockClear();
        updateValidationMethod.mockClear();
        updateRegistrationErrors.mockClear();
    });

    describe('prepareData', () => {
        it('should remove captcha from form.states', () => {
            const nextStates = Object.assign({}, obj.props.form.states, {
                captcha: undefined
            });

            obj.props.person.hasRecoveryMethod = true;

            delete nextStates.captcha;
            expect(extracted.prepareData.call(obj, 'states')).toEqual(nextStates);
        });

        it('should remove password_confirm from form.states', () => {
            const nextStates = Object.assign({}, obj.props.form.states, {
                password_confirm: undefined
            });

            obj.props.form.states.password_confirm = 'valid';
            obj.props.isMobile = true;

            delete nextStates.password_confirm;

            expect(extracted.prepareData.call(obj, 'states')).toEqual(nextStates);
        });

        it('should remove add state to form.values', () => {
            expect(extracted.prepareData.call(obj, 'values')).toEqual(
                Object.assign({}, obj.props.form.values, {
                    state: obj.props.form.type
                })
            );
        });

        it('should change human-confirmation in form.values', () => {
            const method = 'some_method';
            const nextValues = Object.assign({}, obj.props.form.values, {
                'human-confirmation': method,
                state: ''
            });

            obj.props.form.type = '';
            obj.props.form.validation.method = method;

            expect(extracted.prepareData.call(obj, 'values')).toEqual(nextValues);
        });

        it('should call prepareFormData', () => {
            const {
                isMobile,
                form: {
                    states,
                    validation: {method}
                }
            } = obj.props;

            regMethods.prepareFormData = jest.fn(() => ({}));
            regMethods.prepareFormData.mockClear();
            extracted.prepareData.call(obj, 'states');
            expect(regMethods.prepareFormData).toHaveBeenCalledTimes(1);
            expect(regMethods.prepareFormData).toHaveBeenCalledWith(states, method, isMobile);
        });
    });

    /* describe('validateForm', () => {
        beforeEach(() => {
            obj.state.eulaChecked = true;
        });

        it('shouldnt call any dispatch', () => {
            obj.state.eulaChecked = false;

            extracted.validateForm.call(obj);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(0);
        });

        it('should reject submit', () => {
            obj.props.form.validation = {
                method: 'phone',
                humanConfirmationDone: false
            };

            document.querySelector = jest.fn(() => true);

            extracted.validateForm.call(obj);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(2);
            expect(updateErrorStates).toHaveBeenCalledTimes(1);
            expect(updateGroupErrors).toHaveBeenCalledTimes(1);
            expect(metrics.send).toHaveBeenCalledTimes(1);
            expect(metrics.send).toHaveBeenCalledWith(['Форма', 'Показ ошибок']);
            expect(metrics.goal).toHaveBeenCalledTimes(1);
            expect(metrics.goal).toHaveBeenCalledWith(`${REGISTRATION_COMPLETE_GOAL_PREFIX}_form_invalid`);
            expect(scrollToError).toHaveBeenCalledTimes(1);
            document.querySelector.mockClear();
        });

        it('should reject submit', () => {
            obj.props.form.validation = {
                method: 'phone',
                humanConfirmationDone: false
            };

            document.querySelector = jest.fn(() => false);

            extracted.validateForm.call(obj);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
            expect(updateRegistrationErrors).toHaveBeenCalledTimes(1);
            document.querySelector.mockClear();
        });


        it('should submit form', () => {
            obj.props.form.states = {
                firstname: 'valid',
                lastname: 'valid',
                login: 'valid',
                password: 'valid',
                password_confirm: 'valid',
                hint_question_id: 'valid',
                hint_question: 'valid',
                hint_question_custom: 'valid',
                hint_answer: 'valid',
                captcha: 'valid',
                phone: 'valid',
                phoneCode: 'valid',
                phoneCodeStatus: 'valid'
            };

            extracted.validateForm.call(obj);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
            // expect(regMethods.submitRegistration).toHaveBeenCalledTimes(1);
            expect(metrics.send).toHaveBeenCalledTimes(1);
            expect(metrics.send).toHaveBeenCalledWith(['Форма', 'Отправка формы']);
            expect(metrics.goal).toHaveBeenCalledTimes(1);
            expect(metrics.goal).toHaveBeenCalledWith(`${REGISTRATION_COMPLETE_GOAL_PREFIX}_form_valid`);
        });

        it('should call updateQuestionCustomState and updateErrors', () => {
            const hintQuestionErrorObj = {
                code: 'missingvalue',
                text: errorsTxt.hint.hintQuestionErrors.missingvalue
            };

            obj.props.form = Object.assign({}, obj.props.form, {
                type: 'complete_lite',
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

            obj.props.form.validation.method = 'captcha';
            obj.props.form.values = Object.assign({}, obj.props.form.values, {
                hint_question_id: '99',
                hint_question_custom: false
            });
            extracted.validateForm.call(obj);
            // expect(updateQuestionCustomState).toHaveBeenCalledTimes(1);
            expect(updateQuestionCustomState).toHaveBeenCalledWith({status: 'not_valid'});
            expect(updateErrors).toHaveBeenCalledTimes(1);
            expect(updateErrors).toHaveBeenCalledWith(
                {field: 'hint_question_custom', error: hintQuestionErrorObj, active: true}
            );
        });
    }); */

    describe('toggleValidationMethod', () => {
        it('should dispatch updateValidationMethod with "captcha", and call send and goal of metrics ', () => {
            extracted.toggleValidationMethod.call(obj);

            expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
            expect(updateValidationMethod).toHaveBeenCalledTimes(1);
            expect(updateValidationMethod).toHaveBeenCalledWith('captcha');
            expect(metrics.send).toHaveBeenCalledTimes(1);
            expect(metrics.send).toHaveBeenCalledWith(['Подтверждение телефона', 'Регистрируйтесь без телефона']);
            expect(metrics.goal).toHaveBeenCalledTimes(1);
            expect(metrics.goal).toHaveBeenCalledWith(
                `${REGISTRATION_COMPLETE_MOBILE_GOAL_PREFIX}_phoneconfirm_switch_method`
            );
        });

        it('should dispatch updateValidationMethod with "phone", and call send and goal of metrics ', () => {
            obj.props.form.validation.method = 'captcha';

            extracted.toggleValidationMethod.call(obj);

            expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
            expect(updateValidationMethod).toHaveBeenCalledTimes(1);
            expect(updateValidationMethod).toHaveBeenCalledWith('phone');
            expect(metrics.send).toHaveBeenCalledTimes(1);
            expect(metrics.send).toHaveBeenCalledWith(['Подтверждение телефона', 'Регистрируйтесь без телефона']);
            expect(metrics.goal).toHaveBeenCalledTimes(1);
            expect(metrics.goal).toHaveBeenCalledWith(
                `${REGISTRATION_COMPLETE_MOBILE_GOAL_PREFIX}_phoneconfirm_switch_method`
            );
        });
    });
    describe('updateUserField', () => {
        it('should dispatch updateValues and updateErrorsValid', () => {
            const name = 'name';
            const value = 'value';

            extracted.updateUserField.call(obj, {target: {value, name}});
            expect(obj.props.dispatch).toHaveBeenCalledTimes(2);
            expect(updateValues).toHaveBeenCalledTimes(1);
            expect(updateValues).toHaveBeenCalledWith({
                field: name,
                value
            });
            expect(updateErrorsValid).toHaveBeenCalledTimes(1);
            expect(updateErrorsValid).toHaveBeenCalledWith(name);
        });
    });
    describe('onFormSubmit', () => {
        it('should call preventDefault of event, goal and send of metrics', () => {
            const preventDefault = jest.fn();

            obj.props.form.states = Object.assign({}, obj.props.form.states, {
                phoneCodeStatus: 'code_sent'
            });

            extracted.onFormSubmit.call(obj, {preventDefault});
            expect(preventDefault).toHaveBeenCalledTimes(1);
            expect(metrics.send).toHaveBeenCalledTimes(1);
            expect(metrics.send).toHaveBeenCalledWith(['Форма', 'Попытка отправки']);
            expect(metrics.goal).toHaveBeenCalledTimes(1);
            expect(metrics.goal).toHaveBeenCalledWith(`${REGISTRATION_COMPLETE_GOAL_PREFIX}_form_submitted`);
        });
    });
    describe('handleEula', () => {
        it('should call setState', () => {
            extracted.handleEula.call(obj);
            expect(obj.setState).toHaveBeenCalledTimes(1);
        });
    });
    describe('onTickerUnmount', () => {
        it('should call setState twice', () => {
            jest.useFakeTimers();
            extracted.onTickerUnmount.call(obj, 1);
            jest.runAllTimers();
            expect(obj.setState).toHaveBeenCalledTimes(2);
            expect(obj.setState.mock.calls[0][0]).toEqual({secondsLeft: 1});
            expect(obj.setState.mock.calls[1][0]).toEqual({secondsLeft: 0});
        });
    });
    describe('submit', () => {
        it('renders correctly', () => {
            const submitComponent = shallow(extracted.submit.call(obj));

            expect(submitComponent.find(Button).length).toBe(1);
            expect(submitComponent.find(EulaPopup).length).toBe(1);
        });
        it('should be disabled', () => {
            const submitComponent = shallow(extracted.submit.call(obj));

            obj.state.eulaChecked = false;
            expect(submitComponent.props('disabled')).toBeTruthy();

            obj.state.eulaChecked = true;
            obj.props.isFetching = true;
            expect(submitComponent.props('disabled')).toBeTruthy();

            obj.props.isFetching = false;
            obj.props.form.states.phoneCodeStatus = 'code_sent';
            expect(submitComponent.props('disabled')).toBeTruthy();
        });
    });
});
