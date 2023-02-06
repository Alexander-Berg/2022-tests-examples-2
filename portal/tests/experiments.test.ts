/* eslint-env node, mocha */

import * as assert from 'assert';
import {Response} from 'express';
import {experiments, RequestWithExps} from '@server/libs/experiments';

const req = {
    query: {
        experiments: 'test_exp1,test_exp2,test_exp3=bar',
        flags: 'test_flag1,test_flag2'
    }
};

describe('experiments', () => {
    it('init', () => {
        const mockReq = {...req} as unknown as RequestWithExps;

        experiments.init(mockReq, null as unknown as Response, () => undefined);
        assert.ok(mockReq.experiments.has('test_exp1'));
        assert.ok(mockReq.experiments.has('test_exp2'));
        assert.ok(!mockReq.experiments.has('test_exp3'));

        assert.strictEqual(mockReq.flags.test_flag1, 1);
        assert.strictEqual(mockReq.flags.test_flag2, 1);
        assert.strictEqual(mockReq.flags.test_exp3, 'bar');
    });

    it('test', () => {
        const mockReq = {...req} as unknown as RequestWithExps;
        experiments.init(mockReq, null as unknown as Response, () => undefined);

        assert.ok(experiments.test(mockReq, 'test_exp2'));
    });

    it('testFlag', () => {
        const mockReq = {...req} as unknown as RequestWithExps;
        experiments.init(mockReq, null as unknown as Response, () => undefined);

        assert.ok(experiments.testFlag(mockReq, 'test_flag2'));
        assert.ok(experiments.testFlag(mockReq, 'test_exp3'));
        assert.ok(!experiments.testFlag(mockReq, 'nonexistent_flag'));
    });

    it('getFlag', () => {
        const mockReq = {...req} as unknown as RequestWithExps;
        experiments.init(mockReq, null as unknown as Response, () => undefined);

        assert.strictEqual(experiments.getFlag(mockReq, 'test_flag2'), 1);
        assert.strictEqual(experiments.getFlag(mockReq, 'test_exp3'), 'bar');
        assert.strictEqual(experiments.getFlag(mockReq, 'nonexistent_flag'), undefined);
    });
});
