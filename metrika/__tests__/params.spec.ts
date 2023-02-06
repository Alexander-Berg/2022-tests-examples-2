import * as sinon from 'sinon';

import { CounterOptions } from '@src/utils/counterOptions';
import * as dataLayerUtils from '@src/utils/dataLayerObserver';
import * as counterUtils from '@src/utils/counter';
import { METHOD_NAME_PARAMS } from '@src/providers/params/const';
import { CounterObject } from '@src/utils/counter/type';
import * as locationUtils from '@src/utils/location';
import * as cookieUtils from '../cookie';
import {
    GDPR_OK,
    GDPR_OK_VIEW_DEFAULT,
    GDPR_SETTINGS,
    GDPR_OK_VIEW_DETAILED,
} from '../status';
import { sendGDPRParams } from '../params';

describe('gdpr params', () => {
    const sandbox = sinon.createSandbox();
    const ctx = {} as Window;
    const counterOptions = {} as CounterOptions;

    let paramsSpy: sinon.SinonSpy;

    beforeEach(() => {
        sandbox.stub(dataLayerUtils, 'getInnerDataLayer');
        paramsSpy = sinon.spy();
        sandbox.stub(counterUtils, 'getCounterInstance').returns({
            [METHOD_NAME_PARAMS]: paramsSpy,
        } as any as CounterObject);
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('default view - accept', () => {
        sandbox.stub(locationUtils, 'isYandexOwnerDomain').returns(true);
        sandbox
            .stub(cookieUtils, 'getGDPRStatusRaw')
            .returns(['1', GDPR_OK, GDPR_OK_VIEW_DEFAULT]);
        sendGDPRParams(ctx, counterOptions);
        sinon.assert.calledWith(paramsSpy, 'gdpr', ['ok', 'ok-default']);
    });

    it('disable not yandex domain', () => {
        sandbox.stub(locationUtils, 'isYandexOwnerDomain').returns(false);
        sandbox
            .stub(cookieUtils, 'getGDPRStatusRaw')
            .returns([GDPR_SETTINGS, GDPR_OK, `${GDPR_OK_VIEW_DETAILED}-3`]);
        sendGDPRParams(ctx, counterOptions);
        sinon.assert.notCalled(paramsSpy);
    });

    it('disable for empty list', () => {
        sandbox.stub(locationUtils, 'isYandexOwnerDomain').returns(false);
        sandbox
            .stub(cookieUtils, 'getGDPRStatusRaw')
            .returns(['any-other-event']);
        sendGDPRParams(ctx, counterOptions);
        sinon.assert.notCalled(paramsSpy);
    });
});
