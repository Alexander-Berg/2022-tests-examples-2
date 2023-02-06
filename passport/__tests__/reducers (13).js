import {
    SAVE_KVKO,
    SET_QUESTIONS,
    SAVE_KVKO_FAIL,
    SHOW_KVKO_MODAL,
    SAVE_KVKO_SUCCESS,
    VALIDATE_KVKO_FORM,
    SET_KVKO_UPDATE_STATUS,
    CHANGE_CONTROL_QUESTION
} from '../actions';
import reducer from '../reducers';

const state = {
    visible: null,
    current: null,
    selected: null,
    loading: false,
    updated: false,
    errors: {
        some: 'value'
    }
};

describe('Morda.Security.UserQuestion.reducers', () => {
    it('should return default state', () => {
        expect(reducer(undefined, {})).toEqual({});
    });
    test(CHANGE_CONTROL_QUESTION, () => {
        const action = {
            type: CHANGE_CONTROL_QUESTION,
            id: 'value'
        };

        expect(reducer(state, action)).toEqual(
            Object.assign({}, state, {
                selected: action.id
            })
        );
    });
    test(SAVE_KVKO, () => {
        const action = {
            type: SAVE_KVKO
        };

        expect(reducer(state, action)).toEqual(
            Object.assign({}, state, {
                loading: true
            })
        );
    });
    test(SAVE_KVKO_SUCCESS, () => {
        const action = {
            type: SAVE_KVKO_SUCCESS,
            currentQuestion: 'value'
        };

        expect(reducer(state, action)).toEqual(
            Object.assign({}, state, {
                selected: '0',
                visible: false,
                loading: false,
                current: action.currentQuestion,
                updated: true
            })
        );
    });
    test(SAVE_KVKO_FAIL, () => {
        const action = {
            type: SAVE_KVKO_FAIL,
            res: {
                errors: [
                    'compare.not_matched',
                    'rate.limit_exceeded',
                    'question.long',
                    'new_answer.long',
                    'old_answer.long'
                ]
            }
        };

        expect(reducer(state, action)).toEqual(
            Object.assign({}, state, {
                errors: {
                    newAnswer: 'long',
                    oldAnswer: 'long',
                    ownQuestion: 'long',
                    rateLimitExceeded: true
                },
                loading: false
            })
        );
    });
    test(SET_KVKO_UPDATE_STATUS, () => {
        const action = {
            type: SET_KVKO_UPDATE_STATUS,
            updated: 'value'
        };

        expect(reducer(state, action)).toEqual(
            Object.assign({}, state, {
                updated: action.updated
            })
        );
    });
    test(SET_QUESTIONS, () => {
        const action = {
            type: SET_QUESTIONS,
            questions: 'value'
        };

        expect(reducer(state, action)).toEqual(
            Object.assign({}, state, {
                available: action.questions
            })
        );
    });
    describe(SHOW_KVKO_MODAL, () => {
        it('should set visible', () => {
            const action = {
                type: SHOW_KVKO_MODAL,
                visible: 'value'
            };

            expect(reducer(state, action)).toEqual(
                Object.assign({}, state, {
                    visible: action.visible
                })
            );
        });
        it('should clear errors', () => {
            const action = {
                type: SHOW_KVKO_MODAL,
                visible: false
            };

            expect(reducer(state, action)).toEqual(
                Object.assign({}, state, {
                    errors: {},
                    visible: false
                })
            );
        });
    });
    describe(VALIDATE_KVKO_FORM, () => {
        test('if newQuestionId not 0', () => {
            const action = {
                type: VALIDATE_KVKO_FORM,
                data: {
                    some: 'value',
                    another: ''
                }
            };

            expect(reducer(state, action)).toEqual(
                Object.assign({}, state, {
                    errors: {
                        another: 'empty'
                    }
                })
            );
        });
        test('if newQuestionId 0', () => {
            const action = {
                type: VALIDATE_KVKO_FORM,
                data: {
                    some: 'value',
                    another: '',
                    newQuestionId: '0'
                }
            };

            expect(reducer(state, action)).toEqual(
                Object.assign({}, state, {
                    errors: {
                        another: 'empty',
                        newQuestionId: 'empty'
                    }
                })
            );
        });
    });
});
