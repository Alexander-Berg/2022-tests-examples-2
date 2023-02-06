import * as deferUtils from '@src/utils/defer';
import * as sinon from 'sinon';
import * as chai from 'chai';
import { StylesheetCaptor, STYLECHANGE_EVENT_NAME } from '../StylesheetCaptor';
import { createRecorderMock } from '../../AbstractCaptor/__tests__/createMockRecorder';
import { NODE_ADD_EVENT_KEY_PREFIX } from '../../../indexer/Indexer';
import { EVENT_EVENT_TYPE } from '../../AbstractCaptor/AbstractCaptor';

describe('SrcsetLoadCaptor', () => {
    let setDeferStub: sinon.SinonStub<any, any>;
    let clearDeferStub: sinon.SinonStub<any, any>;
    let recorder: any;

    beforeEach(() => {
        recorder = createRecorderMock();
        const { sandbox } = recorder.test;
        setDeferStub = sandbox.stub(deferUtils, 'setDefer');
        clearDeferStub = sandbox.stub(deferUtils, 'clearDefer');
    });

    afterEach(() => {
        recorder.test.restore();
    });

    it('Records stylesheet dynamic changes', () => {
        const win: any = {
            CSSStyleSheet: {
                prototype: {
                    addRule: function addRule() {
                        // do nothing
                    },
                    insertRule: function insertRule() {
                        // do nothing
                    },
                    removeRule: function removeRule() {
                        // do nothing
                    },
                    deleteRule: function deleteRule() {
                        // do nothing
                    },
                },
            },
        };
        const captor = new StylesheetCaptor(win, recorder, 's');
        captor.start();

        const addRule = sinon.stub();
        const insertRule = sinon.stub();
        const removeRule = sinon.stub();
        const deleteRule = sinon.stub();
        const fakeStyleSheet = {
            rules: [],
            addRule,
            insertRule,
            removeRule,
            deleteRule,
        };
        const styleWithSrc = {
            getAttribute: (name: string) =>
                name === 'src' ? 'something' : null,
            sheet: fakeStyleSheet,
            innerText: null,
        };
        // This one should be ignored
        recorder.test.createEvent(`${NODE_ADD_EVENT_KEY_PREFIX}style`, {
            data: {
                node: styleWithSrc,
                id: 1,
            },
        });

        fakeStyleSheet!.addRule('*', 'color: red');
        let [ctx, cb, timeout] = setDeferStub.getCall(0).args;
        chai.expect(ctx).to.equal(win);
        chai.expect(timeout).to.equal(100);
        cb();

        chai.expect(recorder.test.sendEventObjectSpy.notCalled);
        fakeStyleSheet.addRule.resetHistory();

        const styleWithoutSrc = {
            getAttribute: () => null,
            sheet: fakeStyleSheet,
            innerText: null,
        };
        recorder.test.createEvent(`${NODE_ADD_EVENT_KEY_PREFIX}style`, {
            data: {
                node: styleWithoutSrc,
                id: 2,
            },
        });

        [ctx, cb, timeout] = setDeferStub.getCall(1).args;
        styleWithoutSrc.sheet!.addRule('*', 'color: red');
        styleWithoutSrc.sheet!.insertRule('*{color: blue}', 0);
        styleWithoutSrc.sheet!.removeRule(1);
        styleWithoutSrc.sheet!.deleteRule(0);

        chai.expect(ctx).to.equal(win);
        chai.expect(timeout).to.equal(100);
        cb();

        const [type, data, event] =
            recorder.test.sendEventObjectSpy.getCall(0).args;
        chai.expect(type).to.equal(EVENT_EVENT_TYPE);
        chai.expect(data).to.deep.equal({
            target: 2,
            changes: [
                {
                    op: 'a',
                    index: -1,
                    style: '*{color: red}',
                },
                {
                    op: 'a',
                    index: 0,
                    style: '*{color: blue}',
                },
                {
                    op: 'r',
                    index: 1,
                    style: '',
                },
                {
                    op: 'r',
                    index: 0,
                    style: '',
                },
            ],
        });
        chai.expect(event).to.equal(STYLECHANGE_EVENT_NAME);

        sinon.assert.calledWith(addRule, '*', 'color: red');
        sinon.assert.calledWith(insertRule, '*{color: blue}');
        sinon.assert.calledWith(removeRule, 1);
        sinon.assert.calledWith(deleteRule, 0);

        sinon.assert.calledOn(addRule, fakeStyleSheet);
        sinon.assert.calledOn(insertRule, fakeStyleSheet);
        sinon.assert.calledOn(removeRule, fakeStyleSheet);
        sinon.assert.calledOn(deleteRule, fakeStyleSheet);

        captor.stop();

        chai.expect(fakeStyleSheet.addRule.name).to.equal('bound addRule');
        chai.expect(fakeStyleSheet.removeRule.name).to.equal(
            'bound removeRule',
        );
        chai.expect(fakeStyleSheet.insertRule.name).to.equal(
            'bound insertRule',
        );
        chai.expect(fakeStyleSheet.deleteRule.name).to.equal(
            'bound deleteRule',
        );

        chai.assert(clearDeferStub.called);
    });
});
