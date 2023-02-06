import dashboard from '../reducers';
import {SET_DB_DATA, SET_PLUS_ENABLED, SET_PLUS_NEXT_CHARGE_TIME} from '../actions';

const state = {
    clientWidth: 0
};

describe('social reducer', () => {
    test(SET_PLUS_NEXT_CHARGE_TIME, () => {
        expect(
            dashboard(state, {
                nextChargeTime: 'lol',
                type: SET_PLUS_NEXT_CHARGE_TIME
            })
        ).toEqual(
            Object.assign({}, state, {
                plus: {
                    nextChargeTime: 'lol'
                }
            })
        );
    });
    describe(SET_PLUS_ENABLED, () => {
        it('should drop nextChargeTime', () => {
            expect(
                dashboard(state, {
                    type: SET_PLUS_ENABLED,
                    enabled: false
                })
            ).toEqual(
                Object.assign({}, state, {
                    plus: {
                        nextChargeTime: 0,
                        enabled: false
                    }
                })
            );
        });
        it('should set enabled', () => {
            expect(
                dashboard(state, {
                    type: SET_PLUS_ENABLED,
                    enabled: true
                }).plus.enabled
            ).toBe(true);
        });
    });
    test(SET_DB_DATA, () => {
        expect(
            dashboard(
                {},
                {
                    type: SET_DB_DATA,
                    service: 'someService',
                    data: 'data'
                }
            )
        ).toEqual({
            someService: 'data'
        });
    });
    test('action not found', () => {
        expect(dashboard(state, {type: 'LOL_ACTION_NOT_FOUND'})).toEqual(state);
    });
    test('state default value', () => {
        expect(dashboard(undefined, {type: 'LOL_ACTION_NOT_FOUND'})).toEqual({});
    });
});
