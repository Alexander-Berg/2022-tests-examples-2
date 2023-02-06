import * as sinon from 'sinon';
import * as chai from 'chai';
import * as browser from '@src/utils/browser';
import * as dom from '@src/utils/dom';
import * as iframeSender from '@src/utils/iframeConnector/iframeSender';
import { IFRAME_MESSAGE_TYPE } from '@src/utils/iframeConnector';
import * as status from '@src/middleware/gdpr/status';
import {
    GDPR_LANG_DEFAULT,
    GDPR_LANG_LIST,
    GDPRPopUp,
    getLang,
    getSrc,
} from '../popUp';

const { GDPR_OPEN_FAIL, GDPR_OPEN_START, GDPR_OPEN_SUCCESS } = status;

describe('gdpr popup', () => {
    const sandbox = sinon.createSandbox();
    const win = {} as any;

    let lang: string;
    let bundle: any;
    let triggerSpy: sinon.SinonSpy;
    let loadScriptStub: sinon.SinonStub;
    let dataLayerEmitterOnSpy: sinon.SinonSpy;

    const eventType = 'test-type';
    const parsedValue = '2';
    let sendToChildrenSpy: sinon.SinonSpy;
    let parseGdprValueStub: sinon.SinonStub;

    beforeEach(() => {
        lang = GDPR_LANG_DEFAULT;
        bundle = {};
        triggerSpy = sandbox.spy(() => {});
        sandbox.stub(browser, 'getLanguage').callsFake(() => lang);
        loadScriptStub = sandbox
            .stub(dom, 'loadScript')
            .callsFake(() => bundle);
        dataLayerEmitterOnSpy = sandbox.spy((events, cb) => {
            chai.expect(events).to.deep.eq([
                'GDPR-ok-view-default',
                'GDPR-ok-view-detailed',
                'GDPR-ok-view-detailed-0',
                'GDPR-ok-view-detailed-1',
                'GDPR-ok-view-detailed-2',
                'GDPR-ok-view-detailed-3',
            ]);
            cb({ [IFRAME_MESSAGE_TYPE]: eventType });
        });

        sendToChildrenSpy = sandbox.spy();
        sandbox.stub(iframeSender, 'counterIframeSender').returns({
            sendToChildren: sendToChildrenSpy,
        } as any);
        parseGdprValueStub = sandbox
            .stub(status, 'parseGdprValue')
            .returns(parsedValue);
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('no bundle', () => {
        bundle = undefined;
        lang = 'ru';

        return GDPRPopUp(win, triggerSpy, {} as any, {} as any)
            .then(() => {
                chai.assert.fail();
            })
            .catch(() => {
                sinon.assert.calledWith(loadScriptStub, win, {
                    src: getSrc(lang),
                });
                sinon.assert.calledWith(triggerSpy, GDPR_OPEN_FAIL);
            });
    });

    it('bundle load error', () => {
        lang = 'nonexistent_lang';
        Object.defineProperty(bundle, 'onerror', {
            set(val) {
                val();
            },
        });

        return GDPRPopUp(win, triggerSpy, {} as any, {} as any).then(() => {
            sinon.assert.calledWith(loadScriptStub, win, {
                src: getSrc(GDPR_LANG_DEFAULT),
            });
            sinon.assert.calledWith(triggerSpy, GDPR_OPEN_START);
        });
    });

    it('bundle load success', () => {
        Object.defineProperty(bundle, 'onload', {
            set(val) {
                val();
            },
        });

        return GDPRPopUp(
            win,
            triggerSpy,
            { on: dataLayerEmitterOnSpy } as any,
            {} as any,
        ).then((result) => {
            sinon.assert.calledWith(loadScriptStub, win, {
                src: getSrc(GDPR_LANG_DEFAULT),
            });
            sinon.assert.calledWith(triggerSpy.firstCall, GDPR_OPEN_START);
            sinon.assert.calledWith(triggerSpy.secondCall, GDPR_OPEN_SUCCESS);
            sinon.assert.calledWith(sendToChildrenSpy, {
                [IFRAME_MESSAGE_TYPE]: eventType,
            });
            sinon.assert.calledWith(parseGdprValueStub, eventType);
            chai.expect(result).to.deep.eq({ value: parsedValue });
        });
    });

    describe('getLang', () => {
        it('respects forceLang', () => {
            const forceLang = GDPR_LANG_LIST.find(
                (langItem) => langItem !== GDPR_LANG_DEFAULT,
            );
            const computedLang = getLang({} as unknown as Window, forceLang);

            chai.expect(computedLang).to.be.equal(forceLang);
        });

        it('forceLang checked to be correct', () => {
            const forceLang = 'non_existent_lang';
            const computedLang = getLang({} as unknown as Window, forceLang);

            chai.expect(computedLang).to.be.equal(GDPR_LANG_DEFAULT);
        });
    });
});
