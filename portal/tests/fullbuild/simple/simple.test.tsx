import * as path from 'path';
import { buildServerBundle, getServerExecView } from '../getServerExecView';
import { buildClientBundle, getClientFunc } from '../getClientFunc';
import { runSubTest } from '../runSubTest';
// noinspection ES6PreferShortImport
import { Block } from './common/block/block.view';

jest.setTimeout(60000);

describe('simple', () => {
    beforeAll(() => {
        return Promise.all([
            buildServerBundle(__dirname),
            buildClientBundle(__dirname, path.resolve(__dirname, 'common/block/block.ts'), path.resolve(__dirname, 'common')),
        ]);
    });

    test('server', () => {
        const execView = getServerExecView(__dirname, 'commonViews');
        expect(execView(Block)).toEqual('Hello');
    });

    test('client', () => {
        const run = getClientFunc(__dirname, 'run');
        expect(run()).toEqual('Hello');
    });

    // eslint-disable-next-line jest/expect-expect
    test('tests', () => {
        const testPath = path.resolve(__dirname, 'common/block/block.test.tsx');

        return runSubTest(testPath);
    });
});
