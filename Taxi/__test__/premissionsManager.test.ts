
import {createStore} from 'redux';

import PermissionsManager from '../PermissionsManager';

const PERMISSIONS_SET = {
    permission_1: true,
    permission_2: true,
    permission_3: true
};

const rootReducer = () => {
    return  {
        userInfo: {
            permissions: PERMISSIONS_SET
        }
    };
};

const store = createStore(rootReducer);

const permissionsManager = new PermissionsManager(store, s => s.userInfo.permissions);

describe('PermissionsManager', function () {
    test('single permission', () => {
        expect(permissionsManager.hasPermission('permission_1')).toBe(true);
    });

    test('permissions set', () => {
        expect(permissionsManager.hasPermission(['permission_1', 'permission_4'])).toBe(true);
    });

    test('has all permission', () => {
        expect(permissionsManager.hasPermission(['permission_1', 'permission_4'], false)).toBe(false);
        expect(permissionsManager.hasPermission(['permission_1', 'permission_2'], false)).toBe(true);
    });

    test('empty permission', () => {
        expect(permissionsManager.hasPermission(undefined)).toBe(true);
        expect(permissionsManager.hasPermission('')).toBe(true);
        expect(permissionsManager.hasPermission(null)).toBe(true);
        expect(permissionsManager.hasPermission([])).toBe(true);
    });
});
