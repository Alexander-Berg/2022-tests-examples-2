import { DEBUG_URL_PARAM } from '@src/providers/debugConsole/const';
import * as domUtils from '@src/utils/dom';
import * as chai from 'chai';
import * as sinon from 'sinon';
import * as cookie from '@src/storage/cookie';
import { insertDebugScript } from '../insertDebugScript';
import { INSERT_DEBUG_SCRIPT_COOKIE } from '../const';

describe('providers / insertDebugScript', () => {
    const ctx = (debug: string) =>
        ({
            location: {
                href: `https://example.com${
                    debug && `?${DEBUG_URL_PARAM}=${debug}`
                }`,
            },
        } as Window);
    let insertDebugScriptCookieValue: string | null;

    let loadScriptStub: sinon.SinonStub<
        [ctx: Window, options: domUtils.ScriptOptions]
    >;

    const sandbox = sinon.createSandbox();
    const setCookieVal = sandbox.stub();
    beforeEach(() => {
        loadScriptStub = sandbox
            .stub(domUtils, 'loadScript')
            .returns({} as HTMLScriptElement);
        sandbox.stub(cookie, 'globalCookieStorage').returns({
            setVal: setCookieVal,
            getVal: (name: string) => {
                chai.expect(name).to.equal(INSERT_DEBUG_SCRIPT_COOKIE);
                return insertDebugScriptCookieValue;
            },
        } as any);
        insertDebugScriptCookieValue = null;
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('Does not load debugger script for no URL parameter', () => {
        const win = ctx('');
        const isDebugEnabled = insertDebugScript(win);

        chai.expect(isDebugEnabled).to.be.undefined;
        sinon.assert.notCalled(loadScriptStub);
    });

    it('Does not load debugger script for URL parameter set to wrong value', () => {
        const win = ctx('1');
        const isDebugEnabled = insertDebugScript(win);

        chai.expect(isDebugEnabled).to.be.undefined;
        sinon.assert.notCalled(loadScriptStub);
    });

    it('Loads debugger script only once for cookie', () => {
        const win = ctx('');
        insertDebugScriptCookieValue = '25';
        const isDebugEnabled = insertDebugScript(win);
        insertDebugScript(win);

        chai.expect(isDebugEnabled).to.be.ok;
        sinon.assert.calledWith(
            setCookieVal,
            INSERT_DEBUG_SCRIPT_COOKIE,
            insertDebugScriptCookieValue,
        );
        sinon.assert.calledOnce(loadScriptStub);
    });

    it('Loads debugger script only once for set URL parameter', () => {
        const win = ctx('200500');
        const isDebugEnabled = insertDebugScript(win);
        insertDebugScript(win);

        chai.expect(isDebugEnabled).to.be.ok;
        sinon.assert.calledWith(setCookieVal, INSERT_DEBUG_SCRIPT_COOKIE, '25');
        sinon.assert.calledOnce(loadScriptStub);
    });
});
