import * as sinon from 'sinon';
import * as chai from 'chai';
import * as treeWalker from '@src/utils/treeWalker';
import { JSDOMWrapper } from '@src/__tests__/utils/jsdom';
import * as valid from '../../../utils/checkCtx';
import {
    MutationCaptor,
    NODE_REMOVE_EVENT_NAME,
    NODE_ADD_EVENT_NAME,
    TEXT_CHANGE_EVENT_NAME,
    ATTR_CHANGE_EVENT_NAME,
} from '../MutationsCaptor';
import * as collectNodeInfo from '../../../utils/collectNodeInfo';
import { MUTATION_EVENT_TYPE } from '../../AbstractCaptor/AbstractCaptor';

describe('MutationCaptor', () => {
    const { window } = new JSDOMWrapper();
    const { document } = window;
    const sandbox = sinon.createSandbox();
    let isValid: sinon.SinonStub<any, any>;

    beforeEach(() => {
        isValid = sandbox.stub(valid, 'isValidCtx');
        isValid.returns(true);
        sandbox
            .stub(treeWalker, 'eachNode')
            .callsFake((ctx, node, callback) => {
                callback(node);
            });
        sandbox
            .stub(collectNodeInfo, 'normalizeAttibute')
            .callsFake((ctx, name, attr, value) => {
                return { isHidden: false, value };
            });
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('Handles mutations and collects forced data of all sorts', () => {
        const observeStub = sinon.stub();
        const disconnectStub = sinon.stub();
        let observerCallback: Function = () => {};
        class FakeMutationObserver {
            observe: Function;

            disconnect: Function;

            constructor(callback: Function) {
                observerCallback = callback;
                this.observe = observeStub;
                this.disconnect = disconnectStub;
            }
        }

        let stamp = 100;
        const fakeContext: any = {
            Array,
            document: {
                documentElement: {},
            },
            MutationObserver: FakeMutationObserver,
        };
        const fakeIndexer: any = {
            setIndexOptions: sinon.stub(),
            indexNode: sinon.stub().callsFake((node: any) => {
                return node.indexId;
            }),
            removeNode: sinon.stub().callsFake((node: any) => {
                return node.indexId;
            }),
            handleNodesAdd: sinon.stub(),
        };
        const fakeRecorder: any = {
            getOptions: () => ({}),
            getIndexer: () => fakeIndexer,
            getEventWrapper: () => ({}),
            stamp: () => stamp,
            sendEventObject: sinon.stub(),
        };

        const captor = new MutationCaptor(fakeContext, fakeRecorder, 'a');
        captor.start();

        const [observeElement, observeOptions] = observeStub.getCall(0).args;
        chai.expect(observeElement).to.equal(
            fakeContext.document.documentElement,
        );
        chai.expect(observeOptions).deep.equal({
            attributes: true,
            characterData: true,
            childList: true,
            subtree: true,
            attributeOldValue: true,
            characterDataOldValue: true,
        });

        const parentNode = document.createElement('div');
        (parentNode as any).indexId = 1;

        const untouchedNode = document.createElement('div');
        (untouchedNode as any).indexId = 2;
        parentNode.appendChild(untouchedNode);

        const removedNode = document.createElement('div');
        (removedNode as any).indexId = 3;
        parentNode.appendChild(removedNode);

        const attributesChangedNode = document.createElement('div');
        (attributesChangedNode as any).indexId = 4;
        parentNode.appendChild(attributesChangedNode);

        const contentTextChangedNode = document.createTextNode('new data');
        (contentTextChangedNode as any).indexId = 5;
        parentNode.appendChild(contentTextChangedNode);

        observerCallback([
            {
                type: 'childList',
                target: parentNode,
                addedNodes: [
                    untouchedNode,
                    removedNode,
                    attributesChangedNode,
                    contentTextChangedNode,
                ],
            },
        ]);

        stamp = 200;

        observerCallback([
            {
                target: parentNode,
                type: 'childList',
                removedNodes: [removedNode],
            },
            {
                target: attributesChangedNode,
                type: 'attributes',
                attributeName: 'attr',
                oldValue: 'old attribute',
            },
            {
                target: contentTextChangedNode,
                type: 'characterData',
                oldValue: 'old text content',
            },
        ]);

        let [optionsNode, indexOptions] =
            fakeIndexer.setIndexOptions.getCall(0).args;
        chai.expect(optionsNode).to.equal(removedNode);
        chai.expect({
            forceAttributes: {},
            forceNext: undefined,
            forcePrevious: undefined,
            forceParent: parentNode,
        }).deep.equal(indexOptions);
        [optionsNode, indexOptions] =
            fakeIndexer.setIndexOptions.getCall(1).args;
        chai.expect({
            forceAttributes: {
                attr: 'old attribute',
            },
        }).deep.equal(indexOptions);
        [optionsNode, indexOptions] =
            fakeIndexer.setIndexOptions.getCall(2).args;
        chai.expect({
            forceAttributes: {},
            forceTextContent: 'old text content',
        }).deep.equal(indexOptions);

        let [indexNode] = fakeIndexer.removeNode.getCall(0).args;
        chai.expect(indexNode).to.equal(removedNode);
        let [type, data, event, eventStamp] =
            fakeRecorder.sendEventObject.getCall(0).args;
        chai.expect({
            index: 1,
            nodes: [3],
        }).deep.equal(data);
        chai.expect(type).to.equal(MUTATION_EVENT_TYPE);
        chai.expect(event).to.equal(NODE_REMOVE_EVENT_NAME);
        chai.expect(eventStamp).to.equal(200);

        [indexNode] = fakeIndexer.indexNode.getCall(0).args;
        chai.expect(contentTextChangedNode).to.equal(indexNode);
        [type, data, event, eventStamp] =
            fakeRecorder.sendEventObject.getCall(1).args;
        chai.expect({
            index: 2,
            value: 'new data',
            target: 5,
        }).deep.equal(data);
        chai.expect(type).to.equal(MUTATION_EVENT_TYPE);
        chai.expect(event).to.equal(TEXT_CHANGE_EVENT_NAME);
        chai.expect(eventStamp).to.equal(200);

        [indexNode] = fakeIndexer.indexNode.getCall(1).args;
        chai.expect(attributesChangedNode).to.equal(indexNode);
        [type, data, event, eventStamp] =
            fakeRecorder.sendEventObject.getCall(2).args;
        chai.expect(type).to.equal(MUTATION_EVENT_TYPE);
        chai.expect(event).to.equal(ATTR_CHANGE_EVENT_NAME);
        chai.expect(eventStamp).to.equal(200);

        const [{ nodes, sendResult }] =
            fakeIndexer.handleNodesAdd.getCall(0).args;
        chai.expect(nodes).deep.equal([
            untouchedNode,
            removedNode,
            attributesChangedNode,
            contentTextChangedNode,
        ]);

        sendResult([
            { id: (untouchedNode as any).indexId },
            { id: (removedNode as any).indexId },
            { id: (attributesChangedNode as any).indexId },
            { id: (contentTextChangedNode as any).indexId },
        ]);
        [type, data, event, eventStamp] =
            fakeRecorder.sendEventObject.getCall(3).args;
        chai.expect({
            index: 0,
            nodes: [
                {
                    id: 2,
                },
                {
                    id: 3,
                },
                {
                    id: 4,
                },
                {
                    id: 5,
                },
            ],
        }).deep.equal(data);
        chai.expect(type).to.equal(MUTATION_EVENT_TYPE);
        chai.expect(event).to.equal(NODE_ADD_EVENT_NAME);
        chai.expect(eventStamp).to.equal(100);

        captor.stop();
        sinon.assert.called(disconnectStub);
    });
});
