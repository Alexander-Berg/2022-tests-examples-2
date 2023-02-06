import { taskFork } from '@src/utils/async';
import { noop } from '@src/utils/function';
import * as JSONModule from '@src/utils/json';
import * as sinon from 'sinon';
import { expect } from 'chai';
import { JSONBufferSerializer } from '../JSONBufferSerializer';

describe('JSONBufferSerializer', () => {
    const data = [{ data: { a: 'b' } }, { data: { c: 'd' } }];
    const win = {} as any;
    const serializer = new JSONBufferSerializer(win as any);
    const sandbox = sinon.createSandbox();
    const testStr = 'testStr';
    let stringifyStub: sinon.SinonStub<any, any>;
    beforeEach(() => {
        stringifyStub = sandbox.stub(JSONModule, 'stringify').returns(testStr);
    });
    afterEach(() => {
        sandbox.restore();
    });
    it('Serializes stuff', () => {
        const task = serializer.serialize(data as any);
        task(
            taskFork(noop, (result) => {
                expect(result).to.be.eq(testStr);
                const [firstBuffer, secondBufFer, packet] =
                    stringifyStub.getCalls();
                let [ctx, buffer] = firstBuffer.args;
                expect(ctx).to.be.eq(win);
                expect(buffer).to.be.deep.eq({ a: 'b' });
                [ctx, buffer] = secondBufFer.args;
                expect(ctx).to.be.eq(win);
                expect(buffer).to.be.deep.eq({ c: 'd' });
                [ctx, buffer] = packet.args;
                expect(ctx).to.be.eq(win);
                expect(buffer).to.be.deep.eq([
                    { data: testStr },
                    { data: testStr },
                ]);
            }),
        );
    });

    it("Calculates it's size", () => {
        const task = serializer.serialize(data as any);
        task(
            taskFork(noop, (info) => {
                expect(serializer.getRequestBodySize(info!)).to.be.ok;
            }),
        );
    });

    it("Doesn't serializes data", () => {
        const newData = [{ data: '{"field": "value"}' }];
        const task = serializer.serialize(newData as any);
        task(
            taskFork(noop, (info) => {
                expect(info).to.be.eq(testStr);
                const calls = stringifyStub.getCalls();
                expect(calls).to.be.lengthOf(1);
                const [packet] = calls;
                const [, buffer] = packet.args;
                expect(buffer).to.be.deep.eq(newData);
            }),
        );
    });
});
