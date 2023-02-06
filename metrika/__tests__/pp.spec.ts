/* eslint-env mocha */
import * as chai from 'chai';
import * as sinon from 'sinon';
import { CounterOptions } from '@src/utils/counterOptions';
import { GlobalStorage } from '@src/storage/global';
import * as gFunction from '@src/utils/function';
import * as gArray from '@src/utils/array';
import * as gObject from '@src/utils/object';
import * as fnv from '@src/utils/fnv32a';
import { initPP } from '../pp';
import { PP_RTC_FN } from '../const';

describe('crossDomain midlleware PP', () => {
    const fakeWindow = {} as any as Window;
    const sandbox = sinon.createSandbox();
    const opt = () => {
        const counterOptions: CounterOptions = { id: 1, counterType: '0' };
        return counterOptions;
    };
    let cFind;
    let bindArg;
    let bind: any;
    let isUndefined: any;
    let getPath: any;
    let isFunctionStub: any;
    let fnv32a: any;
    let mix: any;
    const setVal = sinon.spy();
    const getVal = sinon.spy();
    const globalStorage = {
        setVal,
        getVal,
    } as unknown as GlobalStorage;
    let getPathAnswers: Record<string, any>;

    beforeEach(() => {
        mix = sandbox.stub(gObject, 'mix');
        cFind = sandbox.stub(gArray, 'cFind');
        cFind.returns(PP_RTC_FN[0]);
        bindArg = sandbox.stub(gFunction, 'bindArg');
        bindArg.returns('' as any);
        bind = sandbox.stub(gFunction as any, 'bind');
        bind.returns(() => {});
        isUndefined = sandbox.stub(gObject, 'isUndefined');
        isUndefined.returns(false);
        getPath = sandbox.stub(gObject, 'getPath');
        getPath.callsFake((obj: any, path: string) => getPathAnswers[path]);
        isFunctionStub = sandbox.stub(gObject, 'isFunction');
        fnv32a = sandbox.stub(fnv, 'fnv32a');
        fnv32a.returns(1);
    });

    afterEach(() => {
        setVal.resetHistory();
        getVal.resetHistory();
        sandbox.restore();
    });

    it('initPP drops if no getPath(ctx, rtcFnName)', () => {
        getPathAnswers = {
            RTCPeerConnection: null,
            'navigator.onLine': true,
        };
        initPP(fakeWindow, opt(), globalStorage);
        chai.expect(getPath.getCall(0).args[1]).to.be.equal(
            'RTCPeerConnection',
        );
        chai.expect(getPath.getCall(1).args[1]).to.be.equal('navigator.onLine');
        chai.expect(getPath.getCall(2)).to.be.null;
    });

    it('initPP drops if no navigator.onLine', () => {
        getPathAnswers = {
            RTCPeerConnection: function rtcfake() {},
            'navigator.onLine': false,
        };
        initPP(fakeWindow, opt(), globalStorage);

        chai.expect(getPath.getCall(0).args[1]).to.be.equal(
            'RTCPeerConnection',
        );
        chai.expect(getPath.getCall(1).args[1]).to.be.equal('navigator.onLine');
        chai.expect(getPath.getCall(2)).to.be.null;
    });

    it('initPP drops if no RTC.prototype.constructor.name', () => {
        getPathAnswers = {
            RTCPeerConnection: function rtcfake() {},
            'prototype.constructor.name': null,
            'navigator.onLine': true,
        };
        initPP(fakeWindow, opt(), globalStorage);

        chai.expect(getPath.getCall(2).args[1]).to.be.equal(
            'prototype.constructor.name',
        );
        chai.expect(getPath.getCall(3)).to.be.null;
    });

    it('initPP drops if RTC.createDataChannel is no function', () => {
        isFunctionStub.returns(false);

        getPathAnswers = {
            RTCPeerConnection: function rtcfake() {},
            'prototype.constructor.name': 'something',
            'navigator.onLine': true,
            createDataChannel: true,
        };
        initPP(fakeWindow, opt(), globalStorage);

        chai.expect(getPath.getCall(3).args[1]).to.be.equal(
            'createDataChannel',
        );
        chai.expect(bind.called).to.be.false;
        chai.expect(getPath.getCall(4)).to.be.null;
    });

    it('initPP drops if pc.createOffer.length', () => {
        isFunctionStub.returns(true);
        bind.returns(() => {});
        getPathAnswers = {
            RTCPeerConnection: function rtcfake() {},
            'prototype.constructor.name': 'something',
            'navigator.onLine': true,
            createDataChannel: true,
            createOffer: [1, 2],
        };
        initPP(fakeWindow, opt(), globalStorage);
        chai.expect(getPath.getCall(4).args[1]).to.be.equal('createOffer');
        sinon.assert.called(bind);
        chai.expect(getPath.getCall(5)).to.be.null;
    });

    it('initPP drops if pc.createOffer is not a function', () => {
        isFunctionStub.callsFake((obj: any) => {
            if (obj === 'createOffer') {
                return false;
            }
            return true;
        });
        bind.returns(() => {});
        getPathAnswers = {
            RTCPeerConnection: function rtcfake() {},
            'prototype.constructor.name': 'something',
            'navigator.onLine': true,
            createDataChannel: true,
            createOffer: 'createOffer',
        };
        initPP(fakeWindow, opt(), globalStorage);

        chai.expect(getPath.getCall(4).args[1]).to.be.equal('createOffer');
        chai.expect(bind.called).to.be.true;
        chai.expect(getPath.getCall(5)).to.be.null;
    });

    it('initPP setLocalDescription is not a function', () => {
        isFunctionStub.callsFake((obj: any) => {
            if (obj === 'testSetLocalDescription') {
                return false;
            }
            return true;
        });
        bind.returns(() => {});
        getPathAnswers = {
            RTCPeerConnection: function rtcfake() {},
            'prototype.constructor.name': 'something',
            'navigator.onLine': true,
            createDataChannel: true,
            createOffer: true,
            then: 'testThen',
            setLocalDescription: 'testSetLocalDescription',
        };
        initPP(fakeWindow, opt(), globalStorage);

        chai.expect(getPath.getCall(5).args[1]).to.be.equal('then');
        chai.expect(bind.getCall(2).args[0]).to.be.equal('testThen');

        bind.getCall(2).args[2]('test description');

        chai.expect(getPath.getCall(6).args[1]).to.be.equal(
            'setLocalDescription',
        );

        chai.expect(bind.getCall(3)).to.be.null;
    });

    it('initPP setLocalDescription is a function', () => {
        isFunctionStub.returns(true);
        bind.returns(() => {});
        getPathAnswers = {
            RTCPeerConnection: function rtcfake() {},
            'prototype.constructor.name': 'something',
            'navigator.onLine': true,
            createDataChannel: true,
            createOffer: true,
            then: 'testThen',
            setLocalDescription: 'testSetLocalDescription',
        };
        initPP(fakeWindow, opt(), globalStorage);

        bind.getCall(2).args[2]('test description');

        chai.expect(bind.getCall(3).args[2]).to.be.equal('test description');
    });

    it('initPP onicecandidate', () => {
        isFunctionStub.returns(true);
        bind.returns(() => {});
        getPathAnswers = {
            RTCPeerConnection: function rtcfake() {},
            'prototype.constructor.name': 'something',
            'navigator.onLine': true,
            createDataChannel: true,
            createOffer: true,
            then: 'testThen',
            setLocalDescription: 'testSetLocalDescription',
            close: 'testClose',
            'localDescription.sdp': 'c=IN 1234 5.6.7.8',
        };
        initPP(fakeWindow, opt(), globalStorage);

        chai.expect(mix.called).to.be.true;

        const obj = mix.getCall(0).args[1];
        obj.onicecandidate();

        chai.expect(fnv32a.getCall(0).args[0]).to.be.equal('5.6.7.8');
    });
});
