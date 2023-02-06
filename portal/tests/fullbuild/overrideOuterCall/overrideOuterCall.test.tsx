import * as path from 'path';
import { buildServerBundle, getServerExecView } from '../getServerExecView';
import { buildClientBundle, getClientFunc } from '../getClientFunc';
import { runSubTest } from '../runSubTest';
// noinspection ES6PreferShortImport
import { Block2 } from './common/block2/block2.view';

jest.setTimeout(60000);

describe('overrideOuterCall', () => {
    beforeAll(() => {
        return Promise.all([
            buildServerBundle(__dirname),
            buildClientBundle(__dirname, path.resolve(__dirname, 'common/block2/block2.ts'), path.resolve(__dirname, 'desktop')),
        ]);
    });

    test('server', () => {
        const execView = getServerExecView(__dirname, 'desktopViews');
        expect(execView(Block2)).toEqual('HelloDesktop');
    });

    test('client', () => {
        const run = getClientFunc(__dirname, 'run');
        expect(run()).toEqual('HelloDesktop');
    });

    // eslint-disable-next-line jest/expect-expect
    test('tests', async() => {
        return Promise.all([
            runSubTest(path.resolve(__dirname, 'common/block/block.test.tsx')),
            runSubTest(path.resolve(__dirname, 'common/block2/block2.test.tsx')),
            runSubTest(path.resolve(__dirname, 'desktop/block2/block2.test.tsx'))
        ]);
    });
});
