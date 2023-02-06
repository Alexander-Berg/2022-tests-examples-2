import {createAction, handleActions} from 'redux-actions';

const defaultState = {
    status: null,
    topics: null,
    question: null,
    results: null
};

export const actions = {
    getTopics: createAction('GET_TOPICS'),
    getTopicsSuccess: createAction('GET_TOPICS_SUCCESS'),
    getTopicsError: createAction('GET_TOPICS_ERROR'),
    resetTopics: createAction('RESET_TOPICS'),

    getQuestionSuccess: createAction('GET_QUESTION_SUCCESS'),
    resetQuestion: createAction('RESET_QUESTION'),

    getResultsSuccess: createAction('GET_RESULT_SUCCESS'),
    resetResults: createAction('RESET_RESULTS')
};

const reducer = handleActions({
    [actions.getTopics]: (state, action) => {
        return {
            ...state,
            status: 'pending'
        };
    },
    [actions.getTopicsSuccess]: (state, action) => {
        return {
            ...state,
            status: 'success',
            topics: action.payload
        };
    },
    [actions.getTopicsError]: state => {
        return {...state, topics: 'error'};
    },
    [actions.resetTopics]: state => {
        return {...state, topics: null};
    },
    [actions.getQuestionSuccess]: (state, action) => {
        return {...state, question: action.payload};
    },
    [actions.resetQuestion]: state => {
        return {...state, question: null};
    },
    [actions.getResultsSuccess]: (state, action) => {
        return {...state, results: action.payload};
    },
    [actions.resetResults]: state => {
        return {...state, results: null};
    }
}, defaultState);

export default reducer;
