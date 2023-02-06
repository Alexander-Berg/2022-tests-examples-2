import { expect } from 'chai';
import * as sinon from 'sinon';
import { getdiff, getPerformanceDiff, PerfDiffs } from '../performanceTiming';

describe('perfomanceTiming', function test() {
    const ctx: Record<string, any> = {};
    const sandbox = sinon.createSandbox();
    beforeEach(() => {
        ctx.perfomanceMock = {} as any;
        ctx.timingMock = {} as any;
        ctx.leftStub = sandbox.stub();
        ctx.rightStub = sandbox.stub();
        ctx.diffs = () => [[ctx.leftStub, ctx.rightStub]];
    });
    afterEach(() => {
        sandbox.restore();
    });
    describe('perfomance Diff', () => {
        it(`checks  empty array`, () => {
            const diffs: PerfDiffs = [];
            const result = getPerformanceDiff(
                ctx.perfomanceMock,
                ctx.timingMock,
                diffs,
            );
            expect(result).to.be.empty;
        });
        it(`checks left function undef`, () => {
            ctx.leftStub.returns(0);
            const result = getPerformanceDiff(
                ctx.perfomanceMock,
                ctx.timingMock,
                ctx.diffs(),
            );
            sinon.assert.calledWith(
                ctx.leftStub,
                ctx.perfomanceMock,
                ctx.timingMock,
            );
            expect(result).to.be.deep.eq([null]);
        });
        it(`checks left function val`, () => {
            ctx.leftStub.returns(1);
            const result = getPerformanceDiff(
                ctx.perfomanceMock,
                ctx.timingMock,
                ctx.diffs(),
            );
            sinon.assert.calledWith(
                ctx.leftStub,
                ctx.perfomanceMock,
                ctx.timingMock,
            );
            expect(result).to.be.deep.eq([1]);
        });
        it(`checks right function`, () => {
            ctx.leftStub = '';
            ctx.rightStub = sandbox.spy();
            const result = getPerformanceDiff(
                ctx.perfomanceMock,
                ctx.timingMock,
                ctx.diffs(),
            );
            sinon.assert.notCalled(ctx.rightStub);
            expect(result).to.be.deep.eq([null]);
        });
        it('returns null when timing is negative', () => {
            ctx.leftStub = 'a';
            ctx.rightStub = 'b';
            ctx.timingMock.a = 1;
            ctx.timingMock.b = 10;
            const result = getPerformanceDiff(
                ctx.perfomanceMock,
                ctx.timingMock,
                ctx.diffs(),
            );
            expect(result).to.be.deep.eq([null]);
        });
        it('returns val when timing is positive', () => {
            ctx.leftStub = 'a';
            ctx.rightStub = 'b';
            ctx.timingMock.a = 10.3;
            ctx.timingMock.b = 1;
            const result = getPerformanceDiff(
                ctx.perfomanceMock,
                ctx.timingMock,
                ctx.diffs(),
            );
            expect(result).to.be.deep.eq([9]);
        });
        it('returns null when timing is too big', () => {
            ctx.leftStub = 'a';
            ctx.rightStub = 'b';
            ctx.timingMock.a = 37e5;
            ctx.timingMock.b = 10;
            const result = getPerformanceDiff(
                ctx.perfomanceMock,
                ctx.timingMock,
                ctx.diffs(),
            );
            expect(result).to.be.deep.eq([null]);
        });
        it('returns null when timing will be late', () => {
            ctx.leftStub = 'loadEventStart';
            ctx.rightStub = 'b';
            ctx.timingMock.loadEventStart = 0;
            ctx.timingMock.b = 0;
            const result = getPerformanceDiff(
                ctx.perfomanceMock,
                ctx.timingMock,
                ctx.diffs(),
            );
            expect(result).to.be.deep.eq([null]);
        });
        it('returns 0 when timing actual', () => {
            ctx.leftStub = 'domainLookupEnd';
            ctx.rightStub = 'b';
            ctx.timingMock.domainLookupEnd = 0;
            ctx.timingMock.b = 0;
            const result = getPerformanceDiff(
                ctx.perfomanceMock,
                ctx.timingMock,
                ctx.diffs(),
            );
            expect(result).to.be.deep.eq([0]);
        });
        it('returns val if only one timing', () => {
            const diffs = [['a']] as any;
            ctx.timingMock.a = 9.5;
            const result = getPerformanceDiff(
                ctx.perfomanceMock,
                ctx.timingMock,
                diffs,
            );
            expect(result).to.be.deep.eq([10]);
        });
    });
    describe('getDiff', () => {
        it('returns null if emplty diff', () => {
            const result = getdiff([], []);
            expect(result).to.be.eq(null);
        });
        it('rewrite new vals', () => {
            const lastPerf = [0, 10];
            const newPerf = [0, 1];
            const result = getdiff(lastPerf, newPerf);
            expect(result).to.be.deep.eq([null, 1]);
            expect(lastPerf).to.be.deep.eq([0, 1]);
        });
        it('create new vals if old is empty', () => {
            const lastPerf: any[] = [];
            const newPerf = [0, 1];
            const result = getdiff(lastPerf, newPerf);
            expect(result).to.be.deep.eq([0, 1]);
            expect(lastPerf).to.be.deep.eq([0, 1]);
        });
    });
});
