import { expect } from 'chai';
import { jsHeap } from '../jsHeap';

describe('jsHeap', () => {
    it('returns string', () => {
        const result = jsHeap({
            performance: {
                memory: {
                    jsHeapSizeLimit: 100,
                },
            },
        } as any);
        expect(result).to.be.eq('100');
    });
});
