import * as sinon from 'sinon';
import * as defer from '@src/utils/defer';
import { VisorBuffer } from '../VisorBuffer';
import { AbstractBufferInterface } from '../AbstractBuffer';
import { AbstractBufferSerializerInterface } from '../serializer/AbstractBufferSerializer';

describe('VisorBuffer', () => {
    let win: Window;
    const sandbox = sinon.createSandbox();
    let serializer: AbstractBufferSerializerInterface<Event, number[]>;
    let sender: sinon.SinonStub;
    let buffer: AbstractBufferInterface<Event, number[]>;
    const serializedData = [0, 1, 2, 3];
    const event = {
        type: 'click',
    } as any as Event;
    const targetType = 'window';

    beforeEach(() => {
        win = {} as any as Window;

        sender = sandbox.stub().returns(Promise.resolve());
        serializer = {
            getRequestBodySize: sandbox.stub().returns(1),
            serializeData: sandbox.stub().returns(serializedData),
        } as any;

        sandbox.stub(defer, 'setDefer');

        buffer = new VisorBuffer(win, serializer, sender);
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('should push event into buffer and then flush it manually', () => {
        buffer.push(event, { type: targetType });
        sinon.assert.notCalled(sender);

        // Флашим вручную
        buffer.flush();
        sinon.assert.calledOnce(sender);
        sinon.assert.calledWith(sender, serializedData, [], 1);
    });

    it('should immediately flush buffer if size greater than MAX_CHUNK_SIZE', () => {
        serializer.getRequestBodySize = sandbox.stub().returns(700001);

        // Флашится автоматически (переполнение буффера)
        buffer.push(event, { type: targetType });
        sinon.assert.calledOnce(sender);
    });
});
