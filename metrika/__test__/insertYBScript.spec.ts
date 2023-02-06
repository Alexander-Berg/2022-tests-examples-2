import Sinon, * as sinon from 'sinon';
import * as chai from 'chai';
import * as getSettings from '@src/utils/counterSettings';
import * as dom from '@src/utils/dom';
import { insertYBScriptRaw, YB_SCRITP_URL } from '../insertYBScript';

describe('insertYBScript', () => {
    const location = {
        href: 'http://example.com?a=b',
    };
    const settings: any = {
        settings: {},
    };
    const counterOptions: any = {};
    const sandbox = sinon.createSandbox();

    let counterSettingsStub: Sinon.SinonStub;
    let loadScript: Sinon.SinonStub;

    beforeEach(() => {
        loadScript = sandbox.stub(dom, 'loadScript');
        counterSettingsStub = sandbox.stub(getSettings, 'getCounterSettings');
    });

    afterEach(() => {
        sandbox.restore();
    });

    it("desn't do anything if yb is false", () => {
        const ctx: any = {
            location,
        };
        insertYBScriptRaw(ctx, counterOptions);
        const [settingsCtx, opts, callback] =
            counterSettingsStub.getCall(0).args;
        chai.expect(settingsCtx).to.equal(ctx);
        chai.expect(opts).to.equal(counterOptions);
        settings.settings.yb = 0;
        callback(settings);
        sinon.assert.notCalled(loadScript);
    });

    it('inserts yb script', () => {
        const ctx: any = {
            location,
        };
        insertYBScriptRaw(ctx, counterOptions);
        const [settingsCtx, opts, callback] =
            counterSettingsStub.getCall(0).args;
        chai.expect(settingsCtx).to.equal(ctx);
        chai.expect(opts).to.equal(counterOptions);
        settings.settings.yb = 1;
        callback(settings);
        const [loadCtx, options] = loadScript.getCall(0).args;
        chai.expect(loadCtx).to.equal(ctx);
        chai.expect(options).to.deep.equal({
            src: `${YB_SCRITP_URL}?url=${encodeURIComponent(location.href)}`,
        });
    });
});
