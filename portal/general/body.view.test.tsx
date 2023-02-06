/* eslint-disable @typescript-eslint/ban-ts-comment */

import { execView } from '@lib/views/execView';
import { mockView, restoreViews } from '@lib/views/mock';
import { mockReq } from '@lib/views/mockReq';
import { DepsTree } from '@lib/utils/depsTree';
// import { Search3 } from '@block/search3/search3.view';
// import { Mtabs } from '@block/mtabs/mtabs.view';
import { Mlogo } from '@block/mlogo/mlogo.view';
import { BannerDebug } from '@block/banner-debug/banner-debug.view';
import { Body__blocksBottom, Body__blocksTail } from '@block/body/body.view';
import { Search3 } from '@block/search3/search3.view';
import { News } from '@block/news/news.view';
// @ts-ignore
import { Banner } from '@block/banner/banner.view';
// @ts-ignore
import { Tv } from '@block/tv/tv.view';

// todo move to imports

describe('body', () => {
    describe('split-inline', () => {
        let getSpy: jest.SpyInstance;
        let postponeSpy: jest.SpyInstance;
        const createOverride = () => {
            const depsTree = new DepsTree({}, new Proxy({}, {
                get: (target, key) => key
            }));
            getSpy = jest.spyOn(depsTree, 'get');
            postponeSpy = jest.spyOn(depsTree, 'postpone');
            return {
                depsTree,
                blocks_layout: [
                    'news',
                    'tv'
                ],
                options: {
                    disable_plus_wallet_touch: '1'
                }
            };
        };

        let origFlag: boolean;
        beforeEach(() => {
            mockView(BannerDebug, () => '');
            mockView(Mlogo, () => 'Logo');
            mockView(Search3, () => '');

            mockView(Banner, () => '');
            mockView(Body__blocksBottom, () => []);
            mockView(Body__blocksTail, () => []);

            mockView(News, () => 'News');
            mockView(Tv, () => 'Tv');

            origFlag = home.env.inlineCss;
            home.env.inlineCss = true;
        });

        afterEach(() => {
            restoreViews();

            home.env.inlineCss = origFlag;
        });

        test('process without group exp', () => {
            const req = mockReq({}, createOverride());

            expect(execView('Body__content', {}, req)).toMatchSnapshot();
            expect(getSpy.mock.calls).toMatchSnapshot();
            expect(postponeSpy.mock.calls).toMatchSnapshot();
        });
    });
});
