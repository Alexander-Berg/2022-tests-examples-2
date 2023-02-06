import * as sinon from 'sinon';
import {
    PRERENDER_BR_KEY,
    usePrerenderProvider,
} from '@src/providers/prerender';
import { CounterOptions } from '@src/utils/counterOptions';
import * as browserUtils from '@src/utils/browser';
import * as sender from '@src/sender';
import * as browserInfoUtils from '@src/utils/browserInfo';
import { WATCH_REFERER_PARAM, WATCH_URL_PARAM } from '@src/sender/watch';
import * as location from '@src/utils/location';
import { ARTIFICIAL_BR_KEY } from '@src/providers/artificialHit/type';

describe('prerender provider', () => {
    const url = 'test.ru';
    const ref = 'ref.ru';
    const options = {};
    const almostPromise = { catch() {} } as any;
    let isPrerender: boolean;

    let browserInfoStub: sinon.SinonStub;
    let senderSpy: sinon.SinonSpy;
    const sandbox = sinon.createSandbox();

    beforeEach(() => {
        senderSpy = sandbox.stub().returns(almostPromise);
        sandbox.stub(browserUtils, 'isPrerender').callsFake(() => isPrerender);
        sandbox.stub(sender, 'getSender').returns(senderSpy);
        browserInfoStub = sandbox
            .stub(browserInfoUtils, 'browserInfo')
            .returns({ test: 'test' } as any);
        sandbox.stub(location, 'getLocation').returns({ href: url } as any);
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('should not send prerender hit', () => {
        isPrerender = false;
        usePrerenderProvider({} as any, {} as any);
        sinon.assert.notCalled(browserInfoStub);
        sinon.assert.notCalled(senderSpy);
    });
    it('should send prerender hit', () => {
        isPrerender = true;
        usePrerenderProvider(
            { document: { referrer: ref } } as any,
            options as CounterOptions,
        );
        sinon.assert.calledWith(browserInfoStub, {
            [PRERENDER_BR_KEY]: 1,
            [ARTIFICIAL_BR_KEY]: 1,
        });
        sinon.assert.calledWith(
            senderSpy,
            {
                brInfo: browserInfoStub.returnValues[0],
                urlParams: {
                    [WATCH_URL_PARAM]: url,
                    [WATCH_REFERER_PARAM]: ref,
                },
            },
            options,
        );
    });
});
