import createActionTypes from '../createActionTypes';

const requestActionTypes = {
    request: 'TEST_REQUEST',
    requestSuccess: 'TEST_REQUEST_SUCCESS',
    requestError: 'TEST_REQUEST_ERROR',
    requestClear: 'TEST_REQUEST_CLEAR'
};
const updateActionTypes = {
    update: 'TEST_UPDATE',
    updateSuccess: 'TEST_UPDATE_SUCCESS',
    updateError: 'TEST_UPDATE_ERROR'
};

describe('utils:createEntityReducer:createActionTypes', () => {
    test('should throw an error for unknown action group', () => {
        expect(() => createActionTypes({unknown: 'UNKNOWN'})).toThrow('Unknown action group "unknown"');
    });

    test('should throw an error for falsy type prefix', () => {
        const errorMessage = 'Incorrect group "request" type prefix. It can\'t be falsy value';
        expect(() => createActionTypes({request: undefined})).toThrow(errorMessage);
        expect(() => createActionTypes({request: null})).toThrow(errorMessage);
        expect(() => createActionTypes({request: ''})).toThrow(errorMessage);
    });

    test('request action types', () => {
        expect(createActionTypes({request: 'TEST'})).toEqual(requestActionTypes);
    });

    test('load action types', () => {
        expect(createActionTypes({load: 'TEST'})).toEqual({
            load: 'TEST_LOAD',
            loadSuccess: 'TEST_LOAD_SUCCESS',
            loadError: 'TEST_LOAD_ERROR'
        });
    });

    test('create action types', () => {
        expect(createActionTypes({create: 'TEST'})).toEqual({
            create: 'TEST_CREATE',
            createSuccess: 'TEST_CREATE_SUCCESS',
            createError: 'TEST_CREATE_ERROR'
        });
    });

    test('update action types', () => {
        expect(createActionTypes({update: 'TEST'})).toEqual(updateActionTypes);
    });

    test('remove action types', () => {
        expect(createActionTypes({remove: 'TEST'})).toEqual({
            remove: 'TEST_REMOVE',
            removeSuccess: 'TEST_REMOVE_SUCCESS',
            removeError: 'TEST_REMOVE_ERROR'
        });
    });

    test('find action types', () => {
        expect(createActionTypes({find: 'TEST'})).toEqual({
            find: 'TEST_FIND',
            findSuccess: 'TEST_FIND_SUCCESS',
            findError: 'TEST_FIND_ERROR',
            findClear: 'TEST_FIND_CLEAR'
        });
    });

    test('should correctly merge actions of different groups', () => {
        expect(createActionTypes({request: 'TEST', update: 'TEST'})).toEqual({
            ...requestActionTypes,
            ...updateActionTypes
        });
    });
});
