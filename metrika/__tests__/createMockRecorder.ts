import * as sinon from 'sinon';
import chai from 'chai';
import * as errorLogger from '@src/utils/errorLogger';
import * as utils from '../../../utils/ThrottleManager';

export const STAMP = 1;
export const ORIENTATION = 'horizontal';

export const createRecorderMock = () => {
    const sandbox = sinon.createSandbox();
    let handlers = {} as any;

    const sendEventObjectSpy = sandbox.stub();
    const offEventSpy = sandbox.spy();
    const eventWrapperOnStub = sandbox
        .stub()
        .callsFake((target: Window, events: string[], handler: () => void) => {
            events.forEach((event) => {
                handlers[event] = handlers[event] || [];
                handlers[event].push(handler);
            });

            return offEventSpy;
        });
    sandbox
        .stub(errorLogger, 'errorLogger')
        .callsFake((ctx, name, method: any, _: any, that: any) =>
            method.bind(that || null),
        );
    let throttledHandlerSpy = sandbox.spy();
    const flushSpy = sandbox.spy();
    const createThrottledFunctionSpy = sandbox.spy((fn: any) => {
        throttledHandlerSpy = sandbox.spy(fn);
        return throttledHandlerSpy;
    });
    const throttleManagerStub = sandbox.stub(utils, 'ThrottleManager').returns({
        createThrottledFunction: createThrottledFunctionSpy,
        flush: flushSpy,
    });
    const indexerMock = {
        indexNode: (item: any) => item,
        on: (nodeName: string, event: string, handler: () => void) => {
            const key = `${event}${nodeName}`;
            handlers[key] = handlers[key] || [];
            handlers[key].push(handler);
        },
        off: () => undefined,
    };

    return {
        getEventWrapper: () => ({
            on: eventWrapperOnStub,
        }),
        getIndexer: () => indexerMock,
        getBrowser: () => ({
            getOrientation: () => ORIENTATION,
            isAndroid: () => true,
        }),
        sendEventObject: sendEventObjectSpy,
        stamp: () => STAMP,
        getOptions: () => ({}),
        test: {
            // captor.recorder.sendEventObject
            sendEventObjectSpy,
            // captor.offEventFunctions[number]
            offEventSpy,
            // this.throttleManager.createThrottledFunction
            createThrottledFunctionSpy,
            // this.throttleManager.flush
            flushSpy,
            sandbox,
            restore: () => {
                handlers = {};
                sandbox.restore();
            },
            createEvent: (key: string, event: any) => {
                handlers[key].map((item: any) => item(event));
            },
            checkSendEvent: (
                type: string,
                data: any,
                event: string,
                index = 0,
                stamp?: number,
            ) => {
                chai.expect(sendEventObjectSpy.args[index][0]).to.eq(type);
                chai.expect(sendEventObjectSpy.args[index][1]).to.deep.eq(data);
                chai.expect(sendEventObjectSpy.args[index][2]).to.eq(event);
                chai.expect(sendEventObjectSpy.args[index][3]).to.eq(stamp);
            },
            checkThrottleManagerUsage: (ctx: Window) => {
                sinon.assert.calledWith(throttleManagerStub, ctx);
                sinon.assert.called(createThrottledFunctionSpy);
            },
            checkCallThrottledHandler: () =>
                sinon.assert.called(throttledHandlerSpy),
            checkCallOriginalHandler: () =>
                sinon.assert.notCalled(throttledHandlerSpy),
            checkNoEvent: () => {
                sinon.assert.notCalled(sendEventObjectSpy);
            },
        },
    } as any;
};
