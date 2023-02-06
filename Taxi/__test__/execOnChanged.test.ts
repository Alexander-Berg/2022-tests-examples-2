import {execOnChanged, LERNA_CHANGED_COMMAND} from '../utils';

jest.mock('child_process');

describe('execOnChanged', () => {
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

        const res = await execOnChanged(`test`);
        expect(res?.trim()).toBe(
            'npx lerna exec --stream --scope @tariff-editor/users --scope @tariff-editor/vendors test'
        );
    });

    test('no changed', async () => {
        require('child_process').__setResponse(LERNA_CHANGED_COMMAND(), () => [undefined, '', '']);

        const res = await execOnChanged(`test`);
        expect(res).toBe(undefined);
    });

    test('unexpected output', async () => {
        require('child_process').__setResponse(LERNA_CHANGED_COMMAND(), () => [undefined, 'bla bla bla', '']);

        const res = await execOnChanged(`test`);
        expect(res).toBe(undefined);
    });
});
