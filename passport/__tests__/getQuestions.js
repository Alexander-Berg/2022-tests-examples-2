jest.mock('../../api', () => ({
    request: jest.fn()
}));
import api from '../../api';
import {getUserQuestionsList, updateQuestionValues, updateQuestionStates} from '@blocks/actions/form';
import getQuestions from '../methods/getQuestions';
import mockData from './__mocks__/data';

jest.mock('@blocks/actions/form', () => ({
    getUserQuestionsList: jest.fn(),
    updateQuestionValues: jest.fn(),
    updateQuestionStates: jest.fn()
}));

describe('getQuestions', () => {
    beforeEach(function() {
        api.request.mockImplementation(function() {
            const FakeP = function() {
                this.then = function(fn) {
                    const questions = [
                        {id: '0', value: 'не выбран'},
                        {id: '12', value: 'Фамилия вашего любимого музыканта'},
                        {id: '13', value: 'Название улицы, на которой вы выросли'}
                    ];

                    fn({status: 'ok', questions});
                    return this;
                };
            };

            return new FakeP();
        });
    });
    afterEach(function() {
        api.request.mockClear();
    });
    it('should dispatch getUserQuestionsList with array of questions', () => {
        const updatedList = [
            {id: 'q1', text: 'Фамилия вашего любимого музыканта', val: '12'},
            {id: 'q2', text: 'Название улицы, на которой вы выросли', val: '13'}
        ];

        getQuestions()(mockData.props.dispatch, mockData.getState);
        expect(getUserQuestionsList).toBeCalled();
        expect(getUserQuestionsList).toBeCalledWith(updatedList);
    });
    it('should dispatch updateQuestionValues', () => {
        getQuestions()(mockData.props.dispatch, mockData.getState);
        expect(updateQuestionValues).toBeCalled();
        expect(updateQuestionValues).toBeCalledWith({
            hint_question_id: '12',
            hint_question: 'Фамилия вашего любимого музыканта'
        });
    });
    it('should dispatch updateQuestionStates with valid status', () => {
        getQuestions()(mockData.props.dispatch, mockData.getState);
        expect(updateQuestionStates).toBeCalled();
        expect(updateQuestionStates).toBeCalledWith({status: 'valid'});
    });
});
