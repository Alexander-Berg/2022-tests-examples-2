import * as path from 'path';
import { buildServerBundle, getServerExecView } from '../getServerExecView';
import { buildClientBundle, getClientFunc } from '../getClientFunc';
import { runSubTest } from '../runSubTest';
// noinspection ES6PreferShortImport
import { Block, BlockSecond } from './desktop/block/block.view';

jest.setTimeout(60000);

describe('oldViews', () => {
    beforeAll(() => {
        return Promise.all([
            buildServerBundle(__dirname),
            buildClientBundle(__dirname, path.resolve(__dirname, 'desktop/block/block.ts'), path.resolve(__dirname, 'desktop')),
        ]);
    });

    test('server', () => {
        const execView = getServerExecView(__dirname, 'desktopViews');
        expect(execView(Block)).toEqual('Hello inner desktop');
        expect(execView(BlockSecond)).toEqual('second inner2');
    });

    test('client', () => {
        const run = getClientFunc(__dirname, 'run');
        expect(run()).toEqual('second inner2');
    });

    // eslint-disable-next-line jest/expect-expect
    test('tests', () => {
        return Promise.all([
            runSubTest(path.resolve(__dirname, 'common/block/block.test.tsx')),
            runSubTest(path.resolve(__dirname, 'desktop/block/block.test.tsx'))
        ]);
    });
});
