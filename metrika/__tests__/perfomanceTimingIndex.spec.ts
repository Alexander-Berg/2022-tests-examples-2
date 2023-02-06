import { expect } from 'chai';
import * as optLib from '@src/utils/counterOptions';
import * as perfLib from '@src/utils/time/performance';
import * as sinon from 'sinon';
import { CounterOptions } from '@src/utils/counterOptions';
import { DEFER_KEY } from '@src/sender/SenderInfo';
import { performanceTiming } from '..';
import * as timingLib from '../performanceTiming';
import { PERF_DIFS_TIMING } from '../legacyPerformanceTiming';

describe('perfomanceTiming brInfo key', function test(this: any) {
    const sandbox = sinon.createSandbox();
    const win = {} as any;
    const opt: CounterOptions = {
        id: 12312,
        counterType: '0',
    };
    const testResult = '1,2';
    const dataSource = {};
    beforeEach(() => {
        this.counterKeyStub = sandbox
            .stub(optLib, 'getCounterKey')
            .returns('jj');
        this.performanceStub = sandbox.stub(perfLib, 'getPerformance');
        this.newPerfStub = sandbox.stub(timingLib, 'getPerformanceDiff');
        this.lastPerfStub = sandbox.stub(timingLib, 'getPerformanceState');
        this.diffStub = sandbox.stub(timingLib, 'getdiff').returns([1, 2]);
    });
    afterEach(() => {
        sandbox.restore();
    });
    it(`return null when it defer hit`, () => {
        const result = performanceTiming(win, opt, {
            urlParams: {
                [DEFER_KEY]: '1',
            },
        });
        sinon.assert.calledWith(this.counterKeyStub, opt);
        sinon.assert.calledWith(this.performanceStub, win);
        expect(result).to.be.null;
    });
    it(`return null when API doesn't supported`, () => {
        const result = performanceTiming(win, opt, {});
        expect(result).to.be.null;
    });
    it(`use new API`, () => {
        const APIStub = sandbox.stub().returns([dataSource]);
        const perfAPI = {
            getEntriesByType: APIStub,
        };
        this.performanceStub.returns(perfAPI);
        const result = performanceTiming(win, opt, {});
        sinon.assert.calledWith(
            this.newPerfStub,
            perfAPI,
            dataSource,
            timingLib.PERF_DIFS_ENTRIES,
        );
        expect(result).to.be.eq(testResult);
    });
    it(`use a old API`, () => {
        const perfAPI = {
            timing: dataSource,
        };
        this.performanceStub.returns(perfAPI);
        const result = performanceTiming(win, opt, {});
        sinon.assert.calledWith(
            this.newPerfStub,
            perfAPI,
            dataSource,
            PERF_DIFS_TIMING,
        );
        expect(result).to.be.eq(testResult);
    });
    it(`use old API if navigation doesn't exist`, () => {
        const APIStub = sandbox.stub().returns([]);
        const perfAPI = {
            getEntriesByType: APIStub,
            timing: dataSource,
        };
        this.performanceStub.returns(perfAPI);
        const result = performanceTiming(win, opt, {});
        sinon.assert.calledWith(
            this.newPerfStub,
            perfAPI,
            dataSource,
            PERF_DIFS_TIMING,
        );
        expect(result).to.be.eq(testResult);
    });
});
