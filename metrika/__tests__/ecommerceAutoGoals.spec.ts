import * as sinon from 'sinon';
import { GTagEcommerceEvent } from '@src/providers/ecommerce';
import { parseEcommerceEvent } from '../ecommerceAutoGoals';
import { GA3_SOURCE, GA4_SOURCE } from '../const';

describe('ecommerceExperiment', () => {
    const event = 'begin_checkout';

    const GA4version = GA4_SOURCE;
    const GA3version = GA3_SOURCE;
    const ecommerceEventVersion = '1';

    let sendParamsSpy: sinon.SinonSpy<any, any>;
    beforeEach(() => {
        sendParamsSpy = sinon.spy();
    });

    it('test GA4 event', () => {
        const result = {
            version: GA4version,
            eventName: event,
        };
        const testEvent = { event, ecommerce: {} };
        parseEcommerceEvent(sendParamsSpy)(testEvent);

        sinon.assert.calledOnce(sendParamsSpy);
        sinon.assert.calledWith(sendParamsSpy, result);
    });

    it('test GA3 event', () => {
        const result = {
            version: GA3version,
            eventName: event,
        };
        const testEvent = ['event', event, { ecommerce: {} }];
        parseEcommerceEvent(sendParamsSpy)(testEvent as GTagEcommerceEvent);

        sinon.assert.calledOnce(sendParamsSpy);
        sinon.assert.calledWith(sendParamsSpy, result);
    });

    it('test ecommerce event', () => {
        const result = {
            version: ecommerceEventVersion,
            eventName: event,
        };
        const testEvent = { ecommerce: { [event]: {} } };
        parseEcommerceEvent(sendParamsSpy)(testEvent);

        sinon.assert.calledOnce(sendParamsSpy);
        sinon.assert.calledWith(sendParamsSpy, result);
    });

    it('test invalid event', () => {
        const testEvent = { event } as any;
        parseEcommerceEvent(sendParamsSpy)(testEvent);

        sinon.assert.notCalled(sendParamsSpy);
    });
});
