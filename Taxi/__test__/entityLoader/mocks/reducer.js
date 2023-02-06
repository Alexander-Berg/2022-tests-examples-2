import createConsts from '_pkg/utils/createConsts';
import createEntityReducer from '_pkg/utils/createEntityReducer';

const constants = createConsts('TEST')({
    REQUEST: null,
    REQUEST_SUCCESS: null,
    REQUEST_ERROR: null,

    LOAD: null,
    LOAD_SUCCESS: null,
    LOAD_ERROR: null,

    CREATE: null,
    CREATE_SUCCESS: null,
    CREATE_ERROR: null,

    UPDATE: null,
    UPDATE_SUCCESS: null,
    UPDATE_ERROR: null,

    REMOVE: null,
    REMOVE_SUCCESS: null,
    REMOVE_ERROR: null,

    FIND: null,
    FIND_SUCCESS: null,
    FIND_ERROR: null
});

const reducer = createEntityReducer({
    request: [constants.REQUEST, constants.REQUEST_SUCCESS, constants.REQUEST_ERROR],
    load: [constants.LOAD, constants.LOAD_SUCCESS, constants.LOAD_ERROR],
    create: [constants.CREATE, constants.CREATE_SUCCESS, constants.CREATE_ERROR],
    update: [constants.UPDATE, constants.UPDATE_SUCCESS, constants.UPDATE_ERROR],
    remove: [constants.REMOVE, constants.REMOVE_SUCCESS, constants.REMOVE_ERROR],
    find: [constants.FIND, constants.FIND_SUCCESS, constants.FIND_ERROR]
}, {}, {idKey: 'id'});

export const actions = reducer.actions;
export default reducer;
