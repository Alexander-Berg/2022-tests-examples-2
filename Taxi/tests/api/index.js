import {notification} from 'antd';

import {api} from '../../../../../utils/httpApi';
import {actions} from '../reducers';

export default class Tests {
    static loadTopics = () => dispatch => {
        return api.get('training/get_topics')
            .then(response => {
                dispatch(actions.getTopicsSuccess(response));
            })
            .catch(error => {
                notification.error({message: 'Тесты не загрузились'});
                dispatch(actions.getTopicsError());
                throw error;
            });
    };

    static loadQuestion = topic => dispatch => {
        return api.post('training/get_question', {topic})
            .then(response => {
                dispatch(actions.getQuestionSuccess(response));
            })
            .catch(error => {
                dispatch(actions.resetQuestion());
                throw error;
            });
    };

    static resetQuestion = () => dispatch => dispatch(actions.resetQuestion());

    static validateAnswer = answer => dispatch => {
        return api.post('training/validate_answer', answer)
            .then(response => {
                return response;
            })
            .catch(error => {
                throw error;
            });
    };

    static getResults = topic => dispatch => {
        return api.post('training/get_result', {topic})
            .then(response => {
                return dispatch(actions.getResultsSuccess(response));
            })
            .catch(error => {
                throw error;
            });
    };

    static resetResults = () => dispatch => dispatch(actions.resetResults());

    static dropAnswers = topic => dispatch => {
        return api.get('training/drop_answers')
            .then(() => {
                if (topic) {
                    dispatch(Tests.loadQuestion(topic));
                } else {
                    dispatch(actions.resetTopics());
                    dispatch(Tests.loadTopics());
                }
            })
            .catch(error => {
                throw error;
            });
    };
}
