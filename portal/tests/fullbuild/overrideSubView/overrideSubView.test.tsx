import * as path from 'path';
import { buildServerBundle, getServerExecView } from '../getServerExecView';
import { buildClientBundle, getClientFunc } from '../getClientFunc';
import { runSubTest } from '../runSubTest';
// noinspection ES6PreferShortImport
import { Block } from './desktop/block/block.view';

jest.setTimeout(60000);

describe('overrideSubView', () => {
    beforeAll(() => {
        return Promise.all([
            buildServerBundle(__dirname),
            buildClientBundle(__dirname, path.resolve(__dirname, 'desktop/block/block.ts'), path.resolve(__dirname, 'desktop')),
        ]);
    });

    test('server', () => {
        const execView = getServerExecView(__dirname, 'desktopViews');
        expect(execView(Block)).toEqual('Hello inner desktop other+other2_desktop');
    });

    test('client', () => {
        const run = getClientFunc(__dirname, 'run');
        expect(run()).toEqual('Hello inner desktop other+other2_desktop');
        const runInner = getClientFunc(__dirname, 'runInner');
        expect(runInner()).toEqual('inner desktop');
    });

    // eslint-disable-next-line jest/expect-expect
    test('tests', () => {
        return Promise.all([
            runSubTest(path.resolve(__dirname, 'common/block/block.test.tsx')),
            runSubTest(path.resolve(__dirname, 'desktop/block/block.test.tsx'))
        ]);
    });
});
