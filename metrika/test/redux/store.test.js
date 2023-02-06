import test from 'ava';
import getInitialStore from '../../src/redux/state';
import configureDevStore from '../../src/redux/store/configure-store.dev';
import configureProdStore from '../../src/redux/store/configure-store.prod';

test.beforeEach(() => {
    global.window = {};
});

test('Configure dev store', t => {
    const initialState = getInitialStore({});
    const store = configureDevStore(initialState);

    t.is(typeof store, 'object');
    t.deepEqual(store.getState(), initialState);
});

test('Configure production store', t => {
    const initialState = getInitialStore({});
    const store = configureProdStore(initialState);

    t.is(typeof store, 'object');
    t.deepEqual(store.getState(), initialState);
});
