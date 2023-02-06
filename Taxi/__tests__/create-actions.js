import createActions, {createActionTypes} from '../create-actions';

describe('utils:createAction', () => {
    const actionTypes = {
        testAction: 'TEST_ACTION_TYPE'
    };

    test('createActionTypes', () => {
        const actionTypes = {request: null, requestSuccess: null, requestError: null};
        expect(createActionTypes(actionTypes)).toEqual({
            request: 'REQUEST',
            requestSuccess: 'REQUEST_SUCCESS',
            requestError: 'REQUEST_ERROR'
        });

        expect(createActionTypes(actionTypes, 'TEST')).toEqual({
            request: 'TEST_REQUEST',
            requestSuccess: 'TEST_REQUEST_SUCCESS',
            requestError: 'TEST_REQUEST_ERROR'
        });
    });

    test('Должен возвращаться объект правильного формата', () => {
        expect(createActions(actionTypes)).toEqual({
            testAction: expect.any(Function)
        });
    });

    test('Должен возвращаеться правильный экшн', () => {
        const payload = 'test payload';
        const actions = createActions(actionTypes);
        expect(actions.testAction(payload)).toEqual({type: actionTypes.testAction, payload});
    });
});
