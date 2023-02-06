import {isPackageChanged, LERNA_CHANGED_COMMAND} from '../utils';

jest.mock('child_process');

describe('isPackageChanged', () => {
    test('has changed', async () => {
        require('child_process').__setResponse(LERNA_CHANGED_COMMAND(), () => [
            undefined,
            `
                [{
                    "name": "@tariff-editor/users",
                    "version": "0.106.0",
                    "private": true,
                    "location": "/home/ktnglazachev/www/tariff-editor/packages/users"
                },
                {
                    "name": "@tariff-editor/vendors",
                    "version": "0.49.0",
                    "private": true,
                    "location": "/home/ktnglazachev/www/tariff-editor/packages/vendors"
                }]
            `,
            ''
        ]);

        expect(await isPackageChanged('test')).toBe(false);
        expect(await isPackageChanged('users')).toBe(true);
        expect(await isPackageChanged('@tariff-editor/vendors')).toBe(true);
    });

    test('no changed', async () => {
        require('child_process').__setResponse(LERNA_CHANGED_COMMAND(), () => [undefined, '', '']);

        expect(await isPackageChanged('test')).toBe(false);
        expect(await isPackageChanged('users')).toBe(false);
        expect(await isPackageChanged('@tariff-editor/vendors')).toBe(false);
    });

    test('unexpected output', async () => {
        require('child_process').__setResponse(LERNA_CHANGED_COMMAND(), () => [undefined, 'bla bla bla', '']);

        expect(await isPackageChanged('test')).toBe(false);
        expect(await isPackageChanged('users')).toBe(false);
        expect(await isPackageChanged('@tariff-editor/vendors')).toBe(false);
    });
});
