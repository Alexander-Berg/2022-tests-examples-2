import * as sinon from 'sinon';
import { GTagEcommerceEvent } from '@src/providers/ecommerce';
import { handleEcommerceEvent, handleFbqEvent } from '../eventHandlers';
import {
    EcommercePlatform,
    EVENT_STRING_SEPARATOR,
    GTAG_ECOMMERCE_KEY,
} from '../const';

describe('ecommerceExperiment', () => {
    const event = 'begin_checkout';

    let sendParamsSpy: sinon.SinonSpy<[eventInfo: string], void>;
    beforeEach(() => {
        sendParamsSpy = sinon.spy((eventInfo: string) => {});
    });

    describe('handleEcommerceEvent', () => {
        const GA: EcommercePlatform = 'ga';

        it('handles dataLayer object', () => {
            const result = `${GA}${EVENT_STRING_SEPARATOR}${event}${EVENT_STRING_SEPARATOR}`;
            const testEvent = { event, ecommerce: {} };
            handleEcommerceEvent(sendParamsSpy, testEvent);

            sinon.assert.calledOnceWithExactly(sendParamsSpy, result);
        });

        it('handles dataLayer array', () => {
            const result = `${GA}${EVENT_STRING_SEPARATOR}${event}${EVENT_STRING_SEPARATOR}`;
            const testEvent = ['event', event, { ecommerce: {} }];
            handleEcommerceEvent(
                sendParamsSpy,
                testEvent as GTagEcommerceEvent,
            );

            sinon.assert.calledOnceWithExactly(sendParamsSpy, result);
        });

        it('handles events from a "ga" function call', () => {
            const result = `${GA}${EVENT_STRING_SEPARATOR}${event}${EVENT_STRING_SEPARATOR}`;
            const testEvent = [`${GTAG_ECOMMERCE_KEY}:${event}`, {}];
            handleEcommerceEvent(
                sendParamsSpy,
                testEvent as GTagEcommerceEvent,
            );

            sinon.assert.calledOnceWithExactly(sendParamsSpy, result);
        });

        it('handles events from a "gtag" function call', () => {
            const result = `${GA}${EVENT_STRING_SEPARATOR}${event}${EVENT_STRING_SEPARATOR}`;
            let testEvent: IArguments;
            (function a(...providedEvent: any[]) {
                // eslint-disable-next-line prefer-rest-params
                testEvent = arguments;
            })('event', event, { ecommerce: {} });
            handleEcommerceEvent(sendParamsSpy, testEvent);

            sinon.assert.calledOnceWithExactly(sendParamsSpy, result);
        });

        it('handles unknown ecommerce events', () => {
            const otherProperty = 'other-property';
            const result = `${GA}${EVENT_STRING_SEPARATOR}${[
                event,
                otherProperty,
            ].join(',')}${EVENT_STRING_SEPARATOR}`;
            const testEvent = {
                ecommerce: {
                    [event]: {},
                    [otherProperty]: {},
                },
            };
            handleEcommerceEvent(sendParamsSpy, testEvent);

            sinon.assert.calledOnceWithExactly(sendParamsSpy, result);
        });

        it('rejects invalid events', () => {
            const testEvent = { event };
            handleEcommerceEvent(sendParamsSpy, testEvent);

            sinon.assert.notCalled(sendParamsSpy);
        });

        describe('collects values', () => {
            [
                'pagetype',
                'ecomm_pageType',
                'list',
                'list_name',
                'item_list_name',
            ].forEach((prop) => {
                it(`for "${prop}" property`, () => {
                    const testValue1 = 'testValue1';
                    const testValue2 = 'testValue2';
                    const value = `${prop}=${testValue1},${prop}=${testValue2}`;
                    const result = `${GA}${EVENT_STRING_SEPARATOR}${event}${EVENT_STRING_SEPARATOR}${value}`;
                    const testEvent = [
                        'event',
                        event,
                        {
                            ecommerce: {
                                [prop]: testValue1,
                                items: [{ [prop]: testValue2 }, {}],
                            },
                        },
                    ];
                    handleEcommerceEvent(
                        sendParamsSpy,
                        testEvent as GTagEcommerceEvent,
                    );

                    sinon.assert.calledOnceWithExactly(sendParamsSpy, result);
                });
            });
        });

        it('collects "pagetype" value', () => {
            const pagetype = 'testValue';
            const result = `${GA}${EVENT_STRING_SEPARATOR}${event}${EVENT_STRING_SEPARATOR}pagetype=${pagetype}`;
            const testEvent = ['event', event, { ecommerce: { pagetype } }];
            handleEcommerceEvent(
                sendParamsSpy,
                testEvent as GTagEcommerceEvent,
            );

            sinon.assert.calledOnceWithExactly(sendParamsSpy, result);
        });

        it('collects "ecomm_pageType" value', () => {
            /* eslint-disable camelcase */
            const ecomm_pageType = 'testValue';
            const result = `${GA}${EVENT_STRING_SEPARATOR}${event}${EVENT_STRING_SEPARATOR}ecomm_pageType=${ecomm_pageType}`;
            /* eslint-enable camelcase */
            const testEvent = [
                'event',
                event,
                { ecommerce: { ecomm_pageType } },
            ];
            handleEcommerceEvent(
                sendParamsSpy,
                testEvent as GTagEcommerceEvent,
            );

            sinon.assert.calledOnceWithExactly(sendParamsSpy, result);
        });

        it('collects "list" value', () => {
            const testValue1 = 'testValue1';
            const testValue2 = 'testValue2';
            const result = `${GA}${EVENT_STRING_SEPARATOR}${event}${EVENT_STRING_SEPARATOR}list=${testValue1},list=${testValue2}`;
            const testEvent = [
                'event',
                event,
                {
                    ecommerce: { list: testValue1 },
                    list: testValue2,
                },
            ];
            handleEcommerceEvent(
                sendParamsSpy,
                testEvent as GTagEcommerceEvent,
            );

            sinon.assert.calledOnceWithExactly(sendParamsSpy, result);
        });

        it('collects "list_name" value', () => {
            const testValue1 = 'testValue1';
            const testValue2 = 'testValue2';
            const result = `${GA}${EVENT_STRING_SEPARATOR}${event}${EVENT_STRING_SEPARATOR}list_name=${testValue1},list_name=${testValue2}`;
            const testEvent = [
                'event',
                event,
                {
                    ecommerce: { list_name: testValue1 },
                    list_name: testValue2,
                },
            ];
            handleEcommerceEvent(
                sendParamsSpy,
                testEvent as GTagEcommerceEvent,
            );

            sinon.assert.calledOnceWithExactly(sendParamsSpy, result);
        });

        it('collects "item_list_name" value', () => {
            const testValue1 = 'testValue1';
            const testValue2 = 'testValue2';
            const result = `${GA}${EVENT_STRING_SEPARATOR}${event}${EVENT_STRING_SEPARATOR}item_list_name=${testValue1},item_list_name=${testValue2}`;
            const testEvent = [
                'event',
                event,
                {
                    ecommerce: { item_list_name: testValue1 },
                    item_list_name: testValue2,
                },
            ];
            handleEcommerceEvent(
                sendParamsSpy,
                testEvent as GTagEcommerceEvent,
            );

            sinon.assert.calledOnceWithExactly(sendParamsSpy, result);
        });
    });

    describe('handleFbqEvent', () => {
        const FB: EcommercePlatform = 'fb';

        it('handles "track" events', () => {
            const result = `${FB}${EVENT_STRING_SEPARATOR}${event}`;
            const testEvent = ['track', event, { currency: 'USD' }];
            handleFbqEvent(sendParamsSpy, testEvent);

            sinon.assert.calledOnceWithExactly(sendParamsSpy, result);
        });

        it('rejects invalid events', () => {
            const testEvent = ['smack', event, { currency: 'USD' }];
            handleFbqEvent(sendParamsSpy, testEvent);

            sinon.assert.notCalled(sendParamsSpy);
        });
    });
});
