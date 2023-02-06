import * as path from 'path';
import { buildServerBundle, getServerExecView } from '../getServerExecView';
import { buildClientBundle, getClientBundleContents, getClientFunc } from '../getClientFunc';
// noinspection ES6PreferShortImport
import { Block } from './common/block/block.view';

jest.setTimeout(60000);

describe('replaceConst', () => {
    beforeAll(() => {
        return Promise.all([
            buildServerBundle(__dirname),
            buildClientBundle(__dirname, path.resolve(__dirname, 'common/block/block.ts'), path.resolve(__dirname, 'common')),
        ]);
    });

    test('server', () => {
        const execView = getServerExecView(__dirname, 'commonViews');
        expect(execView(Block)).toEqual('only-server string');
    });

    test('client run', () => {
        const run = getClientFunc(__dirname, 'run');
        expect(run()).toEqual('client string');
    });

    test('client script should not contain server template', () => {
        const bundle = getClientBundleContents(__dirname);
        expect(bundle).not.toContain('only-server string');
    });

    test('client script should not contain unused templates', () => {
        const bundle = getClientBundleContents(__dirname);
        expect(bundle).not.toContain('Unused code');
    });
});
