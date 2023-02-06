import test from 'ava';
import reducer from '../../src/redux/reducers';
import { SET_CAROUSEL } from '../../src/redux/actions/types';

test.beforeEach(() => {
    global.window = {};
});

test('Reducer', t => {
    const action = { type: SET_CAROUSEL, payload: { height: 42 } };
    let state = { appData: {}, carousel: null };

    state = reducer(state, action);

    t.is(state.carousel.height, 42);
});
