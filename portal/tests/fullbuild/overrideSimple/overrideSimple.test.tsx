/* eslint-disable @typescript-eslint/ban-ts-comment */

import * as path from 'path';
import { buildServerBundle, getServerExecView } from '../getServerExecView';
import { buildClientBundle, getClientFunc } from '../getClientFunc';
import { runSubTest } from '../runSubTest';
// noinspection ES6PreferShortImport
// @ts-ignore
import { Block as BlockCommon } from './common/block/block.view';
// @ts-ignore
import { Block as BlockDesktop } from './desktop/block/block.view';
import { Block as BlockDesktop2 } from './desktop2/block/block.view';

jest.setTimeout(60000);

describe('overrideSimple', () => {
    beforeAll(() => {
        return Promise.all([
            buildServerBundle(__dirname),
            buildClientBundle(__dirname, path.resolve(__dirname, 'desktop2/block/block.ts'), path.resolve(__dirname, 'desktop2')),
        ]);
    });

    test('server', () => {
        const execViewCommon = getServerExecView(__dirname, 'commonViews');
        expect(execViewCommon(BlockCommon)).toEqual('Hello');
        const execViewDesktop = getServerExecView(__dirname, 'desktopViews');
        expect(execViewDesktop(BlockDesktop)).toEqual('HelloDesktop');
        const execViewDesktop2 = getServerExecView(__dirname, 'desktop2Views');
        expect(execViewDesktop2(BlockDesktop2)).toEqual('HelloDesktop2');
    });

    test('client', () => {
        const run = getClientFunc(__dirname, 'run');
        expect(run()).toEqual('HelloDesktop2');
    });

    // eslint-disable-next-line jest/expect-expect
    test('tests', () => {
        return Promise.all([
            runSubTest(path.resolve(__dirname, 'common/block/block.test.tsx')),
            runSubTest(path.resolve(__dirname, 'desktop/block/block.test.tsx'))
        ]);
    });
});
