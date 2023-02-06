import * as chai from 'chai';
import * as sinon from 'sinon';
import { taskFork } from '@src/utils/async';
import { noop } from '@src/utils/function';
import { AbstractBufferSerializerInterface } from '../AbstractBufferSerializer';
import { FormvisorSerializer } from '../FormvisorSerializer';

describe('FormvisorSerializer', () => {
    let win: Window;
    const sandbox = sinon.createSandbox();
    let transformer: sinon.SinonStub;
    let getCallbacks: sinon.SinonStub;
    let serializer: AbstractBufferSerializerInterface<Event, number[]>;
    const serializedData = [0, 1, 2, 3];

    beforeEach(() => {
        win = {} as any as Window;

        transformer = sandbox.stub().returns(serializedData);
        getCallbacks = sandbox.stub().returns([transformer]);

        serializer = new FormvisorSerializer(win, getCallbacks);
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('should serialize data', () => {
        const event = {
            type: 'click',
        } as any as Event;
        const targetType = 'window';
        const res = serializer.serializeData(event, {
            type: targetType,
        });
        chai.expect(res).to.be.deep.eq(serializedData);

        sinon.assert.calledWith(transformer, {
            ctx: win,
            evt: event,
        });
        sinon.assert.calledWith(getCallbacks, win, targetType, event.type);
    });

    it('should serialize multiple events', () => {
        const event = {
            type: 'click',
        } as any as Event;
        const serializeTask = serializer.serialize([event, event]);
        serializeTask(
            taskFork(noop, (data) => {
                chai.expect(data).to.be.deep.eq([
                    ...serializedData,
                    ...serializedData,
                ]);
            }),
        );
    });

    it('should calculate serialized data length', () => {
        chai.expect(serializer.getRequestBodySize(serializedData)).to.be.eq(
            serializedData.length,
        );
    });

    it('should return [] when getCallbacks returns nothing', () => {
        getCallbacks.returns(undefined);
        const event = {} as any as Event;
        const res = serializer.serializeData(event);
        chai.expect(res).to.be.deep.eq([]);
    });
});
