/* eslint-env mocha */
import * as chai from 'chai';
import * as sinon from 'sinon';
import { CounterOptions } from '@src/utils/counterOptions';
import * as cS from '@src/utils/counterSettings';
import * as br from '@src/utils/browser';
import * as gUtils from '@src/utils/object';
import * as defer from '@src/utils/defer';
import * as dom from '@src/utils/dom';
import * as base64 from '@src/utils/decoder';
import * as events from '@src/utils/events';

import * as utils from '../utils';

import { initZZ } from '../zz';

describe('crossDomain midlleware ZZ', () => {
    const fakeWindow = {} as any as Window;
    const counterOptions: CounterOptions = { id: 1, counterType: '0' };
    const sandbox = sinon.createSandbox();
    const setVal = sandbox.spy();
    const getVal = sandbox.spy();
    const setValGlobal = sandbox.spy();
    const getValGlobal = sandbox.spy();
    const localStorage = {
        setVal,
        getVal,
    } as unknown;
    const globalStorage = {
        setVal: setValGlobal,
        getVal: getValGlobal,
    };
    let getPath: any;
    let getPathAnswers: Record<string, any>;
    let counterSettingsStorage: sinon.SinonStub<any, any>;
    let isFFVersion: sinon.SinonStub<any, any>;
    let isEdgeMinVersion: sinon.SinonStub<any, any>;
    let getElemCreateFunction: sinon.SinonStub<any, any>;
    const createElement = sandbox.stub();
    let getRootElement: sinon.SinonStub<any, any>;
    let decodeBase64: sinon.SinonStub<any, any>;
    let cEvent: sinon.SinonStub<any, any>;
    let fromCharCodeStub: sinon.SinonStub<any, any>;
    const appendChild = sandbox.stub();
    const eventHandlerUnsubscribe = sandbox
        .stub()
        .named('eventHandlerUnsubscribe');
    const eventHandlerOn = sandbox.stub().returns(eventHandlerUnsubscribe);
    const eventHandlerUn = sandbox.stub();
    const srcSpy = sandbox.spy();
    let setDefer: any;
    let clearDefer: any;
    let removeNode: any;
    const frame = {
        style: {},
    };
    Object.defineProperty(frame, 'src', {
        set: srcSpy,
    });

    beforeEach(() => {
        fromCharCodeStub = sandbox.stub(br, 'isBrokenFromCharCode');
        fromCharCodeStub.returns(false);
        counterSettingsStorage = sandbox.stub(cS, 'getCounterSettings');
        counterSettingsStorage.callsFake((_, _1, fn) => fn());
        getPath = sandbox.stub(gUtils, 'getPath');
        getPath.callsFake((obj: any, path: string) => getPathAnswers[path]);
        isFFVersion = sandbox.stub(utils, 'isFFVersion');
        isEdgeMinVersion = sandbox.stub(utils, 'isEdgeMinVersion');
        getElemCreateFunction = sandbox.stub(dom, 'getElemCreateFunction');
        getRootElement = sandbox.stub(dom, 'getRootElement');
        removeNode = sandbox.stub(dom, 'removeNode').named('removeNode');
        decodeBase64 = sandbox.stub(base64, 'decodeBase64');
        decodeBase64.returns('');
        cEvent = sandbox.stub(events, 'cEvent').returns({
            on: eventHandlerOn,
            un: eventHandlerUn,
        });
        setDefer = sandbox.stub(defer, 'setDefer');
        clearDefer = sandbox.stub(defer, 'clearDefer');
    });

    afterEach(() => {
        sandbox.restore();
        sandbox.resetHistory();
        srcSpy.resetHistory();
    });

    it('initZZ drops if settings.pcs != 0', () => {
        getPathAnswers = {
            'settings.pcs': '1',
        };

        initZZ(
            fakeWindow,
            counterOptions,
            globalStorage as any,
            localStorage as any,
        );
        sinon.assert.notCalled(isFFVersion);
    });

    it('initZZ drops if no createElement function', () => {
        getPathAnswers = {
            'settings.pcs': '0',
        };
        getElemCreateFunction.returns(null);
        initZZ(
            fakeWindow,
            counterOptions,
            globalStorage as any,
            localStorage as any,
        );

        sinon.assert.calledOnce(isFFVersion);
        sinon.assert.calledOnce(getElemCreateFunction);
    });

    it('initZZ drops if no root element', () => {
        getPathAnswers = {
            'settings.pcs': '0',
        };
        getElemCreateFunction.returns(createElement);
        createElement.returns({
            style: {},
        });
        getRootElement.returns(null);
        initZZ(
            fakeWindow,
            counterOptions,
            globalStorage as any,
            localStorage as any,
        );

        sinon.assert.calledOnce(getRootElement);
        sinon.assert.notCalled(cEvent);
    });

    it('initZZ timeout', () => {
        getPathAnswers = {
            'settings.pcs': '0',
        };
        getElemCreateFunction.returns(createElement);
        createElement.returns(frame);
        getRootElement.returns({ appendChild });
        initZZ(
            fakeWindow,
            counterOptions,
            globalStorage as any,
            localStorage as any,
        );

        const [iframeUrl] = srcSpy.getCall(0).args;
        chai.expect(iframeUrl.substr(-2)).to.be.eq('ru');

        sinon.assert.calledOnce(getRootElement);
        // do not use deepEqual - original frame data is changed with styles
        sinon.assert.calledWith(appendChild, frame);
        sinon.assert.calledOnce(cEvent);

        sinon.assert.calledWith(setDefer, fakeWindow, sinon.match.func, 3000);

        setDefer.getCall(0).args[1]();

        sinon.assert.calledOnce(eventHandlerUnsubscribe);
        sinon.assert.calledWith(removeNode, frame);
    });

    it('initZZ event handler drops if !message.data', () => {
        getPathAnswers = {
            'settings.pcs': '0',
            data: null,
        };
        getElemCreateFunction.returns(createElement);
        createElement.returns(frame);
        getRootElement.returns({ appendChild });
        isFFVersion.returns(true);
        initZZ(
            fakeWindow,
            counterOptions,
            globalStorage as any,
            localStorage as any,
        );
        const [iframeUrl] = srcSpy.getCall(0).args;
        chai.expect(iframeUrl.substr(-2)).to.be.eq('md');
        eventHandlerOn.getCall(0).args[2]();
        sinon.assert.notCalled(setVal);
    });

    it('initZZ event handler does not react on a random message', () => {
        getPathAnswers = {
            'settings.pcs': '0',
            data: 'some random message',
        };
        getElemCreateFunction.returns(createElement);
        createElement.returns(frame);
        getRootElement.returns({ appendChild });
        isEdgeMinVersion.returns(true);
        initZZ(
            fakeWindow,
            counterOptions,
            globalStorage as any,
            localStorage as any,
        );
        const [iframeUrl] = srcSpy.getCall(0).args;
        chai.expect(iframeUrl.substr(-2)).to.be.eq('md');
        eventHandlerOn.getCall(0).args[2]();
        sinon.assert.notCalled(setVal);
    });

    it('initZZ event handler reacts on a well formed message', () => {
        getPathAnswers = {
            'settings.pcs': '0',
            data: '__ym__zztest string',
        };
        getElemCreateFunction.returns(createElement);
        createElement.returns(frame);
        getRootElement.returns({ appendChild });
        initZZ(
            fakeWindow,
            counterOptions,
            globalStorage as any,
            localStorage as any,
        );
        eventHandlerOn.getCall(0).args[2]();
        chai.expect(setVal.getCall(0).args).to.be.deep.eq([
            'zzlc',
            'test string',
        ]);
        sinon.assert.calledOnce(removeNode);
        sinon.assert.calledTwice(eventHandlerUnsubscribe);
        sinon.assert.calledOnce(clearDefer);
    });
});
