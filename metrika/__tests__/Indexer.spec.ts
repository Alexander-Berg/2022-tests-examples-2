import * as chai from 'chai';
import * as sinon from 'sinon';
import * as treeWalker from '@src/utils/treeWalker';
import * as events from '@src/utils/events';
import * as time from '@src/utils/time';
import * as asyncUtils from '@src/utils/async';
import * as defer from '@src/utils/defer';
import * as valid from '../../utils/checkCtx';
import { NODE_ID_PROPERTY } from '../consts';
import {
    Indexer,
    TIMEOUT_BETWEEN_SENDING_DATA,
    NODE_ADD_EVENT_KEY_PREFIX,
    NODE_REMOVAL_EVENT_KEY_PREFIX,
    MAX_EXECUTION_TIME,
} from '../Indexer';
import * as nodeInfo from '../../utils/collectNodeInfo';

describe('Indexer', () => {
    const timeoutId = 123;
    const sandbox = sinon.createSandbox();
    const fakeEmitter: any = {
        on: sandbox.stub(),
        trigger: sandbox.stub(),
    };
    const fakeTime: any = {
        getMs: sandbox.stub().returns(100),
    };

    let timeOneStub: sinon.SinonStub<any, any>;
    let walkTreeStub: sinon.SinonStub<any, any>;
    let emitterStub: sinon.SinonStub<any, any>;
    let collectNodeInfoStub: sinon.SinonStub<any, any>;
    let iterForOfStub: sinon.SinonStub<any, any>;
    let iterForEachStub: sinon.SinonStub<any, any>;
    let iterForEachUntilMaxTimeStub: sinon.SinonStub<any, any>;
    let setDeferStub: sinon.SinonStub<any, any>;
    let clearDeferStub: sinon.SinonStub<any, any>;
    let isValid: sinon.SinonStub<any, any>;

    let iterator: any = null;

    beforeEach(() => {
        iterator = null;
        isValid = sandbox.stub(valid, 'isValidCtx');
        isValid.returns(true);
        timeOneStub = sandbox.stub(time, 'TimeOne');
        timeOneStub.returns(fakeTime);
        collectNodeInfoStub = sandbox.stub(nodeInfo, 'collectNodeInfo');
        collectNodeInfoStub.callsFake(
            (_: any, node: any) =>
                ({
                    name: node.nodeName,
                    id: node[NODE_ID_PROPERTY],
                } as any),
        );
        clearDeferStub = sandbox.stub(defer, 'clearDefer');
        setDeferStub = sandbox.stub(defer, 'setDefer');
        setDeferStub.returns(timeoutId);
        walkTreeStub = sandbox.stub(treeWalker, 'eachNode');
        walkTreeStub.callsFake((_, rootNode, callback) => callback(rootNode));
        emitterStub = sandbox.stub(events, 'emitter');
        emitterStub.returns(fakeEmitter);
        iterForOfStub = sandbox.stub(asyncUtils, 'iterForOf');
        iterForOfStub.callsFake((array: any[], cb: Function) => {
            return (iter: any) => {
                iterator = iter;
                array.forEach(cb as any);
            };
        });
        iterForEachStub = sandbox.stub(asyncUtils, 'iterForEach');
        iterForEachStub.returns('forEach');
        iterForEachUntilMaxTimeStub = sandbox.stub(
            asyncUtils,
            'iterForEachUntilMaxTime',
        );
        iterForEachUntilMaxTimeStub.returns('maxTime');
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('Indexes data correctly', () => {
        const ctx: any = {
            Array,
            document: {
                documentElement: { nodeName: 'html' },
            },
        };
        const recorderOptions: any = {};
        const indexer = new Indexer(ctx, recorderOptions);
        chai.assert(emitterStub.calledWith(ctx));

        const eventCB = () => {
            // DO NOTHING
        };
        indexer.on('div', NODE_ADD_EVENT_KEY_PREFIX, eventCB);
        indexer.on('div', NODE_REMOVAL_EVENT_KEY_PREFIX, eventCB);
        let [name, callback] = fakeEmitter.on.getCall(0).args;
        chai.expect(name).to.deep.equal([`${NODE_ADD_EVENT_KEY_PREFIX}div`]);
        chai.expect(callback).to.equal(eventCB);
        [name, callback] = fakeEmitter.on.getCall(1).args;
        chai.expect(name).to.deep.equal([
            `${NODE_REMOVAL_EVENT_KEY_PREFIX}div`,
        ]);
        chai.expect(callback).to.equal(eventCB);

        indexer.start();
        const [deferCtx, cb, timeout, eventLoggerName] =
            setDeferStub.getCall(0).args;
        chai.expect(deferCtx).to.equal(ctx);
        chai.expect(timeout).to.be.equal(TIMEOUT_BETWEEN_SENDING_DATA);
        chai.expect(eventLoggerName).equals('i.s');

        const node: any = {
            nodeName: 'div',
        };
        const parent: any = {
            nodeName: 'div',
        };
        const next: any = {
            nodeName: 'div',
        };
        const prev: any = {
            nodeName: 'div',
        };
        const sendResult = sinon.stub();
        indexer.handleNodesAdd({
            nodes: [parent, node, next, prev],
            sendResult,
        });

        chai.expect(parent[NODE_ID_PROPERTY]).to.equal(1);
        chai.expect(node[NODE_ID_PROPERTY]).to.equal(2);
        chai.expect(next[NODE_ID_PROPERTY]).to.equal(3);
        chai.expect(prev[NODE_ID_PROPERTY]).to.equal(4);

        indexer.setIndexOptions(node, {
            forceParent: parent,
            forceNext: next,
            forcePrevious: prev,
            forceTextContent: 'text',
            forceAttributes: { attr: 'val1' },
        });

        let [eventName, event] = fakeEmitter.trigger.getCall(0).args;
        chai.expect(eventName).to.equal(`${NODE_ADD_EVENT_KEY_PREFIX}div`);
        chai.expect(event).to.deep.equal({
            data: {
                id: 1,
                node: parent,
            },
        });

        [eventName, event] = fakeEmitter.trigger.getCall(1).args;
        chai.expect(eventName).to.equal(`${NODE_ADD_EVENT_KEY_PREFIX}div`);
        chai.expect(event).to.deep.equal({
            data: {
                id: 2,
                node,
            },
        });

        [eventName, event] = fakeEmitter.trigger.getCall(2).args;
        chai.expect(eventName).to.deep.equal(`${NODE_ADD_EVENT_KEY_PREFIX}div`);
        chai.expect(event).to.deep.equal({
            data: {
                id: 3,
                node: next,
            },
        });

        [eventName, event] = fakeEmitter.trigger.getCall(3).args;
        chai.expect(eventName).to.equal(`${NODE_ADD_EVENT_KEY_PREFIX}div`);
        chai.expect(event).to.deep.equal({
            data: {
                id: 4,
                node: prev,
            },
        });

        indexer.removeNode(node);

        let [
            collectCtx,
            nodeInfoNode,
            recorderOpts,
            id,
            forceParent,
            forcePrevious,
            forceNext,
            forceAttributes,
            forceTextContent,
        ] = collectNodeInfoStub.getCall(0).args;

        chai.expect(collectCtx).to.equal(ctx);
        chai.expect(recorderOptions).to.equal(recorderOpts);
        chai.expect(id).to.equal(2);

        chai.expect(forceTextContent).to.equal('text');
        chai.expect(forceAttributes).to.deep.equal({ attr: 'val1' });

        chai.expect(nodeInfoNode).to.equal(node);
        chai.expect(forceParent).to.equal(1);
        chai.expect(forcePrevious).to.equal(4);
        chai.expect(forceNext).to.equal(3);

        [eventName, event] = fakeEmitter.trigger.getCall(4).args;
        chai.expect(eventName).to.equal(`${NODE_REMOVAL_EVENT_KEY_PREFIX}div`);
        chai.expect(event).to.deep.equal({
            data: {
                id: 2,
                node,
            },
        });

        cb();

        chai.assert(setDeferStub.calledTwice);
        chai.expect(iterator).to.equal('maxTime');
        chai.assert(
            iterForEachUntilMaxTimeStub.calledWith(ctx, MAX_EXECUTION_TIME),
        );
        let [indexedNodes] = sendResult.getCall(0).args;
        chai.expect(indexedNodes).to.deep.equal([
            {
                id: 1,
                name: 'div',
            },
            {
                id: 2,
                name: 'div',
            },
            {
                id: 3,
                name: 'div',
            },
            {
                id: 4,
                name: 'div',
            },
        ]);

        collectNodeInfoStub.resetHistory();
        indexer.handleNodesAdd({
            nodes: [ctx.document.documentElement],
            sendResult,
        });

        indexer.stop();

        chai.assert(clearDeferStub.calledWith(ctx, timeoutId));
        [
            collectCtx,
            nodeInfoNode,
            recorderOpts,
            id,
            forceParent,
            forcePrevious,
            forceNext,
            forceAttributes,
            forceTextContent,
        ] = collectNodeInfoStub.getCall(0).args;

        chai.expect(collectCtx).to.equal(ctx);
        chai.expect(recorderOptions).to.equal(recorderOpts);
        chai.expect(id).to.equal(5);

        chai.expect(forceTextContent).to.equal(undefined);
        chai.expect(forceAttributes).to.deep.equal(undefined);

        chai.expect(nodeInfoNode).to.equal(ctx.document.documentElement);
        chai.expect(forceParent).to.equal(0);
        chai.expect(forcePrevious).to.equal(null);
        chai.expect(forceNext).to.equal(null);

        [indexedNodes] = sendResult.getCall(1).args;
        chai.expect(indexedNodes).to.deep.equal([
            {
                id: 5,
                name: 'html',
            },
        ]);
        chai.expect(iterator).to.equal('forEach');
        chai.assert(iterForEachStub.called);
    });

    it('Accumulates indexOptions correctly', () => {
        const ctx: any = {
            Array,
            document: {
                documentElement: { nodeName: 'html' },
            },
        };
        const recorderOptions: any = {};
        const indexer = new Indexer(ctx, recorderOptions);
        const sendResult = sinon.stub();
        const node = {
            nodeName: 'html',
        } as any;
        indexer.handleNodesAdd({
            sendResult,
            nodes: [node],
        });

        indexer.setIndexOptions(node, { forceTextContent: 'this is first' });
        indexer.setIndexOptions(node, { forceTextContent: 'this is second' });

        let [
            collectCtx,
            nodeInfoNode,
            recorderOpts,
            id,
            forceParent,
            forcePrevious,
            forceNext,
            forceAttributes,
            forceTextContent,
        ] = collectNodeInfoStub.getCall(0).args;

        chai.expect(collectCtx).to.equal(ctx);
        chai.expect(recorderOptions).to.equal(recorderOpts);
        chai.expect(id).to.equal(1);

        chai.expect(forceTextContent).to.equal('this is first');
        chai.expect(forceAttributes).to.deep.equal(undefined);

        chai.expect(nodeInfoNode).to.equal(node);
        chai.expect(forceParent).to.equal(0);
        chai.expect(forcePrevious).to.equal(null);
        chai.expect(forceNext).to.equal(null);

        let [indexedNodes] = sendResult.getCall(0).args;
        chai.expect(indexedNodes).to.deep.equal([
            {
                id: 1,
                name: 'html',
            },
        ]);

        indexer.handleNodesAdd({
            sendResult,
            nodes: [node],
        });
        indexer.indexNode(node);

        [
            collectCtx,
            nodeInfoNode,
            recorderOpts,
            id,
            forceParent,
            forcePrevious,
            forceNext,
            forceAttributes,
            forceTextContent,
        ] = collectNodeInfoStub.getCall(1).args;

        chai.expect(collectCtx).to.equal(ctx);
        chai.expect(recorderOptions).to.equal(recorderOpts);
        chai.expect(id).to.equal(1);

        chai.expect(forceTextContent).to.equal('this is second');
        chai.expect(forceAttributes).to.deep.equal(undefined);

        chai.expect(nodeInfoNode).to.equal(node);
        chai.expect(forceParent).to.equal(0);
        chai.expect(forcePrevious).to.equal(null);
        chai.expect(forceNext).to.equal(null);

        [indexedNodes] = sendResult.getCall(1).args;
        chai.expect(indexedNodes).to.deep.equal([
            {
                id: 1,
                name: 'html',
            },
        ]);
    });
});
