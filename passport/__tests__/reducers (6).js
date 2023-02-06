import {UPDATE_AVATAR, SET_AVATAR_ERROR} from '../actions';
import reducer from '../reducers';

const state = {
    track_id: undefined,
    url: null,
    backupAvatar: {
        url: ''
    },
    hasChanged: false,
    isByUrl: false,
    loadUrlPath: '',
    isDeletePossible: false,
    status: 'normal',
    type: 'jpeg',
    error: ''
};

describe('Morda.Avatar.reducers', () => {
    describe(UPDATE_AVATAR, () => {
        it('should set many things', () => {
            const action = {
                type: UPDATE_AVATAR,
                data: {
                    hasChanged: true,
                    avatarUrl: 'value',
                    backupAvatar: 'value',
                    isByUrl: 'value',
                    queryUid: 'value',
                    loadUrlPath: 'value'
                }
            };

            expect(reducer(state, action)).toEqual(
                Object.assign({}, state, {
                    hasChanged: action.data.hasChanged,
                    url: action.data.avatarUrl,
                    backupAvatar: action.data.backupAvatar,
                    isByUrl: action.data.isByUrl,
                    queryUid: action.data.queryUid,
                    loadUrlPath: action.data.loadUrlPath,
                    isDeletePossible: false
                })
            );
        });
        it('should set hasChanged to false by default', () => {
            expect(
                reducer(state, {
                    type: UPDATE_AVATAR,
                    data: {}
                }).hasChanged
            ).toBe(false);
        });
    });
    describe(SET_AVATAR_ERROR, () => {
        it('should set error, hasChanged and status', () => {
            const action = {
                type: SET_AVATAR_ERROR,
                error: 'value'
            };

            expect(reducer(state, action)).toEqual(
                Object.assign({}, state, {
                    error: action.error,
                    hasChanged: false
                })
            );
        });
        it('should set status from state', () => {
            const action = {
                type: SET_AVATAR_ERROR
            };

            expect(reducer(state, action)).toEqual(
                Object.assign({}, state, {
                    error: '',
                    hasChanged: false
                })
            );
        });
        it('should set normal status', () => {
            const copy = Object.assign({}, state, {
                status: undefined
            });
            const action = {
                type: SET_AVATAR_ERROR
            };

            expect(reducer(copy, action)).toEqual(
                Object.assign({}, copy, {
                    error: '',
                    hasChanged: false
                })
            );
        });
    });
    it('should return same state', () => {
        expect(reducer()).toEqual(state);
    });
});
