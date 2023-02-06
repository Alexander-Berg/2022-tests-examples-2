import {cloneDeep} from 'lodash';

import {STORAGE_PREFIX} from '_pkg/constants/application';
import {PersistentKey, StorageType} from '_types/common/infrastructure';

import persistent, {actions} from '../persistent';

describe('persistent reducer', () => {
    beforeEach(() => {
        localStorage.clear();
        sessionStorage.clear();
    });

    test('defaults', () => {
        const state = persistent(undefined, null);
        expect(state).toEqual({
            [StorageType.LocalStorage]: {},
            [StorageType.SessionStorage]: {}
        });
    });

    test('set local storage value', () => {
        const key = 'key' as PersistentKey<{x: {y: number}}>;
        let state = persistent(undefined, null);

        const value = {x: {y: 1}};
        state = persistent(state, actions.set(key, value));

        expect(localStorage.setItem)
            .toHaveBeenLastCalledWith(`${STORAGE_PREFIX}.${key}`, JSON.stringify({value}));
        expect(state[StorageType.LocalStorage]).toEqual({
            [key]: cloneDeep(value)
        });
    });

    test('set session storage value', () => {
        const key = 'key' as PersistentKey<{x: {y: number}}>;
        let state = persistent(undefined, null);

        const value = {x: {y: 1}};
        state = persistent(state, actions.set(key, value, StorageType.SessionStorage));

        expect(sessionStorage.setItem)
            .toHaveBeenLastCalledWith(`${STORAGE_PREFIX}.${key}`, JSON.stringify({value}));
        expect(state[StorageType.SessionStorage]).toEqual({
            [key]: cloneDeep(value)
        });
    });

    test('set local storage equal value', () => {
        const key = 'key' as PersistentKey<{x: {y: number}}>;
        const lsCalled = (localStorage.setItem as jest.Mock).mock.calls.length;

        let state = persistent(undefined, null);

        state = persistent(state, actions.set(key, {x: {y: 1}}));
        const prevData = state[StorageType.LocalStorage][key];

        state = persistent(state, actions.set(key, {x: {y: 1}}));
        expect(state[StorageType.LocalStorage][key]).toBe(prevData);

        // для одинаковых значений не вызывается повтороно запись в сторедж
        expect(localStorage.setItem).toHaveBeenCalledTimes(lsCalled + 1);
    });

    test('set session storage equal value', () => {
        const key = 'key' as PersistentKey<{x: {y: number}}>;
        const lsCalled = (sessionStorage.setItem as jest.Mock).mock.calls.length;

        let state = persistent(undefined, null);

        state = persistent(state, actions.set(key, {x: {y: 1}}, StorageType.SessionStorage));
        const prevData = state[StorageType.SessionStorage][key];

        state = persistent(state, actions.set(key, {x: {y: 1}}, StorageType.SessionStorage));
        expect(state[StorageType.SessionStorage][key]).toBe(prevData);

        // для одинаковых значений не вызывается повтороно запись в сторедж
        expect(sessionStorage.setItem).toHaveBeenCalledTimes(lsCalled + 1);
    });

    test('set local storage different value', () => {
        const key = 'key' as PersistentKey<{x: {y: number}}>;
        const lsCalled = (localStorage.setItem as jest.Mock).mock.calls.length;

        let state = persistent(undefined, null);

        state = persistent(state, actions.set(key, {x: {y: 1}}));
        state = persistent(state, actions.set(key, {x: {y: 2}}));
        expect(state[StorageType.LocalStorage][key]).toEqual({x: {y: 2}});

        expect(localStorage.setItem).toHaveBeenCalledTimes(lsCalled + 2);
    });

    test('set session storage different value', () => {
        const key = 'key' as PersistentKey<{x: {y: number}}>;
        const lsCalled = (sessionStorage.setItem as jest.Mock).mock.calls.length;

        let state = persistent(undefined, null);

        state = persistent(state, actions.set(key, {x: {y: 1}}, StorageType.SessionStorage));
        state = persistent(state, actions.set(key, {x: {y: 2}}, StorageType.SessionStorage));
        expect(state[StorageType.SessionStorage][key]).toEqual({x: {y: 2}});

        expect(sessionStorage.setItem).toHaveBeenCalledTimes(lsCalled + 2);
    });

    test('set local storage different keys', () => {
        const key1 = 'key1' as PersistentKey<{x: {y: number}}>;
        const key2 = 'key2' as PersistentKey<{x: {y: number}}>;
        const lsCalled = (localStorage.setItem as jest.Mock).mock.calls.length;

        let state = persistent(undefined, null);

        state = persistent(state, actions.set(key1, {x: {y: 1}}));
        state = persistent(state, actions.set(key2, {x: {y: 2}}));
        expect(state[StorageType.LocalStorage]).toEqual({
            [key1]: {x: {y: 1}},
            [key2]: {x: {y: 2}}
        });

        expect(localStorage.setItem).toHaveBeenCalledTimes(lsCalled + 2);
    });

    test('set session storage different keys', () => {
        const key1 = 'key1' as PersistentKey<{x: {y: number}}>;
        const key2 = 'key2' as PersistentKey<{x: {y: number}}>;
        const lsCalled = (sessionStorage.setItem as jest.Mock).mock.calls.length;

        let state = persistent(undefined, null);

        state = persistent(state, actions.set(key1, {x: {y: 1}}, StorageType.SessionStorage));
        state = persistent(state, actions.set(key2, {x: {y: 2}}, StorageType.SessionStorage));
        expect(state[StorageType.SessionStorage]).toEqual({
            [key1]: {x: {y: 1}},
            [key2]: {x: {y: 2}}
        });

        expect(sessionStorage.setItem).toHaveBeenCalledTimes(lsCalled + 2);
    });

    describe('existing local storage', () => {
        const key = 'key' as PersistentKey<number>;

        beforeEach(() => {
            localStorage.clear();
            localStorage.setItem(`${STORAGE_PREFIX}.${key}`, JSON.stringify({
                value: 2
            }));
        });

        test('restore value', () => {
            const state = persistent(undefined, null);
            expect(state[StorageType.LocalStorage][key]).toBe(2);
        });
    });

    describe('existing session storage', () => {
        const key = 'key' as PersistentKey<number>;

        beforeEach(() => {
            sessionStorage.clear();
            sessionStorage.setItem(`${STORAGE_PREFIX}.${key}`, JSON.stringify({
                value: 2
            }));
        });

        test('restore value', () => {
            const state = persistent(undefined, null);
            expect(state[StorageType.SessionStorage][key]).toBe(2);
        });
    });
});
