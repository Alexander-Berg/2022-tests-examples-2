import * as sinon from 'sinon';
import { AbstractCaptor } from '../AbstractCaptor';
import { createRecorderMock } from './createMockRecorder';

describe('AbstractCaptor', () => {
    const win: any = {};
    const target = {};

    let testHandler: sinon.SinonSpy;
    let secondTestHandler: sinon.SinonSpy;

    let recorder: any;

    class TestCaptor extends AbstractCaptor {
        handlers = [
            [['testEvent'], testHandler, target],
            [['secondTestEvent'], secondTestHandler, target],
        ] as any;
    }

    const sandbox = sinon.createSandbox();

    beforeEach(() => {
        testHandler = sandbox.spy();
        secondTestHandler = sandbox.spy();
        recorder = createRecorderMock();
    });

    afterEach(() => {
        sandbox.restore();
        recorder.test.restore();
    });

    it('captor lifecycle', () => {
        const captor = new TestCaptor(win, recorder, 'a');
        captor.start();
        [
            { name: 'testEvent', handler: testHandler },
            { name: 'secondTestEvent', handler: secondTestHandler },
        ].forEach(({ name, handler }) => {
            recorder.test.createEvent(name);
            sinon.assert.called(handler);
        });

        captor.stop();
        sinon.assert.calledTwice(recorder.test.offEventSpy);
    });
});
