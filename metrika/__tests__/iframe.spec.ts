import * as sinon from 'sinon';
import * as chai from 'chai';
import {
    GDPR_IS_YANDEX_PARENT,
    GDPRIframe,
    initIframe,
} from '@src/middleware/gdpr/iframe';
import * as location from '@src/utils/location';
import * as iframeSender from '@src/utils/iframeConnector/iframeSender';
import { IFRAME_MESSAGE_TYPE } from '@src/utils/iframeConnector';
import * as status from '@src/middleware/gdpr/status';
import * as deferUtils from '@src/utils/defer';

const { GDPR_FRAME_YA, GDPR_FRAME_NOYA, GDPR_FRAME_SKIP } = status;

describe('gdpr iframe', () => {
    const sandbox = sinon.createSandbox();
    const win = {} as any;
    const counterOptions = {} as any;

    let isYandexDomainValue: boolean;
    let iframeController: any;
    let iframeSenderOnSpy: sinon.SinonSpy;

    let triggerSpy: sinon.SinonSpy;
    const event = '2';

    let failSendToParents: boolean;

    beforeEach(() => {
        sandbox
            .stub(location, 'isYandexDomain')
            .callsFake(() => isYandexDomainValue);
        iframeSenderOnSpy = sinon.spy((_, cb) => {
            return cb([{}, { [IFRAME_MESSAGE_TYPE]: event }]);
        });
        failSendToParents = false;
        iframeController = {
            emitter: {
                on: iframeSenderOnSpy,
            },
            sendToParents: (data: any) => {
                chai.expect(data).to.deep.equal({
                    [IFRAME_MESSAGE_TYPE]: GDPR_IS_YANDEX_PARENT,
                });

                return failSendToParents
                    ? Promise.reject(new Error('failSendToParents'))
                    : Promise.resolve({
                          [GDPR_IS_YANDEX_PARENT]: isYandexDomainValue,
                      });
            },
        } as any;
        sandbox
            .stub(iframeSender, 'counterIframeSender')
            .returns(iframeController);
        triggerSpy = sandbox.spy(() => {});
        sandbox.stub(status, 'parseGdprValue').callsFake((value) => value);
        sandbox.stub(deferUtils, 'clearDefer');
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('initIframe', () => {
        isYandexDomainValue = true;
        const result = initIframe(win, counterOptions);
        chai.expect(result).to.eq(iframeController);
        const [[eventName]] = iframeSenderOnSpy.getCall(0).args;
        chai.expect(eventName).to.equal(GDPR_IS_YANDEX_PARENT);
        chai.expect(iframeSenderOnSpy.returnValues[0], {
            type: GDPR_IS_YANDEX_PARENT,
            [GDPR_IS_YANDEX_PARENT]: isYandexDomainValue,
        } as any);
    });

    it('GDPRIframe - yandex parent', () => {
        isYandexDomainValue = true;
        sandbox.stub(deferUtils, 'setDefer');

        return GDPRIframe(win, triggerSpy, counterOptions).then((result) => {
            sinon.assert.calledWith(triggerSpy, GDPR_FRAME_YA);
            const [events] = iframeSenderOnSpy.getCall(0).args;
            chai.expect(events).to.deep.equal([
                'GDPR-ok-view-default',
                'GDPR-ok-view-detailed',
                'GDPR-ok-view-detailed-0',
                'GDPR-ok-view-detailed-1',
                'GDPR-ok-view-detailed-2',
                'GDPR-ok-view-detailed-3',
            ]);
            chai.expect(result).to.deep.eq({ value: event });
        });
    });

    it('GDPRIframe - not yandex parent', () => {
        isYandexDomainValue = false;
        sandbox.stub(deferUtils, 'setDefer');

        return GDPRIframe(win, triggerSpy, counterOptions).then((result) => {
            sinon.assert.calledWith(triggerSpy, GDPR_FRAME_NOYA);
            chai.expect(result).to.be.null;
        });
    });
    it('GDPRIframe - fail send to parents', () => {
        failSendToParents = true;
        sandbox.stub(deferUtils, 'setDefer');

        return GDPRIframe(win, triggerSpy, counterOptions).then((result) => {
            sinon.assert.calledWith(triggerSpy.firstCall, GDPR_FRAME_SKIP);
            chai.expect(result).to.be.null;
        });
    });
    it('GDPRIframe - fail timeout', () => {
        sandbox.stub(deferUtils, 'setDefer').callsFake((_ctx, fn) => fn());

        return GDPRIframe(win, triggerSpy, counterOptions).then((result) => {
            sinon.assert.calledWith(triggerSpy.firstCall, GDPR_FRAME_SKIP);
            chai.expect(result).to.be.null;
        });
    });
});
