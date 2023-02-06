import * as chai from 'chai';
import * as sinon from 'sinon';
import * as consoleUtils from '@src/utils/console';
import * as cookieStorage from '@src/storage/cookie';
import * as optoutProvider from '@src/providers/optout';
import { noop } from '@src/utils/function';
import * as inject from '@inject';
import { DEBUG_CONSOLE_FEATURE } from '@generated/features';
import { DebugConsole } from '../debugConsole';
import { DEBUG_STORAGE_FLAG, DEBUG_URL_PARAM } from '../const';

describe('providers / DebugConsole', () => {
    const myConsole = {} as any;
    const cookieStore = {
        getVal: () => null,
        setVal: sinon.stub(),
    };
    const sandbox = sinon.createSandbox();

    beforeEach(() => {
        sandbox.stub(consoleUtils, 'getConsole').returns(myConsole);
        sandbox
            .stub(cookieStorage, 'globalCookieStorage')
            .returns(cookieStore as any);
    });

    afterEach(() => {
        cookieStore.setVal.resetHistory();
        sandbox.restore();
    });

    it('Creates debug console if feature flag is set, and sets debug cookie', () => {
        const ctx = {
            location: {
                href: `https://example.com?${DEBUG_URL_PARAM}=1`,
                host: 'example.com',
            },
        };
        const dConsole = DebugConsole(ctx as any, '1');

        chai.expect(
            cookieStore.setVal.calledWith(
                DEBUG_STORAGE_FLAG,
                '1',
                undefined,
                ctx.location.host,
            ),
            'set flag not called',
        ).to.be.true;
        chai.expect(dConsole, 'console didn match').to.equal(myConsole);
    });

    it('Returns noop console if feature flag is not set', () => {
        sandbox.stub(inject.flags, DEBUG_CONSOLE_FEATURE).value(false);
        const dConsole = DebugConsole({} as any, '2');

        chai.expect(dConsole.log).to.equal(noop);
        chai.expect(dConsole.warn).to.equal(noop);
        chai.expect(dConsole.error).to.equal(noop);
    });

    it('Returns noop console if optout enabled', () => {
        sandbox.stub(inject.flags, DEBUG_CONSOLE_FEATURE).value(true);
        const dConsole = DebugConsole({} as any, '3');
        sandbox.stub(optoutProvider, 'isOptoutEnabled').returns(true);

        chai.expect(dConsole.log).to.equal(noop);
        chai.expect(dConsole.warn).to.equal(noop);
        chai.expect(dConsole.error).to.equal(noop);
    });
});
