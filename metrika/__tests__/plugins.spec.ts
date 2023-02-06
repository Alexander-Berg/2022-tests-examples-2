import * as chai from 'chai';
import { pluginsFactor } from '../plugins';

describe('Antifrod pluginsFactor', () => {
    const plugins = [
        {
            0: { type: 'pdf', suffixes: 'test-pdf', description: 'mimedesc0' },
            1: { type: 'exe', suffixes: 'test-exe', description: 'mimedesc1' },
            name: 'test1',
            description: 'desc1',
        } as any,
        {
            0: { type: 'zip', suffixes: 'test-zip', description: 'mimedesc2' },
            1: {
                type: 'xlsx',
                suffixes: 'test-xlsx',
                description: 'mimedesc3',
            },
            name: 'test2',
            description: 'desc2',
        } as any,
        {
            0: null,
            name: 'null Plugin',
        } as any,
    ];

    it('should send plugins length', () => {
        const res = pluginsFactor({
            navigator: { plugins },
        } as any);
        chai.expect(res).to.be.eq(plugins.length);
    });

    it('should return empty str if plugins is empty', () => {
        const res = pluginsFactor({} as any);
        chai.expect(res).to.be.eq(null);
    });
});
