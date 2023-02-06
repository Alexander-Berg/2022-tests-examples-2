/* eslint-env mocha */
import * as chai from 'chai';
import * as sinon from 'sinon';
import { CounterOptions } from '@src/utils/counterOptions';
import * as gUtils from '@src/utils/object';
import * as defer from '@src/utils/defer';
import * as uidUtils from '@src/middleware/watchSyncFlags/brinfoFlags/uid';
import { GlobalStorage } from '@src/storage/global';
import * as frameConnector from '@src/utils/iframeConnector';
import * as fnv from '@src/utils/fnv32a';
import { initPU, generate } from '../pu';

describe('crossDomain midlleware PU', () => {
    const fakeWindow = {} as any as Window;
    const counterOptions: CounterOptions = { id: 1, counterType: '0' };
    let getPath: any;
    let getUid: any;
    let counterIframeConnector: any;
    let setDefer: any;
    let clearDefer: any;
    let fnv32a: any;

    beforeEach(() => {
        fnv32a = sinon.stub(fnv, 'fnv32a').returns(1);
        getPath = sinon.stub(gUtils, 'getPath');
        getUid = sinon.stub(uidUtils, 'getUidFlag');
        counterIframeConnector = sinon.stub(
            frameConnector,
            'counterIframeConnector',
        );
        setDefer = sinon.stub(defer, 'setDefer');
        clearDefer = sinon.stub(defer, 'clearDefer');
    });

    afterEach(() => {
        fnv32a.restore();
        getPath.restore();
        getUid.restore();
        counterIframeConnector.restore();
        setDefer.restore();
        clearDefer.restore();
    });

    it('generate', () => {
        getPath.returns('path');
        getUid.returns('uid');
        const setVal = sinon.spy();
        generate(fakeWindow, counterOptions, {
            setVal,
        } as unknown as GlobalStorage);
        chai.expect(setVal.getCall(0).args).to.deep.equal(
            ['pu', '1uid'],
            'should call setVal with correct values',
        );
    });

    it('initPU w/o opener', () => {
        getPath.callsFake((ctx: Window, varName: string) => {
            if (varName === 'opener') {
                return null;
            }
            if (varName === 'location.host') {
                return 'host';
            }
            return false;
        });
        getUid.returns('uid');
        const setVal = sinon.spy();
        const getVal = sinon.stub().returns('value');
        const emitterOn = sinon.spy();
        counterIframeConnector.returns({
            emitter: {
                on: emitterOn,
            },
        });
        getPath.callsFake;
        initPU(fakeWindow, counterOptions, {
            setVal,
            getVal,
        } as unknown as GlobalStorage);

        const emitterCall = emitterOn.getCall(0);
        chai.expect(
            emitterCall.args[0],
            'provides callback for connector.emitter',
        ).to.deep.equal(['gpu-get']);

        chai.expect(emitterCall.args[1]()).to.deep.equal(
            { type: 'gpu-get', pu: 'value' },
            'message callback should return valid data',
        );

        chai.expect(setVal.getCall(0).args).to.deep.equal(
            ['pu', '1uid'],
            'should call setVal from generate with correct values',
        );

        chai.expect(setDefer.called, 'w/o opener should return before setDefer')
            .to.be.false;
    });

    it('initPU with opener', () => {
        getPath.callsFake((ctx: Window, varName: string) => {
            if (varName === 'opener') {
                return 'opener';
            }
            if (varName === 'location.host') {
                return 'host';
            }
            if (varName === 'pu') {
                return 'pu from storage';
            }
            return false;
        });
        getUid.returns('uid');
        const setVal = sinon.spy();
        const getVal = sinon.stub().returns('value');
        const emitterOn = sinon.spy();
        const sendToFrame = sinon.spy();
        counterIframeConnector.returns({
            emitter: {
                on: emitterOn,
            },
            sendToFrame,
        });
        getPath.callsFake;
        initPU(fakeWindow, counterOptions, {
            setVal,
            getVal,
        } as unknown as GlobalStorage);

        const emitterCall = emitterOn.getCall(0);
        chai.expect(
            emitterCall.args[0],
            'provides callback for connector.emitter',
        ).to.deep.equal(['gpu-get']);

        chai.expect(emitterCall.args[1]()).to.deep.equal(
            { type: 'gpu-get', pu: 'value' },
            'message callback should return valid data',
        );

        chai.expect(setDefer.called, 'with opener should call setDefer').to.be
            .true;

        chai.expect(sendToFrame.called, 'with opener should call sendToFrame')
            .to.be.true;

        chai.expect(
            sendToFrame.getCall(0).args[0],
            'should call sendToFrame with adequate parameters',
        ).to.be.equal('opener');

        chai.expect(sendToFrame.getCall(0).args[1]).to.deep.equal(
            { type: 'gpu-get' },
            'should call sendToFrame with adequate parameters',
        );

        sendToFrame.getCall(0).args[2]({}, {});

        chai.expect(
            clearDefer.called,
            'should call clearDefer from sendtoFrame callback',
        ).to.be.true;

        chai.expect(
            clearDefer.called,
            'should call clearDefer from sendtoFrame callback',
        ).to.be.true;

        chai.expect(setVal.getCall(0).args).to.deep.equal(
            ['pu', 'pu from storage'],
            'should call setVal from sendFrame callback',
        );

        chai.expect(setVal.calledOnce, 'setVal should be called once').to.be
            .true;
    });
});
