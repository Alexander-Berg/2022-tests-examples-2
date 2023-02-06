import * as actions from '../actions';
import * as formActions from '@blocks/actions/form';

const getState = () => ({
    settings: {
        language: 'ru',
        uatraits: {
            isMobile: false,
            isTouch: false
        }
    },
    common: {
        csrf: '12345',
        track_id: '1234',
        from: 'mail'
    },
    form: {
        values: {
            name: 'test',
            lastname: 'example',
            login: 'testlogin',
            password: ''
        },
        states: {
            name: 'valid',
            lastname: 'valid',
            login: 'valid',
            email: 'valid'
        },
        errors: {
            login: {
                code: 'login.not_available',
                text: 'логин недоступен'
            }
        }
    }
});

const dispatch = jest.fn();

describe('registration actions', () => {
    it('should return type: CLEAR_SUGGESTED_LOGINS', () => {
        expect(actions.clearSuggestedLogins()).toEqual({
            type: actions.CLEAR_SUGGESTED_LOGINS
        });
    });

    it('should return type: SET_SUGGESTION_VALIDATING_STATUS', () => {
        const isValidating = true;

        expect(actions.setSuggestionFetching(isValidating)).toEqual({
            type: actions.SET_SUGGESTION_VALIDATING_STATUS,
            isValidating: true
        });
    });

    it('should return type: SET_CAPTCHA_REQUIRED', () => {
        const isRequired = true;

        expect(formActions.setCaptchaRequired(isRequired)).toEqual({
            type: formActions.SET_CAPTCHA_REQUIRED,
            isRequired: true
        });
    });

    it('should return type: UPDATE_VALIDATION_METHOD', () => {
        expect(formActions.updateValidationMethod('phone')).toEqual({
            type: formActions.UPDATE_VALIDATION_METHOD,
            method: 'phone'
        });
    });

    it('should return type: HUMAN_CONFIRMATION_DONE', () => {
        expect(formActions.updateHumanConfirmationStatus(false)).toEqual({
            type: formActions.HUMAN_CONFIRMATION_DONE,
            state: false
        });
    });

    it('should return type: UPDATE_CONFIRMATION_FETCHING_STATUS', () => {
        const data = {
            isFetching: true
        };

        expect(formActions.updateConfirmationFetchingStatus(data)).toEqual({
            type: formActions.UPDATE_CONFIRMATION_FETCHING_STATUS,
            data: {isFetching: true}
        });
    });

    it('should return type: GET_QUESTIONS_LIST', () => {
        const questions = [
            {
                id: 'q1',
                val: '12',
                text: 'Your favorite musician surname'
            }
        ];

        expect(formActions.getUserQuestionsList(questions)).toEqual({
            type: formActions.GET_QUESTIONS_LIST,
            questions
        });
    });

    it('should return type: UPDATE_VALUES', () => {
        const data = {
            field: 'firstname',
            value: 'test'
        };

        expect(formActions.updateValues(data)).toEqual({
            type: formActions.UPDATE_VALUES,
            data: {
                field: 'firstname',
                value: 'test'
            }
        });
    });

    it('should return type: UPDATE_QUESTION_VALUES', () => {
        const data = {
            hint_question_id: '13',
            hint_question: 'The street you grew up on'
        };

        expect(formActions.updateQuestionValues(data)).toEqual({
            type: formActions.UPDATE_QUESTION_VALUES,
            data: {
                hint_question_id: '13',
                hint_question: 'The street you grew up on'
            }
        });
    });

    it('should return type: UPDATE_STATES and send metrics', () => {
        const data = {
            field: 'firstname',
            status: 'valid'
        };

        formActions.updateStates(data)(dispatch, getState);
        expect(dispatch).toBeCalled();
        expect(dispatch).toBeCalledWith({
            type: formActions.UPDATE_STATES,
            data: {
                field: 'firstname',
                status: 'valid'
            }
        });
    });

    it('should return type: UPDATE_STATES and dont send metrics', () => {
        const data = {
            field: 'phone',
            status: 'valid'
        };

        formActions.updateStates(data)(dispatch, getState);
        expect(dispatch).toBeCalled();
        expect(dispatch).toBeCalledWith({
            type: formActions.UPDATE_STATES,
            data: {
                field: 'firstname',
                status: 'valid'
            }
        });
    });

    it('should return type: UPDATE_HINT_QUESTION_STATES', () => {
        const data = {
            status: 'valid'
        };

        expect(formActions.updateQuestionStates(data)).toEqual({
            type: formActions.UPDATE_HINT_QUESTION_STATES,
            data: {
                status: 'valid'
            }
        });
    });

    it('should return type: UPDATE_HINT_CUSTOM_QUESTION_STATE', () => {
        const data = {
            status: 'valid'
        };

        expect(formActions.updateQuestionCustomState(data)).toEqual({
            type: formActions.UPDATE_HINT_CUSTOM_QUESTION_STATE,
            data: {
                status: 'valid'
            }
        });
    });

    it('should return type: UPDATE_ERRORS', () => {
        const data = {
            field: 'captcha',
            error: {
                code: 'missingvalue',
                text: 'Необходимо ввести символы'
            },
            active: true
        };

        expect(formActions.updateErrors(data)).toEqual({
            type: formActions.UPDATE_ERRORS,
            data: {
                field: 'captcha',
                error: {
                    code: 'missingvalue',
                    text: 'Необходимо ввести символы'
                },
                active: true
            }
        });
    });

    it('should return type: SET_GROUP_ERRORS', () => {
        const data = {
            active: 'firstname',
            firsname: {
                code: 'missingvalue',
                text: 'Необходимо ввести символы'
            },
            lastname: {
                code: 'missingvalue',
                text: 'Необходимо ввести символы'
            }
        };

        expect(formActions.updateGroupErrors(data)).toEqual({
            type: formActions.SET_GROUP_ERRORS,
            data: {
                active: 'firstname',
                firsname: {
                    code: 'missingvalue',
                    text: 'Необходимо ввести символы'
                },
                lastname: {
                    code: 'missingvalue',
                    text: 'Необходимо ввести символы'
                }
            }
        });
    });

    it('should return type: UPDATE_REG_ERROR', () => {
        const data = {
            status: 'error',
            code: 'invalid',
            text: 'Ошибка',
            descriptionText: 'Ошибка регистрации'
        };

        expect(actions.updateRegistrationErrors(data)).toEqual({
            type: actions.UPDATE_REG_ERROR,
            data: {
                status: 'error',
                code: 'invalid',
                text: 'Ошибка',
                descriptionText: 'Ошибка регистрации'
            }
        });
    });

    it('should return type: SET_FIELD_ERROR_ACTIVE', () => {
        expect(formActions.setFieldErrorActive('firstname')).toEqual({
            type: formActions.SET_FIELD_ERROR_ACTIVE,
            field: 'firstname'
        });
    });

    it('should return type: UPDATE_ERRORS_VALID', () => {
        expect(formActions.updateErrorsValid('firstname')).toEqual({
            type: formActions.UPDATE_ERRORS_VALID,
            field: 'firstname'
        });
    });

    it('should return type: UPDATE_EMPTY_ERRORS', () => {
        const fields = {firstname: 'not_valid'};

        expect(formActions.updateErrorStates(fields)).toEqual({
            type: formActions.UPDATE_EMPTY_ERRORS,
            fields
        });
    });

    it('should return type: UPDATE_FETCHING_STATUS', () => {
        expect(actions.updateFetchingStatus(true)).toEqual({
            type: actions.UPDATE_FETCHING_STATUS,
            isFetching: true
        });
    });

    it('should return type: GET_SUGGESTED_LOGINS', () => {
        const data = {
            logins: ['test1', 'test2'],
            showAll: false,
            isFetching: false
        };

        expect(actions.updateSuggestedLogins(data)).toEqual({
            type: actions.GET_SUGGESTED_LOGINS,
            data: {
                logins: ['test1', 'test2'],
                showAll: false,
                isFetching: false
            }
        });
    });

    it('should return type: UPDATE_PHONE_VALUES_TO_DEFAULTS', () => {
        expect(formActions.updatePhoneValuesToDefaults()).toEqual({
            type: formActions.UPDATE_PHONE_VALUES_TO_DEFAULTS
        });
    });

    it('should return type: UPDATE_PHONE_STATES_TO_DEFAULTS', () => {
        expect(formActions.updatePhoneStatesToDefaults()).toEqual({
            type: formActions.UPDATE_PHONE_STATES_TO_DEFAULTS
        });
    });

    it('should return type: UPDATE_GLOBAL_HINT_STATUS', () => {
        expect(formActions.updateHintStatus(true)).toEqual({
            type: formActions.UPDATE_GLOBAL_HINT_STATUS,
            status: true
        });
    });

    it('should return type: SET_CURRENT_STEP', () => {
        expect(actions.setCurrentStep(1)).toEqual({
            type: actions.SET_CURRENT_STEP,
            step: 1
        });
    });

    it('should return type: CHANGE_ACTIVE_FIELD', () => {
        expect(formActions.changeActiveField('firstname')).toEqual({
            type: formActions.CHANGE_ACTIVE_FIELD,
            field: 'firstname'
        });
    });

    it('should return type: VALIDATE_PHONE_FOR_CALL', () => {
        expect(formActions.validatePhoneForCall(true)).toEqual({
            type: formActions.VALIDATE_PHONE_FOR_CALL,
            isValid: true
        });
    });

    it('should return type: CHANGE_PHONE_CONFIRMATION_TYPE', () => {
        expect(formActions.changePhoneConfirmationType('call')).toEqual({
            type: formActions.CHANGE_PHONE_CONFIRMATION_TYPE,
            phoneConfirmationType: 'call'
        });
    });
});
