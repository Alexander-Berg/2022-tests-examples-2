import {
    GET_EMAILS,
    GET_EMAILS_SUCCESS,
    GET_EMAILS_ERROR,
    DELETE_EMAIL,
    DELETE_EMAIL_SUCCESS,
    DELETE_EMAIL_ERROR,
    SEND_CONFIRMATION_EMAIL,
    SEND_CONFIRMATION_EMAIL_SUCCESS,
    SEND_CONFIRMATION_EMAIL_ERROR,
    RESEND_CONFIRMATION_EMAIL,
    RESEND_CONFIRMATION_EMAIL_SUCCESS,
    RESEND_CONFIRMATION_EMAIL_ERROR,
    CONFIRM_EMAIL_BY_CODE,
    CONFIRM_EMAIL_BY_CODE_SUCCESS,
    CONFIRM_EMAIL_BY_CODE_ERROR,
    EMAIL_SET_SAFE_SUCCESS,
    SET_EMAIL_ERROR,
    CHANGE_EMAILS_STATE,
    TOGGLE_ALIASES_LIST,
    TOGGLE_EMAIL_SELECTION,
    SHOW_EMAIL_DELETE_REQUEST_POPUP,
    EMAILS_STATES
} from '../actions';
import reducer from '../reducers';

const INITIAL_STATE = {
    openAliasesList: false,
    selectedEmail: null
};
const state = {
    openAliasesList: false,
    selectedEmail: null,
    email: {
        some: 'email'
    },
    states: []
};

describe('Morda.Emails.reducers', () => {
    it('should return default state', () => {
        expect(reducer(undefined, {})).toEqual(INITIAL_STATE);
    });
    test(GET_EMAILS, () => {
        const action = {
            type: GET_EMAILS
        };

        expect(reducer(state, action)).toEqual(
            Object.assign({}, state, {
                loading: 'widget'
            })
        );
    });
    test(GET_EMAILS_SUCCESS, () => {
        const action = {
            type: GET_EMAILS_SUCCESS,
            emails: []
        };

        expect(reducer(state, action)).toEqual(
            Object.assign({}, state, {
                loading: null,
                emails: action.emails
            })
        );
    });
    test(GET_EMAILS_ERROR, () => {
        const action = {
            type: GET_EMAILS_ERROR,
            error: 'value'
        };

        expect(reducer(state, action)).toEqual(
            Object.assign({}, state, {
                loading: null,
                error: action.error
            })
        );
    });
    test(DELETE_EMAIL, () => {
        const action = {
            type: DELETE_EMAIL
        };

        expect(reducer(state, action)).toEqual(
            Object.assign({}, state, {
                loading: 'deleteEmail'
            })
        );
    });
    test(DELETE_EMAIL_SUCCESS, () => {
        const action = {
            type: DELETE_EMAIL_SUCCESS,
            email: 'some'
        };

        expect(reducer(state, action)).toEqual(
            Object.assign({}, state, {
                emails: {},
                deleteRequestEmail: ''
            })
        );
    });
    test(SEND_CONFIRMATION_EMAIL_SUCCESS, () => {
        const action = {
            type: SEND_CONFIRMATION_EMAIL_SUCCESS,
            emails: [],
            addedEmail: 'value'
        };

        expect(reducer(state, action)).toEqual(
            Object.assign({}, state, {
                states: state.states.concat(EMAILS_STATES.sent),
                loading: null,
                emails: action.emails,
                addedEmail: action.email
            })
        );
    });
    test(CONFIRM_EMAIL_BY_CODE_SUCCESS, () => {
        const action = {
            type: CONFIRM_EMAIL_BY_CODE_SUCCESS,
            emails: []
        };

        expect(reducer(state, action)).toEqual(
            Object.assign({}, state, {
                states: state.states.concat(EMAILS_STATES.confirmed),
                loading: null,
                emails: action.emails
            })
        );
    });
    test(SEND_CONFIRMATION_EMAIL, () => {
        const action = {
            type: SEND_CONFIRMATION_EMAIL
        };

        expect(reducer(state, action)).toEqual(
            Object.assign({}, state, {
                loading: 'email'
            })
        );
    });
    test(RESEND_CONFIRMATION_EMAIL, () => {
        const action = {
            type: RESEND_CONFIRMATION_EMAIL
        };

        expect(reducer(state, action)).toEqual(
            Object.assign({}, state, {
                loading: 'email'
            })
        );
    });
    test(RESEND_CONFIRMATION_EMAIL_SUCCESS, () => {
        const action = {
            type: RESEND_CONFIRMATION_EMAIL_SUCCESS
        };

        expect(reducer(state, action)).toEqual(
            Object.assign({}, state, {
                loading: null
            })
        );
    });
    test(CONFIRM_EMAIL_BY_CODE, () => {
        const action = {
            type: CONFIRM_EMAIL_BY_CODE
        };

        expect(reducer(state, action)).toEqual(
            Object.assign({}, state, {
                loading: 'code'
            })
        );
    });
    test(EMAIL_SET_SAFE_SUCCESS, () => {
        const action = {
            type: EMAIL_SET_SAFE_SUCCESS,
            emails: []
        };

        expect(reducer(state, action)).toEqual(
            Object.assign({}, state, {
                loading: null,
                emails: action.emails
            })
        );
    });
    test(SET_EMAIL_ERROR, () => {
        const action = {
            type: SET_EMAIL_ERROR,
            error: 'value'
        };

        expect(reducer(state, action)).toEqual(
            Object.assign({}, state, {
                error: action.error
            })
        );
    });
    test(TOGGLE_ALIASES_LIST, () => {
        const action = {
            type: TOGGLE_ALIASES_LIST
        };

        expect(reducer(state, action)).toEqual(
            Object.assign({}, state, {
                openAliasesList: !state.openAliasesList
            })
        );
    });
    test(TOGGLE_EMAIL_SELECTION, () => {
        const action = {
            type: TOGGLE_EMAIL_SELECTION,
            email: 'mail'
        };

        expect(reducer(state, action)).toEqual(
            Object.assign({}, state, {
                selectedEmail: action.email
            })
        );
    });
    test(SHOW_EMAIL_DELETE_REQUEST_POPUP, () => {
        const action = {
            type: SHOW_EMAIL_DELETE_REQUEST_POPUP,
            email: 'mail'
        };

        expect(reducer(state, action)).toEqual(
            Object.assign({}, state, {
                selectedEmail: action.email,
                deleteRequestEmail: action.email
            })
        );
    });
    describe(DELETE_EMAIL_ERROR, () => {
        it('should set loading to null', () => {
            const action = {
                type: DELETE_EMAIL_ERROR,
                errors: []
            };

            expect(reducer(state, action)).toEqual(
                Object.assign({}, state, {
                    loading: null
                })
            );
        });
        it('should remove email', () => {
            const action = {
                type: DELETE_EMAIL_ERROR,
                errors: ['email.not_found'],
                email: 'some'
            };

            expect(reducer(state, action)).toEqual(
                Object.assign({}, state, {
                    loading: null,
                    emails: {}
                })
            );
        });
    });
    describe(SEND_CONFIRMATION_EMAIL_ERROR, () => {
        it('should set first error', () => {
            const action = {
                type: SEND_CONFIRMATION_EMAIL_ERROR,
                errors: ['email.not_found']
            };

            expect(reducer(state, action)).toEqual(
                Object.assign({}, state, {
                    loading: null,
                    error: action.errors[0]
                })
            );
        });
        it('should set default error', () => {
            const action = {
                type: SEND_CONFIRMATION_EMAIL_ERROR,
                errors: []
            };

            expect(reducer(state, action)).toEqual(
                Object.assign({}, state, {
                    loading: null,
                    error: 'email.other'
                })
            );
        });
    });
    describe(RESEND_CONFIRMATION_EMAIL_ERROR, () => {
        it('should set first error', () => {
            const action = {
                type: RESEND_CONFIRMATION_EMAIL_ERROR,
                errors: ['email.not_found']
            };

            expect(reducer(state, action)).toEqual(
                Object.assign({}, state, {
                    loading: null,
                    error: action.errors[0]
                })
            );
        });
        it('should set default error', () => {
            const action = {
                type: RESEND_CONFIRMATION_EMAIL_ERROR,
                errors: []
            };

            expect(reducer(state, action)).toEqual(
                Object.assign({}, state, {
                    loading: null,
                    error: 'email.other'
                })
            );
        });
    });
    describe(CONFIRM_EMAIL_BY_CODE_ERROR, () => {
        it('should set first error', () => {
            const action = {
                type: CONFIRM_EMAIL_BY_CODE_ERROR,
                errors: ['email.not_found']
            };

            expect(reducer(state, action)).toEqual(
                Object.assign({}, state, {
                    loading: null,
                    error: action.errors[0]
                })
            );
        });
        it('should set default error', () => {
            const action = {
                type: CONFIRM_EMAIL_BY_CODE_ERROR,
                errors: []
            };

            expect(reducer(state, action)).toEqual(
                Object.assign({}, state, {
                    loading: null,
                    error: 'email.other'
                })
            );
        });
    });
    describe(CHANGE_EMAILS_STATE, () => {
        it('should set custom state', () => {
            const action = {
                type: CHANGE_EMAILS_STATE,
                state: 'some-initial'
            };

            expect(reducer(state, action)).toEqual(
                Object.assign({}, state, {
                    error: null,
                    loading: null,
                    states: ['some']
                })
            );
        });
        it('should set first state', () => {
            const action = {
                type: CHANGE_EMAILS_STATE,
                state: EMAILS_STATES.root
            };

            expect(reducer(state, action)).toEqual(
                Object.assign({}, state, {
                    error: null,
                    loading: null,
                    states: [state.states[0]]
                })
            );
        });
        it('should add state', () => {
            const action = {
                type: CHANGE_EMAILS_STATE,
                state: 'custom'
            };

            expect(reducer(state, action)).toEqual(
                Object.assign({}, state, {
                    error: null,
                    loading: null,
                    states: state.states.concat(action.state)
                })
            );
        });
    });
});
