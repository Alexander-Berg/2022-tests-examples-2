import * as chai from 'chai';
import * as sinon from 'sinon';
import * as obj from '@src/utils/object';
import { plugins } from '../plugins';

describe('plugins', () => {
    let commonWindowStub: Window;
    const sandbox = sinon.createSandbox();

    const pluginsList = [
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
    pluginsList.forEach((plugin) => {
        // eslint-disable-next-line no-param-reassign
        plugin[Symbol.iterator] = () => {
            let current = -1;
            return {
                next() {
                    if (current + 1 in plugin) {
                        current += 1;
                        return {
                            done: false,
                            value: plugin[current],
                        };
                    }
                    return {
                        done: true,
                    };
                },
            };
        };
    });
    let lenStub: sinon.SinonStub<any, any>;
    beforeEach(() => {
        lenStub = sandbox.stub(obj, 'len');
    });
    afterEach(() => {
        sandbox.restore();
    });
    it('should handle empty mimeType', () => {
        const plug = {
            name: 'test1',
            description: 'desc1',
        };
        const plugList = {
            0: plug,
            length: 1,
        };
        lenStub.callsFake((lenObj) => {
            if (lenObj === plugList) {
                return 1;
            }
            return false;
        });
        const res = plugins({
            navigator: {
                plugins: plugList,
            },
        } as any);
        chai.expect(res).to.be.deep.eq(['test1,desc1,']);
    });
    it('should return empty str if plugins is empty', () => {
        lenStub.returns(null);
        const res = plugins({} as any);
        chai.expect(res).to.be.eq('');
    });

    it('should return test plugins as strings', () => {
        lenStub.returns(1);
        const answer = [
            'test1,desc1,mimedesc0,test-pdf,pdf,mimedesc1,test-exe,exe',
            'test2,desc2,mimedesc2,test-zip,zip,mimedesc3,test-xlsx,xlsx',
            'null Plugin,,',
        ];
        commonWindowStub = {
            navigator: {
                plugins: pluginsList,
            },
        } as any;
        const result = plugins(commonWindowStub);
        chai.expect(result).to.have.deep.members(answer);
    });
});
